"""MCP server implementing JSON-RPC 2.0 protocol."""

import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional


class JsonRpcError(Exception):
    """Custom JSON-RPC error to map into JSON-RPC error objects."""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        """Initialize a JSON-RPC error.
        
        Args:
            code: JSON-RPC error code.
            message: Human-readable error message.
            data: Optional additional error data.
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to JSON-RPC error object format.
        
        Returns:
            Dictionary with code, message, and optional data fields.
        """
        error: Dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            error["data"] = self.data
        return error


@dataclass
class Tool:
    """Represents an MCP tool."""

    name: str
    description: str
    # Extend with params/schema metadata later as needed.


class ToolRegistry:
    """In-memory registry of MCP tools."""

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry.
        
        Args:
            tool: The tool to register.
        """
        self._tools[tool.name] = tool

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools.
        
        Returns:
            A plain list of tool dictionaries (not wrapped in an object).
            This matches JSON-RPC client expectations for mcp.listTools result.
        """
        # Requirement: listTools result must be a plain list, not wrapped in {"tools": ...}
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]


class MCPServer:
    """Minimal MCP server implementing a subset of JSON-RPC 2.0 behavior."""

    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        """Initialize the MCP server.
        
        Args:
            tool_registry: Optional tool registry. If not provided, creates an empty one.
        """
        self._logger = logging.getLogger(__name__)
        self._tool_registry = tool_registry or ToolRegistry()

        # Map JSON-RPC method -> async handler(params) -> result
        self._methods: Dict[str, Callable[[Optional[Dict[str, Any]]], Awaitable[Any]]] = {
            "mcp.listTools": self.handle_list_tools,
        }

    async def handle_list_tools(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Handler for mcp.listTools, returns a plain list of tool objects.
        
        Args:
            params: Optional parameters (unused for listTools).
            
        Returns:
            A plain list of tool dictionaries.
        """
        return await self._tool_registry.list_tools()

    async def _dispatch_request(self, method: str, params: Optional[Dict[str, Any]]) -> Any:
        """Dispatch a JSON-RPC request to the appropriate handler.
        
        Args:
            method: The JSON-RPC method name.
            params: Optional method parameters.
            
        Returns:
            The result from the method handler.
            
        Raises:
            JsonRpcError: If the method is not found.
        """
        handler = self._methods.get(method)
        if handler is None:
            raise JsonRpcError(code=-32601, message="Method not found")
        return await handler(params)

    async def _dispatch_notification(self, method: str, params: Optional[Dict[str, Any]]) -> None:
        """Dispatch a JSON-RPC notification (no response expected).
        
        Args:
            method: The JSON-RPC method name.
            params: Optional method parameters.
        """
        handler = self._methods.get(method)
        if handler is None:
            # Unknown notification: log but do not raise, and never respond.
            self._logger.warning("Unknown notification method: %s", method)
            return
        # We intentionally ignore the return value for notifications.
        await handler(params)

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a single JSON-RPC 2.0 request or notification.

        JSON-RPC 2.0 distinguishes between requests (which have an "id" field and expect
        a response) and notifications (which lack an "id" field and must not receive a response).

        Args:
            request: The JSON-RPC request object.

        Returns:
            - For requests (with "id"): A JSON-RPC response object with "result" or "error".
            - For notifications (without "id"): None, indicating no response should be sent.
        """
        jsonrpc = request.get("jsonrpc")
        method = request.get("method")
        has_id = "id" in request  # Check for presence of "id" field, not if it's None
        request_id = request.get("id")

        # Basic validation per JSON-RPC 2.0
        if jsonrpc != "2.0" or not isinstance(method, str):
            # Invalid Request
            if has_id:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32600, "message": "Invalid Request"},
                }
            # For notifications, swallow errors and return None (no response).
            return None

        # Notification: no "id" field at all
        if not has_id:
            try:
                await self._dispatch_notification(method, request.get("params"))
            except Exception:
                # Requirement: log but do not send any response for notifications
                self._logger.exception("Error handling JSON-RPC notification %s", method)
            return None

        # Normal request/response flow
        try:
            result = await self._dispatch_request(method, request.get("params"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            }
        except JsonRpcError as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": e.to_dict(),
            }
        except Exception:
            self._logger.exception("Unhandled MCP server error")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": "Internal error"},
            }
