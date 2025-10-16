"""Standalone HF tokenizer adapter backed by the `tokenizers` library."""

from __future__ import annotations

import warnings

from codex_ml.tokenization.hf_adapter import HFTokenizerAdapter as _HFTokenizerAdapter

warnings.warn(
    "codex_ml.interfaces.tokenizer_hf is deprecated; import HFTokenizerAdapter "
    "from codex_ml.tokenization.hf_adapter instead.",
    DeprecationWarning,
    stacklevel=2,
)

HFTokenizerAdapter = _HFTokenizerAdapter

__all__ = ["HFTokenizerAdapter"]
