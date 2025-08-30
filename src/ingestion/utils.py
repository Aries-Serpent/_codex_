from __future__ import annotations

from pathlib import Path
from typing import Union

from .io_text import read_text as _read_text
from .io_text import seeded_shuffle as _seeded_shuffle

__all__ = ["read_text", "seeded_shuffle", "read_text_file"]

read_text = _read_text
seeded_shuffle = _seeded_shuffle


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for :func:`read_text`."""
    return read_text(path, encoding=encoding)
