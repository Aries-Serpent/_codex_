"""
Artifact helpers: compute hashes and write sidecar metadata for files produced
by tests/pipelines. These are safe to use in offline CI.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional


def compute_sha256(path: os.PathLike | str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_hash_sidecar(path: os.PathLike | str) -> str:
    """
    Compute the sha256 for `path` and write `<path>.sha256` containing the hex digest.
    Returns the digest string.
    """

    p = Path(path)
    digest = compute_sha256(p)
    sidecar = p.with_suffix(p.suffix + ".sha256")
    sidecar.write_text(digest + "\n", encoding="utf-8")
    return digest


@dataclass
class ArtifactMeta:
    path: str
    sha256: str
    size: int
    extra: Optional[Dict[str, object]] = None


def write_metadata(path: os.PathLike | str, extra: Optional[Dict[str, object]] = None) -> Path:
    """
    Write `<path>.meta.json` including sha256 and size, with optional extra fields.
    """

    p = Path(path)
    meta = ArtifactMeta(
        path=str(p),
        sha256=compute_sha256(p),
        size=p.stat().st_size,
        extra=extra or {},
    )
    out = p.with_suffix(p.suffix + ".meta.json")
    out.write_text(json.dumps(asdict(meta), indent=2, sort_keys=True), encoding="utf-8")
    return out
