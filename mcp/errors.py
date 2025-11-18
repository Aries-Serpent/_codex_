class MCPError(Exception):
    """
    Base class for MCP-specific errors.
    Carries a protocol-independent error code and an associated HTTP status for HTTP contexts.
    """
    code: str = "MCP_ERROR"
    http_status: int = 500
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message or self.code
    def to_dict(self):
        return {"code": self.code, "message": self.message}


class ToolNotFound(MCPError):
    code = "TOOL_NOT_FOUND"
    http_status = 404


class ValidationError(MCPError):
    code = "VALIDATION_ERROR"
    http_status = 400


class RateLimitExceeded(MCPError):
    code = "RATE_LIMIT_EXCEEDED"
    http_status = 429


class Unauthorized(MCPError):
    code = "UNAUTHORIZED"
    http_status = 401
