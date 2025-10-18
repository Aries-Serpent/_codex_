from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "tokenization.api is deprecated; use codex_ml.tokenization.api instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical API for backward compatibility
try:
    from codex_ml.tokenization.api import *  # noqa: F401,F403
except Exception:  # pragma: no cover
    # Provide a clearer import-time hint if optional deps are missing
    raise
