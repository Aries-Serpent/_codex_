"""Stream text data from files for training."""

from __future__ import annotations

from collections.abc import Iterator
from glob import glob

from ingestion import ingest


def stream_texts(
    path_glob: str,
    *,
    encoding: str | None = "auto",
    chunk_size: int = 1 << 20,
    max_samples: int | None = None,
    sample_every_k: int = 1,
) -> Iterator[str]:
    """Stream text chunks from files matching ``path_glob``.

    Files are expanded using :func:`glob` and read via :func:`ingest` from the
    :mod:`ingestion` package which handles encoding detection and chunked
    reading.  The iterator yields text chunks and respects ``max_samples`` and
    ``sample_every_k`` for quick subsampling.
    """
    produced = 0
    for path in glob(path_glob, recursive=True):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        chunks = [result] if isinstance(result, str) else result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


__all__ = ["stream_texts"]
