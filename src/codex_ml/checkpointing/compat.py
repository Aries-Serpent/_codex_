"""Backward-compatibility shim for checkpointing.

Deprecated: import from `codex_ml.checkpointing.checkpoint_core` (or the
documented public API) instead.
"""

from __future__ import annotations

import importlib
import warnings


_TARGET_MODULE = "codex_ml.checkpointing.checkpoint_core"
_core = importlib.import_module(_TARGET_MODULE)
_warned = False


def _warn_once() -> None:
    global _warned
    if not _warned:
        warnings.warn(
            "codex_ml.checkpointing.compat is deprecated; "
            "use codex_ml.checkpointing.checkpoint_core instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        _warned = True


def __getattr__(name: str):  # pragma: no cover - exercised via tests
    _warn_once()
    return getattr(_core, name)


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(dir(_core)))


try:
    __all__ = list(getattr(_core, "__all__", []))
except Exception:  # pragma: no cover
    __all__ = []  # type: ignore[assignment]
