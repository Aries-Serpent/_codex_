"""
Jsonl Stream Module

This module provides functionality for jsonl stream.

Usage:
    from data.jsonl_stream import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
from collections.abc import Iterator, Mapping, MutableMapping  # noqa: E402
from pathlib import Path  # noqa: E402

__all__ = ["iter_jsonl"]


def iter_jsonl(path: str | Path, *, strict: bool = True) -> Iterator[dict[str, object]]:
    """Yield JSON objects from *path* line by line without loading the file.

    Parameters
    ----------
    path:
        Location of the JSONL/NDJSON file.
    strict:
        When ``True`` (default) a malformed line raises ``ValueError``. When
        ``False`` the line is skipped and iteration continues. Empty lines are
        ignored in both cases.
    """

    file_path = Path(path)
    if not file_path.exists():  # pragma: no cover - defensive guard
        raise FileNotFoundError(f"JSONL file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except (IOError, OSError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                if strict:
                    raise ValueError(
                        f"Invalid JSON on line {line_number} in {file_path}: {exc}"
                    ) from exc
                continue
            if not isinstance(obj, MutableMapping):
                if isinstance(obj, Mapping):
                    obj = dict(obj)
                else:
                    raise ValueError(
                        f"Line {line_number} in {file_path} did not contain a JSON object"
                    )
            yield dict(obj)
