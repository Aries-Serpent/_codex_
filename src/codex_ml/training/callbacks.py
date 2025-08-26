# BEGIN: CODEX_TRAINING_CALLBACKS
from __future__ import annotations


class EarlyStopping:
    def __init__(self, patience: int = 3, min_delta: float = 0.0):
        self.patience, self.min_delta = patience, min_delta
        self.best = None
        self.bad = 0

    def step(self, metric: float) -> bool:
        if self.best is None or metric < self.best - self.min_delta:
            self.best, self.bad = metric, 0
            return False
        self.bad += 1
        return self.bad > self.patience


# END: CODEX_TRAINING_CALLBACKS
