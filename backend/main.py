# backend/main.py

import os
import shutil
import cv2
import base64

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything that reads env vars

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq

# ── Internal modules ──────────────────────────────────────────────────────────
from backend.classify.clasification import classify_image as predict_disease, model
from backend.vision.gradcam import analyze_region, detect_region
from backend.rag.retriever import retrieve_documents, retrieve_hybrid
from backend.rag.report_generator import generate_report
from backend.utils.preprocess import preprocess_image
from backend.rag.query_generator import generate_query
from backend.rag.dual_retrieval import generate_dual_queries
from backend.rag.imedrag import refine_report

# ── Optional cloud integrations (gracefully disabled if keys are missing) ──────
try:
    from database.crud import save_scan_report, get_reports_for_user
    from database.models import new_scan_report
    _mongo_enabled = bool(os.getenv("MONGODB_URI"))
except ImportError:
    _mongo_enabled = False

try:
    from cloud.gcs_client import upload_scan as gcs_upload_scan
    _gcs_enabled = bool(os.getenv("GCS_BUCKET_NAME"))
except ImportError:
    _gcs_enabled = False

# ── Sentry ────────────────────────────────────────────────────────────────────
_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        traces_sample_rate=0.2,
        environment=os.getenv("ENVIRONMENT", "production"),
    )

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Synaura AI Backend",
    description="Radiology AI analysis — GradCAM · Dual-RAG · i-MedRAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://synaura.vercel.app",  # update with your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


llm = ChatGroq(
    temperature=0.2,
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)
UPLOAD_PATH = "backend/temp_xray.png"


@app.get("/health")
async def health():
    """Lightweight health-check endpoint for Cloud Run readiness probe."""
    return {"status": "ok", "version": "1.0.0"}



@app.post("/analyze_xray")
async def analyze_xray(
    file: UploadFile = File(...),
    x_user_id: str | None = Header(default=None),  # Clerk user ID passed from frontend
):

    # -------------------------
    # 1. Save uploaded image
    # -------------------------
    with open(UPLOAD_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -------------------------
    # 2. Run classifier
    # -------------------------
    results = predict_disease(UPLOAD_PATH)

    # select top disease
    top = max(results, key=lambda x: x["confidence"])

    disease = top["disease"]
    confidence = top["confidence"]
    if confidence > 0.75:
        interpretation = "high likelihood"
    elif confidence > 0.5:
        interpretation = "moderate likelihood"
    else:
        interpretation = "low likelihood"
    interval = top["interval"]
    fuzzy_info = {
        "lower": interval[0],
        "upper": interval[1],
        "interpretation": interpretation
    }

    # -------------------------
    # 3. Prepare for GradCAM
    # -------------------------
    image_tensor = preprocess_image(UPLOAD_PATH)

    original_image = cv2.imread(UPLOAD_PATH)
    original_image = cv2.resize(original_image, (224, 224))
    original_image = original_image / 255.0

    # -------------------------
    # 4. GradCAM (region)
    # -------------------------
    heatmap, region = analyze_region(
        model,
        image_tensor,
        original_image,
        disease
    )

    # -------------------------
    # 5. RAG Retrieval
    # -------------------------
    query = f"{disease} chest x-ray findings treatment"
    rag_query = generate_query(disease, region, fuzzy_info, llm)
    q1, q2 = generate_dual_queries(disease, region, fuzzy_info, llm)

    docs_q1 = retrieve_hybrid(q1)
    docs_q2 = retrieve_hybrid(q2)

    # combine and deduplicate if needed

    # -------------------------
    # 6. Report Generation
    # -------------------------
    # Step 1: initial report (DER)
    report = generate_report(
        disease,
        region,
        fuzzy_info,
        docs_q1,
        docs_q2
)

    # Prepare contexts again
    support_context = "\n".join([doc.page_content for doc in docs_q1[:5]])
    diff_context = "\n".join([doc.page_content for doc in docs_q2[:5]])

    # Step 2: refinement (i-MedRAG)
    report = refine_report(report, support_context, diff_context, llm)

    # -------------------------
    # 7. Final Response
    # -------------------------
    
    # Convert heatmap to base64
    # heatmap is an RGB numpy array from show_cam_on_image (uint8, 0-255)
    # Convert RGB to BGR for cv2.imencode
    heatmap_bgr = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.png', heatmap_bgr)
    heatmap_base64 = base64.b64encode(buffer).decode('utf-8')

    # -------------------------
    # 8. Persist to MongoDB (optional)
    # -------------------------
    gcs_url = None
    if _gcs_enabled:
        try:
            gcs_url = gcs_upload_scan(UPLOAD_PATH)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)

    report_id = None
    if _mongo_enabled and x_user_id:
        try:
            doc = new_scan_report(
                user_id=x_user_id,
                filename=file.filename or "upload.png",
                disease=disease,
                confidence=float(confidence),
                interval=[float(interval[0]), float(interval[1])],
                region=region,
                report=report,
                heatmap_base64=heatmap_base64,
                gcs_url=gcs_url,
            )
            report_id = save_scan_report(doc)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)

    # numpy scalar types are not JSON-serializable by FastAPI
    return {
        "disease": disease,
        "confidence": float(confidence),
        "interval": [float(interval[0]), float(interval[1])],
        "region": region,
        "report": report,
        "heatmap_base64": heatmap_base64,
        "report_id": report_id,
        "gcs_url": gcs_url,
    }


@app.get("/reports/{user_id}")
async def get_user_reports(user_id: str, limit: int = 20):
    """
    Fetch the most recent scan reports for a user.
    Requires MongoDB to be configured (MONGODB_URI in .env).
    """
    if not _mongo_enabled:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Set MONGODB_URI in your environment.",
        )
    reports = get_reports_for_user(user_id, limit=limit)
    return {"user_id": user_id, "reports": reports, "count": len(reports)}