"""Comprehensive error handling tests."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional


class ErrorCode(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        result = {"code": self.code, "message": self.message}
        if self.data:
            result["data"] = self.data
        return result


def test_parse_error():
    """Test parse error creation."""
    error = JsonRpcError(ErrorCode.PARSE_ERROR.value, "Invalid JSON")

    assert error.code == -32700, "Error should be raised or set"
    assert error.message == "Invalid JSON", "Error should be raised or set"


def test_invalid_request_error():
    """Test invalid request error."""
    error = JsonRpcError(ErrorCode.INVALID_REQUEST.value, "Missing method")

    assert error.code == -32600, "Error should be raised or set"


def test_method_not_found_error():
    """Test method not found error."""
    error = JsonRpcError(ErrorCode.METHOD_NOT_FOUND.value, "mcp.unknown")

    assert error.code == -32601, "Error should be raised or set"
    assert error.message == "mcp.unknown", "Error should be raised or set"


def test_invalid_params_error():
    """Test invalid params error."""
    error = JsonRpcError(
        ErrorCode.INVALID_PARAMS.value,
        "Invalid parameters",
        data={"param": "x", "expected": "string", "got": "number"},
    )

    assert error.code == -32602, "Error should be raised or set"
    assert error.data["param"] == "x", "Data must not be empty"


def test_error_to_dict():
    """Test error serialization."""
    error = JsonRpcError(-32603, "Internal error", data={"details": "test"})
    result = error.to_dict()

    assert result["code"] == -32603, "Result must not be empty"
    assert result["message"] == "Internal error", "Result must not be empty"
    assert result["data"]["details"] == "test", "Result must not be empty"


def test_server_error_range():
    """Test server error code ranges."""
    for code in range(-32099, -32000):
        error = JsonRpcError(code, f"Server error {code}")
        assert error.code == code, "Error should be raised or set"
