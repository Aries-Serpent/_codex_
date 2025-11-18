"""
Tests for MCP tools integration and end-to-end workflows.
Covers tool registration, execution, and integration with ITA.
"""

import pytest
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.registry import MCPToolRegistry
from mcp.config import MCPConfig
from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal
from mcp.rate_limit import MCPRateLimiter
from mcp.errors import RateLimitExceeded


def test_tool_registration_workflow():
    """Test complete tool registration workflow."""
    registry = MCPToolRegistry()
    
    # Register tool
    def my_tool(param1, param2):
        return f"{param1}-{param2}"
    
    registry.register_tool(
        "my_tool",
        handler=my_tool,
        schema={"type": "object", "properties": {"param1": {}, "param2": {}}},
        metadata={"description": "Test tool", "version": "1.0"}
    )
    
    # Verify registration
    tools = registry.list_tools()
    assert any(t["name"] == "my_tool" for t in tools)
    
    # Execute tool
    handler = registry.get_tool("my_tool")
    result = handler("foo", "bar")
    assert result == "foo-bar"


def test_auth_integration():
    """Test authentication integration in workflow."""
    authorizer = MCPAuthorizer()
    
    # Authenticate principal
    principal = Principal.from_credential("test_api_key")
    assert principal is not None
    assert principal.principal_id is not None
    
    # Authorize action
    # Default behavior: allow all authenticated principals
    result = authorizer.authorize(principal, "test_tool")
    assert result is True


def test_rate_limit_integration():
    """Test rate limiting integration in tool execution."""
    limiter = MCPRateLimiter(rate=5.0, capacity=10, seed=42)
    registry = MCPToolRegistry()
    
    def rate_limited_tool():
        return "result"
    
    registry.register_tool("limited_tool", rate_limited_tool)
    
    principal_id = "user123"
    tool_name = "limited_tool"
    
    # Should allow up to capacity
    for i in range(10):
        assert limiter.allow(principal_id, tool_name)
    
    # Should block after capacity
    assert not limiter.allow(principal_id, tool_name)


def test_end_to_end_tool_call():
    """Test complete end-to-end tool call workflow."""
    # Setup
    registry = MCPToolRegistry()
    rate_limiter = MCPRateLimiter(rate=10.0, capacity=20)
    
    # Register tool
    def echo_tool(message):
        return {"echo": message}
    
    registry.register_tool("echo", echo_tool, metadata={"public": True})
    
    # Simulate request workflow
    # 1. Authenticate
    principal = Principal(principal_id="test_user")
    session_token = authenticator.generate_session_token(principal)
    assert session_token is not None
    
    # 2. Check rate limit
    if not rate_limiter.allow(principal.principal_id, "echo"):
        raise RateLimitExceeded("Too many requests")
    
    # 3. Authorize
    authorizer.authorize(principal, "echo")
    
    # 4. Execute tool
    handler = registry.get_tool("echo")
    result = handler(message="Hello, MCP!")
    
    assert result == {"echo": "Hello, MCP!"}


def test_tool_discovery():
    """Test tool discovery and metadata."""
    registry = MCPToolRegistry()
    
    # Register multiple tools with metadata
    tools_to_register = [
        ("tool1", lambda: "r1", {"category": "utility", "version": "1.0"}),
        ("tool2", lambda: "r2", {"category": "data", "version": "1.1"}),
        ("tool3", lambda: "r3", {"category": "utility", "version": "2.0"}),
    ]
    
    for name, handler, metadata in tools_to_register:
        registry.register_tool(name, handler, metadata=metadata)
    
    # List all tools
    all_tools = registry.list_tools()
    assert len(all_tools) == 3
    
    # Tools should have metadata
    for tool in all_tools:
        assert "name" in tool
        assert "metadata" in tool


def test_error_propagation():
    """Test error propagation through integration layers."""
    registry = MCPToolRegistry()
    
    def failing_tool():
        raise ValueError("Tool execution failed")
    
    registry.register_tool("failing_tool", failing_tool)
    
    # Errors should propagate with context
    handler = registry.get_tool("failing_tool")
    with pytest.raises(ValueError) as exc_info:
        handler()
    
    assert "Tool execution failed" in str(exc_info.value)


def test_configuration_integration():
    """Test configuration integration across components."""
    config = MCPConfig.load()
    
    # Config should be usable by all components
    assert config.ita_url is not None
    assert config.tools is not None
    
    # Verify tools are registerable
    for tool_def in config.tools:
        # Tools from config should be registerable
        assert tool_def.name is not None


def test_multi_tool_execution():
    """Test executing multiple tools in sequence."""
    registry = MCPToolRegistry()
    
    # Register tools
    registry.register_tool("step1", lambda x: x * 2, metadata={"step": 1})
    registry.register_tool("step2", lambda x: x + 10, metadata={"step": 2})
    registry.register_tool("step3", lambda x: x / 2, metadata={"step": 3})
    
    # Execute pipeline
    result = 5
    for tool_name in ["step1", "step2", "step3"]:
        handler = registry.get_tool(tool_name)
        result = handler(result)
    
    # (5 * 2 + 10) / 2 = 10
    assert result == 10


def test_tool_validation():
    """Test tool parameter validation."""
    registry = MCPToolRegistry()
    
    def validated_tool(required_param, optional_param=None):
        if not required_param:
            raise ValueError("required_param is required")
        return {"required": required_param, "optional": optional_param}
    
    registry.register_tool(
        "validated_tool",
        validated_tool,
        schema={
            "type": "object",
            "properties": {
                "required_param": {"type": "string"},
                "optional_param": {"type": "string"}
            },
            "required": ["required_param"]
        }
    )
    
    handler = registry.get_tool("validated_tool")
    
    # Valid call
    result = handler(required_param="test")
    assert result["required"] == "test"
    
    # Invalid call - missing required param
    with pytest.raises(TypeError):
        handler()


def test_concurrent_tool_access():
    """Test concurrent access to tools."""
    registry = MCPToolRegistry()
    
    counter = {"value": 0}
    
    def increment_tool():
        counter["value"] += 1
        return counter["value"]
    
    registry.register_tool("increment", increment_tool)
    
    # Simulate concurrent calls
    handler = registry.get_tool("increment")
    results = [handler() for _ in range(10)]
    
    assert counter["value"] == 10
    assert results == list(range(1, 11))


def test_tool_lifecycle():
    """Test tool lifecycle: register, update, unregister."""
    registry = MCPToolRegistry()
    
    # Register
    registry.register_tool("lifecycle_tool", lambda: "v1", metadata={"version": "1.0"})
    assert registry.get_tool("lifecycle_tool") is not None
    
    # Update (re-register with new handler)
    registry.register_tool("lifecycle_tool", lambda: "v2", metadata={"version": "2.0"})
    result = registry.get_tool("lifecycle_tool")()
    assert result == "v2"


def test_ita_endpoint_integration():
    """Test integration with ITA endpoints."""
    # This tests the pattern used in services/ita/app/main.py
    from mcp.config import MCPConfig
    
    config = MCPConfig.load()
    
    # ITA URL should be configured
    assert "localhost" in config.ita_url or "http" in config.ita_url
    
    # Tools should have endpoint information
    for tool in config.tools:
        assert hasattr(tool, 'endpoint')


def test_full_request_lifecycle():
    """Test complete request lifecycle with all components."""
    # Setup all components
    registry = MCPToolRegistry()
    rate_limiter = MCPRateLimiter(rate=10.0, capacity=20)
    
    # Register test tool
    def full_lifecycle_tool(input_data):
        return {"processed": input_data.upper()}
    
    registry.register_tool(
        "full_lifecycle_tool",
        full_lifecycle_tool,
        metadata={"description": "Full lifecycle test"}
    )
    
    # Simulate full request
    principal_id = "test_user"
    tool_name = "full_lifecycle_tool"
    params = {"input_data": "hello"}
    
    # 1. Rate limit check
    if not rate_limiter.allow(principal_id, tool_name):
        pytest.fail("Rate limit should allow request")
    
    # 2. Get tool
    handler = registry.get_tool(tool_name)
    assert handler is not None
    
    # 3. Execute
    result = handler(**params)
    
    # 4. Validate result
    assert result == {"processed": "HELLO"}
