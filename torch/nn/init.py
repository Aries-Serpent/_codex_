"""Minimal torch.nn.init stub for offline/test readiness checks."""

from __future__ import annotations

from typing import Any


def normal_(tensor: Any, mean: float = 0.0, std: float = 1.0) -> Any:
    return tensor


def zeros_(tensor: Any) -> Any:
    return tensor


def ones_(tensor: Any) -> Any:
    return tensor


def uniform_(tensor: Any, a: float = 0.0, b: float = 1.0) -> Any:
    return tensor


def xavier_uniform_(tensor: Any, gain: float = 1.0) -> Any:
    return tensor


def kaiming_uniform_(tensor: Any, a: float = 0.0, mode: str = "fan_in", nonlinearity: str = "leaky_relu") -> Any:
    return tensor


__all__ = [
    "normal_",
    "zeros_",
    "ones_",
    "uniform_",
    "xavier_uniform_",
    "kaiming_uniform_",
]
