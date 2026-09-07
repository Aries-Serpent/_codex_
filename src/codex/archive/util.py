"""Compatibility wrapper for the legacy ``codex.archive.util`` import path."""

from __future__ import annotations

import json

from aries_serpent_core.archive.util import (  # noqa: F401
    ISO_FORMAT,
    append_evidence,
    chunked,
    compression_codec,
    decompress_payload,
    ensure_directory,
    evidence_file,
    json_dumps_sorted,
    redact_text_credentials,
    redact_url_credentials,
    sha256_bytes,
    sha256_file,
    sha256_hex,
    utcnow,
    utcnow_iso,
    zlib_compress,
    zstd_compress,
    zstd_decompress,
)


def parse_value(value):
    """Normalize a value for compatibility use in legacy archive helpers."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return value


def format_data(data):
    """Render JSON-like data while guarding against recursive structures."""
    seen: set[int] = set()

    def _detect(obj):
        obj_id = id(obj)
        if obj_id in seen:
            raise RecursionError("Circular reference detected")
        seen.add(obj_id)
        try:
            if isinstance(obj, dict):
                for value in obj.values():
                    _detect(value)
            elif isinstance(obj, (list, tuple, set)):
                for value in obj:
                    _detect(value)
        finally:
            seen.discard(obj_id)

    _detect(data)
    return json.dumps(data, sort_keys=True, default=str)


__all__ = [
    "ISO_FORMAT",
    "append_evidence",
    "chunked",
    "compression_codec",
    "decompress_payload",
    "ensure_directory",
    "evidence_file",
    "format_data",
    "json_dumps_sorted",
    "parse_value",
    "redact_text_credentials",
    "redact_url_credentials",
    "sha256_bytes",
    "sha256_file",
    "sha256_hex",
    "utcnow",
    "utcnow_iso",
    "zlib_compress",
    "zstd_compress",
    "zstd_decompress",
]
