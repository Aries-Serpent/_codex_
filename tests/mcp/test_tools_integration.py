"""
Tests for MCP tools integration capability.

Covers tool discovery, registration, execution, ITA endpoint integration,
and end-to-end tool invocation workflows.
"""

from typing import Any

import pytest

from mcp.registry import MCPToolRegistry


def test_tool_discovery():
    """Test tool discovery via registry."""
    registry = MCPToolRegistry()
    registry.register_tool("tool1", lambda x: x, schema={}, metadata={"desc": "Tool 1"})
    registry.register_tool("tool2", lambda x: x * 2, schema={}, metadata={"desc": "Tool 2"})

    tools = registry.list_tools()
    assert len(tools) == 2, "Tools must not be empty"
    assert any(t["name"] == "tool1" for t in tools), "Condition must be true"
    assert any(t["name"] == "tool2" for t in tools), "Condition must be true"


def test_tool_registration_with_metadata():
    """Test tool registration includes metadata."""
    registry = MCPToolRegistry()
    metadata = {"description": "Search knowledge base", "version": "1.0", "tags": ["search", "kb"]}
    registry.register_tool("kb.search", lambda q: [], schema={}, metadata=metadata)

    tools = registry.list_tools()
    tool = next(t for t in tools if t["name"] == "kb.search")
    assert tool["metadata"]["description"] == "Search knowledge base", "Data must not be empty"
    assert "search" in tool["metadata"]["tags"], "Data must not be empty"


def test_tool_registration_with_schema():
    """Test tool registration includes JSON schema."""
    registry = MCPToolRegistry()
    schema = {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    registry.register_tool("search", lambda q: [], schema=schema)

    tools = registry.list_tools()
    tool = next(t for t in tools if t["name"] == "search")
    assert tool["schema"]["type"] == "object", "Object must be initialized"
    assert "query" in tool["schema"]["properties"], "Condition must be true"


def test_tool_execution():
    """Test tool execution via registry."""
    registry = MCPToolRegistry()

    def echo_tool(params: dict[str, Any]) -> dict[str, Any]:
        return {"echo": params.get("message", "")}

    registry.register_tool("echo", echo_tool)

    handler = registry.get_tool("echo")
    assert handler is not None, "handler must be initialized"
    result = handler({"message": "hello"})
    assert result["echo"] == "hello", "Result must not be empty"


def test_tool_not_found():
    """Test handling of non-existent tool."""
    registry = MCPToolRegistry()
    handler = registry.get_tool("nonexistent")
    assert handler is None, "handler is not valid"


def test_tool_overwrite():
    """Test tool can be overwritten in registry."""
    registry = MCPToolRegistry()
    registry.register_tool("tool", lambda x: "v1")
    registry.register_tool("tool", lambda x: "v2")

    handler = registry.get_tool("tool")
    result = handler(None)
    assert result == "v2", "Result must not be empty"


def test_multiple_tool_execution():
    """Test execution of multiple different tools."""
    registry = MCPToolRegistry()
    registry.register_tool("add", lambda p: p["a"] + p["b"])
    registry.register_tool("mul", lambda p: p["a"] * p["b"])

    add_handler = registry.get_tool("add")
    mul_handler = registry.get_tool("mul")

    assert add_handler({"a": 2, "b": 3}) == 5
    assert mul_handler({"a": 2, "b": 3}) == 6


def test_tool_with_complex_return():
    """Test tool returning complex data structures."""
    registry = MCPToolRegistry()

    def complex_tool(params):
        return {"status": "success", "data": {"items": [1, 2, 3]}, "metadata": {"count": 3}}

    registry.register_tool("complex", complex_tool)
    handler = registry.get_tool("complex")
    result = handler({})

    assert result["status"] == "success", "Result must not be empty"
    assert len(result["data"]["items"]) == 3, "Collection must not be empty"


def test_tool_list_excludes_handlers():
    """Test tool list doesn't expose handler functions."""
    registry = MCPToolRegistry()
    registry.register_tool("tool", lambda x: x, metadata={"key": "value"})

    tools = registry.list_tools()
    tool = tools[0]

    # Handler should not be in the list output
    assert "handler" not in tool, "Condition must be true"
    assert "name" in tool, "Condition must be true"
    assert "metadata" in tool, "Data must not be empty"


def test_tool_with_error_handling():
    """Test tool execution with error handling."""
    registry = MCPToolRegistry()

    def failing_tool(params):
        if params.get("fail"):
            raise ValueError("Intentional failure")
        return {"success": True}

    registry.register_tool("risky", failing_tool)
    handler = registry.get_tool("risky")

    # Success case
    result = handler({"fail": False})
    assert result["success"] is True, "Result must not be empty"

    # Failure case
    with pytest.raises(ValueError):
        handler({"fail": True})


def test_ita_endpoint_integration_pattern():
    """Test ITA endpoint integration pattern for tools."""
    # This simulates how tools integrate with ITA endpoints
    registry = MCPToolRegistry()

    def ita_search_wrapper(params):
        # In production, this would call ITA endpoint
        query = params["query"]
        # Mock ITA response
        return {"results": [f"match for: {query}"]}

    registry.register_tool("kb.search", ita_search_wrapper, metadata={"endpoint": "/api/kb/search"})

    handler = registry.get_tool("kb.search")
    result = handler({"query": "test"})
    assert "results" in result, "Result must not be empty"


def test_tool_registration_with_confirmation():
    """Test tool registration with confirmation flag."""
    registry = MCPToolRegistry()
    # In production, require_confirm would prompt user
    registry.register_tool(
        "dangerous", lambda x: "executed", require_confirm=True  # Offline mode auto-confirms
    )

    handler = registry.get_tool("dangerous")
    assert handler is not None, "handler must be initialized"


def test_tool_checksum_validation():
    """Test tool registration includes checksum."""
    from mcp.registry import compute_tool_checksum

    schema = {"type": "object"}
    checksum = compute_tool_checksum("tool", schema)

    assert len(checksum) == 64, "Checksum must not be empty"
    assert checksum.isalnum(), "Condition must be true"


def test_tool_discovery_by_metadata():
    """Test filtering tools by metadata attributes."""
    registry = MCPToolRegistry()
    registry.register_tool("t1", lambda x: x, metadata={"category": "search"})
    registry.register_tool("t2", lambda x: x, metadata={"category": "transform"})
    registry.register_tool("t3", lambda x: x, metadata={"category": "search"})

    tools = registry.list_tools()
    search_tools = [t for t in tools if t["metadata"].get("category") == "search"]

    assert len(search_tools) == 2, "Search_tools must not be empty"


def test_tool_versioning():
    """Test tool versioning in metadata."""
    registry = MCPToolRegistry()
    registry.register_tool(
        "versioned", lambda x: x, metadata={"version": "1.0", "deprecated": False}
    )
    registry.register_tool("old", lambda x: x, metadata={"version": "0.9", "deprecated": True})

    tools = registry.list_tools()
    active_tools = [t for t in tools if not t["metadata"].get("deprecated", False)]

    assert len(active_tools) == 1, "Active_tools must not be empty"
    assert active_tools[0]["name"] == "versioned", "Condition must be true"


def test_concurrent_tool_access():
    """Test concurrent access to tool registry."""
    import threading

    registry = MCPToolRegistry()
    registry.register_tool("concurrent", lambda x: x)

    results = []

    def access_tool():
        handler = registry.get_tool("concurrent")
        results.append(handler("test"))

    threads = [threading.Thread(target=access_tool) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 10, "Results must not be empty"
    assert all(r == "test" for r in results), "Result must not be empty"


def test_tool_lifecycle():
    """Test complete tool lifecycle: register, list, execute."""
    registry = MCPToolRegistry()

    # Register
    def lifecycle_tool(params):
        return {"stage": "executed", "input": params}

    registry.register_tool(
        "lifecycle",
        lifecycle_tool,
        schema={"type": "object"},
        metadata={"description": "Lifecycle test"},
    )

    # List
    tools = registry.list_tools()
    assert any(t["name"] == "lifecycle" for t in tools), "Condition must be true"

    # Execute
    handler = registry.get_tool("lifecycle")
    result = handler({"test": "data"})
    assert result["stage"] == "executed", "Result must not be empty"
    assert result["input"]["test"] == "data", "Result must not be empty"


def test_tool_integration_with_validation():
    """Test tool integration includes input validation."""
    registry = MCPToolRegistry()

    def validated_tool(params):
        required = ["field1", "field2"]
        for field in required:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")
        return {"status": "ok"}

    registry.register_tool("validated", validated_tool)
    handler = registry.get_tool("validated")

    # Valid input
    result = handler({"field1": "a", "field2": "b"})
    assert result["status"] == "ok", "Result must not be empty"

    # Invalid input
    with pytest.raises(ValueError):
        handler({"field1": "a"})


def test_tool_registry_state_isolation():
    """Test multiple registry instances are isolated."""
    reg1 = MCPToolRegistry()
    reg2 = MCPToolRegistry()

    reg1.register_tool("tool1", lambda x: "reg1")
    reg2.register_tool("tool2", lambda x: "reg2")

    assert reg1.get_tool("tool1") is not None, "Value must be initialized"
    assert reg1.get_tool("tool2") is None, "Condition must be true"
    assert reg2.get_tool("tool2") is not None, "Value must be initialized"
    assert reg2.get_tool("tool1") is None, "Condition must be true"


def test_tool_with_state():
    """Test tools can maintain internal state."""
    counter = {"value": 0}

    def stateful_tool(params):
        counter["value"] += 1
        return {"count": counter["value"]}

    registry = MCPToolRegistry()
    registry.register_tool("counter", stateful_tool)

    handler = registry.get_tool("counter")
    assert handler({})["count"] == 1, "Count must be greater than zero"
    assert handler({})["count"] == 2, "Count must be greater than zero"
    assert handler({})["count"] == 3, "Count must be greater than zero"


def test_tool_integration_end_to_end():
    """Test complete end-to-end tool integration workflow."""
    # Setup
    registry = MCPToolRegistry()

    # Register multiple tools
    registry.register_tool("echo", lambda p: p, metadata={"type": "utility"})
    registry.register_tool(
        "upper", lambda p: {"result": p["text"].upper()}, metadata={"type": "transform"}
    )
    registry.register_tool("search", lambda p: {"results": []}, metadata={"type": "query"})

    # Discover
    tools = registry.list_tools()
    assert len(tools) == 3, "Tools must not be empty"

    # Execute each
    echo_result = registry.get_tool("echo")({"test": "data"})
    upper_result = registry.get_tool("upper")({"text": "hello"})
    search_result = registry.get_tool("search")({"query": "test"})

    assert echo_result == {"test": "data"}, "Result must not be empty"
    assert upper_result["result"] == "HELLO", "Result must not be empty"
    assert "results" in search_result, "Result must not be empty"
