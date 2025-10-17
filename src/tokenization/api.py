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
        HFTokenizerAdapter as _CanonicalLegacyTokenizer,
        SentencePieceTokenizer,
    )
    HFTokenizerAdapter = _CanonicalLegacyTokenizer
except Exception:  # pragma: no cover - defensive placeholders
    _CanonicalLegacyTokenizer = None  # type: ignore[assignment]
    HFTokenizerAdapter = object  # type: ignore[assignment,misc]
    SentencePieceTokenizer = object  # type: ignore[assignment,misc]


def legacy_tokenizer(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Deprecated alias for :class:`HFTokenizerAdapter`."""

    _warnings.warn(
        "src.tokenization.api.legacy_tokenizer is deprecated; use "
        "codex_ml.tokenization.adapter.HFTokenizerAdapter instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _CanonicalLegacyTokenizer is None:
        raise ImportError(
            "HFTokenizerAdapter is unavailable; install codex-ml tokenization extras"
        )
    return _CanonicalLegacyTokenizer(*args, **kwargs)


__all__ = ["HFTokenizerAdapter", "SentencePieceTokenizer", "legacy_tokenizer"]
