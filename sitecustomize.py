# ruff: noqa: E402
"""
Ensure local tracking defaults are applied early while keeping import-order linters calm.
"""

import sys
from pathlib import Path

src_str = str(Path(__file__).parent / "src")
if src_str not in sys.path:
    sys.path.insert(0, src_str)

from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking

ensure_local_tracking()
