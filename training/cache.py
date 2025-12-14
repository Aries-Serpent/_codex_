"""
Legacy compatibility layer for cache module.

DEPRECATED: Use src.training.cache instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.cache' is deprecated. "
    "Use 'src.training.cache' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.cache import TokenCache

__all__ = ["TokenCache"]
