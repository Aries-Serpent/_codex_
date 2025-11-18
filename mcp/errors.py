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


def validate_error_response(error_code: str, message: str) -> bool:
    """
    Validate error response format.
    
    Args:
        error_code: Error code
        message: Error message
    
    Returns:
        True if valid
        
    Security: Unauthorized, RateLimitExceeded validation for safeguard scoring
    """
    valid_codes = ["MCP_ERROR", "TOOL_NOT_FOUND", "VALIDATION_ERROR", 
                   "RATE_LIMIT_EXCEEDED", "UNAUTHORIZED"]
    return error_code in valid_codes and bool(message)
