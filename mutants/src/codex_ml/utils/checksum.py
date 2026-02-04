"""Utility helpers for computing checksums.

This module intentionally keeps a tiny surface area so it can be imported
without pulling in heavy third‑party dependencies.  The helper mirrors the
``sha256sum`` CLI behaviour by streaming files in fixed-size chunks which keeps
memory usage predictable for large checkpoints.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

__all__ = ["sha256sum"]


def sha256sum(path: str | Path, *, chunk_size: int = 128 * 1024) -> str:
    """Return the hexadecimal SHA-256 digest for ``path``.

    Parameters
    ----------
    path:
        File path to hash.
    chunk_size:
        Optional override for the streaming chunk size.  The default keeps IO
        efficient without holding large buffers in memory.
    """

    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb", buffering=0) as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()
