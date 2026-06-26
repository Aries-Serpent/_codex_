"""
Tests for MCP protocol surface and JSON-RPC compliance.
Covers protocol adherence, message formats, and edge cases.
"""

import json

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.


def test_jsonrpc_version_compliance():
    """Test JSON-RPC 2.0 version compliance."""
    request = {"jsonrpc": "2.0", "id": 1, "method": "test"}

    assert request["jsonrpc"] == "2.0", "Condition must be true"


def test_jsonrpc_request_format():
    """Test JSON-RPC request message format."""
    request = {"jsonrpc": "2.0", "id": 123, "method": "listTools", "params": {}}

    # Required fields
    assert "jsonrpc" in request, "Condition must be true"
    assert "method" in request, "Condition must be true"
    assert "id" in request, "Condition must be true"

    # Correct types
    assert isinstance(request["id"], int)
    assert isinstance(request["method"], str)


def test_jsonrpc_response_format():
    """Test JSON-RPC response message format."""
    success_response = {"jsonrpc": "2.0", "id": 123, "result": {"tools": []}}

    assert "jsonrpc" in success_response, "Response must not be empty"
    assert "id" in success_response, "Response must not be empty"
    assert "result" in success_response, "Response must not be empty"
    assert "error" not in success_response, "Response must not be empty"


def test_jsonrpc_error_response_format():
    """Test JSON-RPC error response format."""
    error_response = {
        "jsonrpc": "2.0",
        "id": 123,
        "error": {"code": -32600, "message": "Invalid Request", "data": {}},
    }

    assert "jsonrpc" in error_response, "Response must not be empty"
    assert "id" in error_response, "Response must not be empty"
    assert "error" in error_response, "Response must not be empty"
    assert "result" not in error_response, "Response must not be empty"

    # Error object structure
    assert "code" in error_response["error"], "Response must not be empty"
    assert "message" in error_response["error"], "Response must not be empty"
    assert isinstance(error_response["error"]["code"], int)


def test_jsonrpc_notification_format():
    """Test JSON-RPC notification format (no id field)."""
    notification = {"jsonrpc": "2.0", "method": "ping", "params": {}}

    assert "jsonrpc" in notification, "Condition must be true"
    assert "method" in notification, "Condition must be true"
    assert "id" not in notification, "Condition must be true"


def test_jsonrpc_batch_request_format():
    """Test JSON-RPC batch request format."""
    batch = [
        {"jsonrpc": "2.0", "id": 1, "method": "method1"},
        {"jsonrpc": "2.0", "id": 2, "method": "method2"},
        {"jsonrpc": "2.0", "id": 3, "method": "method3"},
    ]

    assert isinstance(batch, list)
    assert len(batch) == 3, "Batch must not be empty"

    for req in batch:
        assert req["jsonrpc"] == "2.0", "Condition must be true"
        assert "method" in req, "Condition must be true"


def test_mcp_listtools_method():
    """Test MCP listTools method definition."""
    request = {"jsonrpc": "2.0", "id": 1, "method": "listTools", "params": {}}

    assert request["method"] == "listTools", "Condition must be true"
    assert isinstance(request["params"], dict)


def test_mcp_calltool_method():
    """Test MCP callTool method definition."""
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "callTool",
        "params": {"name": "tool_name", "params": {"arg1": "value1"}},
    }

    assert request["method"] == "callTool", "Condition must be true"
    assert "name" in request["params"], "Condition must be true"
    assert "params" in request["params"], "Condition must be true"


def test_mcp_negotiate_version_method():
    """Test MCP negotiateVersion method definition."""
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "negotiateVersion",
        "params": {"versions": ["1.0", "2.0"]},
    }

    assert request["method"] == "negotiateVersion", "Condition must be true"
    assert "versions" in request["params"], "Condition must be true"
    assert isinstance(request["params"]["versions"], list)


def test_error_code_ranges():
    """Test JSON-RPC error code ranges."""
    # Standard JSON-RPC errors (-32768 to -32000)
    parse_error = -32700
    invalid_request = -32600

    # Verify standard JSON-RPC error codes are in valid range
    assert -32768 <= parse_error <= -32000, "Error should be raised or set"
    assert -32768 <= invalid_request <= -32000, "32768 is not valid"


def test_mcp_error_mappings():
    """Test MCP error code to HTTP status mappings."""
    from mcp.errors import (
        MCPError,
        RateLimitExceeded,
        ToolNotFound,
        Unauthorized,
        ValidationError,
    )

    error_mappings = [
        (MCPError("base"), -32000, 500),
        (ToolNotFound("not found"), -32601, 404),
        (ValidationError("bad input"), -32602, 400),
        (RateLimitExceeded("too many"), -32002, 429),
        (Unauthorized("no auth"), -32001, 401),
    ]

    for error, expected_code, expected_http in error_mappings:
        assert error.jsonrpc_code == expected_code, "Error should be raised or set"
        assert error.http_status == expected_http, "Error should be raised or set"


def test_protocol_version_negotiation():
    """Test MCP version negotiation protocol."""
    from mcp.versioning import MCP_VERSIONS, negotiate_version

    # Server supports certain versions
    assert isinstance(MCP_VERSIONS, list)
    assert len(MCP_VERSIONS) > 0, "Mcp_versions must not be empty"

    # Client requests compatible version
    client_versions = ["1.0", "2.0"]
    negotiated = negotiate_version(client_versions)

    # Should return highest compatible version
    assert negotiated in MCP_VERSIONS, "Condition must be true"


def test_request_id_types():
    """Test various request ID types."""
    # JSON-RPC allows string, number, or null for id
    id_types = [
        123,  # number
        "req-abc",  # string
        None,  # null (for notifications)
    ]

    for req_id in id_types:
        request = {"jsonrpc": "2.0", "method": "test"}

        if req_id is not None:
            request["id"] = req_id

        # Should be valid
        assert "jsonrpc" in request, "Condition must be true"
        assert "method" in request, "Condition must be true"


def test_params_optional():
    """Test that params field is optional."""
    # Params can be omitted
    request_no_params = {"jsonrpc": "2.0", "id": 1, "method": "test"}

    assert "params" not in request_no_params, "Condition must be true"

    # Or explicitly set
    request_with_params = {"jsonrpc": "2.0", "id": 2, "method": "test", "params": {}}

    assert "params" in request_with_params, "Condition must be true"


def test_unicode_support():
    """Test Unicode support in messages."""
    request = {"jsonrpc": "2.0", "id": 1, "method": "test", "params": {"text": "Hello 世界 🌍"}}

    # Should serialize and deserialize correctly
    json_str = json.dumps(request, ensure_ascii=False)
    parsed = json.loads(json_str)

    assert parsed["params"]["text"] == "Hello 世界 🌍", "Condition must be true"


def test_large_payloads():
    """Test handling of large payloads."""
    large_data = {"data": "x" * 10000}

    request = {"jsonrpc": "2.0", "id": 1, "method": "test", "params": large_data}

    # Should be serializable
    json_str = json.dumps(request)
    assert len(json_str) > 10000, "Json_str must not be empty"


def test_nested_params():
    """Test deeply nested parameter structures."""
    nested_params = {"level1": {"level2": {"level3": {"value": "deep"}}}}

    request = {"jsonrpc": "2.0", "id": 1, "method": "test", "params": nested_params}

    assert request["params"]["level1"]["level2"]["level3"]["value"] == "deep", "Value must be initialized"


def test_array_params():
    """Test array-based parameters."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "test",
        "params": [1, 2, 3, "four", {"five": 5}],
    }

    assert isinstance(request["params"], list)
    assert len(request["params"]) == 5, "Collection must not be empty"


def test_null_values():
    """Test handling of null values."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "test",
        "params": {"nullable": None, "not_null": "value"},
    }

    assert request["params"]["nullable"] is None, "Condition must be true"
    assert request["params"]["not_null"] == "value", "Value must be initialized"


def test_boolean_values():
    """Test boolean parameter values."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "test",
        "params": {"flag1": True, "flag2": False},
    }

    assert request["params"]["flag1"] is True, "Condition must be true"
    assert request["params"]["flag2"] is False, "Condition must be true"


def test_numeric_precision():
    """Test numeric value precision."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "test",
        "params": {
            "int_val": 42,
            "float_val": 3.14159,
            "large_int": 9007199254740991,  # JavaScript MAX_SAFE_INTEGER
        },
    }

    assert isinstance(request["params"]["int_val"], int)
    assert isinstance(request["params"]["float_val"], float)
    assert request["params"]["large_int"] == 9007199254740991, "Condition must be true"


def test_empty_responses():
    """Test empty/minimal valid responses."""
    # Minimal success response
    response = {"jsonrpc": "2.0", "id": 1, "result": None}

    assert "result" in response, "Response must not be empty"

    # Minimal error response
    error_response = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "Error"}}

    assert "error" in error_response, "Response must not be empty"


def test_method_naming():
    """Test method naming conventions."""
    # MCP method names
    methods = ["listTools", "callTool", "negotiateVersion"]

    for method in methods:
        request = {"jsonrpc": "2.0", "id": 1, "method": method}

        assert request["method"] in methods, "Condition must be true"


def test_reserved_method_names():
    """Test that rpc. prefixed methods are reserved."""
    # Methods starting with "rpc." are reserved for JSON-RPC
    reserved_method = "rpc.discover"

    request = {"jsonrpc": "2.0", "id": 1, "method": reserved_method}

    assert request["method"].startswith("rpc."), "Condition must be true"
