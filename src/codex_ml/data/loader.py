"""Simple dataset loaders for plain text, NDJSON, and CSV files."""

from __future__ import annotations

import csv
import hashlib
import json
import pickle
from pathlib import Path
from typing import Callable, List, Optional


def load_texts(path: Path, encoding: str = "utf-8") -> List[str]:
    """Return a list of texts from ``path`` supporting txt, jsonl, or csv."""
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return [ln.strip() for ln in path.read_text(encoding=encoding).splitlines() if ln.strip()]
    if ext in {".jsonl", ".ndjson"}:
        texts: List[str] = []
        with path.open("r", encoding=encoding) as fh:
            for line in fh:
                if not line.strip():
                    continue
                obj = json.loads(line)
                texts.append(obj["text"])
        return texts
    if ext == ".csv":
        texts: List[str] = []
        with path.open("r", encoding=encoding, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                texts.append(row["text"])
        return texts
    raise ValueError(f"Unsupported file extension {ext}")


def _cache_key(path: Path, encoding: str) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    h.update(encoding.encode("utf-8"))
    return h.hexdigest()


def load_dataset(
    path: Path, cache_dir: Optional[Path] = None, encoding: str = "utf-8"
) -> List[str]:
    """Load dataset from ``path`` with optional caching."""
    cache_dir = cache_dir or (path.parent / ".cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(path, encoding)
    cache_file = cache_dir / f"{key}.pkl"
    if cache_file.exists():
        return pickle.loads(cache_file.read_bytes())
    texts = load_texts(path, encoding)
    cache_file.write_bytes(pickle.dumps(texts))
    return texts


def apply_safety_filter(
    texts: List[str], filter_enabled: bool, safety_fn: Optional[Callable[[str], str]] = None
) -> List[str]:
    """Optionally apply ``safety_fn`` to each text when ``filter_enabled``."""
    if not filter_enabled or safety_fn is None:
        return texts
    return [safety_fn(t) for t in texts]
