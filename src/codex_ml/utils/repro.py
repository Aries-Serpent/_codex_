"""Reproducibility helpers for deterministic seeding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable

from .seeding import set_reproducible  # re-export for backward compatibility


def record_dataset_checksums(files: Iterable[Path], out_path: Path) -> Dict[str, str]:
    """Write SHA256 checksums for ``files`` to ``out_path``."""

    checksums: Dict[str, str] = {}
    for fp in files:
        p = Path(fp)
        if p.exists():
            checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    return checksums


__all__ = ["set_reproducible", "record_dataset_checksums"]
