"""
Legacy checkpoint helpers (compat shim).

This module remains for backward-compatibility only. Prefer:
  - codex_ml.utils.checkpoint_core
  - codex_ml.utils.checkpointing (CheckpointManager)
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "src.utils.checkpoint is legacy; use codex_ml.utils.checkpointing or "
    "codex_ml.utils.checkpoint_core for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# If a local legacy implementation exists in the repository, import it.
# Otherwise provide minimal stubs or re-export from canonical APIs.
try:  # pragma: no cover - legacy path
    from training.checkpoint_manager import CheckpointManager  # type: ignore # noqa: F401
except Exception:  # pragma: no cover - fallback to canonical
    from codex_ml.utils.checkpointing import CheckpointManager  # type: ignore # noqa: F401

try:  # pragma: no cover - prefer canonical helpers
    from codex_ml.utils.checkpoint_core import (  # type: ignore
        load_checkpoint as _canonical_load_checkpoint,
        save_checkpoint as _canonical_save_checkpoint,
    )
except Exception:  # pragma: no cover - canonical helpers unavailable
    _canonical_load_checkpoint = None  # type: ignore[assignment]
    _canonical_save_checkpoint = None  # type: ignore[assignment]


def save_checkpoint(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Deprecated compatibility wrapper for :func:`codex_ml.utils.checkpoint_core.save_checkpoint`."""

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError(
            "save_checkpoint is unavailable; install codex-ml checkpoint extras"
        )
    return _canonical_save_checkpoint(*args, **kwargs)


def load_checkpoint(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Deprecated compatibility wrapper for :func:`codex_ml.utils.checkpoint_core.load_checkpoint`."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")
    return _canonical_load_checkpoint(*args, **kwargs)


__all__ = ["CheckpointManager", "save_checkpoint", "load_checkpoint"]
