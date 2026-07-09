"""Deterministic algorithms enforcement for reproducible training.

This module provides utilities for ensuring bit-exact reproducibility by
enforcing deterministic algorithms and detecting non-deterministic operations.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

__all__ = [
    "DeterministicContext",
    "disable_deterministic_mode",
    "enable_deterministic_mode",
    "is_deterministic_mode_enabled",
]


def enable_deterministic_mode(warn_only: bool = False) -> None:
    """Enable deterministic mode for reproducible training.

    This sets various environment variables and library flags to ensure
    deterministic behavior. Note that this may impact performance.

    Args:
        warn_only: If True, only warns about non-deterministic ops instead of erroring
    """
    logger.info("Enabling deterministic mode for reproducible training")

    # PyTorch deterministic algorithms
    try:
        import torch

        # Enable deterministic algorithms
        torch.use_deterministic_algorithms(mode=True, warn_only=warn_only)

        # Set CuDNN flags for determinism (if CUDA available)
        if torch.cuda.is_available():
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            logger.info("Set CuDNN to deterministic mode")

        logger.info("PyTorch deterministic algorithms enabled")
    except (ImportError, AttributeError) as e:
        if isinstance(e, ImportError):
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            logger.warning("PyTorch not available, skipping torch deterministic setup")
        else:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to enable PyTorch deterministic mode: {e}")

    # TensorFlow deterministic ops (if available)
    try:
        import tensorflow as tf

        # Enable deterministic ops in TF 2.x
        if hasattr(tf.config.experimental, "enable_op_determinism"):
            tf.config.experimental.enable_op_determinism()
            logger.info("TensorFlow deterministic ops enabled")
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)  # TensorFlow not installed
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Failed to enable TensorFlow deterministic mode: <ERROR_TYPE>")

    # Set environment variables for determinism
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"  # For CUDA determinism

    logger.info("✓ Deterministic mode enabled")


def disable_deterministic_mode() -> None:
    """Disable deterministic mode (restore default behavior).

    This can be used to restore performance after deterministic mode
    was enabled temporarily.
    """
    logger.info("Disabling deterministic mode")

    try:
        import torch

        torch.use_deterministic_algorithms(mode=False)

        if torch.cuda.is_available():
            torch.backends.cudnn.deterministic = False
            torch.backends.cudnn.benchmark = True

        logger.info("PyTorch deterministic algorithms disabled")
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Failed to disable PyTorch deterministic mode: <ERROR_TYPE>")

    # Remove determinism environment variables
    os.environ.pop("PYTHONHASHSEED", None)
    os.environ.pop("CUBLAS_WORKSPACE_CONFIG", None)

    logger.info("✓ Deterministic mode disabled")


def is_deterministic_mode_enabled() -> bool:
    """Check if deterministic mode is currently enabled.

    Returns:
        True if deterministic mode is enabled
    """
    try:
        import torch

        return torch.are_deterministic_algorithms_enabled()
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        return False
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return False


class DeterministicContext:
    """Context manager for temporarily enabling deterministic mode.

    Example:
        with DeterministicContext():
            # Training code here will run deterministically
            train_model()
    """

    def __init__(self, warn_only: bool = False):
        """Initialize deterministic context.

        Args:
            warn_only: If True, only warns about non-deterministic ops
        """
        self.warn_only = warn_only
        self._was_enabled = False

    def __enter__(self):
        """Enter deterministic context."""
        self._was_enabled = is_deterministic_mode_enabled()
        if not self._was_enabled:
            enable_deterministic_mode(warn_only=self.warn_only)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit deterministic context."""
        if not self._was_enabled:
            disable_deterministic_mode()


def check_deterministic_operations() -> dict[str, bool | None]:
    """Check which deterministic features are enabled.

    Returns:
        Dict mapping feature names to enabled status
    """
    status = {
        "python_hash_seed": os.environ.get("PYTHONHASHSEED") == "0",
        "cublas_workspace": "CUBLAS_WORKSPACE_CONFIG" in os.environ,
    }

    try:
        import torch

        status["torch_deterministic"] = torch.are_deterministic_algorithms_enabled()
        status["torch_available"] = True

        if torch.cuda.is_available():
            status["cudnn_deterministic"] = torch.backends.cudnn.deterministic
            status["cudnn_benchmark_disabled"] = not torch.backends.cudnn.benchmark
        else:
            status["cudnn_deterministic"] = None  # type: ignore[assignment]
            status["cudnn_benchmark_disabled"] = None  # type: ignore[assignment]
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        status["torch_available"] = False
        status["torch_deterministic"] = False

    return status  # type: ignore[return-value]


def warn_non_deterministic_ops():
    """Warn about common non-deterministic operations.

    This function logs warnings about operations that may break determinism.
    """
    warnings_list = []

    status = check_deterministic_operations()

    if not status["python_hash_seed"]:
        warnings_list.append("PYTHONHASHSEED not set to 0 (dict/set order may vary)")

    if status["torch_available"]:
        if not status["torch_deterministic"]:
            warnings_list.append("PyTorch deterministic algorithms not enabled")

        if status["cudnn_deterministic"] is not None:
            if not status["cudnn_deterministic"]:
                warnings_list.append("CuDNN deterministic mode not enabled")
            if not status["cudnn_benchmark_disabled"]:
                warnings_list.append("CuDNN benchmark mode enabled (non-deterministic)")

    if warnings_list:
        msg = "Non-deterministic operations detected:\n" + "\n".join(
            f"  - {w}" for w in warnings_list
        )
        logger.warning(msg)
        return warnings_list

    logger.info("✓ All deterministic checks passed")
    return []
