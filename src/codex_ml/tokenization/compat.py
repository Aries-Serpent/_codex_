"""Compatibility shims for tokenization imports."""

from __future__ import annotations
import importlib
import warnings
from typing import Any

_ALIASES = {
    # "encode": "codex_ml.tokenization.api:encode",
    # "decode": "codex_ml.tokenization.api:decode",
}


def __getattr__(name: str) -> Any:
    if name in _ALIASES:
        modname, attr = _ALIASES[name].split(":")
        warnings.warn(
            f"codex_ml.tokenization.{name} is deprecated; use {_ALIASES[name]}",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(importlib.import_module(modname), attr)
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_ALIASES.keys()))
