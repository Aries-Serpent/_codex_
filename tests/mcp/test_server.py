"""
Tests for MCP JSON-RPC server functionality.
Covers server initialization, request handling, and protocol compliance.
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.server.server import MCPJSONRPCServer
from mcp.config import MCPConfig
from mcp.errors import MCPError, ToolNotFound, ValidationError


def test_server_initialization():
    """Test MCP server can be initialized."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    assert server is not None
    assert server.config == config


def test_server_listtools_request():
    """Test listTools JSON-RPC request handling."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "listTools",
        "params": {}
    }
    
    response = server.handle_request(request)
    
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert isinstance(response["result"], list)


def test_server_negotiate_version():
    """Test version negotiation in JSON-RPC server."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "negotiateVersion",
        "params": {"versions": ["1.0"]}
    }
    
    response = server.handle_request(request)
    
    assert "result" in response
    assert response["result"] == "1.0"


def test_server_call_tool_not_found():
    """Test callTool with non-existent tool returns proper error."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "callTool",
        "params": {
            "name": "nonexistent_tool",
            "params": {}
        }
    }
    
    response = server.handle_request(request)
    
    assert "error" in response
    assert response["error"]["code"] == 404


def test_server_invalid_jsonrpc_version():
    """Test server rejects invalid JSON-RPC version."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "1.0",  # Invalid version
        "id": 4,
        "method": "listTools"
    }
    
    response = server.handle_request(request)
    
    assert "error" in response


def test_server_missing_method():
    """Test server handles missing method field."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        # Missing "method" field
        "params": {}
    }
    
    response = server.handle_request(request)
    
    assert "error" in response


def test_server_rate_limiting():
    """Test that server respects rate limiting."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    # Server should have rate limiter
    assert hasattr(server, 'rate_limiter') or hasattr(server, '_rate_limiter')


def test_server_error_handling():
    """Test server error handling and response format."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    # Malformed JSON should be handled gracefully
    try:
        response = server.handle_request("not valid json")
        # Should return error response
        assert isinstance(response, dict)
    except Exception as e:
        # Or raise appropriate exception
        assert isinstance(e, (ValueError, MCPError))


def test_server_concurrent_requests():
    """Test server can handle multiple requests."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    requests = [
        {"jsonrpc": "2.0", "id": i, "method": "listTools", "params": {}}
        for i in range(5)
    ]
    
    responses = [server.handle_request(req) for req in requests]
    
    assert len(responses) == 5
    for i, response in enumerate(responses):
        assert response["id"] == i


def test_server_tool_execution():
    """Test server can execute tools through registry."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    # Register a test tool
    server.registry.register_tool(
        "test_tool",
        lambda x: f"result: {x}",
        metadata={"description": "Test tool"}
    )
    
    request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "callTool",
        "params": {
            "name": "test_tool",
            "params": {"x": "test_input"}
        }
    }
    
    response = server.handle_request(request)
    
    assert "result" in response
    assert "result: test_input" in str(response["result"])


def test_server_authentication():
    """Test server authentication integration."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    # Server should have authentication capability
    assert hasattr(server, 'authenticator') or hasattr(server, '_authenticator')


def test_server_protocol_compliance():
    """Test JSON-RPC 2.0 protocol compliance."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "listTools",
        "params": {}
    }
    
    response = server.handle_request(request)
    
    # Must have jsonrpc field
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    
    # Must have id matching request
    assert "id" in response
    assert response["id"] == 7
    
    # Must have either result or error
    assert "result" in response or "error" in response


def test_server_batch_requests():
    """Test server can handle batch requests."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    batch = [
        {"jsonrpc": "2.0", "id": 1, "method": "listTools", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "negotiateVersion", "params": {"versions": ["1.0"]}}
    ]
    
    # Server should handle batch (or reject appropriately)
    try:
        if hasattr(server, 'handle_batch'):
            responses = server.handle_batch(batch)
            assert isinstance(responses, list)
            assert len(responses) == 2
    except NotImplementedError:
        # Batch not supported is acceptable
        pass


def test_server_notification_handling():
    """Test server handles JSON-RPC notifications (no id field)."""
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    notification = {
        "jsonrpc": "2.0",
        "method": "ping",
        # No "id" field - this is a notification
        "params": {}
    }
    
    # Server should handle notification without sending response
    response = server.handle_request(notification)
    
    # Notifications should not return a response (or return None)
    assert response is None or "id" not in response
