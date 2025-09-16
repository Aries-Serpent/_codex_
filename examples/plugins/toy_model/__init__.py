"""Toy model plugin used for registry examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class ToyModel:
    bias: float = 0.0

    def __call__(self, inputs: Iterable[float]) -> List[float]:
        return [float(x) + self.bias for x in inputs]


def build(**kwargs):
    bias = float(kwargs.get("bias", 0.0))
    return ToyModel(bias=bias)


__all__ = ["ToyModel", "build"]
