"""Minimal torch.nn shim for test environments."""

from __future__ import annotations

__all__ = ["Module"]


class Module:  # pragma: no cover - convenience stub
    def __init__(self) -> None:
        self.training = True

    def train(self, mode: bool = True) -> "Module":
        self.training = mode
        return self

    def eval(self) -> "Module":
        return self.train(False)
