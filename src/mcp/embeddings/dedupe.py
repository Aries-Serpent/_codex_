"""
Dedupe Module

This module provides functionality for dedupe.

Usage:
    from embeddings.dedupe import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import hashlib
import json
from typing import Any


def checksum_for_item(item: dict[str, Any]) -> str:
    s = json.dumps(
        {
            "id": item.get("id"),
            "content": item.get("content"),
            "metadata": item.get("metadata", {}),
        },
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class InMemoryDeduper:
    def __init__(self):
        self._seen: set[str] = set()

    def is_duplicate(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(c)
        return False
