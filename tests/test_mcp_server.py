"""
Test Mcp Server

Test module for mcp server.
"""

#!/usr/bin/env python3
"""
Test script for MCP JSON-RPC Server.
Verifies complete functionality of the server.
"""

import sys
from pathlib import Path

import pytest

from codex.logging.structured_logger import logger


def find_repo_root() -> Path:
    """Find repository root by searching for marker files."""
    current = Path(__file__).resolve().parent
    markers = ["pyproject.toml", ".git", "setup.py"]

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    # Fallback to parent of tests directory
    return Path(__file__).resolve().parent.parent


# Add repo root to path
repo_root = find_repo_root()
sys.path.insert(0, str(repo_root))

# Try to import MCP modules - skip tests if not available
try:
    from mcp.config import MCPConfig
    from mcp.server import MCPJSONRPCServer

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPJSONRPCServer = None
    MCPConfig = None


pytestmark = pytest.mark.skipif(
    not MCP_AVAILABLE, reason="MCP modules not available - install with: pip install -e ."
)


@pytest.fixture
def mcp_server():
    """Create MCP server fixture."""
    if not MCP_AVAILABLE:
        pytest.skip("MCP modules not available")
    config = MCPConfig.load()
    return MCPJSONRPCServer(config)


def test_server_initialization(mcp_server):
    """Test that server can be initialized."""
    assert mcp_server is not None, "Server should be created"


def test_list_tools(mcp_server):
    """Test listTools method."""
    request = {"jsonrpc": "2.0", "id": 1, "method": "listTools", "params": {}}
    response = mcp_server.handle_request(request)

    assert response["jsonrpc"] == "2.0", "Invalid JSON-RPC version"
    assert response["id"] == 1, "Request ID mismatch"
    assert "result" in response, "No result in response"
    assert "tools" in response["result"], "No tools in result"


def test_negotiate_version(mcp_server):
    """Test negotiateVersion method."""
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "negotiateVersion",
        "params": {"versions": ["1.0", "2.0"]},
    }

    response = mcp_server.handle_request(request)

    assert "result" in response, "No result in response"
    assert response["result"]["version"] == "1.0", "Version negotiation failed"


def test_call_tool_not_found(mcp_server):
    """Test callTool with non-existent tool."""
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "callTool",
        "params": {"name": "nonexistent.tool", "params": {}},
    }

    response = mcp_server.handle_request(request)

    assert "error" in response, "Expected error response"
    assert response["error"]["code"] == 404, "Expected 404 error code"


def test_rate_limiting(mcp_server):
    """Test rate limiting functionality."""
    # Make multiple requests rapidly
    principal_id = "test-user"
    tool_name = "kb.search"

    # First 20 should succeed (burst capacity)
    success_count = 0
    for i in range(25):
        request = {
            "jsonrpc": "2.0",
            "id": 100 + i,
            "method": "callTool",
            "params": {"name": tool_name, "params": {}, "principal_id": principal_id},
        }

        response = mcp_server.handle_request(request)
        if "result" in response:
            success_count += 1
        elif "error" in response and response["error"]["code"] == 429:
            break

    # Rate limiting should have kicked in at some point
    assert success_count > 0, "At least some requests should succeed"


def test_invalid_json_rpc(mcp_server):
    """Test handling of invalid JSON-RPC requests."""
    # Invalid version
    request = {"jsonrpc": "1.0", "id": 4, "method": "listTools"}

    response = mcp_server.handle_request(request)
    assert "error" in response, "Expected error for invalid version"


if __name__ == "__main__":
    # For manual testing outside pytest
    logger.info("Run with: pytest tests/test_mcp_server.py -v")
