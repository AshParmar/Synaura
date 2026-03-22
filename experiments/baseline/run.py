"""
Experiment A: classifier only — top disease + confidence.
"""

import sys
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

from backend.classify.clasification import classify_image


def run_one(image_path: Path) -> dict:
    path = load_image(image_path)
    results = classify_image(path)
    top = get_top_prediction(results)
    return {
        "image": Path(path).name,
        "disease": top["disease"],
        "confidence": float(top["confidence"]),
    }


def main() -> None:
    images = list_test_images()
    if not images:
        print(f"No images found in {TEST_IMAGES_DIR}")
        return
    for img in images:
        payload = run_one(img)
        out = save_result_json("baseline", img, payload)
        print(f"baseline: {img.name} -> {out}")


if __name__ == "__main__":
    main()
