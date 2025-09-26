"""
Dataset loaders for JSONL and CSV with deterministic checksum.

Enhancements (Extended tests support):
- Empty file returns 0 records, no error.
- UTF-8 BOM automatically handled (utf-8-sig).
- Malformed JSONL lines skipped (count in metadata['skipped_malformed']).
- CSV quoted fields preserved (csv.DictReader handles).
- Additional metadata fields: skipped_malformed, empty_file (bool).

Backward compatible (original signatures unchanged).
"""

from __future__ import annotations

import csv
import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict, Any

__all__ = [
    "load_jsonl",
    "load_csv",
    "compute_file_checksum",
]


def compute_file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: str | Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSONL file not found: {p}")
    records: List[Dict[str, Any]] = []
    skipped = 0
    with p.open("r", encoding="utf-8-sig") as f:  # utf-8-sig handles BOM
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                skipped += 1
                continue
            if not isinstance(obj, dict):
                obj = {"value": obj}
            records.append(obj)
    checksum = compute_file_checksum(p)
    meta = {
        "path": str(p),
        "format": "jsonl",
        "num_records": len(records),
        "checksum": checksum,
        "size_bytes": p.stat().st_size,
        "skipped_malformed": skipped,
        "empty_file": p.stat().st_size == 0,
    }
    return records, meta


def load_csv(path: str | Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {p}")
    records: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8-sig", newline="") as f:  # utf-8-sig covers BOM
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    checksum = compute_file_checksum(p)
    meta = {
        "path": str(p),
        "format": "csv",
        "num_records": len(records),
        "checksum": checksum,
        "size_bytes": p.stat().st_size,
        "empty_file": len(records) == 0,
    }
    return records, meta