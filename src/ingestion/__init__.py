"""Ingestion utilities package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Union

from .encoding_detect import detect_encoding
from .io_text import read_text as _read_text
from .utils import deterministic_shuffle, read_text_file

__all__ = [
    "read_text",
    "deterministic_shuffle",
    "detect_encoding",
    "ingest",
    "Ingestor",
]


def read_text(path: Path | str, encoding: str = "utf-8") -> str:
    text, _ = _read_text(Path(path), encoding=encoding)
    return text


def ingest(
    path: Union[str, Path], *, encoding: str = "utf-8", chunk_size: int | None = None
) -> Union[str, Iterator[str]]:
    """Read text data from ``path`` with optional chunked iteration."""

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    if chunk_size is None:
        return read_text_file(p, encoding=encoding)

    def _gen() -> Iterator[str]:
        with p.open("r", encoding=encoding) as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    return _gen()


class Ingestor:
    """Shim class exposing :func:`ingest` as a static method."""

    @staticmethod
    def ingest(
        path: Union[str, Path],
        encoding: str = "utf-8",
        chunk_size: int | None = None,
    ) -> Union[str, Iterator[str]]:
        return ingest(path, encoding=encoding, chunk_size=chunk_size)
