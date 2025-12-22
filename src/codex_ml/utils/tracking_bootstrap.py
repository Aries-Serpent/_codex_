from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import os
from typing import Optional


def init_mlflow_offline(tracking_uri: Optional[str] = None) -> dict[str, str]:
    """
    Initialize MLflow in offline/local mode.
    If no tracking_uri is provided, defaults to a local file store ('file:./mlruns').
    Returns resolved environment settings.
    """
    resolved: dict[str, str] = {}
    try:
        import mlflow
    except Exception:
        return {"mlflow": "unavailable"}

    uri = tracking_uri or "file:./mlruns"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    resolved["MLFLOW_TRACKING_URI"] = uri
    try:
        mlflow.set_tracking_uri(resolved["MLFLOW_TRACKING_URI"])
    except Exception as e:
        logger.warning(f"Exception: {e}", exc_info=True)
    return resolved


def init_wandb_offline(project: Optional[str] = None) -> dict[str, str]:
    """
    Initialize Weights & Biases in offline mode (no network).
    Use `wandb sync <run_dir>` later to upload if desired.
    """
    resolved: dict[str, str] = {}
    try:
        import wandb
    except Exception:
        return {"wandb": "unavailable"}

    os.environ["WANDB_MODE"] = "offline"
    resolved["WANDB_MODE"] = "offline"
    run = None
    try:
        run = wandb.init(project=project, mode="offline")
        # Surface mode for tests without requiring API calls
        resolved["wandb_mode"] = (
            getattr(getattr(run, "settings", None), "mode", "offline") or "offline"
        )
    except Exception:
        resolved["wandb_mode"] = "offline"
    finally:
        if run is not None:
            try:
                run.finish()
            except Exception as e:
                logger.warning(f"Exception: {e}", exc_info=True)
    return resolved
