from __future__ import annotations

from typing import Callable, Dict

MODELS: Dict[str, Callable[..., object]] = {}


def register_model(name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def deco(fn: Callable[..., object]) -> Callable[..., object]:
        MODELS[name] = fn
        return fn

    return deco


def get_model(name: str) -> Callable[..., object]:
    if name not in MODELS:
        raise KeyError(f"Unknown model: {name}")
    return MODELS[name]


__all__ = ["register_model", "get_model"]
