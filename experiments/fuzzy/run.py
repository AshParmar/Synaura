"""
Experiment B: classifier + fuzzy interval.
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



def run_one(image_path: Path, temperature: float, run_id: int) -> dict:
    path = load_image(image_path)
    results = classify_image(path)
    top = get_top_prediction(results)
    lo, hi = top["interval"]
    return {
        "image": Path(path).name,
        "disease": top["disease"],
        "confidence": float(top["confidence"]),
        "interval": [float(lo), float(hi)],
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
    out_path = save_result_json("fuzzy", Path("all_results.json"), all_results)
    print(f"fuzzy: all results -> {out_path}")


if __name__ == "__main__":
    main()
