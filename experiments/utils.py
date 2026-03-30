"""
Shared helpers for research experiment scripts (no FastAPI).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

EXPERIMENTS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENTS_ROOT.parent
TEST_IMAGES_DIR = PROJECT_ROOT / "data" / "test"
RESULTS_ROOT = PROJECT_ROOT / "results"

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def load_image(path: str | Path) -> str:
    """
    Validate that the image file exists and return its absolute path for downstream use.
    (Classifier and preprocess use file paths; they do not accept in-memory arrays.)
    """
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Image not found: {p}")
    if p.suffix.lower() not in _IMAGE_EXTS:
        raise ValueError(f"Unsupported image extension: {p.suffix}")
    return str(p)


def get_top_prediction(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Select the highest-confidence prediction from classifier output (same rule as API)."""
    if not results:
        raise ValueError(
            "Classifier returned no positive predictions (empty list). "
            "Cannot select a top disease."
        )
    return max(results, key=lambda x: float(x["confidence"]))


def list_test_images() -> List[Path]:
    """Sorted list of image files under data/test_images/."""
    if not TEST_IMAGES_DIR.is_dir():
        return []
    return sorted(
        p
        for p in TEST_IMAGES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
    )


def to_json_safe(obj: Any) -> Any:
    """Convert numpy scalars and nested structures to JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if hasattr(obj, "item") and callable(getattr(obj, "item", None)):
        try:
            return to_json_safe(obj.item())
        except (ValueError, TypeError):
            pass
    return obj


def save_result_json(experiment_subdir: str, image_path: Path, payload: Dict[str, Any]) -> Path:
    """
    Write results/<experiment_subdir>/<image_stem>.json
    """
    out_dir = RESULTS_ROOT / experiment_subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{image_path.stem}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(to_json_safe(payload), f, indent=2, ensure_ascii=False)
    return out_path


def ensure_project_root_on_path() -> Path:
    """Call from experiment scripts so `import backend` works when run as a file."""
    import sys

    root = PROJECT_ROOT
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root
