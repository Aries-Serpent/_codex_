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

from src.training.accelerate_init_guard import (  # noqa: E402
    AccelerateInitResult,
    get_distributed_env_info,
    is_accelerate_available,
    is_gpu_available,
    safe_accelerate_init,
)

# Re-export Accelerator for tests that mock it
try:
    import accelerate as _accelerate_mod  # noqa: E402

    Accelerator = _accelerate_mod.Accelerator
except ImportError:
    Accelerator = None  # type: ignore[misc,assignment]

__all__ = [
    "Accelerator",
    "AccelerateInitResult",
    "get_distributed_env_info",
    "is_accelerate_available",
    "is_gpu_available",
    "safe_accelerate_init",
]
