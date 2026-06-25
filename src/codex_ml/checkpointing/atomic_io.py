"""
Atomic Io Module

This module provides functionality for atomic io.

Usage:
    from checkpointing.atomic_io import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import BinaryIO, Union  # noqa: E402

PathLike = Union[str, os.PathLike]


def file_sha256(path: PathLike, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA256 digest for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _fsync_directory(dir_path: Path) -> None:
    """Ensure directory entries are durable on POSIX (best-effort elsewhere)."""
    try:
        fd = os.open(str(dir_path), os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # Windows/non-POSIX may not support O_DIRECTORY


def atomic_write_bytes(dest: PathLike, data: bytes) -> Path:
    """Atomically write the provided bytes to ``dest``."""
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=dest_p.parent, delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, dest_p)
    _fsync_directory(dest_p.parent)
    return dest_p


def atomic_write_fileobj(dest: PathLike, src: BinaryIO, chunk_size: int = 1024 * 1024) -> Path:
    """Atomically write bytes read from a file-like object to ``dest``."""
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=dest_p.parent, delete=False) as tmp:
        for chunk in iter(lambda: src.read(chunk_size), b""):
            tmp.write(chunk)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, dest_p)
    _fsync_directory(dest_p.parent)
    return dest_p
