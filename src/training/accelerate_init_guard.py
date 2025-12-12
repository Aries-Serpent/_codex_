#!/usr/bin/env python3
"""
Safe accelerate initialization guard with CPU fallback.

Provides structured diagnostics and never raises on CPU-only environments.
Designed to be skip-safe on GitHub runners and CI environments.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AccelerateInitResult:
    """Result of safe_accelerate_init with structured diagnostics."""

    success: bool
    """True if accelerate is available and initialized successfully."""

    accelerate_available: bool
    """True if accelerate package is importable."""

    gpu_available: bool
    """True if GPU/CUDA is available."""

    backend: Optional[str]
    """Distributed backend used (gloo, nccl, mpi, etc.) or None."""

    world_size: int
    """Number of processes in distributed setup (1 if not distributed)."""

    rank: int
    """Current process rank (0 if not distributed)."""

    error: Optional[str]
    """Error message if initialization failed, None otherwise."""

    skip_reason: Optional[str]
    """Reason for skipping initialization (e.g., 'cpu_only', 'no_accelerate')."""

    def __str__(self) -> str:
        """Human-readable summary."""
        if self.success:
            return f"AccelerateInitResult(success=True, backend={self.backend}, world_size={self.world_size})"
        elif self.skip_reason:
            return f"AccelerateInitResult(skipped, reason={self.skip_reason})"
        else:
            return f"AccelerateInitResult(failed, error={self.error})"


def is_accelerate_available() -> bool:
    """Check if accelerate package is importable."""
    spec = importlib.util.find_spec("accelerate")
    return spec is not None


def is_gpu_available() -> bool:
    """Check if GPU/CUDA is available via torch."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
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
    # Check accelerate availability
    if not is_accelerate_available():
        result = AccelerateInitResult(
            success=False,
            accelerate_available=False,
            gpu_available=is_gpu_available(),
            backend=None,
            world_size=1,
            rank=0,
            error=None,
            skip_reason="no_accelerate",
        )
        logger.info("Accelerate package not available, skipping distributed init")
        return result

    # Check GPU availability
    gpu_available = is_gpu_available()
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
        # Check for distributed environment variables
        import os

        from accelerate import Accelerator

        world_size = int(os.getenv("WORLD_SIZE", "1"))
        rank = int(os.getenv("RANK", "0"))

        # Create accelerator (this will auto-detect distributed setup)
        accelerator = Accelerator()

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

    except Exception as e:
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
