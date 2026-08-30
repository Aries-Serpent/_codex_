"""In-memory cache utilities and JSONL shard helpers."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .integrity import crc32_file

__all__ = [
    "SimpleCache",
    "cache_records",
    "derive_key",
    "load_cached_records",
    "write_jsonl_with_crc",
]


class SimpleCache:
    def __init__(self, ttl_s: int = 3600, max_items: int = 1000):
        self.ttl, self.max = ttl_s, max_items
        self._d: dict[str, Any] = {}

    def get(self, k) -> None:
        v = self._d.get(k)
        if not v:
            return None
        val, t = v
        if time.time() - t > self.ttl:
            self._d.pop(k, None)
            return None
        return val

    def set(self, k, val) -> None:
        # Guard against zero-capacity caches and eviction edge cases.
        if self.max is not None and self.max <= 0:
            return

        if self.max is not None and len(self._d) >= self.max and self._d:
            oldest = next(iter(self._d))
            self._d.pop(oldest, None)

        self._d[k] = (val, time.time())


def write_jsonl_with_crc(path: str | Path, rows: Iterable[Mapping[str, object]]) -> Path:
    """Write *rows* to ``path`` as JSONL and emit a ``.crc32`` sidecar."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    checksum = crc32_file(target)
    sidecar = target.with_suffix(target.suffix + ".crc32")
    sidecar.write_text(str(checksum), encoding="utf-8")
    return sidecar


# Dataset caching utilities (hash-based)


def _sha256_text(text: str) -> str:
    """Compute SHA256 hash of text.

    Parameters
    ----------
    text : str
        Text to hash

    Returns
    -------
    str
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def derive_key(*parts: str) -> str:
    """Derive short stable hash (first 16 hex chars) from parts.

    Parameters
    ----------
    *parts : str
        Parts to combine and hash (e.g., dataset name, split, seed)

    Returns
    -------
    str
        Short hash (16 characters)

    Examples
    --------
    >>> key = derive_key("imdb", "train", "42")
    >>> len(key)
    16

    Notes
    -----
    The hash is truncated to 16 hex characters (64 bits) for readability and
    filesystem compatibility. While this reduces collision resistance compared
    to the full 256-bit SHA256, it provides adequate protection for typical
    dataset caching scenarios (up to ~billions of entries before significant
    collision probability). For applications requiring stronger guarantees,
    consider using the full hash or adding version prefixes.
    """
    combined = ":".join(str(p) for p in parts)
    full_hash = _sha256_text(combined)
    return full_hash[:16]


def cache_records(records: Iterable[dict[str, Any]], *, cache_dir: str | Path, key: str) -> Path:
    """Cache JSON-serializable records under cache_dir/key.jsonl.

    Parameters
    ----------
    records : Iterable[dict]
        Records to cache (must be JSON-serializable)
    cache_dir : str | Path
        Cache directory (created if missing)
    key : str
        Stable hash of data params (from derive_key)

    Returns
    -------
    Path
        Path to cached JSONL file

    Examples
    --------
    >>> from pathlib import Path
    >>> records = [{"text": "hello"}, {"text": "world"}]
    >>> key = derive_key("test", "v1")
    >>> path = cache_records(records, cache_dir=os.path.join(tempfile.gettempdir(), "cache"), key=key)
    >>> path.exists()
    True
    >>> path.name.endswith('.jsonl')
    True
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    output_path = cache_path / f"{key}.jsonl"

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    return output_path


def load_cached_records(cache_dir: str | Path, key: str) -> list[dict[str, Any]] | None:
    """Load cached records if available.

    Parameters
    ----------
    cache_dir : str | Path
        Cache directory
    key : str
        Cache key (from derive_key)

    Returns
    -------
    list[dict] | None
        Cached records or None if not found

    Examples
    --------
    >>> key = derive_key("test", "v1")
    >>> records = load_cached_records(os.path.join(tempfile.gettempdir(), "cache"), key)
    >>> records is None or isinstance(records, list)
    True
    """
    cache_path = Path(cache_dir)
    output_path = cache_path / f"{key}.jsonl"

    if not output_path.exists():
        return None

    records = []
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records
