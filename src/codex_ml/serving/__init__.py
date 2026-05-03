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
    create_app,
)

try:
    from .model_loader import ModelLoader
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    ModelLoader = None  # type: ignore[assignment, misc]

__all__ = [
    "AuthManager",
    "ModelConfig",
    "ModelLoadError",
    "ModelLoader",
    "ModelServer",
    "RateLimiter",
    "create_app",
]
