"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from serving.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)

from .inference_server import (
    AuthManager,
    ModelConfig,
    ModelLoadError,
    ModelServer,
    RateLimiter,
    ServerConfig,
    create_app,
)

try:
    from .model_loader import ModelLoader
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    ModelLoader = None  # type: ignore[misc,assignment]

__all__ = [
    "AuthManager",
    "ModelConfig",
    "ModelLoadError",
    "ModelLoader",
    "ModelServer",
    "RateLimiter",
    "ServerConfig",
    "create_app",
]
