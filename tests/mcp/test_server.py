"""Unit tests for MCP server behavior."""

import asyncio
from typing import Any, Dict, Optional

from mcp.server import MCPServer, Tool, ToolRegistry


def _run(coro: Any) -> Any:
    """Helper to run async coroutines in sync tests."""
    return asyncio.run(coro)


def test_server_listtools_request() -> None:
    """Test that mcp.listTools returns a plain list as the JSON-RPC result.
    
    This validates the requirement that listTools must return a plain list
    of tools, not wrapped in an object like {"tools": [...], "version": "..."}.
    This matches JSON-RPC client expectations and the MCP specification.
    """
    # Arrange
    registry = ToolRegistry()
    registry.register(Tool(name="tool1", description="First tool"))
    registry.register(Tool(name="tool2", description="Second tool"))
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request (not notification) for mcp.listTools
    request: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "abc",
        "method": "mcp.listTools",
        "params": {},
    }
    response: Optional[Dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC response structure
    assert response is not None
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == "abc"

    result = response["result"]
    # Requirement: result must be a plain list
    assert isinstance(result, list)
    assert all(isinstance(t, dict) for t in result)

    names = {t["name"] for t in result}
    assert names == {"tool1", "tool2"}


def test_server_notification_handling() -> None:
    """Test that JSON-RPC notifications (requests without 'id') produce no response.
    
    Per JSON-RPC 2.0 spec, notifications are requests that omit the 'id' field.
    The server must execute any side effects but must NOT send back a response,
    even if the method is unknown or errors occur.
    """
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Notification: no "id" field
    request: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": "mcp.listTools",
        "params": {},
    }

    response = _run(server.handle_request(request))

    # Requirement: notifications must NOT produce a response
    assert response is None


def test_server_negotiate_version() -> None:
    """Test that mcp.negotiateVersion returns a plain string as the JSON-RPC result.
    
    This validates the requirement that negotiateVersion must return the negotiated
    version string directly (not wrapped in a dict), matching the expectations from
    PR #2286 discussion_r2538925659.
    """
    # Arrange
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request for mcp.negotiateVersion with client supporting multiple versions
    request: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "vneg",
        "method": "mcp.negotiateVersion",
        "params": {"supported": ["0.9", "1.0"]},
    }
    response: Optional[Dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC response structure
    assert response is not None
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == "vneg"

    # Requirement: result must be a plain string (the negotiated version)
    result = response["result"]
    assert isinstance(result, str)
    assert result == "1.0"


def test_server_negotiate_version_no_overlap() -> None:
    """Test that mcp.negotiateVersion returns a JSON-RPC error when no version matches.
    
    When the client's supported versions have no overlap with the server's supported
    versions, the server must respond with a JSON-RPC error (code -32602).
    """
    # Arrange
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request with no overlapping versions
    request: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "vneg-no-overlap",
        "method": "mcp.negotiateVersion",
        "params": {"supported": ["0.8", "0.9"]},
    }
    response: Optional[Dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC error response
    assert response is not None
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == "vneg-no-overlap"
    assert "error" in response
    assert response["error"]["code"] == -32602
    assert "No compatible version found" in response["error"]["message"]

