"""Stream text data from files for training."""

from __future__ import annotations

from glob import glob
from typing import Iterator

from ingestion import ingest
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_stream_texts__mutmut_orig(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_1(
    path_glob: str,
    *,
    encoding: str | None = "XXautoXX",
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_2(
    path_glob: str,
    *,
    encoding: str | None = "AUTO",
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_3(
    path_glob: str,
    *,
    encoding: str | None = "auto",
    chunk_size: int = 1 << 20,
    max_samples: int | None = None,
    sample_every_k: int = 2,
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_4(
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
    produced = None
    for path in glob(path_glob, recursive=True):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_5(
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
    produced = 1
    for path in glob(path_glob, recursive=True):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_6(
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
    for path in glob(None, recursive=True):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_7(
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
    for path in glob(path_glob, recursive=None):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_8(
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
    for path in glob(recursive=True):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_9(
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
    for path in glob(path_glob, ):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_10(
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
    for path in glob(path_glob, recursive=False):
        result = ingest(path, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_11(
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
        result = None
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_12(
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
        result = ingest(None, encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_13(
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
        result = ingest(path, encoding=None, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_14(
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
        result = ingest(path, encoding=encoding, chunk_size=None)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_15(
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
        result = ingest(encoding=encoding, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_16(
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
        result = ingest(path, chunk_size=chunk_size)
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_17(
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
        result = ingest(path, encoding=encoding, )
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_18(
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
        if isinstance(result, str):
            chunks = None
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_19(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = None
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_20(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 or produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_21(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k >= 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_22(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 2 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_23(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced / sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_24(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k == 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_25(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 1:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_26(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced = 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_27(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced -= 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_28(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 2
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_29(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                break
            yield chunk
            produced += 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_30(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced = 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_31(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced -= 1
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_32(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 2
            if max_samples is not None and produced >= max_samples:
                return


def x_stream_texts__mutmut_33(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None or produced >= max_samples:
                return


def x_stream_texts__mutmut_34(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is None and produced >= max_samples:
                return


def x_stream_texts__mutmut_35(
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
        if isinstance(result, str):
            chunks = [result]
        else:
            chunks = result
        for chunk in chunks:
            if sample_every_k > 1 and produced % sample_every_k != 0:
                produced += 1
                continue
            yield chunk
            produced += 1
            if max_samples is not None and produced > max_samples:
                return

x_stream_texts__mutmut_mutants : ClassVar[MutantDict] = {
'x_stream_texts__mutmut_1': x_stream_texts__mutmut_1, 
    'x_stream_texts__mutmut_2': x_stream_texts__mutmut_2, 
    'x_stream_texts__mutmut_3': x_stream_texts__mutmut_3, 
    'x_stream_texts__mutmut_4': x_stream_texts__mutmut_4, 
    'x_stream_texts__mutmut_5': x_stream_texts__mutmut_5, 
    'x_stream_texts__mutmut_6': x_stream_texts__mutmut_6, 
    'x_stream_texts__mutmut_7': x_stream_texts__mutmut_7, 
    'x_stream_texts__mutmut_8': x_stream_texts__mutmut_8, 
    'x_stream_texts__mutmut_9': x_stream_texts__mutmut_9, 
    'x_stream_texts__mutmut_10': x_stream_texts__mutmut_10, 
    'x_stream_texts__mutmut_11': x_stream_texts__mutmut_11, 
    'x_stream_texts__mutmut_12': x_stream_texts__mutmut_12, 
    'x_stream_texts__mutmut_13': x_stream_texts__mutmut_13, 
    'x_stream_texts__mutmut_14': x_stream_texts__mutmut_14, 
    'x_stream_texts__mutmut_15': x_stream_texts__mutmut_15, 
    'x_stream_texts__mutmut_16': x_stream_texts__mutmut_16, 
    'x_stream_texts__mutmut_17': x_stream_texts__mutmut_17, 
    'x_stream_texts__mutmut_18': x_stream_texts__mutmut_18, 
    'x_stream_texts__mutmut_19': x_stream_texts__mutmut_19, 
    'x_stream_texts__mutmut_20': x_stream_texts__mutmut_20, 
    'x_stream_texts__mutmut_21': x_stream_texts__mutmut_21, 
    'x_stream_texts__mutmut_22': x_stream_texts__mutmut_22, 
    'x_stream_texts__mutmut_23': x_stream_texts__mutmut_23, 
    'x_stream_texts__mutmut_24': x_stream_texts__mutmut_24, 
    'x_stream_texts__mutmut_25': x_stream_texts__mutmut_25, 
    'x_stream_texts__mutmut_26': x_stream_texts__mutmut_26, 
    'x_stream_texts__mutmut_27': x_stream_texts__mutmut_27, 
    'x_stream_texts__mutmut_28': x_stream_texts__mutmut_28, 
    'x_stream_texts__mutmut_29': x_stream_texts__mutmut_29, 
    'x_stream_texts__mutmut_30': x_stream_texts__mutmut_30, 
    'x_stream_texts__mutmut_31': x_stream_texts__mutmut_31, 
    'x_stream_texts__mutmut_32': x_stream_texts__mutmut_32, 
    'x_stream_texts__mutmut_33': x_stream_texts__mutmut_33, 
    'x_stream_texts__mutmut_34': x_stream_texts__mutmut_34, 
    'x_stream_texts__mutmut_35': x_stream_texts__mutmut_35
}

def stream_texts(*args, **kwargs):
    result = _mutmut_trampoline(x_stream_texts__mutmut_orig, x_stream_texts__mutmut_mutants, args, kwargs)
    return result 

stream_texts.__signature__ = _mutmut_signature(x_stream_texts__mutmut_orig)
x_stream_texts__mutmut_orig.__name__ = 'x_stream_texts'


__all__ = ["stream_texts"]
