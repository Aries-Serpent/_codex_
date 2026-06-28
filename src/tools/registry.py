"""
Tool Registry - Central registry for agent tools.

This module provides a registry for managing tools available to agents.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on tool registration
- Bounds checking on tool count
- Defensive error handling
"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_TOOLS = 1000
MAX_TOOL_NAME_LENGTH = 100


@dataclass
class ToolDefinition:
    """Definition of a registered tool."""

    name: str
    description: str
    handler: Callable
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    timeout_seconds: int = 30
    enabled: bool = True


@dataclass
class ToolResult:
    """Result of a tool execution."""

    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0


class ToolRegistry:
    """
    Central registry for agent tools.

    Features:
    - Tool registration and discovery
    - Parameter validation
    - Execution with error handling
    - Tool metadata management

    Safeguards:
    - Maximum tool count limit
    - Name length validation
    - Execution timeout support
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, ToolDefinition] = {}
        logger.info("ToolRegistry initialized")

    def register(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        parameters: dict[str, Any] | None = None,
        requires_confirmation: bool = False,
        timeout_seconds: int = 30,
    ) -> bool:
        """
        Register a tool with the registry.

        Args:
            name: Unique tool name.
            handler: The function to execute.
            description: Human-readable description.
            parameters: Parameter schema.
            requires_confirmation: Whether tool requires user confirmation.
            timeout_seconds: Execution timeout.

        Returns:
            True if registered successfully.
        """
        # Input validation (safeguard)
        if not name or not isinstance(name, str):
            logger.error("Tool name must be a non-empty string")
            return False

        if len(name) > MAX_TOOL_NAME_LENGTH:
            logger.error("Tool name too long: %d > %d", len(name), MAX_TOOL_NAME_LENGTH)
            return False

        if not callable(handler):
            logger.error("Handler must be callable")
            return False

        # Bounds check (safeguard)
        if len(self._tools) >= MAX_TOOLS:
            logger.error("Maximum tools reached: %d", MAX_TOOLS)
            return False

        # Auto-generate description from docstring if not provided
        if not description and handler.__doc__:
            description = handler.__doc__.strip().split("\n")[0]

        # Auto-extract parameters from function signature
        if parameters is None:
            parameters = self._extract_parameters(handler)

        tool = ToolDefinition(
            name=name,
            description=description,
            handler=handler,
            parameters=parameters,
            requires_confirmation=requires_confirmation,
            timeout_seconds=timeout_seconds,
        )

        self._tools[name] = tool
        logger.info("Registered tool: %s", name)
        return True

    def _extract_parameters(self, handler: Callable) -> dict[str, Any]:
        """Extract parameter schema from function signature."""
        sig = inspect.signature(handler)
        params = {}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_info: dict[str, Any] = {"required": param.default is inspect.Parameter.empty}

            # Try to get type annotation
            if param.annotation is not inspect.Parameter.empty:
                param_info["type"] = str(param.annotation)

            params[param_name] = param_info

        return params

    def unregister(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            logger.info("Unregistered tool: %s", name)
            return True
        return False

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def list_tools(self, enabled_only: bool = True) -> list[ToolDefinition]:
        """List all registered tools."""
        tools = list(self._tools.values())
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        return tools

    def get_tool_names(self, enabled_only: bool = True) -> list[str]:
        """Get list of tool names."""
        return [t.name for t in self.list_tools(enabled_only)]

    async def execute(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            ToolResult with output or error.
        """
        import asyncio
        import time

        start_time = time.time()

        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {name}",
            )

        if not tool.enabled:
            return ToolResult(
                success=False,
                error=f"Tool is disabled: {name}",
            )

        try:
            # Execute the handler - only use wait_for for async handlers
            if asyncio.iscoroutinefunction(tool.handler):
                result = await asyncio.wait_for(
                    tool.handler(*args, **kwargs), timeout=tool.timeout_seconds
                )
            else:
                # Sync handlers don't need timeout wrapper
                result = tool.handler(*args, **kwargs)

            duration = (time.time() - start_time) * 1000

            return ToolResult(
                success=True,
                output=result,
                duration_ms=duration,
            )

        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error=f"Tool execution timed out after {tool.timeout_seconds}s",
                duration_ms=(time.time() - start_time) * 1000,
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Tool execution failed: %s - %s", name, e)
            return ToolResult(
                success=False,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def enable(self, name: str) -> bool:
        """Enable a tool."""
        tool = self.get(name)
        if tool:
            tool.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a tool."""
        tool = self.get(name)
        if tool:
            tool.enabled = False
            return True
        return False

    def get_schema(self) -> list[dict[str, Any]]:
        """Get OpenAI-compatible tool schemas."""
        schemas = []
        for tool in self.list_tools():
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": tool.parameters,
                        },
                    },
                }
            )
        return schemas


# Global registry instance
_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def register_tool(
    name: str,
    handler: Callable | None = None,
    **kwargs: Any,
) -> Callable:
    """Decorator to register a tool."""

    def decorator(fn: Callable) -> Callable:
        get_registry().register(name, fn, **kwargs)
        return fn

    if handler is not None:
        # Called as @register_tool("name")
        return decorator(handler)
    # Called as @register_tool("name", description="...")
    return decorator


def main() -> None:
    """Test the tool registry."""
    import asyncio

    logging.basicConfig(level=logging.INFO)

    registry = ToolRegistry()

    # Register some tools
    def echo(text: str) -> str:
        """Echo the input text."""
        return text

    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    registry.register("echo", echo)
    registry.register("add", add, description="Add two integers")

    print(f"Registered tools: {registry.get_tool_names()}")

    # Execute tools
    async def test_execution() -> None:
        result1 = await registry.execute("echo", "Hello")
        print(f"echo result: {result1.output}")

        result2 = await registry.execute("add", 3, 5)
        print(f"add result: {result2.output}")

    asyncio.run(test_execution())


if __name__ == "__main__":
    main()
