"""Minimal torch.optim.lr_scheduler stub."""

from __future__ import annotations

from typing import Any


class _LRScheduler:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def step(self, *args: Any, **kwargs: Any) -> None:
        return None


class StepLR(_LRScheduler):
    pass


class ExponentialLR(_LRScheduler):
    pass


class CosineAnnealingLR(_LRScheduler):
    pass


class ReduceLROnPlateau(_LRScheduler):
    pass


__all__ = [
    "_LRScheduler",
    "StepLR",
    "ExponentialLR",
    "CosineAnnealingLR",
    "ReduceLROnPlateau",
]
