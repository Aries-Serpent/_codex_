"""Simple dataset loading utilities.

This module supports reading plain text, NDJSON, and CSV files containing a
`text` field. Loaded datasets can be cached on disk for faster reloads and an
optional safety filter may be applied to each example.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pickle
from pathlib import Path
from typing import Callable, List, Optional

from codex_ml.safety.filters import SafetyFilters


def load_texts(path: Path, *, encoding: str = "utf-8") -> List[str]:
    """Load texts from *path* supporting .txt, .jsonl and .csv formats."""
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return [ln.strip() for ln in path.read_text(encoding=encoding).splitlines() if ln.strip()]
    if ext in {".jsonl", ".ndjson"}:
        texts: List[str] = []
        with path.open(encoding=encoding) as fh:
            for line in fh:
                obj = json.loads(line)
                texts.append(str(obj["text"]))
        return texts
    if ext == ".csv":
        texts = []
        with path.open(encoding=encoding, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                texts.append(str(row["text"]))
        return texts
    raise ValueError(f"Unsupported file extension {ext}")


def _cache_key(path: Path, encoding: str) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    h.update(encoding.encode("utf-8"))
    return h.hexdigest()


def load_dataset(
    path: Path, *, cache_dir: Optional[Path] = None, encoding: str = "utf-8"
) -> List[str]:
    """Load and optionally cache the dataset located at *path*."""
    cache_dir = cache_dir or path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(path, encoding)
    cache_file = cache_dir / f"{key}.pkl"
    if cache_file.exists():
        return pickle.loads(cache_file.read_bytes())
    texts = load_texts(path, encoding=encoding)
    cache_file.write_bytes(pickle.dumps(texts))
    return texts


def apply_safety_filter(
    texts: List[str], *, enabled: bool, filter_fn: Callable[[str], str] | None = None
) -> List[str]:
    """Apply safety filter to a list of *texts* when *enabled* is True."""
    if not enabled:
        return texts
    filt = filter_fn or SafetyFilters.from_defaults().apply
    return [filt(t) for t in texts]
