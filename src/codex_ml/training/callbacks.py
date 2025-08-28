# BEGIN: CODEX_TRAINING_CALLBACKS
"""Simple training callbacks used across examples.

At the moment only :class:`EarlyStopping` is provided.  It tracks a metric that
should **decrease** during training and signals when progress has stalled::

    es = EarlyStopping(patience=2, min_delta=0.1)
    for loss in losses:
        if es.step(loss):
            break

"""
from __future__ import annotations


class EarlyStopping:
    """Signal training halt when a monitored metric plateaus."""

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
