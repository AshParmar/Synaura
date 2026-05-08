"""
Experiment H: full pipeline — classifier → GradCAM → Dual Hybrid Retrieval → DER report → i-MedRAG refinement (final_reports_imedrag phase).
"""

import sys
import cv2
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.utils import (
    TEST_IMAGES_DIR,
    ensure_project_root_on_path,
    get_top_prediction,
    list_test_images,
    load_image,
    save_result_json,
)

ensure_project_root_on_path()

from backend.classify.clasification import classify_image, model
from backend.rag.report_generator import generate_report
from backend.rag.retriever import retrieve_hybrid
from backend.utils.preprocess import preprocess_image
from backend.vision.gradcam import analyze_region
from backend.rag.dual_retrieval import generate_dual_queries
from backend.rag.imedrag import refine_report
from langchain_groq import ChatGroq
import os

def _fuzzy_info_from_top(top: dict) -> dict:
    confidence = float(top["confidence"])
    interval = top["interval"]
    if confidence > 0.75:
        interpretation = "high likelihood"
    elif confidence > 0.5:
        interpretation = "moderate likelihood"
    else:
        interpretation = "low likelihood"
    return {
        "lower": float(interval[0]),
        "upper": float(interval[1]),
        "interpretation": interpretation,
    }


def run_one(image_path: Path, temperature: float, run_id: int) -> dict:
    path = load_image(image_path)
    results = classify_image(path)
    top = get_top_prediction(results)
    disease = top["disease"]
    confidence = float(top["confidence"])
    interval = [float(top["interval"][0]), float(top["interval"][1])]
    fuzzy_info = _fuzzy_info_from_top(top)

    image_tensor = preprocess_image(path)
    original_image = cv2.imread(path)
    original_image = cv2.resize(original_image, (224, 224))
    original_image = original_image / 255.0

    _, region = analyze_region(model, image_tensor, original_image, disease)

    llm = ChatGroq(
        temperature=temperature,
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    q1, q2 = generate_dual_queries(disease, region, fuzzy_info, llm)
    docs_q1 = retrieve_hybrid(q1)
    docs_q2 = retrieve_hybrid(q2)
    # Step 1: DER report
    report = generate_report(disease, region, fuzzy_info, docs_q1, docs_q2)
    # Step 2: i-MedRAG refinement
    support_context = "\n".join([doc.page_content for doc in docs_q1[:5]])
    diff_context = "\n".join([doc.page_content for doc in docs_q2[:5]])
    report = refine_report(report, support_context, diff_context, llm)

    # Gather retrieved contexts as plain text for both queries
    retrieved_contexts = {
        "support": [getattr(doc, "page_content", str(doc)) for doc in docs_q1],
        "differential": [getattr(doc, "page_content", str(doc)) for doc in docs_q2],
    }

    return {
        "image": Path(path).name,
        "disease": disease,
        "confidence": confidence,
        "interval": interval,
        "region": region,
        "temperature": temperature,
        "run_id": run_id,
        "report": report,
        "support_query": q1,
        "differential_query": q2,
        "retrieved_contexts": retrieved_contexts,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run i-MedRAG final report experiment in batches.")
    parser.add_argument('--start', type=int, default=0, help='Start index (inclusive) of images to process')
    parser.add_argument('--end', type=int, default=None, help='End index (exclusive) of images to process')
    parser.add_argument('--output', type=str, default=None, help='Output filename for this batch')
    args = parser.parse_args()

    images = list_test_images()
    if not images:
        print(f"No images found in {TEST_IMAGES_DIR}")
        return
    start = args.start
    end = args.end if args.end is not None else len(images)
    batch_images = images[start:end]
    temperatures = [0.2, 0.3, 0.4, 0.5, 0.6]
    all_results = []
    for img in batch_images:
        for run_id, temp in enumerate(temperatures):
            payload = run_one(img, temp, run_id)
            all_results.append(payload)
    # Output file naming
    if args.output:
        out_filename = args.output
    else:
        out_filename = f"results_{start}_{end}.json"
    out_path = save_result_json("final_reports_imedrag", Path(out_filename), all_results)
    print(f"final_reports_imedrag: batch results -> {out_path}")

if __name__ == "__main__":
    main()
