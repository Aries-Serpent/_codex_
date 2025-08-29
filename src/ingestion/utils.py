from __future__ import annotations

from pathlib import Path
from typing import Union

from .io_text import _detect_encoding, read_text, seeded_shuffle

__all__ = ["read_text", "seeded_shuffle", "read_text_file"]


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    return read_text(Path(path), encoding=encoding)
