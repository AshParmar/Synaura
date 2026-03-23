# backend/main.py

from fastapi import FastAPI, UploadFile, File
import shutil
import os
import cv2
from langchain_groq import ChatGroq

# --- your modules ---

from backend.classify.clasification import classify_image as predict_disease, model
from backend.vision.gradcam import analyze_region, detect_region
from backend.rag.retriever import retrieve_documents
from backend.rag.report_generator import generate_report
from backend.utils.preprocess import preprocess_image
from backend.rag.query_generator import generate_query
app = FastAPI()


llm = ChatGroq(
    temperature=0.2,
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)
UPLOAD_PATH = "backend/temp_xray.png"


@app.post("/analyze_xray")
async def analyze_xray(file: UploadFile = File(...)):

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
    print("\nBASELINE QUERY:", disease)
    print("RAG QUERY:", rag_query)
    docs = retrieve_documents(rag_query)

    # -------------------------
    # 6. Report Generation
    # -------------------------
    report = generate_report(
        disease,
        region,
        fuzzy_info,
        docs
    )

    # -------------------------
    # 7. Final Response
    # -------------------------
    # numpy scalar types are not JSON-serializable by FastAPI
    return {
        "disease": disease,
        "confidence": float(confidence),
        "interval": [float(interval[0]), float(interval[1])],
        "region": region,
        "report": report,
    }