"""Minimal MCP tool registry for tests and integration."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


def compute_tool_checksum(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class ToolDefinition:
    """Definition of a tool in the MCP registry."""

    name: str
    handler: Callable[..., Any]
    schema: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    require_confirm: bool = False  # Whether tool requires confirmation before execution


class MCPToolRegistry:
    """Minimal MCP tool registry used in tests and integration.

    This registry provides a simple mechanism to register and retrieve tools
    for MCP server implementations. It supports tool discovery (list_tools)
    and tool execution (get_tool).
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        schema: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        require_confirm: bool = False,
    ) -> None:
        """Register a new tool with the registry.

        Args:
            name: Unique tool name identifier
            handler: Callable that implements the tool logic
            schema: Optional JSON schema for tool parameters
            metadata: Optional metadata dictionary
            require_confirm: Whether tool requires confirmation before execution
        """
        self._tools[name] = ToolDefinition(
            name=name,
            handler=handler,
            schema=schema,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
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


__all__ = ["MCPToolRegistry", "ToolDefinition", "compute_tool_checksum"]
