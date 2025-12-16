"""
Legacy compatibility layer for accelerate_init_guard module.

DEPRECATED: Use src.training.accelerate_init_guard instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.accelerate_init_guard' is deprecated. "
    "Use 'src.training.accelerate_init_guard' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.accelerate_init_guard import (
    AccelerateInitResult,
    get_distributed_env_info,
    is_accelerate_available,
    is_gpu_available,
    safe_accelerate_init,
)

__all__ = [
    "AccelerateInitResult",
    "get_distributed_env_info",
    "is_accelerate_available",
    "is_gpu_available",
    "safe_accelerate_init",
]
