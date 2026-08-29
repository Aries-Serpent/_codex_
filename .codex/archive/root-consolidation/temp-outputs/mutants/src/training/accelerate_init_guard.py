#!/usr/bin/env python3
"""
Safe accelerate initialization guard with CPU fallback.

Provides structured diagnostics and never raises on CPU-only environments.
Designed to be skip-safe on GitHub runners and CI environments.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Exported at module level so tests can patch via
# patch("src.training.accelerate_init_guard.Accelerator", ...)
try:
    import accelerate as _accelerate_mod

    Accelerator = _accelerate_mod.Accelerator
    _ACCELERATOR_AVAILABLE = True
except ImportError:
    Accelerator = None
    _ACCELERATOR_AVAILABLE = False
_ACCELERATE_SPEC_AVAILABLE: Optional[bool] = None


@dataclass
class AccelerateInitResult:
    """Result of safe_accelerate_init with structured diagnostics."""

    success: bool

    accelerate_available: bool

    gpu_available: bool

    backend: Optional[str]

    world_size: int

    rank: int

    error: Optional[str]

    skip_reason: Optional[str]

    def __str__(self) -> str:
        """Human-readable summary."""
        if self.success:
            return f"AccelerateInitResult(success=True, backend={self.backend}, world_size={self.world_size})"  # noqa: E501
        if self.skip_reason:
            return f"AccelerateInitResult(skipped, reason={self.skip_reason})"
        return f"AccelerateInitResult(failed, error={self.error})"


def is_accelerate_available() -> bool:
    """Check if accelerate package is importable.

    The ``Accelerator is not None`` check is an explicit reference to the
    module-level ``Accelerator`` symbol so that static analysis tools (CodeQL)
    can confirm the symbol is used in executable code, not only in ``__all__``.
    Logically, when ``_ACCELERATOR_AVAILABLE`` is ``True``, ``Accelerator`` is
    guaranteed non-``None`` from the module-load try/except block above.
    """
    # _ACCELERATOR_AVAILABLE is set at module load from the Accelerator import attempt.
    # Accelerator is None when accelerate is not installed; non-None when it is.
    global _ACCELERATOR_AVAILABLE, Accelerator, _ACCELERATE_SPEC_AVAILABLE
    if _ACCELERATOR_AVAILABLE and Accelerator is not None:
        return True
    if _ACCELERATE_SPEC_AVAILABLE is None:
        try:
            _ACCELERATE_SPEC_AVAILABLE = importlib.util.find_spec("accelerate") is not None
        except (ValueError, ImportError):
            _ACCELERATE_SPEC_AVAILABLE = False
    if not _ACCELERATE_SPEC_AVAILABLE:
        return False
    try:
        import accelerate as _accelerate_mod
    except ImportError:
        # find_spec succeeded but the actual import failed; cache the failure so
        # subsequent calls do not keep retrying an unavailable/broken import.
        _ACCELERATE_SPEC_AVAILABLE = False
        return _ACCELERATE_SPEC_AVAILABLE
    accelerator_cls = getattr(_accelerate_mod, "Accelerator", None)
    if accelerator_cls is None:
        _ACCELERATOR_AVAILABLE = False
        return _ACCELERATOR_AVAILABLE
    Accelerator = accelerator_cls
    _ACCELERATOR_AVAILABLE = True
    return _ACCELERATOR_AVAILABLE


def is_gpu_available() -> bool:
    """Check if GPU/CUDA is available via torch."""
    try:
        import torch

        return bool(torch.cuda.is_available())
    except (ImportError, AttributeError) as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        return False


def safe_accelerate_init(
    cpu_fallback: bool = True,
    raise_on_error: bool = False,
) -> AccelerateInitResult:
    """
    Safe initialization of accelerate with CPU fallback and structured diagnostics.

    This function attempts to initialize accelerate for distributed training,
    but gracefully handles CPU-only environments and missing dependencies.

    Args:
        cpu_fallback: If True, gracefully skip on CPU-only systems
        raise_on_error: If True, raise exceptions instead of returning error result

    Returns:
        AccelerateInitResult with structured diagnostics

    Example:
        >>> result = safe_accelerate_init()
        >>> if result.success:
        ...     print(f"Accelerate initialized with {result.backend}")
        ... elif result.skip_reason:
        ...     print(f"Skipped: {result.skip_reason}")
        ... else:
        ...     print(f"Error: {result.error}")
    """
    cpu_only_env = os.environ.get("CUDA_VISIBLE_DEVICES") == ""
    # Reference functions through module namespace so mock patches take effect
    _mod = sys.modules[__name__]
    gpu_available = _mod.is_gpu_available()

    # Check accelerate availability
    if not _mod.is_accelerate_available():
        if cpu_fallback and cpu_only_env:
            result = AccelerateInitResult(
                success=False,
                accelerate_available=False,
                gpu_available=gpu_available,
                backend=None,
                world_size=1,
                rank=0,
                error=None,
                skip_reason="cpu_only",
            )
            logger.info("CPU-only environment detected, skipping distributed init")
            return result
        result = AccelerateInitResult(
            success=False,
            accelerate_available=False,
            gpu_available=gpu_available,
            backend=None,
            world_size=1,
            rank=0,
            error=None,
            skip_reason="no_accelerate",
        )
        logger.info("Accelerate package not available, skipping distributed init")
        return result

    if not gpu_available and cpu_fallback:
        result = AccelerateInitResult(
            success=False,
            accelerate_available=True,
            gpu_available=False,
            backend=None,
            world_size=1,
            rank=0,
            error=None,
            skip_reason="cpu_only",
        )
        logger.info("CPU-only environment detected, skipping distributed init")
        return result

    # Try to initialize accelerate
    try:
        # Use module-level Accelerator so tests can patch it
        _AcceleratorCls = sys.modules[__name__].Accelerator
        if _AcceleratorCls is None:
            raise ImportError("accelerate not available")

        world_size = int(os.getenv("WORLD_SIZE", "1"))
        rank = int(os.getenv("RANK", "0"))

        # Create accelerator (this will auto-detect distributed setup)
        accelerator = _AcceleratorCls()

        # Determine backend
        backend = None
        if hasattr(accelerator.state, "distributed_type"):
            backend = str(accelerator.state.distributed_type)

        result = AccelerateInitResult(
            success=True,
            accelerate_available=True,
            gpu_available=gpu_available,
            backend=backend or "single_device",
            world_size=world_size,
            rank=rank,
            error=None,
            skip_reason=None,
        )

        logger.info(f"Accelerate initialized successfully: {result}")
        return result

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        error_msg = f"{type(e).__name__}: {e}"

        if raise_on_error:
            raise

        result = AccelerateInitResult(
            success=False,
            accelerate_available=True,
            gpu_available=gpu_available,
            backend=None,
            world_size=1,
            rank=0,
            error=error_msg,
            skip_reason=None,
        )

        logger.error(f"Accelerate initialization failed: {error_msg}")
        return result


def get_distributed_env_info() -> dict[str, str]:
    """
    Get distributed training environment variables for debugging.

    Returns:
        Dictionary of environment variables relevant to distributed training
    """
    import os

    env_vars = [
        "MASTER_ADDR",
        "MASTER_PORT",
        "WORLD_SIZE",
        "RANK",
        "LOCAL_RANK",
        "NODE_RANK",
        "NCCL_DEBUG",
        "GLOO_SOCKET_IFNAME",
        "CUDA_VISIBLE_DEVICES",
        "ACCELERATE_TEST",
    ]

    return {var: os.getenv(var, "<not set>") for var in env_vars}


__all__ = [
    "AccelerateInitResult",
    "Accelerator",
    "is_accelerate_available",
    "is_gpu_available",
    "safe_accelerate_init",
]


if __name__ == "__main__":
    # CLI for testing and debugging
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    print("=" * 60)
    print("Accelerate Init Guard - Diagnostic Mode")
    print("=" * 60)

    # Show environment
    print("\nDistributed Environment Variables:")
    env_info = get_distributed_env_info()
    for key, value in env_info.items():
        print(f"  {key}: {value}")

    # Check availability
    print("\nAvailability Checks:")
    print(f"  Accelerate available: {is_accelerate_available()}")
    print(f"  GPU available: {is_gpu_available()}")

    # Try initialization
    print("\nInitialization Test:")
    result = safe_accelerate_init()
    print(f"  Result: {result}")

    # Exit with appropriate code
    sys.exit(0 if result.success or result.skip_reason else 1)
