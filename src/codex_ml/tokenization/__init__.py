"""Unified tokenization export surface with deprecation shims."""

from __future__ import annotations

from ._protocols import TokenizerAdapter
from ._types import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN
from .adapter import WhitespaceTokenizer
from .api import get_tokenizer, load_tokenizer, pad_sequences

try:
    from codex_ml.interfaces.tokenizer import HFTokenizer
except Exception:  # pragma: no cover - optional dependency guard
    HFTokenizer = None  # type: ignore[assignment]

try:
    from .hf_tokenizer import HFTokenizerAdapter
except Exception:  # pragma: no cover - optional dependency guard
    HFTokenizerAdapter = None  # type: ignore[assignment]

try:
    from .sp_trainer import SPTokenizer
except Exception:  # pragma: no cover - optional dependency guard
    SPTokenizer = None  # type: ignore[assignment]

__all__ = [
    "load_tokenizer",
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
    "pad_sequences",
]
