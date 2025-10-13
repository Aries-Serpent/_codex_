"""Utility helpers for the Codex archival workflow."""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import zstandard as _zstd  # type: ignore
except Exception:  # pragma: no cover - best-effort fallback
    _zstd = None

import zlib

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utcnow() -> str:
    """Return a UTC timestamp truncated to seconds."""

    return _dt.datetime.utcnow().replace(microsecond=0).strftime(ISO_FORMAT)


def utcnow_iso() -> str:
    """Return a UTC timestamp (alias for compatibility)."""

    return utcnow()


def sha256_hex(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data*."""

    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest for *data* (alias helper)."""

    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest for the contents of *path* if it exists."""

    if not path.exists():
        return ""
    return sha256_bytes(path.read_bytes())


def zstd_compress(data: bytes, level: int = 9) -> bytes:
    """Compress *data* using zstandard if available, otherwise zlib."""

    if _zstd is not None:  # pragma: no branch - fast path
        compressor = _zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    # Fallback to deterministic zlib compression for environments without zstd.
    return zlib.compress(data, level)


def zlib_compress(data: bytes, level: int = 9) -> bytes:
    """Explicit zlib compression helper used by legacy APIs."""

    return zlib.compress(data, level)


def zstd_decompress(data: bytes) -> bytes:
    """Inverse operation for :func:`zstd_compress`."""

    if _zstd is not None:  # pragma: no branch - fast path
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    return zlib.decompress(data)


def decompress_payload(data: bytes, codec: str) -> bytes:
    """Decompress *data* using the explicit *codec* identifier."""

    if codec == "zstd":
        if _zstd is None:
            raise RuntimeError(
                "zstandard codec requested but python-zstandard is not available"
            )
        decompressor = _zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    if codec == "zlib":
        return zlib.decompress(data)
    raise ValueError(f"Unsupported compression codec: {codec}")


def compression_codec() -> str:
    """Return the codec identifier used by :func:`zstd_compress`."""

    return "zstd" if _zstd is not None else "zlib"


def ensure_directory(path: Path) -> None:
    """Ensure *path* exists, creating parent directories as needed."""

    path.mkdir(parents=True, exist_ok=True)


def json_dumps_sorted(payload: dict[str, Any]) -> str:
    """Serialise *payload* with sorted keys for reproducibility."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def evidence_file() -> Path:
    """Return the evidence file location, creating directories if necessary."""

    base = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    ensure_directory(base)
    return base / "archive_ops.jsonl"


def append_evidence(record: dict[str, Any]) -> None:
    """Append a JSON record to the evidence log."""

    record = dict(record)
    record.setdefault("ts", utcnow())
    path = evidence_file()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json_dumps_sorted(record) + "\n")


def chunked(iterable: Iterable[Any], *, size: int) -> Iterable[list[Any]]:
    """Yield items from *iterable* in fixed-size chunks."""

    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
