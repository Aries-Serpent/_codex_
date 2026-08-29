"""
Determinism utilities for reproducible training.

Provides functions to enable deterministic behavior in PyTorch,
including CuDNN settings and random seed management.
"""

import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = hasattr(torch, "manual_seed")
except (ImportError, AttributeError):
    torch = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False


def set_seed(seed: int = 42) -> None:
    """Set random seeds for Python, NumPy, and PyTorch.

    Args:
        seed: Random seed value
    """
    random.seed(seed)

    if NUMPY_AVAILABLE:
        np.random.seed(seed)

    if TORCH_AVAILABLE:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def set_deterministic_mode(
    enabled: bool = True, warn: bool = True, seed: Optional[int] = None
) -> bool:
    """Enable or disable deterministic mode for reproducibility.

    Warning: Enabling deterministic mode may reduce performance SIGNIFICANTLY
    due to algorithmic constraints in cuDNN and other backends.

    Args:
        enabled: Whether to enable deterministic mode
        warn: Whether to log performance warning when enabling
        seed: Optional random seed to set when enabling (default: 42)

    Returns:
        True if operation succeeded, False otherwise

    Example:
        # Enable for reproducibility with default seed
        set_deterministic_mode(True)

        # Enable with custom seed
        set_deterministic_mode(True, seed=123)

        # Disable for performance
        set_deterministic_mode(False)
    """
    if not TORCH_AVAILABLE:
        if warn:
            logger.warning("PyTorch not available - deterministic mode not set")
        return False

    try:
        if enabled:
            # Set random seeds first
            if seed is None:
                seed = 42
            set_seed(seed)

            # Enable CuDNN determinism
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

            # PyTorch 1.8+ deterministic algorithms
            if hasattr(torch, "use_deterministic_algorithms"):
                try:
                    # PyTorch 1.11+ supports warn_only parameter
                    torch.use_deterministic_algorithms(True, warn_only=False)
                except TypeError as e:
                    type(e).__name__
                    logger.debug("TypeError: <ERROR_TYPE>")
                    logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
                    # Older PyTorch version without warn_only
                    torch.use_deterministic_algorithms(True)

            if warn:
                logger.warning(
                    "Deterministic mode enabled. This may significantly reduce performance "
                    "due to algorithmic constraints."
                )
        else:
            # Disable determinism for performance
            torch.backends.cudnn.deterministic = False
            torch.backends.cudnn.benchmark = True

            if hasattr(torch, "use_deterministic_algorithms"):
                torch.use_deterministic_algorithms(False)

            if warn:
                logger.info("Deterministic mode disabled - performance optimizations enabled")

        return True

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.error("Failed to set deterministic mode: <ERROR_TYPE>")
        return False


def get_deterministic_status() -> dict[str, Optional[bool]]:
    """
    Get current deterministic mode status.

    Returns:
        Dictionary with status of deterministic settings
    """
    if not TORCH_AVAILABLE:
        return {
            "torch_available": False,
            "cudnn_deterministic": False,
            "cudnn_benchmark": False,
            "use_deterministic_algorithms": False,
        }

    status = {
        "torch_available": True,
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
    }

    # Check if use_deterministic_algorithms is available
    if hasattr(torch, "are_deterministic_algorithms_enabled"):
        status["use_deterministic_algorithms"] = torch.are_deterministic_algorithms_enabled()
    else:
        status["use_deterministic_algorithms"] = None

    return status


__all__ = [
    "get_deterministic_status",
    "set_deterministic_mode",
    "set_seed",
]
