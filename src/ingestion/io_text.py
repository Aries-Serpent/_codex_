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


def _detect_encoding(p: Path) -> str:
    """Best-effort encoding detection via charset-normalizer; defaults to utf-8."""
    try:  # pragma: no cover - optional dep
        from charset_normalizer import from_path  # type: ignore

        best = from_path(str(p)).best()
        if best and best.encoding:
            return best.encoding
    except Exception:
        pass
    return "utf-8"


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read text with explicit or automatically detected encoding.

    - encoding="auto" attempts detection via charset-normalizer; falls back to utf-8.
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
