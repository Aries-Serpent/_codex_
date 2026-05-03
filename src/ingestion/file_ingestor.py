"""
File Ingestor Module

This module provides functionality for file ingestor.

Usage:
    from ingestion.file_ingestor import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from pathlib import Path

from .io_text import detect_encoding


def read_file(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Return the contents of ``path`` decoded as text.

    Parameters
    ----------
    path:
        Filesystem path to a text file.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = detect_encoding(p)
    return p.read_text(encoding=encoding)
