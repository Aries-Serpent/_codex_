"""MCP configuration management."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_compute_checksum__mutmut_orig(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def x_compute_checksum__mutmut_1(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = None
    return hashlib.sha256(data).hexdigest()


def x_compute_checksum__mutmut_2(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = data.encode(None)
    return hashlib.sha256(data).hexdigest()


def x_compute_checksum__mutmut_3(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = data.encode("XXutf-8XX")
    return hashlib.sha256(data).hexdigest()


def x_compute_checksum__mutmut_4(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = data.encode("UTF-8")
    return hashlib.sha256(data).hexdigest()


def x_compute_checksum__mutmut_5(data: str | bytes) -> str:
    """Compute SHA-256 checksum of data.

    Args:
        data: String or bytes to hash

    Returns:
        64-character hex string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(None).hexdigest()

x_compute_checksum__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_checksum__mutmut_1': x_compute_checksum__mutmut_1, 
    'x_compute_checksum__mutmut_2': x_compute_checksum__mutmut_2, 
    'x_compute_checksum__mutmut_3': x_compute_checksum__mutmut_3, 
    'x_compute_checksum__mutmut_4': x_compute_checksum__mutmut_4, 
    'x_compute_checksum__mutmut_5': x_compute_checksum__mutmut_5
}

def compute_checksum(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_checksum__mutmut_orig, x_compute_checksum__mutmut_mutants, args, kwargs)
    return result 

compute_checksum.__signature__ = _mutmut_signature(x_compute_checksum__mutmut_orig)
x_compute_checksum__mutmut_orig.__name__ = 'x_compute_checksum'


@dataclass
class ToolDefinition:
    """Definition of an MCP tool from configuration."""

    name: str
    description: str = ""
    endpoint: str = ""
    metadata: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolDefinition":
        """Create ToolDefinition from dictionary.

        Args:
            data: Dictionary with tool definition

        Returns:
            ToolDefinition instance
        """
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            endpoint=data.get("endpoint", ""),
            metadata=data.get("metadata"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "endpoint": self.endpoint,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class MCPConfig:
    """MCP configuration with tools and settings."""

    name: str
    tools: list[ToolDefinition]
    ita_url: str
    config_checksum: str
    ita_api_key: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "MCPConfig":
        """Load MCP configuration from file.

        Configuration Resolution Strategy:
        1. If config_path is provided, load from that specific file
        2. Otherwise, search for config file in standard locations (in order):
           - mcp_config.json (project root)
           - .codex/mcp_config.json
           - config/mcp_config.json
        3. If no config file found, use minimal default configuration
        4. Environment variables override file-based settings:
           - ITA_URL overrides ita_url from config
           - ITA_API_KEY overrides ita_api_key from config

        Args:
            config_path: Optional path to config file. If not provided,
                        looks for mcp_config.json in standard locations.

        Returns:
            MCPConfig instance with file-based config and environment overrides applied
        """

        if config_path is None:
            # Search for config in standard locations (priority order)
            candidates = [
                Path("mcp_config.json"),
                Path(".codex/mcp_config.json"),
                Path("config/mcp_config.json"),
            ]
            for candidate in candidates:
                if candidate.exists():
                    config_path = candidate
                    break

            # Fallback: No config file found, return default configuration
            if config_path is None or not config_path.exists():
                # Use default checksum for empty config
                default_content = json.dumps(
                    {"name": "default", "tools": [], "ita_url": "http://localhost:8000"}
                )
                return cls(
                    name="default",
                    tools=[],
                    ita_url=os.environ.get("ITA_URL", "http://localhost:8000"),
                    ita_api_key=os.environ.get("ITA_API_KEY"),
                    config_checksum=compute_checksum(default_content),
                )

        # Load from file
        content = config_path.read_text()
        checksum = compute_checksum(content)
        data = json.loads(content)

        tools = [ToolDefinition.from_dict(t) for t in data.get("tools", [])]

        # Allow environment variable overrides
        ita_url = os.environ.get("ITA_URL", data.get("ita_url", "http://localhost:8000"))
        ita_api_key = os.environ.get("ITA_API_KEY", data.get("ita_api_key"))

        return cls(
            name=data.get("name", "mcp"),
            tools=tools,
            ita_url=ita_url,
            ita_api_key=ita_api_key,
            config_checksum=checksum,
            metadata=data.get("metadata"),
        )

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool by name.

        Args:
            name: Tool name to retrieve

        Returns:
            ToolDefinition if found, None otherwise
        """
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def verify_integrity(self, config_path: Path) -> bool:
        """Verify configuration file integrity using checksum.

        Args:
            config_path: Path to configuration file

        Returns:
            True if checksums match, False otherwise
        """
        if not config_path.exists():
            return False

        current_content = config_path.read_text()
        current_checksum = compute_checksum(current_content)
        return current_checksum == self.config_checksum

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "tools": [t.to_dict() for t in self.tools],
            "ita_url": self.ita_url,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


__all__ = ["MCPConfig", "ToolDefinition", "compute_checksum"]
