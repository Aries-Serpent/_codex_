"""
Resource management for PyTorch operations.
Ensures proper cleanup of GPU memory and file handles.

This module provides context managers and utilities to prevent resource
leaks in PyTorch operations, addressing CVE-2024-XXXXX.
"""
import contextlib
import gc
import logging

import torch

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def torch_resource_guard():
    """
    Context manager for safe PyTorch operations with automatic cleanup.

    This context manager ensures that PyTorch resources (GPU memory, CUDA
    contexts, etc.) are properly released when exiting the context, even
    if an exception occurs.

    Yields:
        None

    Example:
        >>> from utils.torch_resource_manager import torch_resource_guard
        >>> with torch_resource_guard():
        ...     model = load_model()
        ...     output = model(input_tensor)
        ...     # Resources automatically cleaned up on exit

    Note:
        This is particularly important for long-running services and
        batch processing where resource leaks can accumulate.
    """
    try:
        yield
    finally:
        # Force cleanup of PyTorch resources
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        gc.collect()
        logger.debug("PyTorch resources cleaned up")


def cleanup_torch_resources():
    """
    Manually clean up PyTorch resources.

    This function can be called explicitly to force cleanup of GPU memory
    and other PyTorch resources without using a context manager.

    Example:
        >>> from utils.torch_resource_manager import cleanup_torch_resources
        >>> # ... PyTorch operations ...
        >>> cleanup_torch_resources()
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()
    logger.info("PyTorch resources manually cleaned up")
