"""
Extended tests for MCP error handling capability.

Covers error hierarchy, error responses, validation, rate limiting errors,
and unauthorized access patterns.
"""

import pytest
from mcp.errors import (
    MCPError, ToolNotFound, ValidationError,
    RateLimitExceeded, Unauthorized, validate_error_response
)


def test_mcp_error_base():
    """Test base MCPError class."""
    error = MCPError("test error")
    assert error.code == "MCP_ERROR"
    assert error.http_status == 500
    assert error.message == "test error"


def test_tool_not_found_error():
    """Test ToolNotFound error."""
    error = ToolNotFound("tool 'xyz' not found")
    assert error.code == "TOOL_NOT_FOUND"
    assert error.http_status == 404


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("invalid input")
    assert error.code == "VALIDATION_ERROR"
    assert error.http_status == 400


def test_rate_limit_exceeded_error():
    """Test RateLimitExceeded error."""
    error = RateLimitExceeded("too many requests")
    assert error.code == "RATE_LIMIT_EXCEEDED"
    assert error.http_status == 429


def test_unauthorized_error():
    """Test Unauthorized error."""
    error = Unauthorized("invalid credentials")
    assert error.code == "UNAUTHORIZED"
    assert error.http_status == 401


def test_error_to_dict():
    """Test error serialization to dict."""
    error = ToolNotFound("tool not found")
    data = error.to_dict()
    assert data["code"] == "TOOL_NOT_FOUND"
    assert data["message"] == "tool not found"


def test_error_inheritance():
    """Test error class inheritance."""
    error = ToolNotFound("test")
    assert isinstance(error, MCPError)
    assert isinstance(error, Exception)


def test_validate_error_response_valid():
    """Test error response validation with valid codes."""
    assert validate_error_response("TOOL_NOT_FOUND", "msg") is True
    assert validate_error_response("UNAUTHORIZED", "msg") is True
    assert validate_error_response("RATE_LIMIT_EXCEEDED", "msg") is True


def test_validate_error_response_invalid():
    """Test error response validation with invalid codes."""
    assert validate_error_response("INVALID_CODE", "msg") is False
    assert validate_error_response("TOOL_NOT_FOUND", "") is False


def test_error_context_handling():
    """Test error handling with context."""
    try:
        raise ToolNotFound("tool 'search' not found")
    except MCPError as e:
        assert "search" in e.message
        assert e.http_status == 404


def test_multiple_error_types():
    """Test handling multiple error types."""
    errors = [
        ToolNotFound("tool1"),
        ValidationError("validation"),
        RateLimitExceeded("rate"),
        Unauthorized("auth")
    ]
    
    for err in errors:
        assert isinstance(err, MCPError)
        assert err.code in ["TOOL_NOT_FOUND", "VALIDATION_ERROR", 
                            "RATE_LIMIT_EXCEEDED", "UNAUTHORIZED"]


def test_error_propagation():
    """Test error propagation through call stack."""
    def level3():
        raise Unauthorized("no access")
    
    def level2():
        level3()
    
    def level1():
        level2()
    
    with pytest.raises(Unauthorized):
        level1()


def test_error_with_details():
    """Test errors can carry additional details."""
    error = ValidationError("Invalid field: age")
    # In production, might add details dict
    assert "age" in error.message


def test_error_http_status_mapping():
    """Test all errors have appropriate HTTP status."""
    mapping = {
        ToolNotFound: 404,
        ValidationError: 400,
        RateLimitExceeded: 429,
        Unauthorized: 401,
        MCPError: 500
    }
    
    for error_class, expected_status in mapping.items():
        assert error_class.http_status == expected_status
