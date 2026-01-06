# MCP Implementation Guide for AI Agents

> Version: 1.0.0 | Generated: Previous Cycle-12-17 | Author: Copilot Agent

This guide provides step-by-step instructions for AI agents to implement, extend, and maintain MCP (Model Context Protocol) capabilities in the `_codex_` repository.

## Quick Reference

### MCP Module Locations

```
src/mcp/
├── __init__.py          # Package exports
├── auth.py              # Authentication (MCPAuthenticator)
├── config.py            # Configuration (MCPConfig)
├── errors.py            # Error hierarchy (MCPError)
├── lifecycle.py         # Lifecycle management (LifecycleManager)
├── observability.py     # Metrics/tracing (MetricsRegistry, Tracer)
├── rate_limit.py        # Rate limiting (TokenBucketRateLimiter)
├── registry.py          # Tool registry (ToolRegistry)
├── versioning.py        # Version compatibility
└── server/
    ├── __init__.py      # MCPServer, JsonRpcError, Tool
    ├── stdio.py         # StdioTransport
    └── json_rpc.py      # JsonRpcHandler
```

### Test Locations

```
tests/mcp/
├── test_server.py
├── test_auth.py
├── test_config.py
├── test_lifecycle.py / test_lifecycle_management.py
├── test_observability.py
├── test_rate_limit.py
├── test_registry.py
├── test_versioning.py
├── test_stdio.py
├── test_json_rpc.py / test_json_rpc_handler.py
└── test_integration.py
```

## Implementation Patterns

### 1. Adding a New MCP Capability

```python
# Step 1: Create the module file
# src/mcp/new_capability.py

"""New MCP capability module.

This module provides [description].
"""

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CapabilityConfig:
    """Configuration for the capability."""
    setting1: str = "default"
    setting2: int = 100


class NewCapability:
    """Implementation of the new capability."""
    
    def __init__(self, config: Optional[CapabilityConfig] = None) -> None:
        self._config = config or CapabilityConfig()
        self._logger = logging.getLogger(__name__)
    
    def do_something(self, param: str) -> str:
        """Perform the capability action.
        
        Args:
            param: Input parameter.
            
        Returns:
            Result of the action.
        """
        self._logger.debug("Doing something with: %s", param)
        return f"Result: {param}"
```

### 2. Adding Tests for a Capability

```python
# tests/mcp/test_new_capability.py

"""Tests for new_capability module."""

import pytest
from src.mcp.new_capability import NewCapability, CapabilityConfig


class TestNewCapability:
    """Test suite for NewCapability."""
    
    def test_init_with_defaults(self):
        """Test initialization with default config."""
        cap = NewCapability()
        assert cap._config.setting1 == "default"
    
    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        config = CapabilityConfig(setting1="custom", setting2=200)
        cap = NewCapability(config)
        assert cap._config.setting1 == "custom"
    
    def test_do_something(self):
        """Test the main capability action."""
        cap = NewCapability()
        result = cap.do_something("test")
        assert result == "Result: test"
    
    def test_do_something_with_empty_input(self):
        """Test with empty input."""
        cap = NewCapability()
        result = cap.do_something("")
        assert result == "Result: "
```

### 3. Updating the Server to Support New Methods

```python
# In src/mcp/server/__init__.py, add to MCPServer.__init__:

self._methods["mcp.newMethod"] = self.handle_new_method

# Add the handler method:
async def handle_new_method(
    self, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handler for mcp.newMethod.
    
    Args:
        params: Method parameters.
        
    Returns:
        Method result.
    """
    # Implementation here
    return {"status": "ok"}
```

## Common Tasks

### Task 1: Add a New Tool to the Registry

```python
from src.mcp.server import Tool, ToolRegistry

# Create registry
registry = ToolRegistry()

# Register a tool
tool = Tool(
    name="my_tool",
    description="Does something useful"
)
registry.register(tool)
```

### Task 2: Implement Rate Limiting

```python
from src.mcp.rate_limit import TokenBucketRateLimiter

# Create limiter
limiter = TokenBucketRateLimiter(
    rate=10.0,  # 10 requests per second
    capacity=20  # Burst capacity
)

# Check rate limit
if limiter.acquire():
    # Proceed with request
    pass
else:
    # Rate limited
    raise Exception("Rate limit exceeded")
```

### Task 3: Add Observability

```python
from src.mcp.observability import get_mcp_metrics, get_tracer

# Record metrics
metrics = get_mcp_metrics()
metrics.record_request("mcp.listTools", duration_ms=15.5, status="success")

# Add tracing
tracer = get_tracer()
with tracer.trace("handle_request") as span:
    # Do work
    span.tags["method"] = "mcp.listTools"
```

### Task 4: Manage Server Lifecycle

```python
from src.mcp.lifecycle import get_lifecycle_manager, ServerState

# Get lifecycle manager
lifecycle = get_lifecycle_manager()

# Initialize and start
await lifecycle.initialize()
await lifecycle.start()

# Check health
health = lifecycle.get_health()
print(f"Healthy: {health.healthy}")

# Graceful shutdown
await lifecycle.shutdown(graceful=True)
```

## Testing Guidelines

### Required Test Coverage

Each MCP module should have:
1. Unit tests for all public methods
2. Edge case tests (empty input, None, invalid types)
3. Integration tests with other MCP components
4. Error handling tests

### Running Tests

```bash
# Run all MCP tests
pytest tests/mcp/ -v

# Run specific test file
pytest tests/mcp/test_lifecycle.py -v

# Run with coverage
pytest tests/mcp/ --cov=src/mcp --cov-report=html
```

## Verification Checklist

Before completing any MCP implementation:

- [ ] Module has docstrings for all public classes/methods
- [ ] Type hints are complete
- [ ] Unit tests cover 90%+ of code
- [ ] Integration tests verify end-to-end functionality
- [ ] Documentation is updated
- [ ] Imports verified with `python -c "from src.mcp.xxx import ..."`
- [ ] No syntax errors (verify with `python -m py_compile`)

## Related Resources

- [Copilot MCP Integration Guide](../../.github/Copilot_MCP_Integration.md)
- [Operational Runbook](../plans/operational_runbook.md)
- [Plan Status Dashboard](../plans/PLAN_STATUS_DASHBOARD.md)
