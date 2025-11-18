"""Minimal MCP tool registry for tests and integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolDefinition:
    """Definition of a tool in the MCP registry."""

    name: str
    handler: Callable[..., Any]
    schema: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPToolRegistry:
    """Minimal MCP tool registry used in tests and integration.

    This registry provides a simple mechanism to register and retrieve tools
    for MCP server implementations. It supports tool discovery (list_tools)
    and tool execution (get_tool).
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        schema: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a new tool with the registry.

        Args:
            name: Unique tool name identifier
            handler: Callable that implements the tool logic
            schema: Optional JSON schema for tool parameters
            metadata: Optional metadata dictionary
        """
        self._tools[name] = ToolDefinition(
            name=name,
            handler=handler,
            schema=schema,
            metadata=metadata,
        )

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            List of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "metadata": td.metadata or {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def get_tool(self, name: str) -> Callable[..., Any] | None:
        """Retrieve a tool handler by name.

        Args:
            name: Tool name to retrieve

        Returns:
            The tool handler callable, or None if not found

        Note:
            Returns None instead of raising ToolNotFound to match test expectations.
            Production code should check for None before invoking.
        """
        tool_def = self._tools.get(name)
        return tool_def.handler if tool_def else None


__all__ = ["MCPToolRegistry", "ToolDefinition"]
