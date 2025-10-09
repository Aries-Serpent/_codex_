"""Atomic file-system helpers for sidecar persistence."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

__all__ = ["canonical_json_dumps", "atomic_write_text", "atomic_write_json"]


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
        with open(path, "rb") as dir_handle:  # type: ignore[arg-type]
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
        except OSError:
            # Best-effort: some filesystems or platforms may not support directory fsync.
            pass
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def atomic_write_json(path: Path | str, obj: dict[str, Any]) -> None:
    """Serialize ``obj`` using :func:`canonical_json_dumps` and write atomically."""

    text = canonical_json_dumps(obj)
    atomic_write_text(path, text)
