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

import logging
from pathlib import Path
from typing import Any, Optional

# Optional backends

logger = logging.getLogger(__name__)

_chardet: Any
try:
    import chardet as _chardet  # preferred if available
except (ImportError, AttributeError):  # pragma: no cover - optional dependency
    _chardet = None

# charset-normalizer provides multiple helpers depending on installed version
_cn_from_bytes: Any
try:
    from charset_normalizer import from_bytes as _cn_from_bytes_module

    _cn_from_bytes = _cn_from_bytes_module
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dependency
    _cn_from_bytes = None

_cn_from_path: Any
try:
    from charset_normalizer import from_path as _cn_from_path_module

    _cn_from_path = _cn_from_path_module
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dependency
    _cn_from_path = None

__all__ = ["autodetect_encoding", "detect_encoding"]

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
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        return None


def _detect_bom(raw: bytes) -> Optional[str]:
    """Detect byte-order marks for common UTF variants.
    
    Returns:
        Detected encoding string or None
    
    Reduces complexity by extracting BOM checks (5 branches).
    """
    try:
        if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32"
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
    return None


def _try_chardet(raw: bytes) -> Optional[str]:
    """Try chardet detection.
    
    Returns:
        Encoding if safe encoding found, None otherwise
    
    Reduces complexity by extracting chardet logic (3 branches).
    """
    if _chardet is None:
        return None
    
    try:
        res = _chardet.detect(raw) or {}
        enc = _norm_encoding(res.get("encoding"))
        if enc in _SAFE_ENCODINGS:
            return "cp1252" if enc == "windows-1252" else enc
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
    return None


def _try_charset_normalizer_bytes(raw: bytes) -> Optional[str]:
    """Try charset-normalizer from_bytes detection.
    
    Returns:
        Encoding if safe encoding found, None otherwise
    
    Reduces complexity by extracting charset-normalizer bytes logic (3 branches).
    """
    if _cn_from_bytes is None:
        return None
    
    try:
        result = _cn_from_bytes(raw)
        best = result.best() if result is not None else None
        enc = _norm_encoding(getattr(best, "encoding", None))
        if enc in _SAFE_ENCODINGS:
            return "cp1252" if enc == "windows-1252" else enc
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
    return None


def _try_charset_normalizer_path(path: Path) -> Optional[str]:
    """Try charset-normalizer from_path detection.
    
    Returns:
        Encoding if safe encoding found, None otherwise
    
    Reduces complexity by extracting charset-normalizer path logic (3 branches).
    """
    if _cn_from_path is None:
        return None
    
    try:
        result = _cn_from_path(str(path))
        best = result.best() if result is not None else None
        enc = _norm_encoding(getattr(best, "encoding", None))
        if enc in _SAFE_ENCODINGS:
            return "cp1252" if enc == "windows-1252" else enc
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
    return None


def _try_decode_heuristics(raw: bytes) -> Optional[str]:
    """Try simple heuristics: attempt to decode using common encodings.
    
    Returns:
        Encoding if successful decode, None otherwise
    
    Reduces complexity by extracting heuristic logic (5 branches).
    """
    for trial in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            raw.decode(trial)
            return trial
        except (UnicodeDecodeError, LookupError):
            logger.debug("Exception caught, continuing", exc_info=True)
            continue
        except (ValueError, TypeError):
            logger.warning("Exception occurred", exc_info=True)
            continue
    return None


def detect_encoding(path: str | Path, default: str = "utf-8", sample_size: int = 131072) -> str:
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

    # Read a sample of bytes early to allow BOM detection and byte-based
    # detectors to operate.
    try:
        raw = p.read_bytes()[: max(1024, int(sample_size))]
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        return default

    # 0) Detect BOMs for common UTF variants
    bom_result = _detect_bom(raw)
    if bom_result:
        return bom_result

    # 1) chardet (preferred if installed)
    chardet_result = _try_chardet(raw)
    if chardet_result:
        return chardet_result

    # 2) charset-normalizer (try from_bytes first, then from_path)
    cn_bytes_result = _try_charset_normalizer_bytes(raw)
    if cn_bytes_result:
        return cn_bytes_result

    cn_path_result = _try_charset_normalizer_path(p)
    if cn_path_result:
        return cn_path_result

    # 3) simple heuristics: attempt to decode using common encodings.
    heuristic_result = _try_decode_heuristics(raw)
    if heuristic_result:
        return heuristic_result

    # 4) Default fallback
    return default


# Backwards compatibility alias (older code used autodetect_encoding)
def autodetect_encoding(path: str | Path, default: str = "utf-8", sample_size: int = 131072) -> str:
    """Alias for detect_encoding to preserve older API name."""
    return detect_encoding(path, default=default, sample_size=sample_size)
