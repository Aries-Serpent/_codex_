"""Utility helpers for ingestion."""

from __future__ import annotations

import random
from pathlib import Path
from typing import List, Sequence, TypeVar

from .encoding_detect import detect_encoding
from .io_text import read_text as _read_text

T = TypeVar("T")

__all__ = [
    "deterministic_shuffle",
    "read_text",
    "read_text_file",
    "_detect_encoding",
]


def deterministic_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled list using ``seed`` for determinism."""

    items = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items


def read_text(path: Path | str, encoding: str = "utf-8") -> str:
    """Read text from ``path`` using optional encoding detection.

    This is a thin wrapper around :func:`ingestion.io_text.read_text` that
    returns just the decoded string for convenience.
    """

    text, _ = _read_text(Path(path), encoding=encoding)
    return text


def read_text_file(path: Path | str, encoding: str = "utf-8") -> str:
    """Alias for :func:`read_text` for backwards compatibility."""

    return read_text(path, encoding=encoding)


def _detect_encoding(path: Path) -> str:
    """Internal helper used by legacy ingestors for encoding detection."""

    return detect_encoding(Path(path))
