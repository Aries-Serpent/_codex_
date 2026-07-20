"""Model serving and inference API for Codex ML.

This module provides production-grade model serving capabilities including:

- Lightweight inference server with FastAPI
- Model loading and caching
- Authentication and rate limiting
- Batch processing and optimization
- RAG (Retrieval-Augmented Generation) support
- Health checks and monitoring

Installation:
    Install the runtime profile to enable serving:
    pip install codex-ml[runtime]

Quick Start:
    from codex_ml.serving import ModelServer, ServerConfig
    
    config = ServerConfig(
        host="0.0.0.0",
        port=8000,
        workers=4
    )
    server = ModelServer(config=config)
    server.load_model("path/to/model")
    server.start()

Features:
    - **Model Loading**: Support for PyTorch, Transformers, ONNX models
    - **Caching**: Automatic model caching and reuse
    - **Authentication**: API key and JWT token support
    - **Rate Limiting**: Request throttling to prevent overload
    - **Batch Processing**: Efficient batch inference with configurable batch sizes
    - **Monitoring**: Prometheus metrics and health checks
    - **Security**: Input validation, CORS, trusted host middleware

Classes:
    ModelServer: Main inference server
    ServerConfig: Server configuration
    ModelConfig: Model configuration
    AuthManager: Authentication management
    RateLimiter: Request rate limiting

Functions:
    create_app: Create FastAPI application

Exceptions:
    ModelLoadError: Raised when model loading fails

See Also:
    - docs/optional_features_guide.md for RAG API details
    - docs/INTEGRATION_GUIDE_COMPREHENSIVE.md for integration examples
    - docs/PERFORMANCE_TUNING.md for optimization tips

Author: Codex Team
Version: 0.3.0
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
