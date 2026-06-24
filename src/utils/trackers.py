"""
Trackers Module

This module provides functionality for trackers.

Usage:
    from utils.trackers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

__all__ = ["init_mlflow_local", "init_wandb_offline"]


def init_wandb_offline(project: str = "codex"):
    """Initialize W&B in offline mode when WANDB_MODE=offline or no WANDB_API_KEY."""
    try:
        import wandb
    except ImportError:
        logger.warning("wandb not installed; skipping W&B init (pip install wandb)")
        return None
    except AttributeError:
        logger.warning("Unexpected error importing wandb", exc_info=True)
        return None
    if not callable(getattr(wandb, "init", None)):
        logger.warning("wandb stub detected or wandb.init unavailable; skipping W&B init")
        return None
    mode = os.environ.get("WANDB_MODE", "offline")
    if mode == "offline" or not os.environ.get("WANDB_API_KEY"):
        os.environ.setdefault("WANDB_MODE", "offline")
    return wandb.init(project=project)


def init_mlflow_local():
    """Ensure MLflow logs locally (default mlruns/) unless a tracking URI is set."""
    if importlib.util.find_spec("mlflow") is None:
        logger.warning("mlflow not installed; skipping MLflow init (pip install mlflow)")
        return None
    try:
        from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking
    except (ConnectionError, TimeoutError):
        logger.warning("Unexpected error importing mlflow", exc_info=True)
        return None

    requested = os.environ.get("MLFLOW_TRACKING_URI")
    bootstrap_offline_tracking(requested_uri=requested)
    return True
