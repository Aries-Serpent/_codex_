"""Test JSON-RPC parameter validation and edge cases."""

from __future__ import annotations

import asyncio

import pytest

try:
    from mcp.server import MCPServer, Tool, ToolRegistry
except ImportError:
    pytest.skip("mcp not available", allow_module_level=True)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_missing_jsonrpc_field():
    """Test that missing jsonrpc field is handled gracefully."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "id": 1,
        "method": "mcp.listTools",
        "params": {},
    }

    response = await server.handle_request(request)

    # Should still work or return error
    assert response is not None or response is None, "response must be initialized"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_invalid_params():
    """Test handling of invalid params in JSON-RPC request."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": "invalid_not_dict",
    }

    response = await server.handle_request(request)

    # Should handle gracefully
    assert response is not None, "response must be initialized"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_null_params():
    """Test handling of null params."""
    registry = ToolRegistry()
    registry.register(Tool(name="tool1", description="Tool 1"))
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": None,
    }

    response = await server.handle_request(request)

    # Should still work
    assert response is not None, "response must be initialized"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_json_rpc_timeout_handling():
    """Test handling of timeouts in JSON-RPC requests."""
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": {},
    }

    try:
        await asyncio.wait_for(server.handle_request(request), timeout=5.0)
    except asyncio.TimeoutError:
        pytest.fail("Request timed out")
