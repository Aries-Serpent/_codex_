"""
Determinism utilities for reproducible training.

Provides functions to enable deterministic behavior in PyTorch,
including CuDNN settings.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = hasattr(torch, 'manual_seed')
except (ImportError, AttributeError):
    torch = None
    TORCH_AVAILABLE = False


def set_deterministic_mode(enabled: bool = True, warn: bool = True) -> bool:
    """
    Enable deterministic operations for reproducibility.
    
    Warning: May reduce performance significantly.
    
    Args:
        enabled: Whether to enable deterministic mode
        warn: Whether to warn about performance impact
        
    Returns:
        True if successfully set, False if PyTorch not available
    
    Example:
        # Enable for reproducibility
        set_deterministic_mode(True)
        
        # Disable for performance
        set_deterministic_mode(False)
    """
    if not TORCH_AVAILABLE:
        if warn:
            logger.warning("PyTorch not available - deterministic mode not set")
        return False
    
    try:
        if enabled:
            # Enable CuDNN determinism
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            
            # PyTorch 1.8+ deterministic algorithms
            if hasattr(torch, "use_deterministic_algorithms"):
                torch.use_deterministic_algorithms(True)
            
            # PyTorch 1.11+ warn_only option
            if hasattr(torch, "use_deterministic_algorithms"):
                try:
                    torch.use_deterministic_algorithms(True, warn_only=False)
                except TypeError:
                    # Older PyTorch version without warn_only
                    pass
            
            if warn:
                logger.warning(
                    "Deterministic mode enabled - this may reduce performance. "
                    "CuDNN benchmark disabled, deterministic algorithms enforced."
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
    
    except Exception as e:
        logger.error(f"Failed to set deterministic mode: {e}")
        return False


def get_deterministic_status() -> dict[str, bool]:
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
    "set_deterministic_mode",
    "get_deterministic_status",
]
