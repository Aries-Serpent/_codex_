"""Weights & Biases (W&B) logging utilities with offline-first defaults.

This module provides wrappers for W&B logging that default to offline mode
and provide graceful fallbacks when W&B is unavailable.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["WandBLogger", "init_wandb", "log_metrics"]


class WandBLogger:
    """Wrapper for W&B logging with offline-first defaults and fallbacks.

    This logger:
    - Defaults to offline mode (respects WANDB_MODE env var)
    - Falls back to NDJSON logging if W&B unavailable
    - Provides consistent API regardless of W&B availability
    """

    def __init__(
        self,
        project: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
        log_dir: Optional[Path | str] = None,
    ):
        """Initialize W&B logger with offline-first defaults.

        Args:
            project: W&B project name
            name: Run name
            config: Configuration dict to log
            log_dir: Directory for fallback NDJSON logs (default: .codex/logs)
        """
        self.project = project or "codex-training"
        self.name = name
        self.config = config or {}
        self.log_dir = Path(log_dir or ".codex/logs")

        self.wandb_available = self._check_wandb()
        self.wandb_run = None

        if self.wandb_available:
            self._init_wandb()
        else:
            self._init_fallback()

    def _check_wandb(self) -> bool:
        """Check if W&B is available and not disabled."""
        if importlib.util.find_spec("wandb") is None:
            logger.info("W&B not installed, using fallback logging")
            return False
        mode = os.getenv("WANDB_MODE", "offline")
        return mode != "disabled"

    def _init_wandb(self):
        """Initialize W&B with offline-first defaults."""
        try:
            import wandb

            mode = os.getenv("WANDB_MODE", "offline")

            self.wandb_run = wandb.init(
                project=self.project,
                name=self.name,
                config=self.config,
                mode=mode,
                reinit=False,
            )

            logger.info(f"✓ W&B initialized (mode={mode}, project={self.project})")
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to initialize W&B: <ERROR_TYPE>. Using fallback.")
            self.wandb_available = False
            self._init_fallback()

    def _init_fallback(self):
        """Initialize fallback NDJSON logging."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.fallback_log = self.log_dir / f"{self.name or 'run'}_metrics.jsonl"

        # Write config as first line
        with open(self.fallback_log, "w", encoding="utf-8") as f:
            json.dump({"config": self.config, "step": "init"}, f)
            f.write("\n")

        logger.info(f"✓ Fallback logging initialized: {self.fallback_log}")

    def log(self, metrics: dict[str, Any], step: Optional[int] = None):
        """Log metrics to W&B or fallback.

        Args:
            metrics: dict of metric name -> value
            step: Optional step number
        """
        if self.wandb_available and self.wandb_run:
            try:
                import wandb

                wandb.log(metrics, step=step)
            except (ImportError, AttributeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("W&B logging failed: <ERROR_TYPE>")
                self._log_fallback(metrics, step)
        else:
            self._log_fallback(metrics, step)

    def _log_fallback(self, metrics: dict[str, Any], step: Optional[int] = None):
        """Write metrics to NDJSON fallback."""
        entry = {"metrics": metrics}
        if step is not None:
            entry["step"] = step  # type: ignore[assignment]

        with open(self.fallback_log, "a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write("\n")

    def finish(self):
        """Finish logging session."""
        if self.wandb_available and self.wandb_run:
            try:
                import wandb

                wandb.finish()
                logger.info("✓ W&B session finished")
            except (ImportError, AttributeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Failed to finish W&B: <ERROR_TYPE>")


def init_wandb(
    project: Optional[str] = None,
    name: Optional[str] = None,
    config: Optional[dict[str, Any]] = None,
    **kwargs,
) -> WandBLogger:
    """Initialize W&B logger with offline-first defaults (convenience function).

    Args:
        project: W&B project name
        name: Run name
        config: Configuration dict to log
        **kwargs: Additional arguments passed to WandBLogger

    Returns:
        WandBLogger instance
    """
    return WandBLogger(project=project, name=name, config=config, **kwargs)


# Global logger instance
_global_logger: Optional[WandBLogger] = None


def log_metrics(metrics: dict[str, Any], step: Optional[int] = None):
    """Log metrics using global logger (convenience function).

    Args:
        metrics: dict of metric name -> value
        step: Optional step number
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = WandBLogger()

    _global_logger.log(metrics, step=step)
