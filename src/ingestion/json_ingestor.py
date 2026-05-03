"""
Json Ingestor Module

This module provides functionality for json ingestor.

Usage:
    from ingestion.json_ingestor import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .io_text import detect_encoding


def load_json(path: str | Path, *, encoding: str = "utf-8") -> Any:
    """Load JSON data from ``path``.

    Parameters
    ----------
    path:
        Filesystem path to a JSON document.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = detect_encoding(p)
    with p.open("r", encoding=encoding) as fh:
        return json.load(fh)
