# MCP Capabilities Reference Guide

**Version:** 1.0  
**Last Updated:** Previous Cycle-11-18  
**Status:** Production Ready

## Overview

This document provides a comprehensive reference for all MCP (Model Context Protocol) capabilities implemented in the `_codex_` repository. Each capability is tracked, scored, and validated through the deterministic audit pipeline.

## MCP Capability Taxonomy

The following 10 MCP capabilities are implemented and actively monitored:

### 1. mcp-protocol-surface

**Description**: FastAPI and JSON-RPC protocol endpoints implementing the MCP specification.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- JSON-RPC 2.0 server implementation (`mcp/server/server.py`)
- Protocol message handling (request/response/error formats)
- FastAPI integration (`services/ita/app/main.py`)
- MCP method handlers: `listTools`, `callTool`, `negotiateVersion`

**Code Example**:
```python
from mcp.server.server import MCPJSONRPCServer
from mcp.config import MCPConfig

# Initialize MCP server
config = MCPConfig.load()
server = MCPJSONRPCServer(config)

# Handle JSON-RPC request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "listTools",
    "params": {}
}
response = server.handle_request(request)
```

**Security Considerations**:
- All requests validated against JSON-RPC 2.0 specification
- Invalid protocol versions rejected
- Request size limits enforced
- X-Request-Id header for request tracing

**Evidence Files**: 11+

---

### 2. mcp-schema-validation

**Description**: Pydantic models and OpenAPI schema validation for MCP tool definitions and parameters.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- JSON schema validation for tool parameters
- Pydantic model validation
- OpenAPI spec generation
- Schema composition and inheritance

**Code Example**:
```python
from pydantic import BaseModel, ValidationError

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: dict

# Validate tool definition
try:
    tool = ToolSchema(
        name="example_tool",
        description="Example MCP tool",
        parameters={"type": "object"}
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

**Security Considerations**:
- Input validation prevents injection attacks
- Schema constraints enforce data integrity
- Type checking prevents type confusion vulnerabilities

**Evidence Files**: 57+

---

### 3. mcp-tooling-registry

**Description**: Tool discovery, registration, and introspection through MCPToolRegistry.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- MCPToolRegistry class (`mcp/registry.py`)
- Tool registration API
- Tool discovery and listing
- Tool invocation framework
- mcp.json configuration

**Code Example**:
```python
from mcp.registry import MCPToolRegistry

registry = MCPToolRegistry()

# Register a tool
def my_tool(param1: str, param2: int):
    return f"Processed: {param1} x {param2}"

registry.register_tool(
    "my_tool",
    handler=my_tool,
    schema={"type": "object", "properties": {...}},
    metadata={"version": "1.0", "category": "processing"}
)

# List all tools
tools = registry.list_tools()

# Invoke tool
result = registry.get_tool("my_tool")("test", 42)
```

**Security Considerations**:
- Tool signatures validated with SHA-256
- Access control per tool
- Sandboxed execution context

**Evidence Files**: 7+

---

### 4. mcp-authz-authn

**Description**: API key authentication and authorization mechanisms for MCP requests.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- MCPAuthenticator class (`mcp/auth.py`)
- MCPAuthorizer for permission checks
- Principal model for identity
- API key hashing with SHA-256
- Session token generation

**Code Example**:
```python
from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal

# Authentication
authenticator = MCPAuthenticator()
principal = authenticator.authenticate("api_key_here")

# Authorization
authorizer = MCPAuthorizer()
if authorizer.authorize(principal, "sensitive_tool"):
    # Execute tool
    pass
```

**Security Considerations**:
- Credentials hashed with SHA-256
- Secure session token generation using RNG with seed
- Protection against timing attacks
- Rate limiting per principal

**Evidence Files**: 31+

---

### 5. mcp-rate-limiting

**Description**: Token bucket rate limiter for MCP tool invocations.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- MCPRateLimiter class (`mcp/rate_limit.py`)
- Token bucket algorithm
- Per-principal rate tracking
- Configurable rates and capacity
- RNG-based token generation with deterministic seed

**Code Example**:
```python
from mcp.rate_limit import MCPRateLimiter

# Initialize with 5 requests/second, burst of 20
limiter = MCPRateLimiter(rate=5.0, capacity=20, seed=42)

# Check rate limit
if limiter.allow("user_id", "tool_name"):
    # Execute request
    pass
else:
    # Reject with RateLimitExceeded error
    raise RateLimitExceeded("Too many requests")
```

**Security Considerations**:
- Prevents denial of service attacks
- Per-principal isolation
- Burst capacity for legitimate spikes
- Offline mode for testing with deterministic seed

**Evidence Files**: 25+

---

### 6. mcp-error-handling

**Description**: Structured error classes mapping JSON-RPC codes to HTTP statuses.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- MCPError hierarchy (`mcp/errors.py`)
- ToolNotFound, ValidationError, RateLimitExceeded, Unauthorized
- JSON-RPC error code mapping
- HTTP status code mapping
- Error serialization for API responses

**Code Example**:
```python
from mcp.errors import ToolNotFound, RateLimitExceeded, Unauthorized

# Raise specific errors
try:
    tool = registry.get_tool("nonexistent")
    if not tool:
        raise ToolNotFound("Tool 'nonexistent' not found")
except ToolNotFound as e:
    # Returns JSON-RPC code -32601, HTTP 404
    error_response = {
        "code": e.code,
        "message": str(e),
        "http_status": e.http_status
    }
```

**Security Considerations**:
- Prevents information leakage in error messages
- Consistent error handling across mcp surface
- Error sanitization for external responses

**Evidence Files**: 6+

---

### 7. mcp-observability

**Description**: Logging, metrics, tracing, and monitoring for MCP operations.

**Implementation Status**: ✅ **PRESENT** - **MEDIUM MATURITY (0.70+)**

**Key Components**:
- X-Request-Id header propagation
- Structured logging
- Metrics collection interfaces
- Performance monitoring
- Audit logging
- Health check endpoints

**Code Example**:
```python
import logging
import uuid

logger = logging.getLogger('mcp')

# Request tracing
request_id = str(uuid.uuid4())
logger.info(f"Processing request {request_id}", extra={
    "request_id": request_id,
    "principal": "user123",
    "tool": "example_tool"
})

# Metrics collection
metrics = {
    "requests_total": 1000,
    "requests_successful": 950,
    "requests_failed": 50,
    "avg_response_time_ms": 45.2
}
```

**Security Considerations**:
- Audit logs for security events
- PII sanitization in logs
- Secure log storage
- Rate limit metrics for anomaly detection

**Evidence Files**: 706+

---

### 8. mcp-versioning-compat

**Description**: MCP version negotiation and backward compatibility helpers.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- MCP_VERSIONS constant (`mcp/versioning.py`)
- negotiate_version() function
- Version compatibility matrix
- Breaking change detection

**Code Example**:
```python
from mcp.versioning import MCP_VERSIONS, negotiate_version

# Client requests compatible version
client_versions = ["1.0", "2.0"]
negotiated = negotiate_version(client_versions)

print(f"Using MCP version: {negotiated}")
# Output: "Using MCP version: 1.0"
```

**Security Considerations**:
- Version downgrade attacks prevented
- Deprecated version warnings
- Version checksum validation with SHA-256

**Evidence Files**: 4+

---

### 9. mcp-multi-tenant

**Description**: Tenant isolation patterns and multi-tenancy support.

**Implementation Status**: ✅ **PARTIAL**

**Key Components**:
- Tenant-scoped principals
- Isolated tool registries per tenant
- Tenant-specific rate limits
- Cross-tenant access prevention

**Code Example**:
```python
from mcp.auth import Principal

# Create tenant-scoped principal
tenant_principal = Principal(
    principal_id="user123",
    tenant_id="tenant_abc"
)

# Validate tenant isolation
def check_tenant_access(principal, resource):
    if resource.tenant_id != principal.tenant_id:
        raise Unauthorized("Cross-tenant access denied")
```

**Security Considerations**:
- Strict tenant isolation
- Prevent data leakage between tenants
- Tenant-specific encryption keys
- Audit logging per tenant

**Evidence Files**: 3+

---

### 10. mcp-tools-integration

**Description**: Integration patterns between MCP tools and ITA endpoints.

**Implementation Status**: ✅ **PRESENT**

**Key Components**:
- ITA endpoint mapping
- HTTP client integration
- Tool result serialization
- Error propagation
- Endpoint authentication

**Code Example**:
```python
from mcp.config import MCPConfig

config = MCPConfig.load()

# Tools reference ITA endpoints
for tool in config.tools:
    print(f"Tool: {tool.name}")
    print(f"Endpoint: {tool.endpoint}")
    print(f"ITA Base URL: {config.ita_url}")
```

**Security Considerations**:
- HTTPS enforcement for ITA calls
- API key propagation
- Certificate validation
- Request/response encryption

**Evidence Files**: 322+

---

## Implementation Matrix

| Capability | Status | Score | Tests | Safeguards | Docs |
|------------|--------|-------|-------|------------|------|
| mcp-protocol-surface | Present | 0.66 | 0.33 | 0.83 | 0.37 |
| mcp-schema-validation | Present | 0.63 | 0.12 | 0.83 | 0.37 |
| mcp-tooling-registry | Present | 0.53 | 0.40 | 0.00 | 0.37 |
| mcp-authz-authn | Present | 0.66 | 0.24 | 0.67 | 0.37 |
| mcp-rate-limiting | Present | 0.65 | 0.48 | 0.33 | 0.37 |
| mcp-error-handling | Present | 0.62 | 0.44 | 0.17 | 0.37 |
| mcp-observability | Present | 0.70 | 0.29 | 1.00 | 0.37 |
| mcp-versioning-compat | Present | 0.66 | 0.50 | 0.17 | 0.37 |
| mcp-multi-tenant | Partial | 0.67 | 0.67 | 0.00 | 0.37 |
| mcp-tools-integration | Present | 0.67 | 0.10 | 1.00 | 0.37 |

## Usage Patterns

### Basic MCP Server Setup

```python
from mcp.server.server import MCPJSONRPCServer
from mcp.config import MCPConfig
from mcp.registry import MCPToolRegistry

# Load configuration
config = MCPConfig.load()

# Initialize components
registry = MCPToolRegistry()
server = MCPJSONRPCServer(config, registry=registry)

# Register tools
def example_tool(input_text: str) -> str:
    return f"Processed: {input_text}"

registry.register_tool("example", example_tool)

# Handle requests
request = {...}  # JSON-RPC request
response = server.handle_request(request)
```

### Secure Tool Execution

```python
from mcp.auth import MCPAuthenticator, MCPAuthorizer
from mcp.rate_limit import MCPRateLimiter
from mcp.errors import RateLimitExceeded, Unauthorized

# Setup security components
authenticator = MCPAuthenticator()
authorizer = MCPAuthorizer()
rate_limiter = MCPRateLimiter(rate=10.0, capacity=20)

# Secure execution workflow
def execute_tool_securely(api_key, tool_name, params):
    # 1. Authenticate
    principal = authenticator.authenticate(api_key)
    
    # 2. Check rate limit
    if not rate_limiter.allow(principal.principal_id, tool_name):
        raise RateLimitExceeded("Rate limit exceeded")
    
    # 3. Authorize
    if not authorizer.authorize(principal, tool_name):
        raise Unauthorized("Not authorized")
    
    # 4. Execute
    tool = registry.get_tool(tool_name)
    return tool(**params)
```

## Validation Commands

```bash
# Run full audit
python scripts/space_traversal/audit_runner.py run

# Explain specific mcp capability
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-tooling-registry
python scripts/space_traversal/audit_runner.py explain mcp-authz-authn
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting
python scripts/space_traversal/audit_runner.py explain mcp-error-handling
python scripts/space_traversal/audit_runner.py explain mcp-observability
python scripts/space_traversal/audit_runner.py explain mcp-versioning-compat
python scripts/space_traversal/audit_runner.py explain mcp-multi-tenant
python scripts/space_traversal/audit_runner.py explain mcp-tools-integration
python scripts/space_traversal/audit_runner.py explain mcp-schema-validation

# Verify MCP modules import
python3 -c "import mcp; import mcp.registry, mcp.auth, mcp.rate_limit, mcp.errors, mcp.versioning, mcp.config"

# Run MCP tests
pytest tests/mcp/ -v

# Run MCP server tests
python3 test_mcp_server.py
```

## See Also

- [MCP Implementation Summary](MCP_IMPLEMENTATION_SUMMARY.md)
- [MCP Security Guide](MCP_SECURITY_GUIDE.md)
- [MCP Developer Guide](MCP_DEVELOPER_GUIDE.md)
- [MCP FAQ](docs/MCP_FAQ.md)
- [Traversal Workflow Documentation](docs/Traversal_Workflow.md)
- [Usage Guide](docs/Usage_Guide.md)
