"""Compatibility shims for legacy checkpointing imports.

This module provides soft-landing aliases while the package surface evolves.
"""

from __future__ import annotations

import importlib
import warnings
from typing import Any

# Map legacy names -> new import paths when they land.
_ALIASES = {
    # "load_checkpoint": "codex_ml.checkpointing.core:load_checkpoint",
    # "save_checkpoint": "codex_ml.checkpointing.core:save_checkpoint",
}


def __getattr__(name: str) -> Any:
    if name in _ALIASES:
        target = _ALIASES[name]
        modname, func = target.split(":")
        warnings.warn(
            f"codex_ml.checkpointing.{name} is deprecated; use {target}",
            DeprecationWarning,
            stacklevel=2,
        )
        mod = importlib.import_module(modname)
        return getattr(mod, func)
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_ALIASES.keys()))
