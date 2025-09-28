"""
Test helper to ensure ``src/`` is importable and configure offline MLflow defaults.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists():
    src_str = str(_src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

if "MLFLOW_TRACKING_URI" not in os.environ:
    try:
        import mlflow  # noqa: F401
    except Exception:
        pass
    else:
        os.environ["MLFLOW_TRACKING_URI"] = "file:./artifacts/mlruns"
