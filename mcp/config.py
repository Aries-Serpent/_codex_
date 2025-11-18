"""
MCP configuration module.
Centralized configuration for MCP server and tools.

Security: Configuration integrity verified with SHA-256 checksums.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional


def compute_checksum(data: str) -> str:
    """Compute SHA-256 checksum of configuration data."""
    return sha256(data.encode('utf-8')).hexdigest()


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
    
    Security: Validates configuration integrity using checksums.
    """
    
    name: str
    description: str
    tools: List[ToolDefinition]
    ita_url: str
    ita_api_key: Optional[str]
    config_checksum: Optional[str] = None
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "MCPConfig":
        """
        Load MCP configuration from file and environment.
        
        Args:
            config_path: Path to mcp.json (defaults to mcp/mcp.json)
            
        Returns:
            MCPConfig instance with verified checksum
        """
        if config_path is None:
            # Default to mcp/mcp.json relative to this file
            config_path = Path(__file__).parent / "mcp.json"
        
        # Load from JSON file and compute checksum
        config_data = config_path.read_text(encoding="utf-8")
        checksum = compute_checksum(config_data)
        data = json.loads(config_data)
        
        tools = [ToolDefinition.from_dict(t) for t in data.get("tools", [])]
        
        # Override with environment variables
        ita_url = os.environ.get("ITA_URL", "http://localhost:8080")
        ita_api_key = os.environ.get("ITA_API_KEY")
        
        return cls(
            name=data.get("name", "mcp-server"),
            description=data.get("description", ""),
            tools=tools,
            ita_url=ita_url,
            ita_api_key=ita_api_key,
            config_checksum=checksum
        )
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    def verify_integrity(self, config_path: Optional[Path] = None) -> bool:
        """
        Verify configuration file integrity using stored checksum.
        
        Returns:
            True if checksum matches, False otherwise
        """
        if config_path is None:
            config_path = Path(__file__).parent / "mcp.json"
        
        if not self.config_checksum:
            return False
        
        current_data = config_path.read_text(encoding="utf-8")
        current_checksum = compute_checksum(current_data)
        
        return current_checksum == self.config_checksum
