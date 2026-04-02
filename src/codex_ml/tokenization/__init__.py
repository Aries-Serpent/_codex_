"""Unified tokenization export surface with deprecation shims."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._protocols import TokenizerAdapter
from ._types import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN
from .adapter import WhitespaceTokenizer
from .api import _load_export as _lazy_load_export  # noqa: PLC2701
from .api import load_tokenizer, pad_sequences

try:
    from codex_ml.interfaces.tokenizer import HFTokenizer
except Exception:  # pragma: no cover - optional dependency guard
    HFTokenizer = None

# HFTokenizerAdapter and SPTokenizer are optional-dependency attributes.  They must
# NOT be bound at module level to None — doing so would prevent __getattr__ from
# firing and would silently return None to callers instead of a helpful error.
if TYPE_CHECKING:  # pragma: no cover
    from .hf_tokenizer import HFTokenizerAdapter
    from .sp_trainer import SPTokenizer


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load optional attributes with deprecation shim for `get_tokenizer`."""
    if name == "get_tokenizer":
        import warnings as _warnings

        from .api import get_tokenizer as _get_tokenizer

        _warnings.warn(
            "Accessing 'codex_ml.tokenization.get_tokenizer' is deprecated; "
            "import from 'codex_ml.tokenization.api' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _get_tokenizer
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
