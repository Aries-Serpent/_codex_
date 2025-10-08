"""Helpers to configure offline tracking providers locally."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional


def init_mlflow_offline(local_dir: str | None = None) -> str:
    """Ensure MLflow tracks to a local ``file://`` URI and return it."""

    import mlflow

    base = Path(local_dir or (Path.cwd() / "mlruns")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    uri = base.as_uri()
    mlflow.set_tracking_uri(uri)
    return uri


def init_wandb_offline(project: str = "offline", **kwargs: Any) -> Optional[Any]:
    """Initialise Weights & Biases in offline mode if available."""

    os.environ.setdefault("WANDB_MODE", "offline")
    try:
        import wandb

        return wandb.init(project=project, **kwargs)
    except Exception:  # pragma: no cover - best effort in minimal env
        return None
