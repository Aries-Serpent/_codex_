from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "tokenization.loader is deprecated; use codex_ml.tokenization.api.load_tokenizer instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical API for backward compatibility
try:
    from codex_ml.tokenization.api import load_tokenizer  # noqa: F401
except Exception:  # pragma: no cover
    # Provide a clearer import-time hint if optional deps are missing
    raise
