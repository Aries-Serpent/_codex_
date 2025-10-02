"""
Test helper to ensure ``src/`` is importable and configure offline MLflow defaults.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking

_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists():
    src_str = str(_src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

ensure_local_tracking()
