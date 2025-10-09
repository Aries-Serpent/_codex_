from __future__ import annotations

import os
from typing import Dict, Optional


def init_mlflow_offline(tracking_uri: Optional[str] = None) -> Dict[str, str]:
    """
    Initialize MLflow in offline/local mode.
    If no tracking_uri is provided, defaults to a local file store ('file:./mlruns').
    Returns resolved environment settings.
    """
    resolved: Dict[str, str] = {}
    try:
        import mlflow  # type: ignore
    except Exception:
        return {"mlflow": "unavailable"}

    uri = tracking_uri or "file:./mlruns"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    resolved["MLFLOW_TRACKING_URI"] = uri
    try:
        mlflow.set_tracking_uri(resolved["MLFLOW_TRACKING_URI"])
    except Exception:
        pass
    return resolved


def init_wandb_offline(project: Optional[str] = None) -> Dict[str, str]:
    """
    Initialize Weights & Biases in offline mode (no network).
    Use `wandb sync <run_dir>` later to upload if desired.
    """
    resolved: Dict[str, str] = {}
    try:
        import wandb  # type: ignore
    except Exception:
        return {"wandb": "unavailable"}

    os.environ["WANDB_MODE"] = "offline"
    resolved["WANDB_MODE"] = "offline"
    run = None
    try:
        run = wandb.init(project=project, mode="offline")
        # Surface mode for tests without requiring API calls
        resolved["wandb_mode"] = getattr(getattr(run, "settings", None), "mode", "offline") or "offline"
    except Exception:
        resolved["wandb_mode"] = "offline"
    finally:
        if run is not None:
            try:
                run.finish()
            except Exception:
                pass
    return resolved
