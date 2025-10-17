"""
Legacy tokenization API shim.

New code should import from:
  - codex_ml.tokenization.adapter
  - codex_ml.tokenization.hf_adapter
  - codex_ml.tokenization.sentencepiece_adapter
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "src.tokenization.api is legacy; use codex_ml.tokenization.* modules.",
    DeprecationWarning,
    stacklevel=2,
)

# Provide thin re-exports for compatibility
try:  # pragma: no cover
    from codex_ml.tokenization.adapter import (  # type: ignore
        HFTokenizerAdapter,
        SentencePieceTokenizer,
    )
except Exception:  # pragma: no cover - defensive placeholders
    HFTokenizerAdapter = object  # type: ignore[assignment,misc]
    SentencePieceTokenizer = object  # type: ignore[assignment,misc]
__all__ = ["HFTokenizerAdapter", "SentencePieceTokenizer"]
