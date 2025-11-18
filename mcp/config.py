"""
MCP configuration module.
Centralized configuration for MCP server and tools.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""
    
    name: str
    description: str
    endpoint: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolDefinition":
        return cls(
            name=data["name"],
            description=data["description"],
            endpoint=data["endpoint"]
        )


@dataclass
class MCPConfig:
    """
    Centralized MCP configuration.
    Loads from mcp.json and environment variables.
    """
    
    name: str
    description: str
    tools: List[ToolDefinition]
    ita_url: str
    ita_api_key: Optional[str]
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "MCPConfig":
        """
        Load MCP configuration from file and environment.
        
        Args:
            config_path: Path to mcp.json (defaults to mcp/mcp.json)
            
        Returns:
            MCPConfig instance
        """
        if config_path is None:
            # Default to mcp/mcp.json relative to this file
            config_path = Path(__file__).parent / "mcp.json"
        
        # Load from JSON file
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        tools = [ToolDefinition.from_dict(t) for t in data.get("tools", [])]
        
        # Override with environment variables
        ita_url = os.environ.get("ITA_URL", "http://localhost:8080")
        ita_api_key = os.environ.get("ITA_API_KEY")
        
        return cls(
            name=data.get("name", "mcp-server"),
            description=data.get("description", ""),
            tools=tools,
            ita_url=ita_url,
            ita_api_key=ita_api_key
        )
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
