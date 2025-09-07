"""Simple registry for pluggable components.

This registry allows registering tokenizers, reward models and RL agents under
string keys. Interfaces are loaded on demand via entry-points or config.
"""
from __future__ import annotations

import os
import warnings
from importlib import import_module
from typing import Any, Callable, Dict

_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        if name in _REGISTRY:
            warnings.warn(f"duplicate registration: {name}", stacklevel=2)
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


def load_component(path: str) -> Any:
    """Load a component from ``module:Class`` notation."""

    module_name, class_name = path.split(":")
    module = import_module(module_name)
    return getattr(module, class_name)


def get_component(cfg_key: str, default_path: str) -> Any:
    """Instantiate component using env var ``cfg_key`` or ``default_path``."""

    path = os.environ.get(cfg_key, default_path)
    cls = load_component(path)
    return cls()
