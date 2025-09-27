"""Lightweight tokenization cache primitives."""

from __future__ import annotations

import os
from collections import OrderedDict
from typing import Any, Hashable, Tuple

__all__ = ["TokenLRU", "GLOBAL_TOKEN_LRU", "cache_key", "is_cache_disabled"]


class TokenLRU:
    """Tiny in-memory LRU cache for tokenization outputs."""

    def __init__(self, maxsize: int = 8192) -> None:
        self.maxsize = maxsize
        self._d: OrderedDict[Hashable, Any] = OrderedDict()

    def get(self, key: Hashable) -> Any | None:
        value = self._d.get(key)
        if value is not None:
            self._d.move_to_end(key)
        return value

    def put(self, key: Hashable, value: Any) -> None:
        if key in self._d:
            self._d.move_to_end(key)
        self._d[key] = value
        if self.maxsize >= 0 and len(self._d) > self.maxsize:
            self._d.popitem(last=False)

    def clear(self) -> None:
        self._d.clear()


GLOBAL_TOKEN_LRU = TokenLRU()


def cache_key(
    text: str,
    padding: str | bool | None,
    truncation: bool | None,
    max_length: int | None,
    add_special_tokens: bool | None,
) -> Tuple[Any, ...]:
    return (text, padding, truncation, max_length, add_special_tokens)


_DISABLE_VALUES = {"1", "true", "yes", "on"}


def is_cache_disabled() -> bool:
    value = os.environ.get("CODEX_ML_TOKEN_CACHE_DISABLE")
    if value is None:
        return False
    return value.strip().lower() in _DISABLE_VALUES
