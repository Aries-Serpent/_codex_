"""
Manager Module

This module provides functionality for manager.

Usage:
    from experiments.manager import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from codex_ml.utils.optional import optional_dependency_error

logger = logging.getLogger(__name__)

try:
    import mlflow
except (IOError, OSError):
    mlflow = None


def init_experiment(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    if mlflow is None:
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        )

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)
