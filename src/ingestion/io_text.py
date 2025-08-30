from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

__all__ = ["read_text", "seeded_shuffle"]


def seeded_shuffle(items: Iterable[str], seed: int) -> List[str]:
    """Return a deterministically shuffled list of items.

    Prefer NumPy's Generator for stable, fast shuffling; gracefully fallback to
    Python's random module if NumPy is unavailable.
    """
    items_list = list(items)
    try:
        import numpy as np  # type: ignore

        arr = np.array(items_list, dtype=object)
        rng = np.random.default_rng(seed)
        rng.shuffle(arr)
        return arr.tolist()
    except Exception:
        # Fallback: deterministic shuffle using stdlib random
        import random

        rng = random.Random(seed)
        rng.shuffle(items_list)
        return items_list


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

    try:  # pragma: no cover - optional dep
        from charset_normalizer import from_path  # type: ignore

        result = from_path(str(path))
        best = result.best() if result is not None else None
        enc = best.encoding.lower().replace("_", "-") if best and best.encoding else None
    except Exception:
        enc = None
    if enc:
        enc_norm = "cp1252" if enc == "windows-1252" else enc
        if enc_norm in safe_encodings:
            return enc_norm

    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue

    return "utf-8"


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read text with explicit or automatically detected encoding.

    - encoding="auto" attempts detection via :func:`_detect_encoding`; falls back to utf-8.
    - Any read or decode error returns an empty string for robustness.
    """
    if encoding == "auto":
        encoding = _detect_encoding(path)
    try:
        return path.read_text(encoding=encoding, errors="replace")
    except Exception:
        # Fallback: retry with utf-8, then empty string
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
