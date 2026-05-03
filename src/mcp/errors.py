"""Error hierarchy for MCP components and tests."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class MCPError(Exception):
    """Base class for MCP-specific errors with codes and HTTP status."""

    code = "MCP_ERROR"
    http_status = 500
    jsonrpc_code = -32000  # JSON-RPC error code

    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload


class ToolNotFound(MCPError):
    code = "TOOL_NOT_FOUND"
    http_status = 404
    jsonrpc_code = -32601  # Method not found


class ValidationError(MCPError):
    code = "VALIDATION_ERROR"
    http_status = 400
    jsonrpc_code = -32602  # Invalid params


class RateLimitExceeded(MCPError):
    code = "RATE_LIMIT_EXCEEDED"
    http_status = 429
    jsonrpc_code = -32002  # Custom: rate limit


class Unauthorized(MCPError):
    code = "UNAUTHORIZED"
    http_status = 401
    jsonrpc_code = -32001  # Custom: unauthorized


_KNOWN_CODES: Iterable[str] = {
    MCPError.code,
    ToolNotFound.code,
    ValidationError.code,
    RateLimitExceeded.code,
    Unauthorized.code,
}


def validate_error_response(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code or not message:
        return False
    return code in _KNOWN_CODES


__all__ = [
    "MCPError",
    "RateLimitExceeded",
    "ToolNotFound",
    "Unauthorized",
    "ValidationError",
    "validate_error_response",
]
