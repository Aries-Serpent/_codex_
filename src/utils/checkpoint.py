"""
Legacy checkpoint helpers (compat shim).

This module remains for backward-compatibility only. Prefer:
  - codex_ml.utils.checkpoint_core
  - codex_ml.utils.checkpointing (CheckpointManager)
"""

from __future__ import annotations

import os
import tempfile
import warnings as _warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Any

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
    from codex_ml.utils.checkpoint_core import (
        load_checkpoint as _canonical_load_checkpoint,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import save_checkpoint as _canonical_save_checkpoint
except Exception:  # pragma: no cover - canonical helpers unavailable
    _canonical_load_checkpoint = None  # type: ignore[assignment]
    _canonical_save_checkpoint = None  # type: ignore[assignment]


def save_checkpoint(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception:
                pass

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception:
            pass
    return None


def load_checkpoint(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device
    state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
    return state


__all__ = ["CheckpointManager", "save_checkpoint", "load_checkpoint"]
