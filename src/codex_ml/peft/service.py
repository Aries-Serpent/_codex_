"""Deprecated forwarding module for :mod:`codex_lora` use-case functions.

Scheduled for removal in ``codex-ml 0.5.0``. The legacy two-argument helper
remains available from :mod:`codex_ml.peft.peft_adapter` and the package root.
"""

from __future__ import annotations

from importlib import import_module

__all__ = ["apply_lora", "load_lora"]

_STANDALONE_EXPORTS = {"apply_lora", "load_lora"}


def __getattr__(name: str) -> object:
    """Resolve standalone service names lazily while preserving monolith use."""
    if name not in _STANDALONE_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        value = getattr(import_module("codex_lora"), name)
    except ImportError as exc:
        raise AttributeError(
            f"{name} requires the optional codex-ml-lora distribution"
        ) from exc
    globals()[name] = value
    return value
