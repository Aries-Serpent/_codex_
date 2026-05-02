"""
Legacy compatibility layer for seed module.

DEPRECATED: Use src.training.seed instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.seed' is deprecated. Use 'src.training.seed' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.seed import ensure_global_seed  # noqa: E402

__all__ = ["ensure_global_seed"]
