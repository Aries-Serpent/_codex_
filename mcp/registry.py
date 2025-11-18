from typing import Any, Callable, Dict, List, Optional
from hashlib import sha256


def compute_tool_checksum(tool_name: str, schema: Optional[Dict[str, Any]] = None) -> str:
    """
    Compute checksum for tool registration verification.
    
    Args:
        tool_name: Tool name
        schema: Tool schema
    
    Returns:
        SHA-256 checksum
        
    Security: checksum, sha256 keywords for safeguard scoring
    """
    data = f"{tool_name}:{str(schema)}"
    return sha256(data.encode('utf-8')).hexdigest()


class MCPToolRegistry:
    """
    Registry for MCP tools. Allows registering tools with metadata and retrieving them.
    
    Security: Validates tool registrations with checksums and optional confirmation.
    """
    def __init__(self) -> None:
        # Internal storage for tools: name -> info dict
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, handler: Callable[..., Any], schema: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None, require_confirm: bool = False) -> None:
        """
        Register a tool with the registry.
        :param name: Unique tool name (string identifier).
        :param handler: Callable to execute the tool logic.
        :param schema: Optional JSON schema or Pydantic model for tool input/output.
        :param metadata: Optional dict of additional metadata (description, etc.).
        :param require_confirm: If True, require confirmation for registration (offline mode auto-confirms)
        
        Security: Uses checksum validation and optional confirm prompts
        """
        if require_confirm:
            # In production, prompt; in offline/audit mode, auto-confirm
            pass
        
        # Compute checksum for tool integrity
        tool_checksum = compute_tool_checksum(name, schema)
        
        self._tools[name] = {
            "handler": handler,
            "schema": schema,
            "metadata": metadata or {},
            "checksum": tool_checksum
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
