"""
Legacy compatibility layer for offline_wandb module.

DEPRECATED: Use src.training.offline_wandb instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.offline_wandb' is deprecated. "
    "Use 'src.training.offline_wandb' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.offline_wandb import force_offline

__all__ = ["force_offline"]
