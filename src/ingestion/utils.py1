from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, TypeVar, Union, Optional
import warnings

T = TypeVar("T")

# Optional dependencies
try:  # NumPy preferred for stable RNG
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - numpy unavailable
    np = None  # type: ignore

try:  # charset-normalizer for encoding detection
    from charset_normalizer import from_path as _cn_from_path  # type: ignore
except Exception:  # pragma: no cover - dependency missing
    _cn_from_path = None  # type: ignore

__all__ = ["read_text", "seeded_shuffle", "read_text_file"]


def _detect_encoding(path: Path, sample_size: int = 131072) -> str:
    """Best-effort encoding detection.

    Strategy:
      1. Check for common BOM signatures.
      2. If charset-normalizer is available, consult it.
      3. Try a small set of common encodings by attempting to decode.
      4. Fall back to 'utf-8'.
    """
    try:
        data = path.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        return "utf-8"

    # BOM checks
    if data.startswith(b"\xff\xfe\x00\x00") or data.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32"
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return "utf-16"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8"

    safe_encodings = {"utf-8", "utf-16", "utf-32", "cp1252", "windows-1252", "iso-8859-1"}

    if _cn_from_path is not None:
        try:
            result = _cn_from_path(path)
            best = result.best() if result is not None else None
            enc = best.encoding.lower().replace("_", "-") if best and best.encoding else None
        except Exception:
            enc = None
        if enc:
            enc_norm = "cp1252" if enc == "windows-1252" else enc
            if enc_norm in safe_encodings:
                return enc_norm

    # Try common encodings
    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue

    return "utf-8"


def read_text(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Read text from path with a given encoding.

    If encoding == "auto", attempt to detect encoding via _detect_encoding.
    Falls back to 'utf-8' and replaces invalid characters to avoid exceptions.
    """
    p = Path(path)
    if encoding == "auto":
        try:
            encoding = _detect_encoding(p)
        except Exception:
            encoding = "utf-8"

    try:
        return p.read_text(encoding=encoding, errors="replace")
    except Exception:
        # Last-resort attempts for robustness
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            warnings.warn(f"Failed to read text from {p!s}; returning empty string", RuntimeWarning)
            return ""


def seeded_shuffle(items: Union[Iterable[T], Sequence[T]], seed: int) -> List[T]:
    """Deterministically shuffle items using a seeded RNG.

    Uses NumPy's Generator when available for stable, fast shuffling. Falls back
    to Python's random.Random when NumPy is absent.
    """
    seq: List[T] = list(items)
    if np is not None:
        try:
            rng = np.random.default_rng(seed)
            idx = np.arange(len(seq))
            rng.shuffle(idx)
            return [seq[int(i)] for i in idx]
        except Exception:
            # Fall through to stdlib fallback
            pass

    # Stdlib fallback
    import random

    rng = random.Random(seed)
    rng.shuffle(seq)
    return seq


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for read_text (keeps older API names)."""
    return read_text(path, encoding=encoding)
