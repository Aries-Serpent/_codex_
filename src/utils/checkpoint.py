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
