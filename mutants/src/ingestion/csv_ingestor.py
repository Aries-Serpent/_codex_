"""
Csv Ingestor Module

This module provides functionality for csv ingestor.

Usage:
    from ingestion.csv_ingestor import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
from pathlib import Path

from .io_text import detect_encoding


def load_csv(path: str | Path, *, encoding: str = "utf-8", **kwargs) -> list[list[str]]:
    """Load CSV rows from ``path`` into a list.

    Parameters
    ----------
    path:
        Filesystem path to a CSV file.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    **kwargs:
        Additional arguments forwarded to :func:`csv.reader`.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = detect_encoding(p)
    with p.open("r", encoding=encoding, newline="") as fh:
        reader = csv.reader(fh, **kwargs)
        return list(reader)
