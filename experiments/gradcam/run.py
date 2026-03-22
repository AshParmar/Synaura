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


def run_one(image_path: Path) -> dict:
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
    }


def main() -> None:
    images = list_test_images()
    if not images:
        print(f"No images found in {TEST_IMAGES_DIR}")
        return
    for img in images:
        payload = run_one(img)
        out = save_result_json("gradcam", img, payload)
        print(f"gradcam: {img.name} -> {out}")


if __name__ == "__main__":
    main()
