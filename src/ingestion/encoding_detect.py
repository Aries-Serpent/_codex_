"""Helpers for text encoding detection.

This module provides a best-effort file encoding detector that combines:
- BOM (byte-order mark) checks
- chardet (if installed)
- charset-normalizer (if installed; supports both from_bytes and from_path)
- simple decoding heuristics

API:
- detect_encoding(path: Union[str, Path], default: str = "utf-8", sample_size: int = 131072) -> str
- autodetect_encoding: alias for detect_encoding (backwards compatibility)

The detection functions are resilient and will return `default` on failure;
they do not raise.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

# Optional backends
try:
    import chardet as _chardet  # preferred if available
except Exception:  # pragma: no cover - optional dependency
    _chardet = None

# charset-normalizer provides multiple helpers depending on installed version
try:
    from charset_normalizer import from_bytes as _cn_from_bytes  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _cn_from_bytes = None  # type: ignore

try:
    from charset_normalizer import from_path as _cn_from_path  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _cn_from_path = None  # type: ignore

__all__ = ["detect_encoding", "autodetect_encoding"]

# A conservative set of encodings we consider "safe" to return directly.
_SAFE_ENCODINGS = {
    "utf-8",
    "utf-16",
    "utf-32",
    "cp1252",
    "windows-1252",
    "iso-8859-1",
}


def _norm_encoding(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    try:
        return name.lower().replace("_", "-")
    except Exception:
        return None


def detect_encoding(
    path: Union[str, Path], default: str = "utf-8", sample_size: int = 131072
) -> str:
    """Return best-effort text encoding for a file at *path*.

    Resolution order (deterministic):
      0) BOM → 1) chardet → 2) charset-normalizer (from_bytes or from_path) →
         3) heuristic trial decode → 4) default

    - `path` may be a string or pathlib.Path.
    - `sample_size` controls how many bytes are read for byte-based detectors
      (chardet / charset-normalizer.from_bytes). It defaults to 128KiB.
    - The function never raises; it returns `default` on any error.
    """
    p = Path(path)

    # 0) Read a sample of bytes early to allow BOM detection and byte-based
    # detectors to operate. If we can use charset-normalizer.from_path we still
    # prefer to use the bytes for BOM + chardet consistency, but we will fall
    # back to from_path if available and bytes-based detection isn't conclusive.
    try:
        raw = p.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        # Could not read file (missing file, permission, etc) — return default.
        return default

    # 0a) Detect BOMs for common UTF variants
    try:
        if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32"
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
    except Exception:
        # If something odd happens while checking BOMs, continue gracefully.
        pass

    # 1) chardet (preferred if installed)
    if _chardet is not None:
        try:
            res = _chardet.detect(raw) or {}
            enc = _norm_encoding(res.get("encoding"))
        except Exception:
            enc = None
        if enc in _SAFE_ENCODINGS:
            # Normalize windows-1252 to cp1252 for consistency with previous code
            return "cp1252" if enc == "windows-1252" else enc

    # 2) charset-normalizer (try from_bytes first, then from_path)
    enc = None
    if _cn_from_bytes is not None:
        try:
            result = _cn_from_bytes(raw)
            best = result.best() if result is not None else None
            enc = _norm_encoding(getattr(best, "encoding", None))
        except Exception:
            enc = None
        if enc in _SAFE_ENCODINGS:
            return "cp1252" if enc == "windows-1252" else enc

    if _cn_from_path is not None:
        try:
            # from_path will read and analyze the file itself (may be slower but
            # can be more accurate for some inputs).
            result = _cn_from_path(str(p))
            best = result.best() if result is not None else None
            enc = _norm_encoding(getattr(best, "encoding", None))
        except Exception:
            enc = None
        if enc in _SAFE_ENCODINGS:
            return "cp1252" if enc == "windows-1252" else enc

    # 3) simple heuristics: attempt to decode using common encodings.
    for trial in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            raw.decode(trial)
            return trial
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception:
            # Any other unexpected error skip to next trial
            continue

    # 4) Default fallback
    return default


# Backwards compatibility alias (older code used autodetect_encoding)
def autodetect_encoding(
    path: Union[str, Path], default: str = "utf-8", sample_size: int = 131072
) -> str:
    """Alias for detect_encoding to preserve older API name."""
    return detect_encoding(path, default=default, sample_size=sample_size)
