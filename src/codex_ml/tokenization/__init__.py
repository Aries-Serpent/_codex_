"""Unified tokenization export surface with deprecation shims."""

from __future__ import annotations

__all__ = [
    "get_tokenizer",
    "WhitespaceTokenizer",
    "HFTokenizer",
    "TokenizerAdapter",
    "HFTokenizerAdapter",
    "SPTokenizer",
    "BOS_TOKEN",
    "EOS_TOKEN",
    "PAD_TOKEN",
    "UNK_TOKEN",
]


def __getattr__(name: str):
    from .api import deprecated_legacy_access

    value = deprecated_legacy_access(name)
    if value is None:
        raise AttributeError(name)
    return value
