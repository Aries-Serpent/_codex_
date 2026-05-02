"""
Checksums Module

This module provides functionality for checksums.

Usage:
    from data.checksums import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Optional


def _sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def manifest_for_paths(
    paths: Iterable[Path],
    out_path: Optional[Path] = None,
    extra_fields: Optional[Mapping[str, object]] = None,
) -> None:
    """
    Write an NDJSON manifest for the given file paths.
    Each line: {"path": "...", "sha256": "...", "bytes": N, "mtime": float, ...extra}
    When *out_path* is ``None`` the manifest is computed but not written.
    """
    if out_path is None:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    extra_fields = dict(extra_fields or {})
    with out_path.open("w", encoding="utf-8") as f_out:
        for p in paths:
            p = Path(p)
            if not p.is_file():
                continue
            st = p.stat()
            row = {
                "path": str(p),
                "sha256": _sha256_file(p),
                "bytes": int(st.st_size),
                "mtime": float(st.st_mtime),
                **extra_fields,
            }
            f_out.write(json.dumps(row) + "\n")
