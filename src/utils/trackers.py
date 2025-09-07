from __future__ import annotations

import os

__all__ = ["init_wandb_offline", "init_mlflow_local"]


def init_wandb_offline(project: str = "codex"):
    """Initialize W&B in offline mode when WANDB_MODE=offline or no WANDB_API_KEY."""
    try:
        import wandb  # type: ignore
    except Exception:
        return None
    mode = os.environ.get("WANDB_MODE", "offline")
    if mode == "offline" or not os.environ.get("WANDB_API_KEY"):
        os.environ.setdefault("WANDB_MODE", "offline")
    return wandb.init(project=project)


def init_mlflow_local():
    """Ensure MLflow logs locally (default mlruns/) unless a tracking URI is set."""
    try:
        import mlflow  # type: ignore  # noqa: F401
    except Exception:
        return None
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        # Default direct/local mode
        pass
    return True
