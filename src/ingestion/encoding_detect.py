"""Helpers for text encoding detection."""

from __future__ import annotations

from pathlib import Path

try:  # pragma: no cover - optional dependency
    from charset_normalizer import from_path as _from_path  # type: ignore
except Exception:  # pragma: no cover
    _from_path = None  # type: ignore

__all__ = ["detect_encoding"]


def detect_encoding(path: Path, default: str = "utf-8") -> str:
    """Best-effort encoding detection.

    ``charset_normalizer`` is used when available; otherwise ``default`` is
    returned.
    """

    if _from_path is None:
        return default
    try:
        result = _from_path(str(path)).best()
        if result and result.encoding:
            return result.encoding
    except Exception:  # pragma: no cover - detection failures
        pass
    return default
