from __future__ import annotations

import warnings
from typing import Any

# This shim provides a transitional layer for legacy tokenization imports.
# It re-exports the new implementations and issues DeprecationWarning
# when legacy-named symbols are accessed via this module.

__all__ = [
    "HFTokenizerAdapter",
    "SentencePieceTokenizer",
    "legacy_tokenizer",
]


def _import_hf_adapter():
    try:
        from src.codex_ml.tokenization.adapter import HFTokenizerAdapter  # type: ignore

        return HFTokenizerAdapter
    except Exception as e:  # pragma: no cover
        # Fallback: raise a clear error at access time
        raise ImportError(
            "HFTokenizerAdapter not found in src.codex_ml.tokenization.adapter"
        ) from e


def _import_spm_tokenizer():
    try:
        from src.codex_ml.tokenization.sentencepiece_tokenizer import SentencePieceTokenizer  # type: ignore

        return SentencePieceTokenizer
    except Exception as e:  # pragma: no cover
        raise ImportError(
            "SentencePieceTokenizer not found in src.codex_ml.tokenization.sentencepiece_tokenizer"
        ) from e


class _DeprecationProxy:
    def __init__(self, getter, legacy_name: str, new_name: str):
        self._getter = getter
        self._legacy = legacy_name
        self._new = new_name

    def __call__(self, *args, **kwargs):
        warnings.warn(
            f"{self._legacy} is deprecated; use {self._new} from src.codex_ml.tokenization.*",
            DeprecationWarning,
            stacklevel=2,
        )
        cls = self._getter()
        return cls(*args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        warnings.warn(
            f"{self._legacy} is deprecated; use {self._new} from src.codex_ml.tokenization.*",
            DeprecationWarning,
            stacklevel=2,
        )
        target = self._getter()
        return getattr(target, item)


# Re-export current names directly (no warning)
try:
    HFTokenizerAdapter = _import_hf_adapter()
except ImportError:
    HFTokenizerAdapter = None  # type: ignore[assignment]
try:
    SentencePieceTokenizer = _import_spm_tokenizer()
except ImportError:
    SentencePieceTokenizer = None  # type: ignore[assignment]

# Legacy alias (access triggers warning)
legacy_tokenizer = _DeprecationProxy(_import_hf_adapter, "legacy_tokenizer", "HFTokenizerAdapter")
