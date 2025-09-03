"""Ingestion utilities: robust text reading, encoding detection, and chunked ingestion.

This module combines functionality from historical variants to provide a single,
backwards-compatible interface for reading text files with optional encoding
autodetection and chunked iteration. It also re-exports deterministic shuffling
helpers used by ingestion pipelines.

Public API:
- read_text(path, encoding="utf-8", errors="strict") -> str
- read_text_file(path, encoding="utf-8") -> str  # legacy alias
- ingest(path, *, encoding="utf-8", chunk_size=None) -> str | Iterator[str]
- Ingestor (class with static ingest method)
- deterministic_shuffle (re-exported from .utils)
- detect_encoding (best-effort detector)
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Iterator, Optional, Tuple, Union

# Local utility imports (optional modules handled gracefully)
try:
    # Prefer a dedicated encoding detector if present in repo
    from .encoding_detect import detect_encoding as _repo_detect_encoding  # type: ignore
except Exception:
    _repo_detect_encoding = None  # type: ignore

try:
    # io_text.read_text historically provided a number of signatures:
    # - read_text(path) -> str
    # - read_text(path, encoding) -> str
    # - read_text(path, encoding, errors) -> (str, used_encoding)
    from .io_text import read_text as _io_text_read_text  # type: ignore
except Exception:
    _io_text_read_text = None  # type: ignore

try:
    # Some callers expect _detect_encoding from io_text
    from .io_text import _detect_encoding as _io_text__detect_encoding  # type: ignore
except Exception:
    _io_text__detect_encoding = None  # type: ignore

# Deterministic shuffle and legacy read_text_file may live in utils
try:
    from .utils import deterministic_shuffle as _deterministic_shuffle  # type: ignore
    from .utils import read_text_file as _utils_read_text_file  # type: ignore
except Exception:
    _deterministic_shuffle = None  # type: ignore
    _utils_read_text_file = None  # type: ignore

__all__ = [
    "read_text",
    "read_text_file",
    "ingest",
    "Ingestor",
    "deterministic_shuffle",
    "detect_encoding",
]

# Expose deterministic_shuffle when available, otherwise provide a local fallback.
if _deterministic_shuffle is None:
    import random
    from typing import List, Sequence, TypeVar

    T = TypeVar("T")

    def deterministic_shuffle(seq: Sequence[T], seed: int) -> list[T]:
        """Deterministic shuffle fallback (seeded RNG)."""
        items = list(seq)
        rng = random.Random(seed)
        rng.shuffle(items)
        return items
else:
    deterministic_shuffle = _deterministic_shuffle  # type: ignore

# Provide a detect_encoding wrapper that uses repo detector, io_text helper, or a conservative fallback.
def detect_encoding(path: Union[str, Path]) -> str:
    """Best-effort detect the file encoding.

    Priority:
      1. repository-provided encoding_detect.detect_encoding
      2. io_text._detect_encoding (legacy)
      3. Conservative builtin fallback
    """
    p = Path(path)
    if _repo_detect_encoding is not None:
        try:
            return _repo_detect_encoding(p)
        except Exception:
            # Fall through to other detectors
            pass
    if _io_text__detect_encoding is not None:
        try:
            return _io_text__detect_encoding(p)
        except Exception:
            pass

    # Fallback conservative detector: BOM checks, then try a few encodings
    try:
        raw = p.read_bytes()[:65536]
    except Exception:
        return "utf-8"

    # BOM checks
    try:
        if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32"
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
    except Exception:
        pass

    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            raw.decode(enc)
            return enc
        except Exception:
            continue

    return "utf-8"


# Internal helper to normalise various historical read_text signatures.
def _call_repo_read_text(path: Path, encoding: str = "utf-8", errors: str = "strict") -> Tuple[str, Optional[str]]:
    """Call repository io_text.read_text in a way that handles multiple historical signatures.

    Returns:
        (text, used_encoding_or_None)
    """
    if _io_text_read_text is None:
        raise RuntimeError("Repository io_text.read_text is not available")
    # Try the richer signatures first and progressively fall back.
    try:
        # Newer helpers may return (text, used_encoding)
        result = _io_text_read_text(path, encoding=encoding, errors=errors)  # type: ignore[misc]
    except TypeError:
        try:
            # Older helper may accept (path, encoding)
            result = _io_text_read_text(path, encoding)  # type: ignore[misc]
        except TypeError:
            try:
                # Very old: only path
                result = _io_text_read_text(path)  # type: ignore[misc]
            except Exception as exc:
                raise RuntimeError(f"repo read_text failed: {exc}") from exc
    except Exception as exc:
        # Pass up other errors as runtime errors
        raise RuntimeError(f"repo read_text failed: {exc}") from exc

    # Normalise return value
    if isinstance(result, tuple) or isinstance(result, list):
        if len(result) >= 1:
            txt = result[0]
            used = result[1] if len(result) > 1 else None
            return str(txt), (str(used) if used is not None else None)
    if isinstance(result, str):
        return result, None
    # Coerce to string for unexpected return types
    return str(result), None


def _manual_read_text(path: Path, encoding: str = "utf-8", errors: str = "strict") -> Tuple[str, str]:
    """Manual robust reader used as a last-resort fallback.

    Returns (text, used_encoding)
    """
    try:
        raw = path.read_bytes()
    except Exception as exc:
        raise RuntimeError(f"Failed to read bytes from {path}: {exc}") from exc

    enc = encoding
    if isinstance(enc, str) and enc.lower() == "auto":
        enc = detect_encoding(path)

    # Try to decode using chosen encoding, and fall back gracefully
    try:
        text = raw.decode(enc, errors)
    except Exception:
        # Try common fallbacks
        for trial in ("utf-8", "cp1252", "iso-8859-1"):
            try:
                text = raw.decode(trial, "replace")
                enc = trial
                break
            except Exception:
                continue
        else:
            # As a last resort
            text = raw.decode("utf-8", "replace")
            enc = "utf-8"

    # Normalize newlines and strip BOM
    try:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if text and text[0] == "\ufeff":
            text = text.lstrip("\ufeff")
    except Exception:
        pass

    return text, str(enc)


def read_text(path: Union[str, Path], encoding: str = "utf-8", errors: str = "strict") -> str:
    """Read text from a path, handling multiple historical helper signatures.

    Behavior:
    - If a repository-provided io_text.read_text exists, attempt to call it
      with the most featureful signature and normalise the return value.
    - Supports encoding="auto" to trigger detection via detect_encoding.
    - Falls back to a robust manual reader if helper is unavailable or fails.

    Returns
    -------
    str: Decoded text.
    """
    p = Path(path)

    # Try repository helper
    if _io_text_read_text is not None:
        try:
            txt, used = _call_repo_read_text(p, encoding=encoding, errors=errors)
            return txt
        except Exception:
            # Fall through to manual reader
            pass

    # Manual fallback
    txt, _used = _manual_read_text(p, encoding=encoding, errors=errors)
    return txt


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for read_text (older callers may call this)."""
    return read_text(path, encoding=encoding)


def ingest(
    path: Union[str, Path],
    *,
    encoding: str = "utf-8",
    chunk_size: Optional[int] = None,
) -> Union[str, Iterator[str]]:
    """Read or stream text content from ``path``.

    Parameters
    ----------
    path : Union[str, Path]
        Filesystem path to a text file.
    encoding : str, default='utf-8'
        Encoding to use when decoding bytes. Pass ``"auto"`` to attempt
        autodetection.
    chunk_size : Optional[int], default=None
        If None, the entire file contents are returned as a single string.
        If a positive integer is provided, an iterator yielding successive
        chunks of up to ``chunk_size`` characters is returned.

    Raises
    ------
    FileNotFoundError
        If ``path`` points to a directory or does not exist.
    ValueError
        If ``chunk_size`` is provided but not a positive integer.
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Path not found: {file_path}")
    if file_path.is_dir():
        raise FileNotFoundError(f"Path is a directory: {file_path}")

    if chunk_size is None:
        # Return full text as string
        return read_text(file_path, encoding=encoding)

    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer when provided")

    def _iter() -> Iterator[str]:
        enc = detect_encoding(file_path) if isinstance(encoding, str) and encoding.lower() == "auto" else encoding
        # Use built-in open with detected encoding to stream text
        try:
            with file_path.open("r", encoding=enc, errors="replace") as fh:
                while True:
                    chunk = fh.read(chunk_size)
                    if chunk == "":
                        break
                    yield chunk
        except Exception as exc:
            # Surface as runtime error to calling code (ingestion pipelines should catch)
            raise RuntimeError(f"Failed to stream file {file_path}: {exc}") from exc

    return _iter()


class Ingestor:
    """Shim class exposing :func:`ingest` as a static method for backwards compatibility."""

    @staticmethod
    def ingest(
        path: Union[str, Path],
        *,
        encoding: str = "utf-8",
        chunk_size: Optional[int] = None,
    ) -> Union[str, Iterator[str]]:
        return ingest(path, encoding=encoding, chunk_size=chunk_size)
