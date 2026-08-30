"""MCP server entrypoints and in-process JSON-RPC handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Tool:
    name: str
    description: str
    schema: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"name": self.name, "description": self.description}
        if self.schema is not None:
            payload["schema"] = self.schema  # type: ignore[assignment]
        return payload


@dataclass
class ToolRegistry:
    _tools: list[Tool] = field(default_factory=list)

    def register(self, tool: Tool) -> None:
        self._tools.append(tool)

    def list_tools(self) -> list[dict[str, Any]]:
        return [tool.to_dict() for tool in self._tools]


class MCPServer:
    """Minimal JSON-RPC server for tests and in-process usage."""

    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.supported_versions = ["1.0"]

    async def handle_request(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self.tool_registry.list_tools(),
            }

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }


def get_app():
    from mcp.server.facade_fastapi import APP

    return APP


__all__ = ["MCPServer", "Tool", "ToolRegistry", "get_app"]
