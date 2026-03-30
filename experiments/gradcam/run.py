"""
Experiment C: classifier + fuzzy interval + GradCAM region (same prep as API).
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
from backend.utils.preprocess import preprocess_image
from backend.vision.gradcam import detect_region, generate_gradcam



def run_one(image_path: Path, temperature: float, run_id: int) -> dict:
    path = load_image(image_path)
    results = classify_image(path)
    top = get_top_prediction(results)
    disease = top["disease"]
    lo, hi = top["interval"]

    image_tensor = preprocess_image(path)
    original_image = cv2.imread(path)
    original_image = cv2.resize(original_image, (224, 224))
    original_image = original_image / 255.0

    _, cam_mask = generate_gradcam(model, image_tensor, original_image)
    region = detect_region(cam_mask, disease)

    return {
        "image": Path(path).name,
        "disease": disease,
        "confidence": float(top["confidence"]),
        "interval": [float(lo), float(hi)],
        "region": region,
        "temperature": temperature,
        "run_id": run_id,
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
    out_path = save_result_json("gradcam", Path("all_results.json"), all_results)
    print(f"gradcam: all results -> {out_path}")


if __name__ == "__main__":
    main()
