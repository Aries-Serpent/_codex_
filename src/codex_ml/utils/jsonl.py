"""
Jsonl Module

This module provides functionality for jsonl.

Usage:
    from utils.jsonl import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path


def append_jsonl(path: str | Path, record: Mapping[str, object]) -> None:
    """Append *record* as a single JSON line to the NDJSON file at *path*.

    The parent directory is created automatically if it does not already exist.
    Each call writes exactly one UTF-8 encoded JSON object followed by a
    newline, making the file a valid `NDJSON
    <https://github.com/ndjson/ndjson-spec>`_ stream.

    Args:
        path: Destination file path (created if absent, appended otherwise).
        record: Mapping whose keys and values must be JSON-serialisable.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")


__all__ = ["append_jsonl"]
