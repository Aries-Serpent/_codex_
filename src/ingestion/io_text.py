"""Text I/O helpers with optional encoding detection.

Provides:
- read_text(path, encoding="utf-8", errors="strict") -> (text, used_encoding)
  - When encoding == "auto" a best-effort detection is attempted using a
    project-provided detect_encoding() if available, otherwise a local
    fallback detector is used.
- Robust error handling: file read / decode failures are handled gracefully
  and a sensible fallback encoding is attempted to return usable text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, Union

# Try to use the repository's encoding detector if present; otherwise provide
# a local, conservative fallback detector to preserve functionality.
try:
    from .encoding_detect import detect_encoding  # type: ignore
except Exception:
    detect_encoding = None  # type: ignore


def _fallback_detect_encoding(path: Path, sample_size: int = 131072) -> str:
    """Conservative best-effort encoding detection used as a fallback.

    Strategy:
      1. Check for common BOM signatures.
      2. If charset_normalizer is available, consult it.
      3. Try a small set of common encodings by attempting to decode.
      4. Fall back to 'utf-8'.

    This fallback never raises and returns a string encoding name.
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
        # defensive: fall through to other strategies
        pass

    safe_encodings = {"utf-8", "utf-16", "utf-32", "cp1252", "windows-1252", "iso-8859-1"}

    # Try charset-normalizer.from_path if available
    try:
        from charset_normalizer import from_path  # type: ignore

        result = from_path(str(path))
        best = result.best() if result is not None else None
        enc = getattr(best, "encoding", None)
        enc_norm = enc.lower().replace("_", "-") if enc else None
    except Exception:
        enc_norm = None

    if enc_norm:
        enc_choice = "cp1252" if enc_norm == "windows-1252" else enc_norm
        if enc_choice in safe_encodings:
            return enc_choice

    # Heuristic trials
    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception:
            continue

    return "utf-8"


# Ensure a usable detect_encoding callable exists
if detect_encoding is None:
    detect_encoding = _fallback_detect_encoding  # type: ignore


__all__ = ["read_text"]


def read_text(path: Union[Path, str], encoding: str = "utf-8", errors: str = "strict") -> Tuple[str, str]:
    """Read text from ``path`` normalising newlines and stripping BOMs.

    Returns a tuple (text, used_encoding).

    Parameters
    - path: Path or str pointing to the file to read.
    - encoding: encoding name or "auto". If "auto", a best-effort detection is
      performed using the project's detect_encoding() helper when available.
    - errors: error handling strategy passed to bytes.decode() (default "strict").

    Behavior and error handling
    - If the file cannot be read, returns ("", encoding).
    - If decoding with the requested encoding fails, a sequence of fallback
      decoders is tried to produce usable text (with 'replace' semantics).
    - Newlines are normalised to '\n' and a leading BOM (U+FEFF) is stripped.
    """
    p = Path(path)

    # Determine encoding to use
    used_encoding = encoding
    if encoding == "auto":
        try:
            used_encoding = detect_encoding(p)  # type: ignore[arg-type]
        except Exception:
            # Defensive fallback: if detection fails, default to utf-8
            used_encoding = "utf-8"

    # Read bytes
    try:
        raw = p.read_bytes()
    except Exception:
        return "", used_encoding

    # Attempt to decode using the chosen encoding and provided error policy.
    try:
        text = raw.decode(used_encoding, errors)
    except (LookupError, UnicodeDecodeError, Exception):
        # Try a set of fallback encodings using replace to avoid errors and
        # provide usable text to callers.
        fallback_encodings = ["utf-8", "cp1252", "iso-8859-1"]
        decoded = None
        for enc in fallback_encodings:
            try:
                decoded = raw.decode(enc, "replace")
                used_encoding = enc
                break
            except Exception:
                decoded = None
                continue
        if decoded is None:
            return "", used_encoding
        text = decoded

    # Normalize newlines and strip BOM (U+FEFF) if present
    try:
        text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    except Exception:
        # If normalization fails for any reason, return decoded text as-is
        pass

    return text, used_encoding
