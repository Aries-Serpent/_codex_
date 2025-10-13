from __future__ import annotations

import hashlib
import json
import zlib
from datetime import datetime, timezone


def sha256_hex(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def zlib_compress(b: bytes, level: int = 9) -> bytes:
    """Deterministic zlib compression for portability."""

    return zlib.compress(b, level)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_dumps(o: object) -> str:
    """Stable JSON representation (sorted keys) for deterministic evidence."""

    return json.dumps(o, sort_keys=True, separators=(",", ":"))
