"""
Batcher Module

This module provides functionality for batcher.

Usage:
    from embeddings.batcher import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import hashlib
import json
from collections.abc import Generator, Iterable
from typing import Any


def compute_checksum(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {
            "id": item.get("id"),
            "content": item.get("content"),
            "metadata": item.get("metadata", {}),
        },
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def batch_iterable(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
