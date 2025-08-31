"""Text I/O helpers with optional encoding detection."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .encoding_detect import detect_encoding

__all__ = ["read_text"]


def read_text(path: Path | str, encoding: str = "utf-8", errors: str = "strict") -> Tuple[str, str]:
    """Read text from ``path`` normalising newlines and stripping BOMs.

    Returns a tuple of ``(text, used_encoding)``. When ``encoding`` is set to
    ``"auto"`` a best-effort detection is attempted using
    :mod:`charset_normalizer` if available; otherwise ``utf-8`` is used.
    """

    p = Path(path)
    enc = detect_encoding(p) if encoding == "auto" else encoding
    data = p.read_bytes()
    text = data.decode(enc, errors)
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    return text, enc
