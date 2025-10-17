"""
Legacy checkpointing manager (compat shim).

Prefer codex_ml.utils.checkpointing.CheckpointManager for new code.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "src.utils.checkpointing is legacy; use codex_ml.utils.checkpointing for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical manager where compatible, to reduce duplication.
try:  # pragma: no cover - mirror class
    from codex_ml.utils.checkpointing import CheckpointManager  # type: ignore
except Exception:  # pragma: no cover - defensive
    CheckpointManager = object  # type: ignore[misc,assignment]


# Optional helper aliases to ease migration of call-sites
def save_ckpt(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import save_checkpoint as _save  # type: ignore

    return _save(*args, **kwargs)


def verify_ckpt_integrity(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import verify_checkpoint as _verify  # type: ignore

    return _verify(*args, **kwargs)


__all__ = ["CheckpointManager", "save_ckpt", "verify_ckpt_integrity"]
