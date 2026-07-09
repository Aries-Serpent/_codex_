"""
Checksums Module

This module provides functionality for checksums.

Usage:
    from utils.checksums import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# BEGIN: CODEX_CHECKSUMS
from __future__ import annotations

import hashlib
import os
from pathlib import Path


def sha256_dir(path: Path) -> str:
    """Compute a deterministic SHA-256 digest of all files under *path*.

    Files are visited in sorted order so the digest is stable across platforms.
    Both filenames and file contents are included in the hash, making it
    sensitive to renames as well as content changes.

    Args:
        path: Root directory to hash.

    Returns:
        64-character lowercase hexadecimal SHA-256 digest string.
    """
    h = hashlib.sha256()
    for root, _, files in os.walk(path):
        for fn in sorted(files):
            fp = Path(root) / fn
            h.update(fp.name.encode())
            h.update(fp.read_bytes())
    return h.hexdigest()


def write_checksum(path: Path):
    """Write a ``checksum.sha256`` sidecar file into *path*.

    Computes the directory checksum via :func:`sha256_dir` and writes the
    resulting hex digest to ``<path>/checksum.sha256``.

    Args:
        path: Directory whose contents should be checksummed.
    """
    (path / "checksum.sha256").write_text(sha256_dir(path))


# END: CODEX_CHECKSUMS
