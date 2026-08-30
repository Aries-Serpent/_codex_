"""Test JSON-RPC routing and message dispatch."""

from __future__ import annotations

import asyncio

import pytest

try:
    from mcp.server import MCPServer, Tool, ToolRegistry  # noqa: F401
except ImportError:
    pytest.skip("mcp not available", allow_module_level=True)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_request_with_id():
    """Test JSON-RPC request with ID produces a response."""
    registry = ToolRegistry()
    registry.register(Tool(name="test_tool", description="Test tool"))
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": {},
    }

    response = await server.handle_request(request)

    assert response is not None, "response must be initialized"
    assert response["jsonrpc"] == "2.0", "Response must not be empty"
    assert response["id"] == 1, "Response must not be empty"
    assert "result" in response, "Response must not be empty"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_notification_no_response():
    """Test JSON-RPC notification (no ID) produces no response."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "method": "mcp.listTools",
        "params": {},
    }

    response = await server.handle_request(request)

    assert response is None, "Response must not be empty"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_error_response():
    """Test JSON-RPC error response for invalid method."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "invalid.method",
        "params": {},
    }

    response = await server.handle_request(request)

    assert response is not None, "response must be initialized"
    assert "error" in response, "Response must not be empty"
    assert response["error"]["code"] == -32601, "Response must not be empty"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_batch_requests():
    """Test JSON-RPC batch request handling."""
    registry = ToolRegistry()
    registry.register(Tool(name="tool1", description="Tool 1"))
    server = MCPServer(tool_registry=registry)

    batch = [
        {"jsonrpc": "2.0", "id": 1, "method": "mcp.listTools", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "mcp.listTools", "params": {}},
    ]

    responses = []
    for req in batch:
        resp = await server.handle_request(req)
        if resp:
            responses.append(resp)

    assert len(responses) == 2, "Responses must not be empty"


def test_json_rpc_version_negotiation():
    """Test version negotiation with multiple supported versions."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": "version_test",
        "method": "mcp.negotiateVersion",
        "params": {"supported": ["0.9", "1.0", "1.1"]},
    }

    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(server.handle_request(request))

    assert response is not None, "response must be initialized"
    assert "result" in response, "Response must not be empty"


def test_json_rpc_large_payload():
    """Test handling of large JSON-RPC payloads."""
    registry = ToolRegistry()
    tools = [Tool(name=f"tool_{i}", description=f"Tool {i}") for i in range(100)]
    for tool in tools:
        registry.register(tool)

    server = MCPServer(tool_registry=registry)
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": {},
    }

    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(server.handle_request(request))

    assert response is not None, "response must be initialized"
    assert isinstance(response["result"], list)
    assert len(response["result"]) == 100, "Collection must not be empty"
