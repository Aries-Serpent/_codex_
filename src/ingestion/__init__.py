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

import logging

logger = logging.getLogger(__name__)

from collections.abc import Iterator
from pathlib import Path
from typing import Optional, Union

# Local utility imports (optional modules handled gracefully)
try:
    # Prefer a dedicated encoding detector if present in repo
    from .encoding_detect import detect_encoding as _repo_detect_encoding
except (IOError, OSError):
    logger.warning("Exception occurred", exc_info=True)
    _repo_detect_encoding = None  # type: ignore[assignment]

try:
    # io_text.read_text historically provided a number of signatures:
    # - read_text(path) -> str
    # - read_text(path, encoding) -> str
    # - read_text(path, encoding, errors) -> (str, used_encoding)
    from .io_text import read_text as _io_text_read_text
except (IOError, OSError):
    logger.warning("Exception occurred", exc_info=True)
    _io_text_read_text = None  # type: ignore[assignment]

try:
    # Some callers expect _detect_encoding from io_text
    from .io_text import _fallback_detect_encoding as _io_text__detect_encoding
except (IOError, OSError):
    logger.warning("Exception occurred", exc_info=True)
    _io_text__detect_encoding = None  # type: ignore[assignment]

# Deterministic shuffle and legacy read_text_file may live in utils
try:
    from .utils import deterministic_shuffle as _deterministic_shuffle
except (IOError, OSError):
    logger.warning("Exception occurred", exc_info=True)
    _deterministic_shuffle = None  # type: ignore[assignment]

__all__ = [
    "Ingestor",
    "_detect_encoding",  # Backward compatibility alias
    "detect_encoding",
    "deterministic_shuffle",
    "ingest",
    "read_text",
    "read_text_file",
]

# Expose deterministic_shuffle when available, otherwise provide a local fallback.
if _deterministic_shuffle is None:
    import random
    from collections.abc import Sequence
    from typing import TypeVar

    T = TypeVar("T")

    def deterministic_shuffle(seq: Sequence[T], seed: int) -> list[T]:
        """Deterministic shuffle fallback (seeded RNG)."""
        items = list(seq)
        rng = random.Random(seed)  # nosec B311 - deterministic fallback shuffle
        rng.shuffle(items)
        return items

else:
    deterministic_shuffle = _deterministic_shuffle


# Provide a detect_encoding wrapper that uses repo detector, io_text helper, or a conservative fallback.  # noqa: E501
def detect_encoding(path: str | Path) -> str:
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
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            # Fall through to other detectors
    if _io_text__detect_encoding is not None:
        try:
            return _io_text__detect_encoding(p)
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    # Fallback conservative detector: BOM checks, then try a few encodings
    try:
        raw = p.read_bytes()[:65536]
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return "utf-8"

    # BOM checks
    try:
        if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32"
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
    except (ValueError, TypeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            raw.decode(enc)
            return enc
        except (ValueError, TypeError):
            logger.warning("Exception occurred", exc_info=True)
            continue

    return "utf-8"


# Provide _detect_encoding as backward-compatible alias for code expecting the underscore version
_detect_encoding = detect_encoding


# Internal helper to normalise various historical read_text signatures.
def _call_repo_read_text(
    path: Path, encoding: str = "utf-8", errors: str = "strict"
) -> tuple[str, Optional[str]]:
    """Call repository io_text.read_text in a way that handles multiple historical signatures.

    Returns:
        (text, used_encoding_or_None)
    """
    if _io_text_read_text is None:
        raise RuntimeError("Repository io_text.read_text is not available")
    # Try the richer signatures first and progressively fall back.
    try:
        # Newer helpers may return (text, used_encoding)
        result = _io_text_read_text(path, encoding=encoding, errors=errors)
    except TypeError as e:
        type(e).__name__
        logger.debug("TypeError: <ERROR_TYPE>")
        logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
        try:
            # Older helper may accept (path, encoding)
            result = _io_text_read_text(path, encoding)
        except TypeError as e:
            type(e).__name__
            logger.debug("TypeError: <ERROR_TYPE>")
            logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
            try:
                # Very old: only path
                result = _io_text_read_text(path)
            except (IOError, OSError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                raise RuntimeError(f"repo read_text failed: {exc}") from exc
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        # Pass up other errors as runtime errors
        raise RuntimeError(f"repo read_text failed: {exc}") from exc

    # Normalise return value
    if (isinstance(result, (tuple, list))) and len(result) >= 1:
        txt = result[0]
        used = result[1] if len(result) > 1 else None
        return str(txt), (str(used) if used is not None else None)
    if isinstance(result, str):
        return result, None
    # Coerce to string for unexpected return types
    return str(result), None


def _manual_read_text(
    path: Path, encoding: str = "utf-8", errors: str = "strict"
) -> tuple[str, str]:
    """Manual robust reader used as a last-resort fallback.

    Returns (text, used_encoding)
    """
    try:
        raw = path.read_bytes()
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        raise RuntimeError(f"Failed to read bytes from {path}: {exc}") from exc

    enc = encoding
    if isinstance(enc, str) and enc.lower() == "auto":
        enc = detect_encoding(path)

    # Try to decode using chosen encoding, and fall back gracefully
    try:
        text = raw.decode(enc, errors)
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # Try common fallbacks
        for trial in ("utf-8", "cp1252", "iso-8859-1"):
            try:
                text = raw.decode(trial, "replace")
                enc = trial
                break
            except (ValueError, TypeError):
                logger.warning("Exception occurred", exc_info=True)
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
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    return text, str(enc)


def read_text(path: str | Path, encoding: str = "utf-8", errors: str = "strict") -> str:
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
            txt, _used = _call_repo_read_text(p, encoding=encoding, errors=errors)
            return txt
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            # Fall through to manual reader

    # Manual fallback
    txt, _used = _manual_read_text(p, encoding=encoding, errors=errors)
    return txt


def read_text_file(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for read_text (older callers may call this)."""
    return read_text(path, encoding=encoding)


def ingest(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    chunk_size: Optional[int] = None,
) -> str | Iterator[str]:
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
        enc = (
            detect_encoding(file_path)
            if isinstance(encoding, str) and encoding.lower() == "auto"
            else encoding
        )
        # Use built-in open with detected encoding to stream text
        try:
            with file_path.open("r", encoding=enc, errors="replace") as fh:
                while True:
                    chunk = fh.read(chunk_size)
                    if chunk == "":
                        break
                    yield chunk
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            # Surface as runtime error to calling code (ingestion pipelines should catch)
            raise RuntimeError(f"Failed to stream file {file_path}: {exc}") from exc

    return _iter()


class Ingestor:
    """Shim class exposing :func:`ingest` as a static method for backwards compatibility."""

    @staticmethod
    def ingest(
        path: str | Path,
        *,
        encoding: str = "utf-8",
        chunk_size: Optional[int] = None,
    ) -> str | Iterator[str]:
        return ingest(path, encoding=encoding, chunk_size=chunk_size)
