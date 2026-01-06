# MCP Developer Guide

**Version:** 1.0  
**Last Updated:** Previous Cycle-11-18  
**Audience:** Developers implementing MCP tools and integrations

## Getting Started with MCP

The Model Context Protocol (MCP) provides a standardized way to register, discover, and invoke tools in the `_codex_` system. This guide covers all 10 mcp capabilities and how to use them effectively.

### Prerequisites

```bash
# Install repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install dependencies
pip install -e .

# Verify MCP modules
python3 -c "
try:
    import mcp
    print('✅ MCP modules loaded successfully')
except ImportError as e:
    print(f'❌ MCP modules not available: {e}')
    print('   Run: pip install -e . to install')
"
```

### Quick Start

```python
# Safe import pattern with error handling
try:
    from mcp.config import MCPConfig
    from mcp.registry import MCPToolRegistry
    from mcp.server.server import MCPJSONRPCServer
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"MCP modules not available: {e}")
    print("Install with: pip install -e .")

if MCP_AVAILABLE:
    # Load MCP configuration
    config = MCPConfig.load()

    # Initialize tool registry
    registry = MCPToolRegistry()

    # Create JSON-RPC server
    server = MCPJSONRPCServer(config, registry=registry)

print(f"MCP server ready with {len(registry.list_tools())} tools")
```

---

## Tool Registry (mcp-tooling-registry)

The `mcp-tooling-registry` capability provides tool management through MCPToolRegistry.

### Registering Tools

**Basic Tool Registration**:
```python
from mcp.registry import MCPToolRegistry

registry = MCPToolRegistry()

def hello_world(name: str) -> str:
    """Simple hello world tool."""
    return f"Hello, {name}!"

# Register the tool
registry.register_tool(
    name="hello_world",
    handler=hello_world,
    metadata={
        "description": "Greets the user",
        "version": "1.0.0",
        "category": "greeting"
    }
)
```

**Tool with Schema**:
```python
# Define JSON schema for parameters
schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Name to greet",
            "minLength": 1,
            "maxLength": 100
        }
    },
    "required": ["name"]
}

registry.register_tool(
    name="hello_world",
    handler=hello_world,
    schema=schema,
    metadata={"description": "Greets the user with validation"}
)
```

### Discovering Tools

**List All Tools**:
```python
# Get list of registered tools
tools = registry.list_tools()

for tool in tools:
    print(f"Tool: {tool['name']}")
    print(f"  Description: {tool['metadata'].get('description', 'N/A')}")
    print(f"  Version: {tool['metadata'].get('version', 'N/A')}")
```

**Filter Tools by Category**:
```python
# Find tools in a specific category
data_tools = [
    tool for tool in registry.list_tools()
    if tool['metadata'].get('category') == 'data'
]
```

### Invoking Tools

**Direct Invocation**:
```python
# Get tool handler
handler = registry.get_tool("hello_world")

# Invoke with parameters
result = handler(name="Alice")
print(result)  # "Hello, Alice!"
```

**Safe Invocation with Error Handling**:
```python
from mcp.errors import ToolNotFound, ToolExecutionError

try:
    handler = registry.get_tool("my_tool")
    if handler is None:
        raise ToolNotFound(f"Tool 'my_tool' not found")
    
    result = handler(param1="value")
except ToolNotFound as e:
    print(f"Tool not found: {e}")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
```

---

## Protocol Surface (mcp-protocol-surface)

The `mcp-protocol-surface` capability implements JSON-RPC 2.0 for MCP.

### JSON-RPC Server

**Initialize Server**:
```python
from mcp.server.server import MCPJSONRPCServer
from mcp.config import MCPConfig

config = MCPConfig.load()
server = MCPJSONRPCServer(config)

# Server handles three main methods:
# - listTools: List available tools
# - callTool: Invoke a specific tool
# - negotiateVersion: Agree on MCP protocol version
```

### JSON-RPC Requests

**listTools Method**:
```python
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "listTools",
    "params": {}
}

response = server.handle_request(request)
# Returns: {
#   "jsonrpc": "2.0",
#   "id": 1,
#   "result": [{"name": "tool1", ...}, ...]
# }
```

**callTool Method**:
```python
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "callTool",
    "params": {
        "name": "hello_world",
        "params": {"name": "Bob"}
    }
}

response = server.handle_request(request)
# Returns: {
#   "jsonrpc": "2.0",
#   "id": 2,
#   "result": "Hello, Bob!"
# }
```

**negotiateVersion Method**:
```python
request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "negotiateVersion",
    "params": {
        "versions": ["1.0", "2.0"]
    }
}

response = server.handle_request(request)
# Returns: {
#   "jsonrpc": "2.0",
#   "id": 3,
#   "result": "1.0"  # Highest compatible version
# }
```

### Error Responses

```python
# Tool not found error
{
    "jsonrpc": "2.0",
    "id": 4,
    "error": {
        "code": -32601,  # Method not found (tool not found)
        "message": "Tool 'nonexistent' not found",
        "data": {"http_status": 404}
    }
}
```

---

## Schema Validation (mcp-schema-validation)

The `mcp-schema-validation` capability validates tool inputs using JSON schemas.

### Defining Schemas

**JSON Schema for Tool Parameters**:
```python
tool_schema = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_-]+$",
            "minLength": 3,
            "maxLength": 50
        },
        "action": {
            "type": "string",
            "enum": ["create", "update", "delete"]
        },
        "data": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name"]
        }
    },
    "required": ["user_id", "action"]
}
```

**Using Pydantic Models**:
```python
from pydantic import BaseModel, EmailStr, Field

class UserAction(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    action: str = Field(..., pattern="^(create|update|delete)$")
    name: str
    email: EmailStr

def process_user_action(user_id: str, action: str, name: str, email: str):
    # Validate with Pydantic
    validated = UserAction(
        user_id=user_id,
        action=action,
        name=name,
        email=email
    )
    # Process validated data
    return f"Processed {validated.action} for {validated.user_id}"

registry.register_tool("process_user", process_user_action, schema=tool_schema)
```

### Validation Errors

```python
from mcp.errors import ValidationError

try:
    # Invalid email format
    result = process_user_action("user123", "create", "Bob", "invalid-email")
except ValidationError as e:
    print(f"Validation failed: {e}")
    # HTTP 400 Bad Request
```

---

## Versioning & Compatibility (mcp-versioning-compat)

The `mcp-versioning-compat` capability ensures protocol compatibility.

### Version Negotiation

```python
from mcp.versioning import MCP_VERSIONS, negotiate_version

# Server supports these versions
print(f"Supported versions: {MCP_VERSIONS}")  # ["1.0"]

# Client requests compatible version
client_versions = ["0.9", "1.0", "1.1"]
negotiated = negotiate_version(client_versions)
print(f"Negotiated version: {negotiated}")  # "1.0"
```

### Version Mismatch Handling

```python
from mcp.errors import VersionMismatchError

try:
    # Client only supports incompatible versions
    version = negotiate_version(["0.5", "0.9"])
except VersionMismatchError as e:
    print(f"Version mismatch: {e}")
    # HTTP 400 Bad Request
```

### Backward Compatibility

```python
# Check if a feature is supported in negotiated version
def is_feature_supported(version: str, feature: str) -> bool:
    feature_matrix = {
        "1.0": ["listTools", "callTool", "negotiateVersion"],
        "2.0": ["listTools", "callTool", "negotiateVersion", "streaming"]
    }
    return feature in feature_matrix.get(version, [])
```

---

## Observability (mcp-observability)

The `mcp-observability` capability provides logging, metrics, and tracing.

### Logging Setup

```python
import logging

# Configure MCP logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp')

# Log tool invocations
logger.info("Tool invoked", extra={
    "tool_name": "hello_world",
    "principal_id": "user123",
    "request_id": "req-abc-123"
})
```

### Request Tracing

```python
import uuid

def process_with_tracing(tool_name: str, params: dict):
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    logger.info(f"Starting request {request_id}", extra={
        "request_id": request_id,
        "tool_name": tool_name
    })
    
    try:
        result = execute_tool(tool_name, params)
        logger.info(f"Request {request_id} succeeded")
        return result
    except Exception as e:
        logger.error(f"Request {request_id} failed", exc_info=True)
        raise
```

### Metrics Collection

```python
# Track MCP metrics
mcp_metrics = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "response_times": []
}

import time

def execute_with_metrics(tool_name: str):
    mcp_metrics["requests_total"] += 1
    start_time = time.time()
    
    try:
        result = execute_tool(tool_name)
        mcp_metrics["requests_successful"] += 1
        return result
    except Exception:
        mcp_metrics["requests_failed"] += 1
        raise
    finally:
        elapsed = (time.time() - start_time) * 1000
        mcp_metrics["response_times"].append(elapsed)
```

### Health Checks

```python
def mcp_health_check():
    """Check MCP system health."""
    return {
        "status": "healthy",
        "checks": {
            "registry": "ok" if registry else "error",
            "server": "ok" if server else "error",
            "mcp_version": MCP_VERSIONS[0]
        }
    }
```

---

## Tools Integration (mcp-tools-integration)

The `mcp-tools-integration` capability connects MCP tools to ITA endpoints.

### Configuration

**mcp.json**:
```json
{
    "name": "codex-mcp-server",
    "description": "MCP server for codex tools",
    "tools": [
        {
            "name": "kb.search",
            "description": "Search knowledge base",
            "endpoint": "/kb/search",
            "method": "POST"
        },
        {
            "name": "repo.hygiene",
            "description": "Run repository hygiene checks",
            "endpoint": "/repo/hygiene",
            "method": "POST"
        }
    ]
}
```

### Loading Configuration

```python
from mcp.config import MCPConfig

config = MCPConfig.load()

print(f"MCP Server: {config.name}")
print(f"ITA URL: {config.ita_url}")
print(f"Tools configured: {len(config.tools)}")

for tool in config.tools:
    print(f"  - {tool.name}: {tool.endpoint}")
```

### ITA Endpoint Integration

```python
import requests

def call_ita_endpoint(tool_name: str, params: dict):
    # Get tool configuration
    tool_def = config.get_tool(tool_name)
    if not tool_def:
        raise ToolNotFound(f"Tool {tool_name} not configured")
    
    # Build full URL
    url = f"{config.ita_url}{tool_def.endpoint}"
    
    # Make request with authentication
    headers = {}
    if config.ita_api_key:
        headers["X-API-Key"] = config.ita_api_key
    
    response = requests.post(url, json=params, headers=headers)
    response.raise_for_status()
    
    return response.json()
```

---

## Best Practices

### 1. Always Use Type Hints

```python
from typing import Dict, Any

def my_tool(user_id: str, data: Dict[str, Any]) -> Dict[str, str]:
    """Process user data."""
    return {"status": "success", "user_id": user_id}
```

### 2. Include Comprehensive Metadata

```python
registry.register_tool(
    name="my_tool",
    handler=my_tool,
    schema={...},
    metadata={
        "description": "Detailed description of what the tool does",
        "version": "1.0.0",
        "category": "data_processing",
        "author": "Your Name",
        "tags": ["data", "processing", "mcp"],
        "examples": [
            {"input": {"user_id": "123"}, "output": {...}}
        ]
    }
```

### 3. Implement Error Handling

```python
from mcp.errors import MCPError, ToolExecutionError

def safe_tool_execution(tool_name: str, params: dict):
    try:
        handler = registry.get_tool(tool_name)
        if not handler:
            raise ToolNotFound(f"Tool '{tool_name}' not found")
        
        return handler(**params)
    except MCPError:
        # Re-raise MCP errors as-is
        raise
    except Exception as e:
        # Wrap other exceptions
        raise ToolExecutionError(f"Execution failed: {str(e)}")
```

### 4. Use Logging Consistently

```python
logger = logging.getLogger('mcp.tools')

def logged_tool_execution(tool_name: str):
    logger.info(f"Executing tool: {tool_name}")
    try:
        result = execute_tool(tool_name)
        logger.info(f"Tool {tool_name} succeeded")
        return result
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
        raise
```

### 5. Validate Inputs

```python
def validate_and_execute(tool_name: str, params: dict):
    # Validate tool exists
    if tool_name not in [t["name"] for t in registry.list_tools()]:
        raise ToolNotFound(f"Unknown tool: {tool_name}")
    
    # Validate parameters (use schema validation)
    # Execute tool
    return execute_tool(tool_name, params)
```

---

## Testing MCP Tools

### Unit Testing

```python
import pytest
from mcp.registry import MCPToolRegistry

def test_tool_registration():
    """Test that tools can be registered."""
    registry = MCPToolRegistry()
    
    def test_tool():
        return "test"
    
    registry.register_tool("test", test_tool)
    
    tools = registry.list_tools()
    assert any(t["name"] == "test" for t in tools)

def test_tool_execution():
    """Test that tools can be executed."""
    registry = MCPToolRegistry()
    
    def add(a: int, b: int) -> int:
        return a + b
    
    registry.register_tool("add", add)
    
    result = registry.get_tool("add")(5, 3)
    assert result == 8
```

### Integration Testing

```bash
# Run MCP server tests
python3 test_mcp_server.py

# Run all MCP tests
pytest tests/mcp/ -v

# Run specific capability tests
pytest tests/mcp/test_registry.py -v
pytest tests/mcp/test_protocol.py -v
pytest tests/mcp/test_integration.py -v
```

---

## Troubleshooting

### Common Issues

**Tool Not Found**:
```python
# Problem: Tool not registered
# Solution: Check tool name and registration
tools = registry.list_tools()
print(f"Registered tools: {[t['name'] for t in tools]}")
```

**Validation Errors**:
```python
# Problem: Invalid parameters
# Solution: Check schema and fix parameters
from mcp.errors import ValidationError
try:
    execute_tool(params)
except ValidationError as e:
    print(f"Fix these validation errors: {e}")
```

**Version Mismatch**:
```python
# Problem: Client/server version incompatibility
# Solution: Negotiate compatible version
from mcp.versioning import MCP_VERSIONS
print(f"Server supports: {MCP_VERSIONS}")
```

---

## Next Steps

1. Read [MCP Capabilities Reference](MCP_CAPABILITIES_REFERENCE.md)
2. Review [MCP Security Guide](MCP_SECURITY_GUIDE.md)
3. Explore MCP Implementation Summary <!-- TODO: MCP_IMPLEMENTATION_SUMMARY.md to be created -->
4. Check API Documentation <!-- TODO: docs/API.md to be created -->
5. Run the audit: `python scripts/space_traversal/audit_runner.py run`

## Additional Resources

- Usage Guide <!-- TODO: docs/Usage_Guide.md to be created -->
- Traversal Workflow <!-- TODO: docs/Traversal_Workflow.md to be created -->
- Test Examples <!-- TODO: tests/mcp/ directory to be created with examples -->
- [MCP Server Implementation](mcp/server/server.py)
- [Tool Registry](mcp/registry.py)
