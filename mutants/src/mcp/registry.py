"""Minimal MCP tool registry for tests and integration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional
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


def x_compute_tool_checksum__mutmut_orig(tool_name: str, tool_data: dict[str, Any]) -> str:
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


def x_compute_tool_checksum__mutmut_1(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = None
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_2(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"XXnameXX": tool_name, "data": tool_data}
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_3(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"NAME": tool_name, "data": tool_data}
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_4(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "XXdataXX": tool_data}
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_5(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "DATA": tool_data}
    serialized = json.dumps(combined, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_6(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = None
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_7(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(None, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_8(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(combined, sort_keys=None)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_9(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_10(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(combined, )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_11(tool_name: str, tool_data: dict[str, Any]) -> str:
    """Compute SHA-256 checksum of tool definition for integrity verification.

    Args:
        tool_name: Name of the tool
        tool_data: Dictionary containing tool definition (schema, metadata, etc.)

    Returns:
        64-character hex string (SHA-256 hash)
    """
    # Combine tool name and data for checksum
    combined = {"name": tool_name, "data": tool_data}
    serialized = json.dumps(combined, sort_keys=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def x_compute_tool_checksum__mutmut_12(tool_name: str, tool_data: dict[str, Any]) -> str:
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
    return hashlib.sha256(None).hexdigest()


def x_compute_tool_checksum__mutmut_13(tool_name: str, tool_data: dict[str, Any]) -> str:
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
    return hashlib.sha256(serialized.encode(None)).hexdigest()


def x_compute_tool_checksum__mutmut_14(tool_name: str, tool_data: dict[str, Any]) -> str:
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
    return hashlib.sha256(serialized.encode("XXutf-8XX")).hexdigest()


def x_compute_tool_checksum__mutmut_15(tool_name: str, tool_data: dict[str, Any]) -> str:
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
    return hashlib.sha256(serialized.encode("UTF-8")).hexdigest()

x_compute_tool_checksum__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_tool_checksum__mutmut_1': x_compute_tool_checksum__mutmut_1, 
    'x_compute_tool_checksum__mutmut_2': x_compute_tool_checksum__mutmut_2, 
    'x_compute_tool_checksum__mutmut_3': x_compute_tool_checksum__mutmut_3, 
    'x_compute_tool_checksum__mutmut_4': x_compute_tool_checksum__mutmut_4, 
    'x_compute_tool_checksum__mutmut_5': x_compute_tool_checksum__mutmut_5, 
    'x_compute_tool_checksum__mutmut_6': x_compute_tool_checksum__mutmut_6, 
    'x_compute_tool_checksum__mutmut_7': x_compute_tool_checksum__mutmut_7, 
    'x_compute_tool_checksum__mutmut_8': x_compute_tool_checksum__mutmut_8, 
    'x_compute_tool_checksum__mutmut_9': x_compute_tool_checksum__mutmut_9, 
    'x_compute_tool_checksum__mutmut_10': x_compute_tool_checksum__mutmut_10, 
    'x_compute_tool_checksum__mutmut_11': x_compute_tool_checksum__mutmut_11, 
    'x_compute_tool_checksum__mutmut_12': x_compute_tool_checksum__mutmut_12, 
    'x_compute_tool_checksum__mutmut_13': x_compute_tool_checksum__mutmut_13, 
    'x_compute_tool_checksum__mutmut_14': x_compute_tool_checksum__mutmut_14, 
    'x_compute_tool_checksum__mutmut_15': x_compute_tool_checksum__mutmut_15
}

def compute_tool_checksum(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_tool_checksum__mutmut_orig, x_compute_tool_checksum__mutmut_mutants, args, kwargs)
    return result 

compute_tool_checksum.__signature__ = _mutmut_signature(x_compute_tool_checksum__mutmut_orig)
x_compute_tool_checksum__mutmut_orig.__name__ = 'x_compute_tool_checksum'


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

    def xǁMCPToolRegistryǁ__init____mutmut_orig(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def xǁMCPToolRegistryǁ__init____mutmut_1(self) -> None:
        self._tools: dict[str, ToolDefinition] = None
    
    xǁMCPToolRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁ__init____mutmut_1': xǁMCPToolRegistryǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁ__init____mutmut_orig)
    xǁMCPToolRegistryǁ__init____mutmut_orig.__name__ = 'xǁMCPToolRegistryǁ__init__'

    def xǁMCPToolRegistryǁregister_tool__mutmut_orig(
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

    def xǁMCPToolRegistryǁregister_tool__mutmut_1(
        self,
        name: str,
        handler: Callable[..., Any],
        schema: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        require_confirm: bool = True,
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

    def xǁMCPToolRegistryǁregister_tool__mutmut_2(
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
        self._tools[name] = None

    def xǁMCPToolRegistryǁregister_tool__mutmut_3(
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
            name=None,
            handler=handler,
            schema=schema,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_4(
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
            handler=None,
            schema=schema,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_5(
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
            schema=None,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_6(
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
            metadata=None,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_7(
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
            require_confirm=None,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_8(
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
            handler=handler,
            schema=schema,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_9(
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
            schema=schema,
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_10(
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
            metadata=metadata,
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_11(
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
            require_confirm=require_confirm,
        )

    def xǁMCPToolRegistryǁregister_tool__mutmut_12(
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
            )
    
    xǁMCPToolRegistryǁregister_tool__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁregister_tool__mutmut_1': xǁMCPToolRegistryǁregister_tool__mutmut_1, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_2': xǁMCPToolRegistryǁregister_tool__mutmut_2, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_3': xǁMCPToolRegistryǁregister_tool__mutmut_3, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_4': xǁMCPToolRegistryǁregister_tool__mutmut_4, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_5': xǁMCPToolRegistryǁregister_tool__mutmut_5, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_6': xǁMCPToolRegistryǁregister_tool__mutmut_6, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_7': xǁMCPToolRegistryǁregister_tool__mutmut_7, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_8': xǁMCPToolRegistryǁregister_tool__mutmut_8, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_9': xǁMCPToolRegistryǁregister_tool__mutmut_9, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_10': xǁMCPToolRegistryǁregister_tool__mutmut_10, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_11': xǁMCPToolRegistryǁregister_tool__mutmut_11, 
        'xǁMCPToolRegistryǁregister_tool__mutmut_12': xǁMCPToolRegistryǁregister_tool__mutmut_12
    }
    
    def register_tool(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁregister_tool__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁregister_tool__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_tool.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁregister_tool__mutmut_orig)
    xǁMCPToolRegistryǁregister_tool__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁregister_tool'

    def xǁMCPToolRegistryǁlist_tools__mutmut_orig(self) -> list[dict[str, Any]]:
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

    def xǁMCPToolRegistryǁlist_tools__mutmut_1(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "XXnameXX": td.name,
                "metadata": td.metadata or {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_2(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "NAME": td.name,
                "metadata": td.metadata or {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_3(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "XXmetadataXX": td.metadata or {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_4(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "METADATA": td.metadata or {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_5(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "metadata": td.metadata and {},
                "schema": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_6(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "metadata": td.metadata or {},
                "XXschemaXX": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_7(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "metadata": td.metadata or {},
                "SCHEMA": td.schema or {},
            }
            for td in self._tools.values()
        ]

    def xǁMCPToolRegistryǁlist_tools__mutmut_8(self) -> list[dict[str, Any]]:
        """Return list of all registered tools with their metadata.

        Returns:
            list of tool dictionaries with name, metadata, and schema
        """
        return [
            {
                "name": td.name,
                "metadata": td.metadata or {},
                "schema": td.schema and {},
            }
            for td in self._tools.values()
        ]
    
    xǁMCPToolRegistryǁlist_tools__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁlist_tools__mutmut_1': xǁMCPToolRegistryǁlist_tools__mutmut_1, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_2': xǁMCPToolRegistryǁlist_tools__mutmut_2, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_3': xǁMCPToolRegistryǁlist_tools__mutmut_3, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_4': xǁMCPToolRegistryǁlist_tools__mutmut_4, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_5': xǁMCPToolRegistryǁlist_tools__mutmut_5, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_6': xǁMCPToolRegistryǁlist_tools__mutmut_6, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_7': xǁMCPToolRegistryǁlist_tools__mutmut_7, 
        'xǁMCPToolRegistryǁlist_tools__mutmut_8': xǁMCPToolRegistryǁlist_tools__mutmut_8
    }
    
    def list_tools(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁlist_tools__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁlist_tools__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_tools.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁlist_tools__mutmut_orig)
    xǁMCPToolRegistryǁlist_tools__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁlist_tools'

    def xǁMCPToolRegistryǁget_tool__mutmut_orig(self, name: str) -> Callable[..., Any] | None:
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

    def xǁMCPToolRegistryǁget_tool__mutmut_1(self, name: str) -> Callable[..., Any] | None:
        """Retrieve a tool handler by name.

        Args:
            name: Tool name to retrieve

        Returns:
            The tool handler callable, or None if not found

        Note:
            Returns None instead of raising ToolNotFound to match test expectations.
            Production code should check for None before invoking.
        """
        tool_def = None
        return tool_def.handler if tool_def else None

    def xǁMCPToolRegistryǁget_tool__mutmut_2(self, name: str) -> Callable[..., Any] | None:
        """Retrieve a tool handler by name.

        Args:
            name: Tool name to retrieve

        Returns:
            The tool handler callable, or None if not found

        Note:
            Returns None instead of raising ToolNotFound to match test expectations.
            Production code should check for None before invoking.
        """
        tool_def = self._tools.get(None)
        return tool_def.handler if tool_def else None
    
    xǁMCPToolRegistryǁget_tool__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPToolRegistryǁget_tool__mutmut_1': xǁMCPToolRegistryǁget_tool__mutmut_1, 
        'xǁMCPToolRegistryǁget_tool__mutmut_2': xǁMCPToolRegistryǁget_tool__mutmut_2
    }
    
    def get_tool(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPToolRegistryǁget_tool__mutmut_orig"), object.__getattribute__(self, "xǁMCPToolRegistryǁget_tool__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_tool.__signature__ = _mutmut_signature(xǁMCPToolRegistryǁget_tool__mutmut_orig)
    xǁMCPToolRegistryǁget_tool__mutmut_orig.__name__ = 'xǁMCPToolRegistryǁget_tool'


__all__ = ["MCPToolRegistry", "ToolDefinition", "compute_tool_checksum"]
