"""
Legacy SentencePiece adapter shim.

Prefer codex_ml.tokenization.sentencepiece_adapter for new code.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "src.tokenization.sentencepiece_adapter is legacy; use "
    "codex_ml.tokenization.sentencepiece_adapter instead.",
    DeprecationWarning,
    stacklevel=2,
)

try:  # pragma: no cover
    from codex_ml.tokenization.sentencepiece_adapter import (
        SentencePieceAdapter as _CanonicalSentencePieceAdapter,  # type: ignore
    )
    from codex_ml.tokenization.sentencepiece_adapter import (
        SentencePieceTokenizer,
        load_sentencepiece_model,
    )
except Exception:  # pragma: no cover - defensive placeholders

    def load_sentencepiece_model(*_args, **_kwargs):
        raise RuntimeError("SentencePiece not available")

    class SentencePieceTokenizer:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("SentencePiece not available")

    class SentencePieceAdapter:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("SentencePiece not available")

else:
    SentencePieceAdapter = _CanonicalSentencePieceAdapter
    SentencePieceAdapter.__doc__ = getattr(  # type: ignore[attr-defined]
        _CanonicalSentencePieceAdapter, "__doc__", None
    )


__all__ = [
    "SentencePieceAdapter",
    "SentencePieceTokenizer",
    "load_sentencepiece_model",
]
