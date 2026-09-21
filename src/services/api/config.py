"""
API configuration with security limits.

This module defines security-focused configuration for the API service,
including upload limits, rate limiting, and request size restrictions.
"""


class APIConfig:
    """
    Security-focused API configuration.

    This class defines security limits and configurations for the API
    service to prevent DoS attacks and resource exhaustion.

    Attributes:
        MAX_UPLOAD_SIZE: Maximum size for file uploads (50MB)
        MAX_FIELD_SIZE: Maximum size per form field (1MB)
        MAX_FIELDS: Maximum number of form fields (1000)
        MAX_REQUEST_SIZE: Maximum total request size (100MB)
        REQUEST_TIMEOUT: Request timeout in seconds (30s)
        RATE_LIMIT_PER_MINUTE: Maximum requests per minute per client (60)
        RATE_LIMIT_BURST: Burst allowance for rate limiting (10)

    Example:
        >>> from fastapi import FastAPI, Request
        >>> from fastapi.responses import JSONResponse
        >>> from services.api.config import APIConfig
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.middleware("http")
        >>> async def enforce_size_limits(request: Request, call_next):
        ...     content_length = request.headers.get("content-length")
        ...     if content_length and int(content_length) > APIConfig.MAX_REQUEST_SIZE:
        ...         return JSONResponse(
        ...             {"error": "Request too large"},
        ...             status_code=413
        ...         )
        ...     return await call_next(request)
    """

    # Form upload limits
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_FIELD_SIZE = 1 * 1024 * 1024  # 1MB per field
    MAX_FIELDS = 1000

    # Request limits
    MAX_REQUEST_SIZE = 100 * 1024 * 1024  # 100MB
    REQUEST_TIMEOUT = 30  # seconds

    # Rate limiting (for future implementation)
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_BURST = 10
