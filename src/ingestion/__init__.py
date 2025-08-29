"""Basic file ingestion utilities with encoding and chunk support.

The module exposes :func:`ingest` for reading text files.  The helper accepts
an optional ``encoding`` argument and an optional ``chunk_size`` parameter.  When
``encoding`` is set to ``"auto"`` a best-effort detection is attempted.  When
``chunk_size`` is ``None`` the full file is returned as a single string; when a
positive integer is provided the function yields successive string chunks of at
most ``chunk_size`` characters.

A minimal :class:`Ingestor` shim is provided for backwards compatibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional, Union

from .io_text import _detect_encoding, read_text


def ingest(
    path: Union[str, Path],
    *,
    encoding: str = "utf-8",
    chunk_size: Optional[int] | None = None,
):
    """Read or stream text content from ``path``.

    Parameters
    ----------
    path:
        Filesystem path to a text file. ``str`` paths are accepted.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    chunk_size:
        ``None`` to return the entire file as a single string.  If a positive
        integer is supplied the function yields successive chunks of at most
        ``chunk_size`` characters.

    Returns
    -------
    str or Iterator[str]
        The full text when ``chunk_size`` is ``None``; otherwise an iterator of
        string chunks.

    Raises
    ------
    FileNotFoundError
        If ``path`` points to a directory.
    ValueError
        If ``chunk_size`` is provided and is not a positive integer.
    """

    file_path = Path(path)
    if file_path.is_dir():
        raise FileNotFoundError(f"Path is a directory: {file_path}")
    if chunk_size is None:
        return read_text(file_path, encoding=encoding)
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer when provided")

    def _iter() -> Iterator[str]:
        enc = _detect_encoding(file_path) if encoding == "auto" else encoding
        with file_path.open("r", encoding=enc) as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    return _iter()


class Ingestor:
    """Shim class exposing :func:`ingest` as a static method."""

    @staticmethod
    def ingest(
        path: Union[str, Path],
        *,
        encoding: str = "utf-8",
        chunk_size: Optional[int] | None = None,
    ) -> str | Iterator[str]:
        """Proxy to :func:`ingest` with optional ``encoding`` parameter.

        ``encoding`` may be ``"auto"`` to trigger best-effort autodetection."""

        return ingest(path, encoding=encoding, chunk_size=chunk_size)
