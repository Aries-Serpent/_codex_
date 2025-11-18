#!/usr/bin/env python3
"""
MCP JSON-RPC Server Bridge.

Implements the Model Context Protocol JSON-RPC interface that bridges to ITA endpoints.
Supports listTools and callTool methods using MCPToolRegistry.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

# Add parent directories to path for imports
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from mcp.registry import MCPToolRegistry
from mcp.config import MCPConfig, ToolDefinition
from mcp.errors import MCPError, ToolNotFound, ValidationError, RateLimitExceeded
from mcp.versioning import MCP_VERSIONS, negotiate_version
from mcp.rate_limit import MCPRateLimiter
from mcp.auth import Principal, MCPAuthenticator

# Try to import httpx for making requests to ITA
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class MCPJSONRPCServer:
    """JSON-RPC 2.0 server implementing MCP protocol."""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.registry = MCPToolRegistry()
        self.rate_limiter = MCPRateLimiter(rate=5.0, capacity=20)  # 5 req/sec, burst 20
        self.authenticator = MCPAuthenticator()
        
        # Register tools from config
        for tool in config.tools:
            self._register_tool_from_config(tool)
    
    def _register_tool_from_config(self, tool: ToolDefinition) -> None:
        """Register a tool from configuration."""
        # Create a handler function that will call ITA
        def handler(**kwargs):
            return self._call_ita_endpoint(tool.endpoint, kwargs)
        
        schema = {
            "type": "object",
            "properties": {},
            "description": tool.description
        }
        
        metadata = {
            "endpoint": tool.endpoint,
            "description": tool.description
        }
        
        self.registry.register_tool(tool.name, handler, schema=schema, metadata=metadata)
    
    def _call_ita_endpoint(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an ITA endpoint via HTTP."""
        if not HAS_HTTPX:
            return {
                "error": "httpx not available - install with: pip install httpx",
                "simulated": True
            }
        
        # Construct full URL
        url = f"{self.config.ita_url}{endpoint.replace(self.config.ita_url, '')}"
        
        headers = {}
        if self.config.ita_api_key:
            headers["X-API-Key"] = self.config.ita_api_key
        headers["X-Request-Id"] = params.get("request_id", "mcp-bridge-request")
        
        try:
            with httpx.Client() as client:
                response = client.post(url, json=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "error": f"Failed to call ITA endpoint: {str(e)}",
                "endpoint": url
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a JSON-RPC 2.0 request.
        
        Args:
            request: JSON-RPC request object
            
        Returns:
            JSON-RPC response object
        """
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            # Validate JSON-RPC version
            if request.get("jsonrpc") != "2.0":
                raise ValidationError("Invalid JSON-RPC version")
            
            # Route to appropriate handler
            if method == "listTools":
                result = self._handle_list_tools(params)
            elif method == "callTool":
                result = self._handle_call_tool(params)
            elif method == "negotiateVersion":
                result = self._handle_negotiate_version(params)
            else:
                raise ToolNotFound(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except MCPError as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": e.http_status,
                    "message": e.message,
                    "data": e.to_dict()
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listTools request."""
        tools = self.registry.list_tools()
        return {
            "tools": tools,
            "version": MCP_VERSIONS[0]
        }
    
    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle callTool request."""
        tool_name = params.get("name")
        tool_params = params.get("params", {})
        principal_id = params.get("principal_id", "anonymous")
        
        if not tool_name:
            raise ValidationError("Tool name is required")
        
        # Check rate limit
        if not self.rate_limiter.allow(principal_id, tool_name):
            raise RateLimitExceeded(f"Rate limit exceeded for tool {tool_name}")
        
        # Get tool handler
        handler = self.registry.get_tool(tool_name)
        if handler is None:
            raise ToolNotFound(f"Tool not found: {tool_name}")
        
        # Execute tool
        try:
            result = handler(**tool_params)
            return {
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "error": str(e)
            }
    
    def _handle_negotiate_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle negotiateVersion request."""
        client_versions = params.get("versions", ["1.0"])
        try:
            version = negotiate_version(client_versions)
            return {
                "version": version,
                "supported": MCP_VERSIONS
            }
        except Exception as e:
            raise ValidationError(f"Version negotiation failed: {str(e)}")
    
    def run_stdio(self) -> None:
        """Run server in stdio mode (line-delimited JSON-RPC)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


def main():
    """Main entry point for MCP JSON-RPC server."""
    # Load configuration
    try:
        config = MCPConfig.load()
    except Exception as e:
        sys.stderr.write(f"Failed to load configuration: {e}\n")
        sys.exit(1)
    
    # Create and run server
    server = MCPJSONRPCServer(config)
    
    # Print startup message to stderr (stdout is for JSON-RPC)
    sys.stderr.write(f"MCP JSON-RPC Server starting...\n")
    sys.stderr.write(f"Server: {config.name}\n")
    sys.stderr.write(f"Tools: {len(config.tools)}\n")
    sys.stderr.write(f"ITA URL: {config.ita_url}\n")
    sys.stderr.write(f"Listening on stdin for JSON-RPC requests...\n")
    sys.stderr.flush()
    
    # Run in stdio mode
    server.run_stdio()


if __name__ == "__main__":
    main()
