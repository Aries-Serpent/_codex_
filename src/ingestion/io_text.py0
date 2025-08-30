from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

__all__ = ["read_text", "seeded_shuffle"]


def seeded_shuffle(items: Iterable[str], seed: int) -> List[str]:
    """Return a deterministically shuffled list of ``items``."""

    import numpy as np

    arr = np.array(list(items))
    rng = np.random.default_rng(seed)
    rng.shuffle(arr)
    return arr.tolist()


def _detect_encoding(p: Path) -> str:
    try:
        from charset_normalizer import from_path  # type: ignore

        best = from_path(str(p)).best()
        if best and best.encoding:
            return best.encoding
    except Exception:
        pass
    return "utf-8"


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read text with explicit or automatically detected encoding."""

    if encoding == "auto":
        encoding = _detect_encoding(path)
    return path.read_text(encoding=encoding, errors="replace")

