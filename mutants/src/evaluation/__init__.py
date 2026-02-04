"""Evaluation helpers (metrics, writers)."""

from __future__ import annotations

import importlib
from types import ModuleType

__all__ = ["metrics", "writers"]


def __getattr__(name: str) -> ModuleType:
    if name in __all__:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
