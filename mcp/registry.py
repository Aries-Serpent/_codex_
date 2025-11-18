from typing import Any, Callable, Dict, List, Optional


class MCPToolRegistry:
    """
    Registry for MCP tools. Allows registering tools with metadata and retrieving them.
    """
    def __init__(self) -> None:
        # Internal storage for tools: name -> info dict
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, handler: Callable[..., Any], schema: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a tool with the registry.
        :param name: Unique tool name (string identifier).
        :param handler: Callable to execute the tool logic.
        :param schema: Optional JSON schema or Pydantic model for tool input/output.
        :param metadata: Optional dict of additional metadata (description, etc.).
        """
        self._tools[name] = {
            "handler": handler,
            "schema": schema,
            "metadata": metadata or {}
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools with their metadata (excluding actual handler for safety).
        """
        tools_info = []
        for name, info in self._tools.items():
            data = {"name": name}
            # include schema and metadata if present
            if info.get("schema"):
                data["schema"] = info["schema"]
            if info.get("metadata"):
                data["metadata"] = info["metadata"]
            tools_info.append(data)
        return tools_info

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Retrieve the handler for a given tool by name.
        """
        entry = self._tools.get(name)
        if entry:
            return entry["handler"]
        return None
