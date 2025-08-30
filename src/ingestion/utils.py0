from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, TypeVar, Union
import warnings

import numpy as np

T = TypeVar("T")

try:  # optional dependency
    from charset_normalizer import from_path as _cn_from_path
except Exception:  # pragma: no cover - dependency missing
    _cn_from_path = None  # type: ignore


def _detect_encoding(path: Path, sample_size: int = 131072) -> str:
    try:
        data = path.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        return "utf-8"
    if data.startswith(b"\xff\xfe\x00\x00") or data.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32"
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return "utf-16"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8"
    safe = {
        "utf-8",
        "utf-16",
        "utf-32",
        "cp1252",
        "windows-1252",
        "iso-8859-1",
    }
    if _cn_from_path is not None:
        try:
            result = _cn_from_path(path)
            best = result.best() if result is not None else None
            enc = best.encoding.lower().replace("_", "-") if best and best.encoding else None
        except Exception:
            enc = None
        if enc in safe:
            return "cp1252" if enc == "windows-1252" else enc
    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def read_text(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    p = Path(path)
    if encoding == "auto":
        encoding = _detect_encoding(p)
    return p.read_text(encoding=encoding)


def seeded_shuffle(data: Sequence[T], seed: int) -> List[T]:
    """Return a deterministically shuffled list based on ``seed``."""

    rng = np.random.default_rng(seed)
    idx = np.arange(len(data))
    rng.shuffle(idx)
    return [data[i] for i in idx]


__all__ = ["read_text", "seeded_shuffle"]


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward compatible alias for :func:`read_text`."""

    return read_text(path, encoding=encoding)


__all__.append("read_text_file")
