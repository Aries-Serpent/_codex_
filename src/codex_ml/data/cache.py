"""In-memory cache utilities and JSONL shard helpers."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable, Mapping

from .integrity import crc32_file

__all__ = ["SimpleCache", "write_jsonl_with_crc"]


class SimpleCache:
    def __init__(self, ttl_s: int = 3600, max_items: int = 1000):
        self.ttl, self.max = ttl_s, max_items
        self._d = {}

    def get(self, k):
        v = self._d.get(k)
        if not v:
            return None
        val, t = v
        if time.time() - t > self.ttl:
            self._d.pop(k, None)
            return None
        return val

    def set(self, k, val):
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
