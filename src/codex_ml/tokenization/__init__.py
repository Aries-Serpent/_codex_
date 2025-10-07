"""Unified tokenization export surface with deprecation shims."""

from __future__ import annotations

from .api import deprecated_legacy_access

__all__ = ["get_tokenizer", "WhitespaceTokenizer", "HFTokenizer"]


def __getattr__(name: str):
    value = deprecated_legacy_access(name)
    if value is not None:
        return value
    raise AttributeError(name)
