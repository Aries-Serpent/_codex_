"""
Logging Factory Module

This module provides functionality for logging factory.

Usage:
    from utils.logging_factory import ...

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


def init_logging(
    mode: Optional[str] = None, project: str = "codex", wandb_disable_env: bool = True
) -> logging.Logger:
    """Initialize logging with safe offline defaults.

    Parameters
    ----------
    mode:
        Optional override for the logging mode.  Supported values:
        ``offline`` (default), ``tensorboard``, or ``wandb``.
    project:
        Logical project name used for logger namespace and optional integrations.
    wandb_disable_env:
        When ``True`` (default) the function enforces ``WANDB_MODE=offline`` unless
        a ``WANDB_API_KEY`` is detected, preventing accidental remote logging.
    """

    resolved_mode = mode or os.environ.get("CODEX_LOG_MODE", "offline")
    logger = logging.getLogger(project)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if not logger.handlers:
        logger.addHandler(handler)

    if resolved_mode == "wandb":
        try:
            import wandb

            if wandb_disable_env and os.environ.get("WANDB_API_KEY") is None:
                logger.warning("WANDB_API_KEY not found — running wandb in offline mode")
                os.environ["WANDB_MODE"] = "offline"
            wandb.init(project=project)
        except (IOError, OSError) as exc:
            logger.exception("Failed to initialize wandb; continuing in offline mode: %s", exc)
    elif resolved_mode == "tensorboard":
        logger.info("TensorBoard logging selected; ensure summary writers are configured.")
    else:
        logger.info("Logging initialized in offline/console mode.")

    return logger
