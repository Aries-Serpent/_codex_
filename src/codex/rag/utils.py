"""
RAG Utility Functions
Shared utilities for RAG modules including model loading helpers.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def safe_model_load(model: Any, device: str = "cpu") -> Any:
    """
    Safely move model from meta device to target device.
    
    This helper addresses the Torch meta tensor error that occurs when
    loading models in test environments. Models on the 'meta' device
    need to be properly moved to a real device before use.
    
    Args:
        model: The model to load
        device: Target device (default: 'cpu')
    
    Returns:
        Model moved to the target device
        
    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer('all-MiniLM-L6-v2')
        >>> model = safe_model_load(model, device='cpu')
    """
    try:
        # Check if model has a device attribute and is on meta device
        if hasattr(model, "device") and str(model.device) == "meta":
            # Use to_empty to move from meta device
            if hasattr(model, "to_empty"):
                return model.to_empty(device=device)
            # Fallback to regular .to() method
            return model.to(device)
        # If not on meta device, just move to target device
        if hasattr(model, "to"):
            return model.to(device)
        return model
    except Exception as e:
        logger.warning(f"Could not safely load model to device {device}: {e}")
        return model
