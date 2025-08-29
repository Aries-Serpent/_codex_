# BEGIN: CODEX_UTILS_TRAINING_CALLBACKS
"""Generic training callbacks used across small examples.

Currently only exposes :class:`EarlyStopping`.
"""
from __future__ import annotations

from typing import Optional


class EarlyStopping:
    """Signal training halt when a monitored metric plateaus."""

    def __init__(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def step(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience


__all__ = ["EarlyStopping"]

# END: CODEX_UTILS_TRAINING_CALLBACKS
