"""
Tests for MCP registry functionality and tool management.
Covers tool registration, discovery, invocation, and lifecycle.
"""

import pytest

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from mcp.registry import MCPToolRegistry


def test_registry_initialization():
    """Test registry can be initialized."""
    registry = MCPToolRegistry()
    assert registry is not None, "registry must be initialized"


def test_register_simple_tool():
    """Test registering a simple tool."""
    registry = MCPToolRegistry()

    def simple_tool():
        return "simple result"

    registry.register_tool("simple", simple_tool)

    handler = registry.get_tool("simple")
    assert handler is not None, "handler must be initialized"
    assert handler() == "simple result", "Result must not be empty"


def test_register_tool_with_params():
    """Test registering tool with parameters."""
    registry = MCPToolRegistry()

    def param_tool(x, y):
        return x + y

    registry.register_tool("add", param_tool)

    handler = registry.get_tool("add")
    result = handler(5, 3)
    assert result == 8, "Result must not be empty"


def test_register_tool_with_schema():
    """Test registering tool with JSON schema."""
    registry = MCPToolRegistry()

    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
        "required": ["name"],
    }

    def schema_tool(name, age=None):
        return {"name": name, "age": age}

    registry.register_tool("person", schema_tool, schema=schema)

    handler = registry.get_tool("person")
    result = handler(name="Alice", age=30)
    assert result["name"] == "Alice", "Result must not be empty"
    assert result["age"] == 30, "Result must not be empty"


def test_register_tool_with_metadata():
    """Test registering tool with metadata."""
    registry = MCPToolRegistry()

    metadata = {"description": "Test tool", "version": "1.0.0", "author": "test"}

    registry.register_tool("meta_tool", lambda: "result", metadata=metadata)

    tools = registry.list_tools()
    meta_tool = next(t for t in tools if t["name"] == "meta_tool")

    assert meta_tool["metadata"]["version"] == "1.0.0", "Data must not be empty"
    assert meta_tool["metadata"]["author"] == "test", "Data must not be empty"


def test_list_all_tools():
    """Test listing all registered tools."""
    registry = MCPToolRegistry()

    registry.register_tool("tool1", lambda: 1)
    registry.register_tool("tool2", lambda: 2)
    registry.register_tool("tool3", lambda: 3)

    tools = registry.list_tools()

    assert len(tools) == 3, "Tools must not be empty"
    tool_names = [t["name"] for t in tools]
    assert "tool1" in tool_names, "Condition must be true"
    assert "tool2" in tool_names, "Condition must be true"
    assert "tool3" in tool_names, "Condition must be true"


def test_get_nonexistent_tool():
    """Test getting a tool that doesn't exist."""
    registry = MCPToolRegistry()

    handler = registry.get_tool("nonexistent")
    assert handler is None, "handler is not valid"


def test_overwrite_existing_tool():
    """Test overwriting an existing tool."""
    registry = MCPToolRegistry()

    registry.register_tool("tool", lambda: "v1")
    result1 = registry.get_tool("tool")()
    assert result1 == "v1", "Result must not be empty"

    # Overwrite
    registry.register_tool("tool", lambda: "v2")
    result2 = registry.get_tool("tool")()
    assert result2 == "v2", "Result must not be empty"


def test_tool_categories():
    """Test organizing tools by categories."""
    registry = MCPToolRegistry()

    registry.register_tool("util1", lambda: "u1", metadata={"category": "utility"})
    registry.register_tool("util2", lambda: "u2", metadata={"category": "utility"})
    registry.register_tool("data1", lambda: "d1", metadata={"category": "data"})

    tools = registry.list_tools()

    util_tools = [t for t in tools if t.get("metadata", {}).get("category") == "utility"]
    data_tools = [t for t in tools if t.get("metadata", {}).get("category") == "data"]

    assert len(util_tools) == 2, "Util_tools must not be empty"
    assert len(data_tools) == 1, "Data_tools must not be empty"


def test_tool_versioning():
    """Test tool versioning."""
    registry = MCPToolRegistry()

    # Register v1
    registry.register_tool("versioned", lambda: "v1.0", metadata={"version": "1.0"})

    # Register v2
    registry.register_tool("versioned", lambda: "v2.0", metadata={"version": "2.0"})

    tools = registry.list_tools()
    versioned_tool = next(t for t in tools if t["name"] == "versioned")

    assert versioned_tool["metadata"]["version"] == "2.0", "Data must not be empty"


def test_tool_discovery_filters():
    """Test filtering tools during discovery."""
    registry = MCPToolRegistry()

    registry.register_tool("public1", lambda: 1, metadata={"public": True})
    registry.register_tool("public2", lambda: 2, metadata={"public": True})
    registry.register_tool("private1", lambda: 3, metadata={"public": False})

    all_tools = registry.list_tools()

    # Can filter public tools
    public_tools = [t for t in all_tools if t.get("metadata", {}).get("public") is True]

    assert len(public_tools) == 2, "Public_tools must not be empty"


def test_tool_with_complex_return():
    """Test tool that returns complex data structures."""
    registry = MCPToolRegistry()

    def complex_tool():
        return {"status": "success", "data": [1, 2, 3], "metadata": {"count": 3}}

    registry.register_tool("complex", complex_tool)

    result = registry.get_tool("complex")()

    assert result["status"] == "success", "Result must not be empty"
    assert result["data"] == [1, 2, 3]
    assert result["metadata"]["count"] == 3, "Result must not be empty"


def test_tool_error_handling():
    """Test tool that raises errors."""
    registry = MCPToolRegistry()

    def error_tool():
        raise ValueError("Tool error")

    registry.register_tool("error_tool", error_tool)

    handler = registry.get_tool("error_tool")

    with pytest.raises(ValueError) as exc_info:
        handler()

    assert "Tool error" in str(exc_info.value), "Value must be initialized"


def test_tool_with_default_params():
    """Test tool with default parameters."""
    registry = MCPToolRegistry()

    def default_tool(required, optional="default"):
        return f"{required}-{optional}"

    registry.register_tool("defaults", default_tool)

    handler = registry.get_tool("defaults")

    # With default
    result1 = handler("test")
    assert result1 == "test-default", "Result must not be empty"

    # Override default
    result2 = handler("test", "custom")
    assert result2 == "test-custom", "Result must not be empty"


def test_tool_introspection():
    """Test introspecting tool properties."""
    registry = MCPToolRegistry()

    def introspect_tool(param1, param2):
        return "result"

    metadata = {
        "description": "Introspection test",
        "parameters": ["param1", "param2"],
        "returns": "string",
    }

    registry.register_tool("introspect", introspect_tool, metadata=metadata)

    tools = registry.list_tools()
    tool = next(t for t in tools if t["name"] == "introspect")

    assert tool["metadata"]["parameters"] == ["param1", "param2"]
    assert tool["metadata"]["returns"] == "string", "Data must not be empty"


def test_registry_empty_state():
    """Test registry in empty state."""
    registry = MCPToolRegistry()

    tools = registry.list_tools()
    assert len(tools) == 0, "Tools must not be empty"

    handler = registry.get_tool("anything")
    assert handler is None, "handler is not valid"


def test_tool_naming_conventions():
    """Test various tool naming conventions."""
    registry = MCPToolRegistry()

    # Different naming styles
    names = [
        "simple_name",
        "camelCaseName",
        "kebab-case-name",
        "dot.separated.name",
        "namespace:tool",
    ]

    for i, name in enumerate(names):
        registry.register_tool(name, lambda x=i: x)

    tools = registry.list_tools()
    registered_names = [t["name"] for t in tools]

    for name in names:
        assert name in registered_names, "Condition must be true"


def test_tool_execution_context():
    """Test tools with execution context."""
    registry = MCPToolRegistry()

    context = {"user": "test_user", "session": "12345"}

    def context_tool(ctx=None):
        return {"context": ctx}

    registry.register_tool("ctx_tool", context_tool)

    result = registry.get_tool("ctx_tool")(ctx=context)

    assert result["context"]["user"] == "test_user", "Result must not be empty"
    assert result["context"]["session"] == "12345", "Result must not be empty"


def test_bulk_tool_registration():
    """Test registering multiple tools at once."""
    registry = MCPToolRegistry()

    tools_to_register = [
        ("bulk1", lambda: "r1", {}),
        ("bulk2", lambda: "r2", {}),
        ("bulk3", lambda: "r3", {}),
        ("bulk4", lambda: "r4", {}),
        ("bulk5", lambda: "r5", {}),
    ]

    for name, handler, metadata in tools_to_register:
        registry.register_tool(name, handler, metadata=metadata)

    tools = registry.list_tools()
    assert len(tools) == 5, "Tools must not be empty"
