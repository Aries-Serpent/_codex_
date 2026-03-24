"""Unified tokenization export surface with deprecation shims."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._protocols import TokenizerAdapter
from ._types import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN
from .adapter import WhitespaceTokenizer
from .api import _load_export as _lazy_load_export  # noqa: PLC2701
from .api import get_tokenizer, load_tokenizer, pad_sequences

try:
    from codex_ml.interfaces.tokenizer import HFTokenizer
except Exception:  # pragma: no cover - optional dependency guard
    HFTokenizer = None  # type: ignore[assignment]

# HFTokenizerAdapter and SPTokenizer are optional-dependency attributes.  They must
# NOT be bound at module level to None — doing so would prevent __getattr__ from
# firing and would silently return None to callers instead of a helpful error.
if TYPE_CHECKING:  # pragma: no cover
    from .hf_tokenizer import HFTokenizerAdapter
    from .sp_trainer import SPTokenizer


def __getattr__(name: str):  # noqa: ANN001, ANN202
    """Lazy-load optional attributes (HFTokenizerAdapter, SPTokenizer)."""
    return _lazy_load_export(name)


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
