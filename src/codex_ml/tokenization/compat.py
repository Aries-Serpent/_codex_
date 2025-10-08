"""Backward-compatibility shim for tokenization.

Deprecated: import from `codex_ml.tokenization.api` instead.

This module forwards attribute access to `codex_ml.tokenization.api`
and emits a DeprecationWarning the first time any symbol is accessed.
"""

from __future__ import annotations

import importlib
import warnings
from typing import Any


_TARGET_MODULE = "codex_ml.tokenization.api"
_api = importlib.import_module(_TARGET_MODULE)
_warned = False


def _warn_once() -> None:
    global _warned
    if not _warned:
        warnings.warn(
            "codex_ml.tokenization.compat is deprecated; use codex_ml.tokenization.api instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        _warned = True


def __getattr__(name: str) -> Any:  # pragma: no cover - exercised via tests
    _warn_once()
    return getattr(_api, name)


def __dir__() -> list[str]:  # pragma: no cover - convenience
    return sorted(set(dir(_api)))


try:  # re-export __all__ when present
    __all__ = list(getattr(_api, "__all__", []))
except Exception:  # pragma: no cover
    __all__ = []  # type: ignore[assignment]
