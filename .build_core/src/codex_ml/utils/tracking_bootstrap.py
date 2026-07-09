"""
Tracking Bootstrap Module

This module provides functionality for tracking bootstrap.

Usage:
    from utils.tracking_bootstrap import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def init_mlflow_offline(tracking_uri: Optional[str] = None) -> dict[str, str]:
    """
    Initialize MLflow in offline/local mode.
    If no tracking_uri is provided, defaults to a local file store ('file:./mlruns').
    Returns resolved environment settings.
    """
    resolved: dict[str, str] = {}
    try:
        import mlflow
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return {"mlflow": "unavailable"}

    uri = tracking_uri or "file:./mlruns"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    resolved["MLFLOW_TRACKING_URI"] = uri
    try:
        mlflow.set_tracking_uri(resolved["MLFLOW_TRACKING_URI"])
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    return resolved


def init_wandb_offline(project: Optional[str] = None) -> dict[str, str]:
    """
    Initialize Weights & Biases in offline mode (no network).
    Use `wandb sync <run_dir>` later to upload if desired.
    """
    resolved: dict[str, str] = {}
    try:
        import wandb
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
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
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        resolved["wandb_mode"] = "offline"
    finally:
        if run is not None:
            try:
                run.finish()
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    return resolved
