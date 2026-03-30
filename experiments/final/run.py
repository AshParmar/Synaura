"""
Experiment D: full pipeline — classifier → GradCAM → RAG → LLM report (aligned with API logic).
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
from experiments.legacy_report_generator_rag import legacy_generate_report_rag as generate_report
from experiments.legacy_vector_retriever import retrieve_documents
from backend.utils.preprocess import preprocess_image
from backend.vision.gradcam import analyze_region


def _fuzzy_info_from_top(top: dict) -> dict:
    """Interpretation tiers consistent with backend/main.py."""
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

    query = f"{disease} chest x-ray findings treatment"
    docs = retrieve_documents(query)
    # Pass temperature to report generator if supported
    report = generate_report(disease, region, fuzzy_info, docs, [], temperature=temperature)

    return {
        "image": Path(path).name,
        "disease": disease,
        "confidence": confidence,
        "interval": interval,
        "region": region,
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
    out_path = save_result_json("final", Path("all_results.json"), all_results)
    print(f"final: all results -> {out_path}")


if __name__ == "__main__":
    main()
