"""Simple registry for pluggable components.

This registry allows registering tokenizers, reward models and RL agents under
string keys. Interfaces are loaded on demand via entry-points or config.
"""
from __future__ import annotations

from importlib import import_module
from typing import Any, Callable, Dict

_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        _REGISTRY[name] = fn
        return fn

    return deco


def get(name: str, *, fallback: str | None = None) -> Any:
    if name in _REGISTRY:
        return _REGISTRY[name]
    if fallback:
        module, attr = fallback.split(":")
        return getattr(import_module(module), attr)
    raise KeyError(f"No registered component named {name}")
