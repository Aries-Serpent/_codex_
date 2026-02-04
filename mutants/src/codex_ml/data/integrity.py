"""Integrity helpers for cached datasets."""

from __future__ import annotations

import zlib
from pathlib import Path

__all__ = ["crc32_file"]


def crc32_file(path: str | Path, *, chunk_size: int = 1 << 16) -> int:
    """Compute the CRC32 checksum for *path* streaming over fixed-size chunks.

    Parameters
    ----------
    path:
        File path to hash.
    chunk_size:
        Number of bytes to read at a time. Defaults to 64 KiB which offers a
        good balance between throughput and memory footprint.
    """

    file_path = Path(path)
    if not file_path.exists():  # pragma: no cover - defensive guard
        raise FileNotFoundError(f"file not found: {file_path}")

    checksum = 0
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            checksum = zlib.crc32(chunk, checksum)
    return checksum & 0xFFFFFFFF
