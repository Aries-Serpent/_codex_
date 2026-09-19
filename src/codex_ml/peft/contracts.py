"""Deprecated forwarding module for :mod:`codex_lora` contracts.

Scheduled for removal in ``codex-ml 0.5.0``.
"""

from __future__ import annotations

from importlib import import_module

__all__ = ["LoraBackend", "LoraConfig"]

_STANDALONE_EXPORTS = {"LoraBackend", "LoraConfig"}


def __getattr__(name: str) -> object:
    """Resolve standalone contract names lazily while preserving monolith use."""
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
