"""
Run all experiment stages sequentially: baseline → fuzzy → gradcam → final.

Execute from project root:
    python experiments/run_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.utils import PROJECT_ROOT


def main() -> None:
    root = PROJECT_ROOT
    stages = ["baseline", "fuzzy", "gradcam","final","final_rag2", "final_der"]
    for name in stages:
        script = root / "experiments" / name / "run.py"
        if not script.is_file():
            raise FileNotFoundError(f"Missing experiment script: {script}")
        print(f"\n=== Running {name} ===")
        subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            check=True,
        )
    print("\n=== All experiments finished ===")


if __name__ == "__main__":
    main()
