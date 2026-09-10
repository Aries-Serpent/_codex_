"""Minimal torch.optim stub."""

from __future__ import annotations

from typing import Any


class Optimizer:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def zero_grad(self, *args: Any, **kwargs: Any) -> None:
        return None

    def step(self, *args: Any, **kwargs: Any) -> None:
        return None


class Adam(Optimizer):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SGD(Optimizer):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


__all__ = ["Optimizer", "Adam", "SGD"]
