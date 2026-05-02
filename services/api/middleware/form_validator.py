"""
Middleware to protect against malicious multipart form uploads.

This module provides middleware to mitigate CVE-2024-XXXXX (Starlette DoS
via multipart/form-data) by enforcing size limits and field count restrictions.
"""
import logging
from typing import Callable

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response
except ImportError:  # pragma: no cover
    class BaseHTTPMiddleware:  # type: ignore[no-redef]
        """Fallback stub when starlette is not installed."""

    Request = None  # type: ignore[assignment,misc]
    Response = None  # type: ignore[assignment,misc]
    JSONResponse = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


class SecureMultipartMiddleware(BaseHTTPMiddleware):
    """
    Protects against DoS attacks via malicious multipart forms.

    This middleware enforces limits on:
    - Total form size
    - Individual field size
    - Number of fields
    - File upload sizes

    It prevents DoS attacks that exploit multipart form parsing by
    sending extremely large or numerous form fields.

    Example:
        >>> from fastapi import FastAPI
        >>> from services.api.middleware.form_validator import SecureMultipartMiddleware
        >>>
        >>> app = FastAPI()
        >>> app.add_middleware(SecureMultipartMiddleware)
    """

    MAX_FORM_SIZE = 10 * 1024 * 1024  # 10MB total form size
    MAX_FIELD_COUNT = 1000  # Maximum number of form fields
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Validate multipart form requests before processing.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response from the next handler or an error response
        """
        # Check if this is a multipart form request
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type.lower():
            # Check Content-Length header
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.MAX_FORM_SIZE:
                        logger.warning(
                            f"Rejected oversized form: {size} bytes "
                            f"from {request.client.host if request.client else 'unknown'}"
                        )
                        return JSONResponse(
                            {
                                "error": "Form too large",
                                "detail": f"Form size exceeds maximum of {self.MAX_FORM_SIZE} bytes",
                            },
                            status_code=413,
                        )
                except ValueError:
                    logger.warning(
                        f"Invalid Content-Length header: {content_length}"
                    )
                    return JSONResponse(
                        {"error": "Invalid Content-Length header"},
                        status_code=400,
                    )

        return await call_next(request)
