"""
Streaming Module

This module provides functionality for streaming.

Usage:
    from data.streaming import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json  # noqa: E402
from collections.abc import Callable, Iterator  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from .datamodule import StreamingDataModule  # noqa: E402
from .datamodule import default_example_validator as _default_example_validator  # noqa: E402

Validator = Callable[[Any], None]

default_example_validator = _default_example_validator


def iter_jsonl_chunks(
    path: str | Path,
    *,
    chunk_size: int = 1024,
    validator: Validator | None = None,
) -> Iterator[tuple[dict[str, Any], ...]]:
    """Yield tuples of records from a JSONL file without loading the entire file."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    p = Path(path)
    buffer: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except (ValueError, TypeError) as exc:  # pragma: no cover - surfaced in tests
                raise ValueError(f"Invalid JSON on line {line_number} of {p}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} of {p} must be a JSON object (got {type(record).__name__})"
                )
            if validator is not None:
                validator(record)
            buffer.append(record)
            if len(buffer) >= chunk_size:
                yield tuple(buffer)
                buffer.clear()
    if buffer:
        yield tuple(buffer)


__all__ = ["StreamingDataModule", "default_example_validator", "iter_jsonl_chunks"]
