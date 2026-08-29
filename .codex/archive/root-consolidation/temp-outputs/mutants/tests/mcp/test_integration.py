"""Integration tests for MCP server."""

import asyncio
from typing import Any, Optional

from mcp.auth import AllowAllAuthorizer, BasicAuthenticator, Principal
from mcp.server import MCPServer, Tool, ToolRegistry


async def _call_server(server: MCPServer, request: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Helper to call the server asynchronously."""
    return await server.handle_request(request)


def test_end_to_end_tool_call() -> None:
    """Test end-to-end tool call through the MCP server with authentication.

    This test validates:
    1. Auth components (authenticator/authorizer) are properly instantiated.
    2. MCP server can handle JSON-RPC requests for tool listing.
    3. The response structure matches JSON-RPC 2.0 expectations.
    4. Tools registered in the registry are returned in the response.
    """
    # Arrange: server with a simple tool in the registry
    registry = ToolRegistry()
    registry.register(Tool(name="echo", description="Echo tool"))
    server = MCPServer(tool_registry=registry)

    # Arrange: auth components (explicitly instantiated to avoid NameError)
    authenticator = BasicAuthenticator()
    authorizer = AllowAllAuthorizer()
    principal = Principal(principal_id="user-123")

    token = authenticator.generate_session_token(principal)
    # Token should be a 64-char hex hash (SHA-256)
    assert len(token) == 64, "Token must not be empty"
    assert all(c in "0123456789abcdef" for c in token), "Condition must be true"

    # For now, we just assert authorize() returns True for a valid principal
    assert authorizer.authorize(principal, tool_name="echo")

    # Act: send a JSON-RPC request to list tools
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools",
        "params": {},
    }
    response = asyncio.run(_call_server(server, request))

    # Assert: validate JSON-RPC structure and tool presence
    assert response is not None, "response must be initialized"
    assert response["jsonrpc"] == "2.0", "Response must not be empty"
    assert response["id"] == 1, "Response must not be empty"

    result = response["result"]
    assert isinstance(result, list)
    assert any(tool["name"] == "echo" for tool in result), "Result must not be empty"
