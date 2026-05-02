"""
Legacy compatibility layer for evaluate module.

DEPRECATED: Use src.training.evaluate instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.evaluate' is deprecated. Use 'src.training.evaluate' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.evaluate import evaluate  # noqa: E402

__all__ = ["evaluate"]
