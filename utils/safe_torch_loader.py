"""
Safe torch loading wrapper to prevent RCE vulnerabilities.
Use this instead of torch.load() directly.

This module provides secure wrappers around PyTorch's model loading
functionality to mitigate CVE-2024-XXXXX (Remote Code Execution via torch.load).
"""
import logging
import os
from typing import Any, Optional

import torch

logger = logging.getLogger(__name__)


def safe_load(
    file_path: str,
    map_location: Optional[str] = None,
    weights_only: bool = True,
) -> Any:
    """
    Safely load PyTorch models with proper security controls.

    This function wraps torch.load() with security best practices to prevent
    Remote Code Execution vulnerabilities. It enforces the use of weights_only=True
    by default, which restricts loading to tensors and prevents arbitrary Python
    object deserialization.

    Args:
        file_path: Path to the model file to load
        map_location: Device to map loaded tensors (e.g., 'cpu', 'cuda:0')
        weights_only: MUST be True for security. Only loads weights/tensors,
                     not arbitrary Python objects. Default: True

    Returns:
        Loaded model state dictionary or weights

    Raises:
        ValueError: If weights_only is False (security violation)
        FileNotFoundError: If the specified file doesn't exist
        RuntimeError: If torch.load fails for any reason

    Example:
        >>> from utils.safe_torch_loader import safe_load
        >>> # Load model weights securely
        >>> model_state = safe_load('model.pth', map_location='cpu')
        >>> model.load_state_dict(model_state)

    Security Note:
        NEVER use weights_only=False unless you fully trust the source of the
        model file. Malicious model files can execute arbitrary code during
        loading if weights_only=False.
    """
    if not weights_only:
        raise ValueError(
            "weights_only=False is a security vulnerability. "
            "Only load trusted checkpoints with weights_only=True. "
            "See CVE-2024-XXXXX for details."
        )

    # Verify file exists and is readable
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {file_path}")

    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")

    # Use torch.load with weights_only=True for security
    try:
        logger.info(f"Safely loading model from {file_path} (weights_only=True)")
        loaded = torch.load(
            file_path,
            map_location=map_location,
            weights_only=True,  # Critical security parameter
        )
        logger.info(f"Successfully loaded model from {file_path}")
        return loaded
    except Exception as e:
        logger.error(f"Failed to load model safely from {file_path}: {e}")
        raise RuntimeError(f"Failed to load model: {e}") from e


# Legacy compatibility alias
load = safe_load
