"""
Test helper to ensure ``src/`` is importable and configure offline MLflow defaults.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists():
    src_str = str(_src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking  # noqa: E402

ensure_local_tracking()
