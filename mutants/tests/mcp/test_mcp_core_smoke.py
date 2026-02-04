"""
Core MCP module smoke tests.
Tests basic functionality of MCP registry, errors, rate limiting, and versioning.
"""

import sys
from pathlib import Path

import pytest

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.errors import MCPError, RateLimitExceeded, ToolNotFound, Unauthorized, ValidationError
from mcp.rate_limit import MCPRateLimiter
from mcp.registry import MCPToolRegistry
from mcp.versioning import MCP_VERSIONS, negotiate_version


def test_registry_basic():
    """Test MCPToolRegistry basic operations."""
    registry = MCPToolRegistry()
    registry.register_tool(
        "echo",
        handler=lambda x: x,
        schema={"type": "object"},
        metadata={"description": "Echo tool"},
    )

    tools = registry.list_tools()
    assert any(t["name"] == "echo" for t in tools)

    handler = registry.get_tool("echo")
    assert handler is not None
    assert handler("ping") == "ping"


def test_registry_list_tools():
    """Test MCPToolRegistry list_tools returns correct structure."""
    registry = MCPToolRegistry()
    registry.register_tool("tool1", lambda: "result1", metadata={"desc": "Tool 1"})
    registry.register_tool("tool2", lambda: "result2", metadata={"desc": "Tool 2"})

    tools = registry.list_tools()
    assert len(tools) == 2
    assert all("name" in t for t in tools)
    assert all("metadata" in t for t in tools)


def test_registry_get_nonexistent_tool():
    """Test that getting nonexistent tool returns None."""
    registry = MCPToolRegistry()
    handler = registry.get_tool("nonexistent")
    assert handler is None


def test_rate_limiter_basic():
    """Test MCPRateLimiter basic token bucket behavior."""
    limiter = MCPRateLimiter(rate=10.0, capacity=2)

    # First two calls should succeed (burst capacity)
    assert limiter.allow("principal", "tool")
    assert limiter.allow("principal", "tool")

    # Third call should be rejected until refill occurs
    assert not limiter.allow("principal", "tool")


def test_rate_limiter_multiple_principals():
    """Test that rate limiter tracks principals independently."""
    limiter = MCPRateLimiter(rate=5.0, capacity=1)

    # Different principals should have separate limits
    assert limiter.allow("principal1", "tool")
    assert limiter.allow("principal2", "tool")

    # Same principal should be rate limited
    assert not limiter.allow("principal1", "tool")


def test_rate_limiter_reset():
    """Test rate limiter reset functionality."""
    limiter = MCPRateLimiter(rate=1.0, capacity=1, seed=42)

    # Exhaust limit
    assert limiter.allow("principal", "tool")
    assert not limiter.allow("principal", "tool")

    # Reset and try again
    limiter.reset("principal", "tool")
    assert limiter.allow("principal", "tool")


def test_errors_codes_and_statuses():
    """Test that MCP error classes have correct codes and HTTP statuses."""
    test_cases = [
        (MCPError, "MCP_ERROR", 500),
        (ToolNotFound, "TOOL_NOT_FOUND", 404),
        (ValidationError, "VALIDATION_ERROR", 400),
        (RateLimitExceeded, "RATE_LIMIT_EXCEEDED", 429),
        (Unauthorized, "UNAUTHORIZED", 401),
    ]

    for cls, expected_code, expected_status in test_cases:
        exc = cls("test message")
        data = exc.to_dict()
        assert data["code"] == expected_code
        assert data["message"] == "test message"
        assert exc.http_status == expected_status


def test_errors_to_dict():
    """Test MCPError to_dict serialization."""
    error = ToolNotFound("Tool 'xyz' not found")
    data = error.to_dict()

    assert isinstance(data, dict)
    assert "code" in data
    assert "message" in data
    assert data["code"] == "TOOL_NOT_FOUND"


def test_version_negotiate_basic():
    """Test basic version negotiation."""
    # Should successfully negotiate a supported version
    chosen = negotiate_version([MCP_VERSIONS[0]])
    assert chosen in MCP_VERSIONS


def test_version_negotiate_multiple_versions():
    """Test negotiation with multiple version options."""
    # Should pick the highest common version
    chosen = negotiate_version(["1.0", "2.0"])
    assert chosen == "1.0"  # Only 1.0 is supported


def test_version_negotiate_mismatch():
    """Test that mismatched versions raise exception."""
    with pytest.raises(Exception) as exc_info:
        negotiate_version(["0.0", "0.5"])
    assert "No compatible MCP version" in str(exc_info.value)


def test_mcp_versions_constant():
    """Test that MCP_VERSIONS is properly defined."""
    assert isinstance(MCP_VERSIONS, list)
    assert len(MCP_VERSIONS) > 0
    assert "1.0" in MCP_VERSIONS
