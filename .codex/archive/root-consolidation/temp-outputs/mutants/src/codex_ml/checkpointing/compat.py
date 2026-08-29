"""Compatibility shims for legacy checkpointing imports.

This module provides soft-landing aliases while the package surface evolves.
"""

from __future__ import annotations

import importlib
import warnings
from functools import lru_cache
from typing import Any

from codex_ml.utils import checkpoint_core as _core

# Map legacy names -> new import paths when they land.
_ALIASES: dict[str, str] = {
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
    warnings.warn(
        "codex_ml.checkpointing.compat is deprecated; attribute lookup failed",
        DeprecationWarning,
        stacklevel=2,
    )
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_ALIASES.keys()))


@lru_cache(maxsize=1)
def _warn_save_checkpoint_deprecated() -> None:
    warnings.warn(
        "codex_ml.checkpointing.compat.save_checkpoint is deprecated; use checkpoint_core.save_checkpoint",  # noqa: E501
        DeprecationWarning,
        stacklevel=2,
    )


def save_checkpoint(*args, **kwargs) -> None:
    _warn_save_checkpoint_deprecated()
    return _core.save_checkpoint(*args, **kwargs)
