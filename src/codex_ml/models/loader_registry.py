"""Lightweight registry for model loader callables."""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Mapping

_ModelFactory = Callable[..., Any]

_MODELS: Dict[str, _ModelFactory] = {}


def register_model(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register ``fn`` under ``name`` and return ``fn``."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _MODELS[name] = fn
        return fn

    return decorator


def unregister_model(name: str) -> None:
    """Remove ``name`` from the registry (no-op if missing)."""

    _MODELS.pop(name, None)


def get_model(name: str) -> _ModelFactory:
    """Return the factory registered under ``name``.

    The registry can be disabled by setting the environment variable
    ``CODEX_MODEL_REGISTRY_DISABLE`` to any truthy value.  A :class:`KeyError`
    is raised when the registry is disabled or when ``name`` has not been
    registered.
    """

    if _registry_disabled():
        raise KeyError(name)
    try:
        return _MODELS[name]
    except KeyError as exc:
        raise exc


def list_models() -> Mapping[str, _ModelFactory]:
    """Return a snapshot of registered factories."""

    return dict(_MODELS)


def _registry_disabled() -> bool:
    value = os.environ.get("CODEX_MODEL_REGISTRY_DISABLE", "0")
    return value.lower() in {"1", "true", "yes", "on"}


__all__ = ["register_model", "unregister_model", "get_model", "list_models"]
