from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Optional


class MCPError(Exception):
    """Base class for MCP-specific errors with checksum serialization."""

    code: int = -32000
    symbol: str = "MCP_ERROR"
    http_status: int = 500
    offline_hint: bool = False

    def __init__(self, message: str = "", *, context: Optional[Dict[str, Any]] = None):
        super().__init__(message or self.symbol)
        self.message = message or self.symbol
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "code": self.symbol,
            "rpc_code": self.code,
            "symbol": self.symbol,
            "message": self.message,
            "context": self.context,
        }
        payload["checksum"] = sha256(f"{self.code}:{self.message}".encode("utf-8")).hexdigest()
        payload["offline"] = self.context.get("offline", self.offline_hint)
        return payload


class ToolNotFound(MCPError):
    code = -32601
    symbol = "TOOL_NOT_FOUND"
    http_status = 404


class ValidationError(MCPError):
    code = -32602
    symbol = "VALIDATION_ERROR"
    http_status = 400


class RateLimitExceeded(MCPError):
    code = -32002
    symbol = "RATE_LIMIT_EXCEEDED"
    http_status = 429


class Unauthorized(MCPError):
    code = -32600
    symbol = "UNAUTHORIZED"
    http_status = 401


class OfflineOnly(MCPError):
    code = -32010
    symbol = "OFFLINE_ONLY"
    http_status = 403
    offline_hint = True


class ConfirmationRequired(MCPError):
    code = -32011
    symbol = "CONFIRMATION_REQUIRED"
    http_status = 412


class DryRunRequired(MCPError):
    code = -32012
    symbol = "DRY_RUN_REQUIRED"
    http_status = 428
