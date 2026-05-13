from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "tokenization.api is deprecated; use codex_ml.tokenization.api instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical API for backward compatibility
try:
    from codex_ml.tokenization.api import (  # noqa: F401
        BOS_TOKEN,
        EOS_TOKEN,
        PAD_TOKEN,
        UNK_TOKEN,
        HFTokenizer,
        HFTokenizerAdapter,
        SPTokenizer,
        TokenizerAdapter,
        WhitespaceTokenizer,
        deprecated_legacy_access,
        get_tokenizer,
        load_tokenizer,
        pad_sequences,
    )
except Exception:  # pragma: no cover
    # Provide a clearer import-time hint if optional deps are missing
    raise

__all__ = [
    "BOS_TOKEN",
    "EOS_TOKEN",
    "HFTokenizer",
    "HFTokenizerAdapter",
    "PAD_TOKEN",
    "SPTokenizer",
    "TokenizerAdapter",
    "UNK_TOKEN",
    "WhitespaceTokenizer",
    "deprecated_legacy_access",
    "get_tokenizer",
    "load_tokenizer",
    "pad_sequences",
]
