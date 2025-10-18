from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "tokenization.sentencepiece_adapter is deprecated; use codex_ml.tokenization.sentencepiece_adapter instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical implementation
try:
    from codex_ml.tokenization.sentencepiece_adapter import *  # noqa: F401,F403
except Exception:  # pragma: no cover
    raise
