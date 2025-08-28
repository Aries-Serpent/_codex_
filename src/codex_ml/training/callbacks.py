# BEGIN: CODEX_TRAINING_CALLBACKS
from __future__ import annotations


class EarlyStopping:
    """Simple metric-based early stopping utility."""

    def __init__(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min"):
        self.patience = patience
        self.min_delta = min_delta
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.mode = mode
        self.best: float | None = None
        self.bad = 0

    def step(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:  # mode == "max"
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.bad = 0
            return False
        self.bad += 1
        return self.bad >= self.patience


# END: CODEX_TRAINING_CALLBACKS

