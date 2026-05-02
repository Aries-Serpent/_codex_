"""
Legacy compatibility layer for seed_utils module.

DEPRECATED: Use src.training.seed_utils instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.seed_utils' is deprecated. Use 'src.training.seed_utils' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.seed_utils import set_all_seeds  # noqa: E402

__all__ = ["set_all_seeds"]
