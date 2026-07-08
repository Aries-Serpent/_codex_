"""
Advanced tests for MCP tools integration.
Focus: ITA endpoint integration, tool chaining, concurrent execution.
"""

import threading

import pytest

from mcp.registry import MCPToolRegistry


def test_ita_endpoint_wrapper_pattern():
    """Test wrapping ITA endpoints as MCP tools."""
    registry = MCPToolRegistry()

    # Mock ITA endpoint wrapper
    def ita_kb_search(params):
        return {"results": [f"match:{params['query']}"]}

    registry.register_tool("ita.kb.search", ita_kb_search, metadata={"endpoint": "/api/kb/search"})

    handler = registry.get_tool("ita.kb.search")
    result = handler({"query": "test"})
    assert "results" in result, "Result must not be empty"


def test_tool_chaining():
    """Test executing multiple tools in sequence."""
    registry = MCPToolRegistry()

    registry.register_tool("upper", lambda p: {"result": p["text"].upper()})
    registry.register_tool("reverse", lambda p: {"result": p["text"][::-1]})

    # Chain: input -> upper -> reverse
    text = "hello"
    step1 = registry.get_tool("upper")({"text": text})
    step2 = registry.get_tool("reverse")({"text": step1["result"]})

    assert step2["result"] == "OLLEH", "Result must not be empty"


def test_tool_composition():
    """Test composing tools into pipeline."""
    registry = MCPToolRegistry()

    def compose(tool1_name, tool2_name):
        t1 = registry.get_tool(tool1_name)
        t2 = registry.get_tool(tool2_name)
        return lambda p: t2({"text": t1(p)["result"]})

    registry.register_tool("double", lambda p: {"result": p["text"] * 2})
    registry.register_tool("bracket", lambda p: {"result": f"[{p['text']}]"})

    composed = compose("double", "bracket")
    result = composed({"text": "A"})

    assert result["result"] == "[AA]", "Result must not be empty"


def test_async_tool_execution_pattern():
    """Test async tool execution pattern."""
    import time

    registry = MCPToolRegistry()

    def slow_tool(params):
        # Simulate async work
        return {"status": "completed", "data": params}

    registry.register_tool("slow", slow_tool)

    start = time.time()
    result = registry.get_tool("slow")({"test": "data"})
    elapsed = time.time() - start

    assert result["status"] == "completed", "Result must not be empty"
    assert elapsed < 0.1, "elapsed is not valid"


def test_tool_metadata_validation():
    """Test tool metadata structure validation."""
    registry = MCPToolRegistry()

    metadata = {
        "description": "Test tool",
        "version": "1.0",
        "category": "test",
        "tags": ["testing"],
    }

    registry.register_tool("validated", lambda x: x, metadata=metadata)

    tools = registry.list_tools()
    tool = next(t for t in tools if t["name"] == "validated")

    assert tool["metadata"]["version"] == "1.0", "Data must not be empty"
    assert "testing" in tool["metadata"]["tags"], "Data must not be empty"


def test_tool_versioning():
    """Test tool versioning patterns."""
    registry = MCPToolRegistry()

    registry.register_tool("api_v1", lambda p: {"version": 1}, metadata={"version": "1.0"})
    registry.register_tool("api_v2", lambda p: {"version": 2}, metadata={"version": "2.0"})

    tools = registry.list_tools()
    versions = [t["metadata"]["version"] for t in tools if t["name"].startswith("api_")]

    assert "1.0" in versions, "Condition must be true"
    assert "2.0" in versions, "Condition must be true"


def test_tool_deprecation_pattern():
    """Test marking tools as deprecated."""
    registry = MCPToolRegistry()

    registry.register_tool("old_api", lambda x: x, metadata={"deprecated": True})
    registry.register_tool("new_api", lambda x: x, metadata={"deprecated": False})

    tools = registry.list_tools()
    active = [t for t in tools if not t["metadata"].get("deprecated", False)]

    assert any(t["name"] == "new_api" for t in active), "Condition must be true"


def test_tool_discovery_by_category():
    """Test discovering tools by category."""
    registry = MCPToolRegistry()

    registry.register_tool("search1", lambda x: x, metadata={"category": "search"})
    registry.register_tool("search2", lambda x: x, metadata={"category": "search"})
    registry.register_tool("transform1", lambda x: x, metadata={"category": "transform"})

    tools = registry.list_tools()
    search_tools = [t for t in tools if t["metadata"].get("category") == "search"]

    assert len(search_tools) == 2, "Search_tools must not be empty"


def test_tool_discovery_by_tags():
    """Test discovering tools by tags."""
    registry = MCPToolRegistry()

    registry.register_tool("t1", lambda x: x, metadata={"tags": ["ml", "ai"]})
    registry.register_tool("t2", lambda x: x, metadata={"tags": ["ml"]})
    registry.register_tool("t3", lambda x: x, metadata={"tags": ["data"]})

    tools = registry.list_tools()
    ml_tools = [t for t in tools if "ml" in t["metadata"].get("tags", [])]

    assert len(ml_tools) == 2, "Ml_tools must not be empty"


def test_tool_execution_with_validation():
    """Test tool execution with parameter validation."""
    registry = MCPToolRegistry()

    def validated_tool(params):
        required = ["param1", "param2"]
        for req in required:
            if req not in params:
                raise ValueError(f"Missing required parameter: {req}")
        return {"valid": True}

    registry.register_tool("strict", validated_tool)

    handler = registry.get_tool("strict")

    # Valid
    result = handler({"param1": "a", "param2": "b"})
    assert result["valid"], "Result must not be empty"

    # Invalid
    with pytest.raises(ValueError):
        handler({"param1": "a"})


def test_tool_error_propagation():
    """Test error propagation through tool execution."""
    registry = MCPToolRegistry()

    def error_tool(params):
        if params.get("error"):
            raise RuntimeError("Tool error")
        return {"ok": True}

    registry.register_tool("risky", error_tool)

    handler = registry.get_tool("risky")

    # Success
    assert handler({"error": False})["ok"], "Error should be raised or set"

    # Error propagates
    with pytest.raises(RuntimeError):
        handler({"error": True})


def test_tool_state_management():
    """Test tools with internal state."""
    registry = MCPToolRegistry()

    state = {"counter": 0}

    def stateful_tool(params):
        state["counter"] += 1
        return {"count": state["counter"]}

    registry.register_tool("counter", stateful_tool)

    handler = registry.get_tool("counter")

    assert handler({})["count"] == 1, "Count must be greater than zero"
    assert handler({})["count"] == 2, "Count must be greater than zero"
    assert handler({})["count"] == 3, "Count must be greater than zero"


def test_tool_performance_tracking():
    """Test tracking tool performance metrics."""
    import time

    registry = MCPToolRegistry()
    metrics = {}

    def tracked_tool(params):
        start = time.time()
        result = {"data": params}
        metrics["duration"] = time.time() - start
        return result

    registry.register_tool("tracked", tracked_tool)

    handler = registry.get_tool("tracked")
    handler({"test": "data"})

    assert "duration" in metrics, "Condition must be true"


def test_concurrent_tool_execution():
    """Test concurrent execution of multiple tools."""
    registry = MCPToolRegistry()

    registry.register_tool("concurrent", lambda p: {"id": p["id"]})

    results = []

    def execute(tool_id):
        handler = registry.get_tool("concurrent")
        result = handler({"id": tool_id})
        results.append(result)

    threads = [threading.Thread(target=execute, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 10, "Results must not be empty"


def test_tool_timeout_pattern():
    """Test tool timeout handling pattern."""

    registry = MCPToolRegistry()

    def long_running_tool(params):
        # In real implementation, would timeout
        return {"completed": True}

    registry.register_tool("long", long_running_tool, metadata={"timeout": 5})

    handler = registry.get_tool("long")
    result = handler({})

    assert result["completed"], "Result must not be empty"


def test_tool_retry_pattern():
    """Test tool retry logic pattern."""
    registry = MCPToolRegistry()

    attempts = {"count": 0}

    def flaky_tool(params):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("Temporary failure")
        return {"success": True}

    registry.register_tool("flaky", flaky_tool)

    # Retry logic
    handler = registry.get_tool("flaky")
    max_retries = 5
    for i in range(max_retries):
        try:
            result = handler({})
            assert result["success"], "Result must not be empty"
            break
        except RuntimeError:
            if i == max_retries - 1:
                raise


def test_tool_circuit_breaker_pattern():
    """Test circuit breaker pattern for tools."""
    registry = MCPToolRegistry()

    circuit = {"failures": 0, "open": False}

    def protected_tool(params):
        if circuit["open"]:
            raise RuntimeError("Circuit breaker open")

        if params.get("fail"):
            circuit["failures"] += 1
            if circuit["failures"] >= 3:
                circuit["open"] = True
            raise RuntimeError("Tool failed")

        return {"ok": True}

    registry.register_tool("protected", protected_tool)
    handler = registry.get_tool("protected")

    # Trigger failures
    for _ in range(3):
        try:
            handler({"fail": True})
        except RuntimeError:
            _ = None  # Expected failure to test circuit breaker mechanism

    # Circuit should be open
    assert circuit["open"], "Condition must be true"


def test_tool_fallback_pattern():
    """Test fallback pattern for tool failures."""
    registry = MCPToolRegistry()

    registry.register_tool("primary", lambda p: {"source": "primary"})
    registry.register_tool("fallback", lambda p: {"source": "fallback"})

    def execute_with_fallback(tool_name, fallback_name, params):
        try:
            handler = registry.get_tool(tool_name)
            if handler:
                return handler(params)
        except Exception as _err:
            _ = None  # Intentionally swallow exception to test fallback mechanism

        fallback = registry.get_tool(fallback_name)
        return fallback(params) if fallback else None

    result = execute_with_fallback("primary", "fallback", {})
    assert result["source"] == "primary", "Result must not be empty"


def test_tool_caching_pattern():
    """Test caching pattern for tool results."""
    registry = MCPToolRegistry()

    call_count = {"count": 0}
    cache = {}

    def expensive_tool(params):
        call_count["count"] += 1
        return {"result": params["input"] * 2}

    registry.register_tool("expensive", expensive_tool)

    def cached_execute(params):
        key = str(params)
        if key not in cache:
            handler = registry.get_tool("expensive")
            cache[key] = handler(params)
        return cache[key]

    # First call - executes
    result1 = cached_execute({"input": 5})
    # Second call - cached
    result2 = cached_execute({"input": 5})

    assert result1 == result2, "Result must not be empty"
    assert call_count["count"] == 1, "Count must be greater than zero"


def test_tool_batch_execution():
    """Test batch execution of tools."""
    registry = MCPToolRegistry()

    registry.register_tool("process", lambda p: {"result": p["value"] * 2})

    handler = registry.get_tool("process")

    batch = [{"value": i} for i in range(5)]
    results = [handler(item) for item in batch]

    assert len(results) == 5, "Results must not be empty"
    assert results[2]["result"] == 4, "Result must not be empty"


def test_tool_pipeline_execution():
    """Test pipeline execution of multiple tools."""
    registry = MCPToolRegistry()

    registry.register_tool("step1", lambda p: {"value": p["value"] + 1})
    registry.register_tool("step2", lambda p: {"value": p["value"] * 2})
    registry.register_tool("step3", lambda p: {"value": p["value"] - 3})

    # Execute pipeline
    data = {"value": 5}
    for tool_name in ["step1", "step2", "step3"]:
        handler = registry.get_tool(tool_name)
        data = handler(data)

    # (5 + 1) * 2 - 3 = 9
    assert data["value"] == 9, "Data must not be empty"


def test_tool_conditional_execution():
    """Test conditional tool execution."""
    registry = MCPToolRegistry()

    registry.register_tool("even", lambda p: {"result": "even"})
    registry.register_tool("odd", lambda p: {"result": "odd"})

    def conditional_execute(value):
        tool_name = "even" if value % 2 == 0 else "odd"
        handler = registry.get_tool(tool_name)
        return handler({})

    assert conditional_execute(4)["result"] == "even", "Result must not be empty"
    assert conditional_execute(5)["result"] == "odd", "Result must not be empty"


def test_tool_dynamic_registration():
    """Test dynamic tool registration at runtime."""
    registry = MCPToolRegistry()

    # Dynamically create and register tools
    for i in range(5):
        tool_name = f"dynamic_{i}"

        def handler(params, idx=i):
            return {"index": idx, "data": params}

        registry.register_tool(tool_name, handler)

    tools = registry.list_tools()
    dynamic_tools = [t for t in tools if t["name"].startswith("dynamic_")]

    assert len(dynamic_tools) == 5, "Dynamic_tools must not be empty"


def test_tool_namespace_pattern():
    """Test namespacing tools by category."""
    registry = MCPToolRegistry()

    registry.register_tool("search.kb", lambda x: {"type": "kb"})
    registry.register_tool("search.docs", lambda x: {"type": "docs"})
    registry.register_tool("transform.upper", lambda x: {"type": "upper"})

    tools = registry.list_tools()
    search_tools = [t for t in tools if t["name"].startswith("search.")]

    assert len(search_tools) == 2, "Search_tools must not be empty"


def test_tool_hot_reload_pattern():
    """Test hot-reloading tool implementations."""
    registry = MCPToolRegistry()

    # Initial version
    registry.register_tool("api", lambda p: {"version": 1})

    result1 = registry.get_tool("api")({})
    assert result1["version"] == 1, "Result must not be empty"

    # Hot reload with new version
    registry.register_tool("api", lambda p: {"version": 2})

    result2 = registry.get_tool("api")({})
    assert result2["version"] == 2, "Result must not be empty"


def test_tool_health_check():
    """Test tool health check pattern."""
    registry = MCPToolRegistry()

    def healthy_tool(params):
        if params.get("health_check"):
            return {"status": "healthy"}
        return {"data": "normal operation"}

    registry.register_tool("monitored", healthy_tool)

    handler = registry.get_tool("monitored")

    # Health check
    health = handler({"health_check": True})
    assert health["status"] == "healthy", "Condition must be true"

    # Normal operation
    data = handler({})
    assert "data" in data, "Data must not be empty"


def test_tool_load_balancing_pattern():
    """Test load balancing across tool instances."""
    registry = MCPToolRegistry()

    # Register multiple instances
    for i in range(3):
        registry.register_tool(f"worker_{i}", lambda p, idx=i: {"worker": idx})

    # Round-robin selection
    current = {"index": 0}

    def get_next_worker():
        worker_id = current["index"] % 3
        current["index"] += 1
        return registry.get_tool(f"worker_{worker_id}")

    workers = [get_next_worker()({}) for _ in range(6)]
    worker_ids = [w["worker"] for w in workers]

    # Should cycle through workers
    assert worker_ids == [0, 1, 2, 0, 1, 2]
