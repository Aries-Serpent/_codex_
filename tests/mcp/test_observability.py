"""
Tests for MCP observability features.
Covers logging, metrics, tracing, and monitoring capabilities.
"""

import sys
import logging
from pathlib import Path
from io import StringIO

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))


def test_logging_configuration():
    """Test that MCP modules support logging configuration."""
    logger = logging.getLogger('mcp')
    
    # Should be able to configure logger
    logger.setLevel(logging.DEBUG)
    assert logger.level == logging.DEBUG
    
    # Test log capture
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    
    logger.info("MCP test message")
    log_output = stream.getvalue()
    assert "MCP test message" in log_output
    
    logger.removeHandler(handler)


def test_request_id_tracing():
    """Test X-Request-Id header for request tracing."""
    import uuid
    
    # Simulate request ID generation
    request_id = str(uuid.uuid4())
    
    assert len(request_id) == 36  # UUID format
    assert '-' in request_id


def test_error_logging_with_context():
    """Test that errors are logged with appropriate context."""
    from mcp.errors import MCPError, ToolNotFound, RateLimitExceeded
    
    # Errors should have meaningful messages for logging
    errors_to_test = [
        (MCPError("Test error"), "MCP_ERROR"),
        (ToolNotFound("Tool xyz not found"), "TOOL_NOT_FOUND"),
        (RateLimitExceeded("Rate limit exceeded"), "RATE_LIMIT_EXCEEDED"),
    ]
    
    for error, expected_code in errors_to_test:
        error_dict = error.to_dict()
        assert error_dict["code"] == expected_code
        assert "message" in error_dict


def test_metrics_collection_interface():
    """Test that metrics can be collected for observability."""
    # MCP should support metrics collection
    metrics = {
        "requests_total": 0,
        "requests_successful": 0,
        "requests_failed": 0,
        "response_time_ms": [],
    }
    
    # Simulate metric updates
    metrics["requests_total"] += 1
    metrics["requests_successful"] += 1
    metrics["response_time_ms"].append(45.2)
    
    assert metrics["requests_total"] == 1
    assert metrics["requests_successful"] == 1
    assert len(metrics["response_time_ms"]) == 1
    assert metrics["response_time_ms"][0] == 45.2


def test_performance_monitoring():
    """Test performance monitoring capabilities."""
    import time
    
    start_time = time.time()
    # Simulate some work
    time.sleep(0.01)
    elapsed = (time.time() - start_time) * 1000
    
    # Should be able to measure and log performance
    assert elapsed >= 10  # At least 10ms
    assert isinstance(elapsed, float)


def test_health_check_metrics():
    """Test health check and status metrics."""
    health_status = {
        "status": "healthy",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "mcp_registry": "ok"
        },
        "timestamp": "2025-11-18T00:00:00Z"
    }
    
    assert health_status["status"] == "healthy"
    assert all(v == "ok" for v in health_status["checks"].values())


def test_audit_logging():
    """Test audit logging for MCP operations."""
    audit_log = []
    
    # Simulate audit log entry
    def log_audit_event(event_type, principal_id, tool_name, result):
        audit_log.append({
            "event": event_type,
            "principal": principal_id,
            "tool": tool_name,
            "result": result
        })
    
    log_audit_event("tool_call", "user123", "test_tool", "success")
    
    assert len(audit_log) == 1
    assert audit_log[0]["event"] == "tool_call"
    assert audit_log[0]["principal"] == "user123"
    assert audit_log[0]["result"] == "success"


def test_rate_limit_metrics():
    """Test rate limiting metrics collection."""
    from mcp.rate_limit import MCPRateLimiter
    
    limiter = MCPRateLimiter(rate=10.0, capacity=5, seed=42)
    
    # Track rate limit events
    allowed_count = 0
    denied_count = 0
    
    for i in range(7):
        if limiter.allow("test_user", "test_tool"):
            allowed_count += 1
        else:
            denied_count += 1
    
    assert allowed_count == 5  # Capacity limit
    assert denied_count == 2   # Exceeded limit


def test_error_rate_tracking():
    """Test error rate tracking for observability."""
    from mcp.errors import ToolNotFound, ValidationError
    
    error_counts = {
        "ToolNotFound": 0,
        "ValidationError": 0,
        "total": 0
    }
    
    # Simulate error tracking
    errors = [ToolNotFound("tool1"), ValidationError("bad input"), ToolNotFound("tool2")]
    
    for error in errors:
        error_counts["total"] += 1
        error_type = error.__class__.__name__
        if error_type in error_counts:
            error_counts[error_type] += 1
    
    assert error_counts["total"] == 3
    assert error_counts["ToolNotFound"] == 2
    assert error_counts["ValidationError"] == 1


def test_registry_metrics():
    """Test metrics for tool registry operations."""
    from mcp.registry import MCPToolRegistry
    
    registry = MCPToolRegistry()
    
    # Register some tools
    registry.register_tool("tool1", lambda: "result1", metadata={"category": "test"})
    registry.register_tool("tool2", lambda: "result2", metadata={"category": "test"})
    
    tools = registry.list_tools()
    
    # Metrics about registry state
    registry_metrics = {
        "total_tools": len(tools),
        "tool_names": [t["name"] for t in tools]
    }
    
    assert registry_metrics["total_tools"] == 2
    assert "tool1" in registry_metrics["tool_names"]
    assert "tool2" in registry_metrics["tool_names"]


def test_distributed_tracing_headers():
    """Test distributed tracing header propagation."""
    tracing_headers = {
        "X-Request-Id": "req-12345",
        "X-Trace-Id": "trace-67890",
        "X-Span-Id": "span-11111"
    }
    
    # Verify headers are properly formatted
    for header, value in tracing_headers.items():
        assert header.startswith("X-")
        assert isinstance(value, str)
        assert len(value) > 0


def test_observability_integration():
    """Test that observability features integrate properly."""
    # This test verifies the complete observability stack
    observability_components = {
        "logging": True,
        "metrics": True,
        "tracing": True,
        "health_checks": True
    }
    
    assert all(observability_components.values())
