"""
Legacy compatibility layer for streaming module.

DEPRECATED: Use src.training.streaming instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.streaming' is deprecated. Use 'src.training.streaming' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.streaming import stream_texts  # noqa: E402

__all__ = ["stream_texts"]
