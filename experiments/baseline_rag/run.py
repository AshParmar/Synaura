"""
Experiment: Baseline RAG — classifier → GradCAM → vector retrieval → legacy RAG report (no differential diagnosis, no external knowledge)
"""

import sys
import cv2
from pathlib import Path
import os

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
from backend.vision.gradcam import analyze_region
from backend.utils.preprocess import preprocess_image
from experiments.legacy_vector_retriever import retrieve_vector_legacy

from experiments.legacy_report_generator_rag import generate_baseline_rag_report

def _fuzzy_info_from_top(top: dict) -> dict:
    confidence = float(top["confidence"])
    interval = top["interval"]
    return {
        "lower": float(interval[0]),
        "upper": float(interval[1]),
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
    original_image = cv2.resize(original_image, (224, 224)) / 255.0

    _, region = analyze_region(model, image_tensor, original_image, disease)

    # Retrieve docs using legacy vector retriever
    docs = retrieve_vector_legacy(disease, region, fuzzy_info)

    # Generate report using legacy RAG prompt (no differential diagnosis)
    report = generate_baseline_rag_report(disease, region, fuzzy_info, docs, temperature=temperature)

    return {
        "image": Path(path).name,
        "disease": disease,
        "region": region,
        "confidence": confidence,
        "interval": interval,
        "temperature": temperature,
        "run_id": run_id,
        "report": report,
    }


def main() -> None:
    images = list_test_images()
    if not images:
        print(f"No images found in {TEST_IMAGES_DIR}")
        return
    temperatures = [0.2, 0.3, 0.4, 0.5, 0.6]
    all_results = []
    for img in images:
        for run_id, temp in enumerate(temperatures):
            payload = run_one(img, temp, run_id)
            all_results.append(payload)
    # Save all results as a single JSON list
    out_path = save_result_json("baseline_rag", Path("all_results.json"), all_results)
    print(f"baseline_rag: all results -> {out_path}")

if __name__ == "__main__":
    main()
