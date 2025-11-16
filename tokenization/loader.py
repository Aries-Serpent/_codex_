"""Compatibility wrapper that re-exports the canonical tokenizer loader."""
from __future__ import annotations

from codex_ml.tokenization.api import TokenizerAdapter, get_tokenizer, load_tokenizer

__all__ = ["TokenizerAdapter", "load_tokenizer", "get_tokenizer"]
