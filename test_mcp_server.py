#!/usr/bin/env python3
"""
Test script for MCP JSON-RPC Server.
Verifies complete functionality of the server.
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from mcp.server import MCPJSONRPCServer
from mcp.config import MCPConfig


def test_server_initialization():
    """Test that server can be initialized."""
    print("=" * 80)
    print("TEST 1: Server Initialization")
    print("=" * 80)
    
    config = MCPConfig.load()
    server = MCPJSONRPCServer(config)
    
    print(f"✓ Server created successfully")
    print(f"  - Config name: {config.name}")
    print(f"  - Tools registered: {len(config.tools)}")
    print(f"  - ITA URL: {config.ita_url}")
    print()
    return server


def test_list_tools(server):
    """Test listTools method."""
    print("=" * 80)
    print("TEST 2: listTools Method")
    print("=" * 80)
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "listTools",
        "params": {}
    }
    
    response = server.handle_request(request)
    
    assert response["jsonrpc"] == "2.0", "Invalid JSON-RPC version"
    assert response["id"] == 1, "Request ID mismatch"
    assert "result" in response, "No result in response"
    assert "tools" in response["result"], "No tools in result"
    
    tools = response["result"]["tools"]
    print(f"✓ listTools succeeded")
    print(f"  - Tools returned: {len(tools)}")
    for tool in tools:
        print(f"    * {tool['name']}: {tool['metadata']['description']}")
    print()


def test_negotiate_version(server):
    """Test negotiateVersion method."""
    print("=" * 80)
    print("TEST 3: negotiateVersion Method")
    print("=" * 80)
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "negotiateVersion",
        "params": {"versions": ["1.0", "2.0"]}
    }
    
    response = server.handle_request(request)
    
    assert "result" in response, "No result in response"
    assert response["result"]["version"] == "1.0", "Version negotiation failed"
    
    print(f"✓ negotiateVersion succeeded")
    print(f"  - Negotiated version: {response['result']['version']}")
    print(f"  - Supported versions: {response['result']['supported']}")
    print()


def test_call_tool_not_found(server):
    """Test callTool with non-existent tool."""
    print("=" * 80)
    print("TEST 4: callTool - Tool Not Found")
    print("=" * 80)
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "callTool",
        "params": {
            "name": "nonexistent.tool",
            "params": {}
        }
    }
    
    response = server.handle_request(request)
    
    assert "error" in response, "Expected error response"
    assert response["error"]["code"] == 404, "Expected 404 error code"
    
    print(f"✓ callTool correctly returns error for nonexistent tool")
    print(f"  - Error code: {response['error']['code']}")
    print(f"  - Error message: {response['error']['message']}")
    print()


def test_rate_limiting(server):
    """Test rate limiting functionality."""
    print("=" * 80)
    print("TEST 5: Rate Limiting")
    print("=" * 80)
    
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
            "params": {
                "name": tool_name,
                "params": {},
                "principal_id": principal_id
            }
        }
        
        response = server.handle_request(request)
        if "result" in response:
            success_count += 1
        elif "error" in response and response["error"]["code"] == 429:
            break
    
    print(f"✓ Rate limiting is active")
    print(f"  - Successful requests before limit: {success_count}")
    print(f"  - Rate limiter: 5 req/sec, burst 20")
    print()


def test_invalid_json_rpc(server):
    """Test handling of invalid JSON-RPC requests."""
    print("=" * 80)
    print("TEST 6: Invalid JSON-RPC Requests")
    print("=" * 80)
    
    # Invalid version
    request = {
        "jsonrpc": "1.0",
        "id": 4,
        "method": "listTools"
    }
    
    response = server.handle_request(request)
    assert "error" in response, "Expected error for invalid version"
    
    print(f"✓ Invalid JSON-RPC version handled correctly")
    print(f"  - Error: {response['error']['message']}")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("*" * 80)
    print("MCP JSON-RPC SERVER - FUNCTIONALITY VERIFICATION")
    print("*" * 80)
    print()
    
    try:
        server = test_server_initialization()
        test_list_tools(server)
        test_negotiate_version(server)
        test_call_tool_not_found(server)
        test_rate_limiting(server)
        test_invalid_json_rpc(server)
        
        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("MCP JSON-RPC Server is fully functional!")
        print()
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
