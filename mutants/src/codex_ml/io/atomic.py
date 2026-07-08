"""
Atomic Module

This module provides functionality for atomic.

Usage:
    from io.atomic import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

__all__ = ["atomic_write_json", "atomic_write_text", "canonical_json_dumps"]


def canonical_json_dumps(obj: Any) -> str:
    """Return deterministic, Unicode-preserving JSON without NaN/Inf."""

    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _fsync_dir(path: Path) -> None:
    """Best-effort directory fsync (skip on platforms lacking support)."""

    flags = getattr(os, "O_RDONLY", 0)
    o_directory = getattr(os, "O_DIRECTORY", 0)
    if o_directory:
        dir_fd = os.open(path, flags | o_directory)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    elif os.name != "nt":
        # On POSIX platforms lacking O_DIRECTORY, opening the directory works.
        with open(path, "rb") as dir_handle:
            os.fsync(dir_handle.fileno())
    else:
        # Windows lacks a straightforward directory fsync; skip best-effort.
        return


def atomic_write_text(path: Path | str, data: str, encoding: str = "utf-8") -> None:
    """Write text to ``path`` atomically via fsync + replace."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f"{path.name}.__tmp__.")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        try:
            _fsync_dir(path.parent)
        except OSError as e:
            type(e).__name__
            logger.debug("OSError: <ERROR_TYPE>")
            logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
            # Best-effort: some filesystems or platforms may not support directory fsync.
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError as e:
                type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)


def atomic_write_json(path: Path | str, obj: dict[str, Any]) -> None:
    """Serialize ``obj`` using :func:`canonical_json_dumps` and write atomically."""

    text = canonical_json_dumps(obj)
    atomic_write_text(path, text)
