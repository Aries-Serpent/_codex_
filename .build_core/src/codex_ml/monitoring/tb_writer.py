"""
Tb Writer Module

This module provides functionality for tb writer.

Usage:
    from monitoring.tb_writer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Optional  # noqa: E402

try:  # pragma: no cover - optional dependency
    from torch.utils.tensorboard import SummaryWriter
except (IOError, OSError):  # pragma: no cover - optional dependency path
    SummaryWriter = None


class TBWriter:
    """Minimal TensorBoard wrapper that degrades to a no-op when unavailable."""

    def __init__(self, enabled: bool, logdir: str = "runs/codex") -> None:
        self.enabled = bool(enabled and SummaryWriter is not None)
        self._writer: Optional[SummaryWriter] = None
        if self.enabled and SummaryWriter is not None:
            try:
                self._writer = SummaryWriter(log_dir=logdir)
            except (IOError, OSError):  # pragma: no cover - tensorboard initialisation failures
                self._writer = None

    def add_scalar(self, tag: str, value: float, step: int) -> None:
        if self._writer is None:
            return
        try:
            self._writer.add_scalar(tag, value, step)
        except (IOError, OSError):  # pragma: no cover - tensorboard runtime errors
            logger.debug("Suppressed exception in handler", exc_info=True)

    def close(self) -> None:
        if self._writer is None:
            return
        try:
            self._writer.flush()
        except (IOError, OSError):  # pragma: no cover - flushing is best-effort
            logger.debug("Suppressed exception in handler", exc_info=True)
        try:
            self._writer.close()
        except (IOError, OSError):  # pragma: no cover - closing is best-effort
            logger.debug("Suppressed exception in handler", exc_info=True)


__all__ = ["TBWriter"]
