"""Utility helpers for file operations, text reading, and deterministic shuffling.

This module provides a unified interface for file operations that combines:
- Text reading with optional/automatic encoding detection
- Deterministic shuffling for reproducible data processing
- Backward-compatible wrappers for different API variants

Key functions:
- read_text(path, encoding="utf-8", errors="strict") -> str
  - A robust wrapper around an internal io_text.read_text when available.
    Accepts older/newer signatures and normalises return values.
- read_text_file(path, encoding="utf-8") -> str
  - Backward-compatible alias for read_text.
- deterministic_shuffle(seq, seed) -> list
  - Reproducible shuffling using a seed.
- seeded_shuffle(seq, seed) -> list
  - Alias for deterministic_shuffle for backwards compatibility.
- _detect_encoding(path) -> str
  - Exposes encoding detection (uses package-provided detect_encoding when available,
    otherwise falls back to a conservative detector).
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import List, Sequence, Tuple, TypeVar, Union

T = TypeVar("T")

# Try to import the repository-provided encoding detector if present.
try:
    from .encoding_detect import detect_encoding as _repo_detect_encoding  # type: ignore
except Exception:
    _repo_detect_encoding = None  # type: ignore

# Try to import the io_text.read_text helper if available. Some historical
# variants return (text, encoding) while others return just text; the wrapper
# below handles both.
try:
    from .io_text import read_text as _io_read_text  # type: ignore
except Exception:
    _io_read_text = None  # type: ignore


__all__ = [
    "deterministic_shuffle",
    "seeded_shuffle",
    "read_text",
    "read_text_file",
    "_detect_encoding",
    "REPO_READ_TEXT_AVAILABLE",
    "write_manifest",
]


# Expose whether the repository io_text.read_text was found (useful for callers/tests)
REPO_READ_TEXT_AVAILABLE = _io_read_text is not None


def _fallback_detect_encoding(path: Path, sample_size: int = 131072) -> str:
    """Conservative best-effort encoding detection used as a fallback.

    Strategy:
      1. Check for common BOM signatures.
      2. If charset_normalizer is available, consult it.
      3. Try a small set of common encodings by attempting to decode.
      4. Fall back to 'utf-8'.
    """
    try:
        data = path.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        return "utf-8"

    # BOM checks
    try:
        if data.startswith(b"\xff\xfe\x00\x00") or data.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32"
        if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
            return "utf-16"
        if data.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
    except Exception:
        pass

    safe_encodings = {"utf-8", "utf-16", "utf-32", "cp1252", "windows-1252", "iso-8859-1"}

    try:  # optional dependency
        from charset_normalizer import from_bytes  # type: ignore

        result = from_bytes(data)
        best = result.best() if result is not None else None
        enc = best.encoding.lower().replace("_", "-") if best and best.encoding else None
    except Exception:
        enc = None
    if enc:
        enc_norm = "cp1252" if enc == "windows-1252" else enc
        if enc_norm in safe_encodings:
            return enc_norm

    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception:
            continue

    return "utf-8"


def _detect_encoding(path: Union[str, Path]) -> str:
    """Expose encoding detection (thin wrapper).

    Uses repository-provided detect_encoding if available; otherwise falls back
    to a conservative internal detector.
    """
    p = Path(path)
    if _repo_detect_encoding is not None:
        try:
            return _repo_detect_encoding(p)
        except Exception:
            # fall through to fallback detector
            pass
    return _fallback_detect_encoding(p)


def deterministic_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled list using ``seed`` for determinism.

    This is the canonical implementation; use this for reproducible shuffles.
    """
    items = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items


# Backward compatibility: ensure seeded_shuffle is available (some callers expect this name)
def seeded_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Alias for deterministic_shuffle for backward compatibility."""
    return deterministic_shuffle(seq, seed)


def write_manifest(
    name: str,
    sources: Sequence[str] | None,
    seed: int,
    split_cfg: dict | None,
    out_dir: str,
) -> None:
    """Write dataset provenance manifest to .codex/datasets/<name>.json."""
    import json
    import subprocess
    from pathlib import Path

    out = Path(out_dir) / ".codex" / "datasets"
    out.mkdir(parents=True, exist_ok=True)
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        sha = None
    manifest = {
        "name": name,
        "sources": list(sources or []),
        "seed": seed,
        "splits": split_cfg or {},
        "commit": sha,
    }
    (out / f"{name}.json").write_text(json.dumps(manifest, indent=2))


def _manual_read_text(
    path: Union[str, Path], encoding: str = "utf-8", errors: str = "strict"
) -> Tuple[str, str]:
    """Read bytes and decode using provided encoding (or detect when 'auto').

    Returns (text, used_encoding)
    """
    p = Path(path)
    try:
        data = p.read_bytes()
    except Exception as exc:
        raise RuntimeError(f"Failed to read bytes from {p}: {exc}") from exc

    enc = encoding
    if isinstance(enc, str) and enc.lower() == "auto":
        enc = _detect_encoding(p)

    try:
        text = data.decode(enc if isinstance(enc, str) else "utf-8", errors)
    except Exception:
        # Fallback: try common encodings with replacement to ensure we return something
        for trial in ("utf-8", "cp1252", "iso-8859-1"):
            try:
                text = data.decode(trial, "replace")
                enc = trial
                break
            except Exception:
                continue
        else:
            # As a last resort, decode as utf-8 with replacement
            text = data.decode("utf-8", "replace")
            enc = "utf-8"
    # Normalize newlines and strip BOM
    try:
        text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    except Exception:
        pass
    return text, str(enc)


def read_text(path: Union[str, Path], encoding: str = "utf-8", errors: str = "strict") -> str:
    """Read text from ``path`` using optional encoding detection.

    This wrapper attempts to call into a repository-provided ``io_text.read_text``
    helper when available. It supports multiple historical signatures:

    - Newer: read_text(path, encoding="utf-8", errors="strict") -> (text, used_encoding)
    - Older: read_text(path, encoding="utf-8") -> str
    - Some implementations may accept only a single positional path argument.

    This function normalises these variants and always returns a string.
    """
    p = Path(path)

    # If repository helper is present, try to call it in a few ways to maximize compatibility.
    if _io_read_text is not None:
        # Try the most featureful call first
        try:
            result = _io_read_text(p, encoding=encoding, errors=errors)  # type: ignore[misc]
        except TypeError:
            # The helper may not accept encoding/errors kwargs — try positional and fewer args
            try:
                result = _io_read_text(p, encoding)  # type: ignore[misc]
            except TypeError:
                try:
                    result = _io_read_text(p)  # type: ignore[misc]
                except Exception:
                    result = None
        except Exception:
            # If the helper raised for any reason, fall back to manual reader below
            result = None

        # If the helper returned something, normalise to string
        if result is not None:
            try:
                # Some implementations return (text, used_encoding)
                if isinstance(result, (tuple, list)) and len(result) >= 1:
                    txt = result[0]
                    if not isinstance(txt, str):
                        txt = str(txt)
                    return txt
                # Or they return a plain string
                if isinstance(result, str):
                    return result
                # Unexpected object: coerce to string
                return str(result)
            except Exception:
                # Fall through to manual reader
                pass

    # Fallback: manual read & decode using our internal logic
    text, _used = _manual_read_text(p, encoding=encoding, errors=errors)
    return text


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for :func:`read_text`.

    Some older callers used the name `read_text_file` and passed encoding; keep
    that behavior.
    """
    return read_text(path, encoding=encoding)


# Provide internal alias for legacy callers expecting a top-level _detect_encoding
# function name.
def _detect_encoding_wrapper(path: Union[str, Path]) -> str:
    return _detect_encoding(path)


# Make the canonical _detect_encoding name available (kept for backward compatibility)
_detect_encoding = _detect_encoding  # type: ignore

# End of file
