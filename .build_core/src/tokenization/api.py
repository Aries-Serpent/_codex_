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
    from codex_ml.tokenization.adapter import HFTokenizerAdapter as _CanonicalLegacyTokenizer
    from codex_ml.tokenization.adapter import (
        SentencePieceTokenizer,
    )

    HFTokenizerAdapter = _CanonicalLegacyTokenizer
except (ImportError, AttributeError):  # pragma: no cover - defensive placeholders
    _CanonicalLegacyTokenizer = None

    class HFTokenizerAdapter:  # type: ignore[no-redef]
        """Placeholder that raises when the canonical adapter is unavailable."""

        def __init__(self, *_args, **_kwargs):
            raise ImportError(
                "HFTokenizerAdapter is unavailable; install codex-ml tokenization extras"
            )

    class SentencePieceTokenizer:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs):
            raise ImportError(
                "SentencePieceTokenizer is unavailable; install codex-ml tokenization extras"
            )


class _LegacyTokenizerProxy:
    """Proxy that forwards to :class:`HFTokenizerAdapter` with a warning."""

    __slots__ = ()

    if _CanonicalLegacyTokenizer is not None:
        __doc__ = getattr(_CanonicalLegacyTokenizer, "__doc__", None)

    def __call__(self, *args, **kwargs):
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

    def __getattr__(self, name):
        _warnings.warn(
            "src.tokenization.api.legacy_tokenizer is deprecated; use "
            "codex_ml.tokenization.adapter.HFTokenizerAdapter instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if _CanonicalLegacyTokenizer is None:
            raise AttributeError(
                "HFTokenizerAdapter is unavailable; install codex-ml tokenization extras"
            )
        return getattr(_CanonicalLegacyTokenizer, name)


legacy_tokenizer = _LegacyTokenizerProxy()
if getattr(legacy_tokenizer, "__doc__", None) is None:
    legacy_tokenizer.__doc__ = "Deprecated alias for HFTokenizerAdapter."  # type: ignore[misc]


__all__ = ["HFTokenizerAdapter", "SentencePieceTokenizer", "legacy_tokenizer"]
