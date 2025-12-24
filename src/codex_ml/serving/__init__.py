import logging
logger = logging.getLogger(__name__)
"""Serving package for ML inference"""

from .inference_server import (
    AuthManager,
    ModelConfig,
    ModelLoadError,
    ModelServer,
    RateLimiter,
    create_app,
)

try:
    from .model_loader import ModelLoader
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    ModelLoader = None

__all__ = [
    "AuthManager",
    "ModelConfig",
    "ModelLoadError",
    "ModelServer",
    "ModelLoader",
    "RateLimiter",
    "create_app",
]
