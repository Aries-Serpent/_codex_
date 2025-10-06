from __future__ import annotations

import os
from pathlib import Path


def init_experiment(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("mlflow is required for experiment initialization") from exc

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
