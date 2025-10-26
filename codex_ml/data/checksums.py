"""Utility helpers for computing file manifests."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Mapping

__all__ = ["manifest_for_paths"]


def manifest_for_paths(paths: Iterable[str | Path]) -> Mapping[str, str]:
    manifest: dict[str, str] = {}
    for item in paths:
        path = Path(item)
        if not path.exists() or not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        manifest[str(path)] = digest.hexdigest()
    return manifest
