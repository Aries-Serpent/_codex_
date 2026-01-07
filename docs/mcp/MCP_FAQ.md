# MCP Frequently Asked Questions (FAQ)

> Generated: 2024-11-18  
> Author: Audit Team  
> Purpose: Common questions about MCP (Model Context Protocol) implementation

---

## General Questions

### What is MCP?

MCP (Model Context Protocol) is a standardized protocol for tool discovery, invocation, and lifecycle management. It provides a consistent interface for AI models to interact with external tools and services.

### Which MCP capabilities are implemented?

The `_codex_` repository implements 10 MCP capabilities:

1. **mcp-protocol-surface** - HTTP/JSON-RPC protocol endpoints
2. **mcp-schema-validation** - Pydantic models and OpenAPI schemas
3. **mcp-tooling-registry** - Tool registration and discovery
4. **mcp-authz-authn** - Authentication and authorization
5. **mcp-rate-limiting** - Request throttling and rate limits
6. **mcp-error-handling** - Structured error responses
7. **mcp-observability** - Logging, metrics, and tracing
8. **mcp-versioning-compat** - Protocol version negotiation
9. **mcp-multi-tenant** - Tenant isolation and multi-tenancy
10. **mcp-tools-integration** - ITA endpoint integration

### Where is the MCP server code located?

The MCP JSON-RPC server is implemented in `mcp/server/server.py`. Core modules are in the `mcp/` package.

### How do I run the MCP server?

```bash
# Start JSON-RPC server on stdio
python3 -m mcp.server.server

# Or test the server
python3 test_mcp_server.py
```

---

## Security Questions

### How does MCP handle authentication?

MCP uses API key authentication via the `X-API-Key` header. Credentials are hashed using SHA-256 for secure storage. See `mcp/auth.py` for implementation details.

```python
from mcp.auth import hash_credential, Principal

# Hash credential securely
hashed = hash_credential("api-key-123")

# Create principal from credential
principal = Principal.from_credential("api-key-123")
```

### What safeguards are in place?

MCP implements multiple security safeguards:

- **SHA-256 hashing** - All credentials and checksums use SHA-256
- **Checksum validation** - Configuration and tool integrity verified with checksums
- **RNG seeding** - Deterministic random number generation for reproducible tests
- **Rate limiting** - Token bucket algorithm prevents abuse (see `mcp-rate-limiting`)
- **Confirmation prompts** - Critical actions require confirmation
- **Offline mode** - Secure offline operation for auditing
- **Unauthorized handling** - Proper 401 responses for auth failures

See `mcp/safeguards.py` for the complete safeguard toolkit.

### How is rate limiting enforced?

Rate limiting uses a token bucket algorithm:

```python
from mcp.rate_limit import MCPRateLimiter

# Configure rate limiter: 5 requests/sec, burst of 20
limiter = MCPRateLimiter(rate=5.0, capacity=20)

# Check if request is allowed
if limiter.allow(principal_id, tool_name):
    # Process request
    pass
else:
    # Return RateLimitExceeded error
    raise RateLimitExceeded("Too many requests")
```

### How does multi-tenant isolation work?

Tenant isolation is enforced at multiple levels:

1. **Principal IDs** include tenant prefix: `tenant1:user123`
2. **Rate limiting** is per-tenant
3. **Resource quotas** are tenant-specific
4. **Data encryption** uses tenant-specific keys
5. **Audit logs** are tenant-scoped

```python
# Extract tenant from principal
def get_tenant_id(principal):
    return principal.principal_id.split(":")[0]
```

---

## Protocol Questions

### What protocol does MCP use?

MCP uses JSON-RPC 2.0 over HTTP or stdio. The protocol surface includes:

- `listTools` - Discover available tools
- `callTool` - Invoke a tool
- `negotiateVersion` - Negotiate protocol version

### How do I list available tools?

```python
# JSON-RPC request
{
  "jsonrpc": "2.0",
  "method": "listTools",
  "params": {},
  "id": 1
}

# Response
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {"name": "kb.search", "schema": {...}, "metadata": {...}},
      {"name": "repo.hygiene", "schema": {...}, "metadata": {...}}
    ]
  },
  "id": 1
}
```

### How do I call a tool?

```python
# JSON-RPC request
{
  "jsonrpc": "2.0",
  "method": "callTool",
  "params": {
    "name": "kb.search",
    "arguments": {"query": "mcp capabilities"}
  },
  "id": 2
}

# Response
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "result": {"matches": ["doc1", "doc2"]}
  },
  "id": 2
}
```

### What error codes does MCP use?

MCP defines standard error codes:

- `TOOL_NOT_FOUND` (404) - Requested tool doesn't exist
- `VALIDATION_ERROR` (400) - Invalid request parameters
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests
- `UNAUTHORIZED` (401) - Authentication failed
- `MCP_ERROR` (500) - Generic server error

```python
from mcp.errors import ToolNotFound, RateLimitExceeded, Unauthorized

# Raise specific errors
raise ToolNotFound("Tool 'xyz' not found")
raise RateLimitExceeded("Rate limit exceeded")
raise Unauthorized("Invalid API key")
```

---

## Integration Questions

### How do I register a new tool?

```python
from mcp.registry import MCPToolRegistry

registry = MCPToolRegistry()

# Define tool handler
def search_handler(params):
    query = params["query"]
    # Perform search
    return {"results": [...]}

# Register tool
registry.register_tool(
    "kb.search",
    handler=search_handler,
    schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    },
    metadata={
        "description": "Search knowledge base",
        "version": "1.0"
    }
)
```

### How do I integrate with ITA endpoints?

MCP tools can wrap ITA endpoints:

```python
import requests

def ita_tool_wrapper(params):
    response = requests.post(
        "http://localhost:8080/api/endpoint",
        json=params,
        headers={"X-API-Key": api_key}
    )
    return response.json()

registry.register_tool("ita.action", ita_tool_wrapper)
```

### How do I validate schemas?

Use Pydantic models for request/response validation:

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    results: list[str]
    count: int

# Validate request
request = SearchRequest(query="mcp", limit=5)

# Validate response
response = SearchResponse(results=["doc1"], count=1)
```

---

## Testing Questions

### Where are the MCP tests located?

All MCP tests are in `tests/mcp/`:

- `test_mcp_core_smoke.py` - Core functionality
- `test_auth.py` - Authentication
- `test_config.py` - Configuration
- `test_registry.py` - Tool registry
- `test_server.py` - JSON-RPC server
- `test_integration.py` - End-to-end workflows
- `test_observability.py` - Logging and metrics
- `test_protocol.py` - Protocol compliance
- `test_schema_validation.py` - Schema validation
- `test_tools_integration.py` - Tool integration
- `test_error_handling_extended.py` - Error handling
- `test_multi_tenant_extended.py` - Multi-tenancy
- `test_authz_authn_extended.py` - Auth extended tests

### How do I run the tests?

```bash
# Run all MCP tests
pytest tests/mcp/ -v

# Run specific test file
pytest tests/mcp/test_registry.py -v

# Run server verification
python3 test_mcp_server.py
```

### How do I test the audit pipeline?

```bash
# Run full audit
python scripts/space_traversal/audit_runner.py run

# Explain specific MCP capability
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting

# Check capability scores
python scripts/space_traversal/audit_runner.py diff
```

---

## Troubleshooting

### MCP server won't start

**Check:**
1. Python version (3.8+)
2. Required modules installed: `python3 -c "import mcp"`
3. Configuration file exists: `mcp/mcp.json`
4. Environment variables: `ITA_URL`, `ITA_API_KEY`

### Tools not showing in listTools

**Check:**
1. Tool registered in registry: `registry.list_tools()`
2. Server initialized correctly
3. mcp.json contains tool definitions

### Authentication failures

**Check:**
1. `X-API-Key` header present in request
2. API key is valid
3. MCPAuthenticator configured correctly
4. Check logs for Unauthorized errors

### Rate limiting errors

**Check:**
1. Rate limiter configuration: `rate`, `capacity`
2. Current usage per principal
3. Reset rate limiter if needed: `limiter.reset()`
4. Check for RateLimitExceeded errors in logs

### Checksum validation fails

**Check:**
1. Configuration file not modified
2. SHA-256 checksum matches expected
3. File encoding is UTF-8
4. No trailing whitespace or BOM

---

## Configuration

### Environment Variables

```bash
# ITA integration
export ITA_URL="http://localhost:8080"
export ITA_API_KEY="your-api-key"

# Offline mode
export MCP_OFFLINE="true"
export OFFLINE_MODE="true"

# Audit configuration
export AUDIT_DEPTH=4
```

### mcp.json Structure

```json
{
  "name": "mcp-server",
  "description": "MCP Server for _codex_",
  "tools": [
    {
      "name": "kb.search",
      "description": "Search knowledge base",
      "endpoint": "/api/kb/search"
    }
  ]
}
```

---

## Best Practices

### Security
- Always hash credentials with SHA-256
- Validate all input with schemas
- Use rate limiting for all endpoints
- Enable confirmation for destructive actions
- Run in offline mode for audits
- Verify checksums for configuration

### Performance
- Use connection pooling for ITA calls
- Cache tool metadata
- Set appropriate rate limits
- Monitor with observability tools

### Testing
- Write deterministic tests (no random data)
- Use RNG seeds for reproducibility
- Mock external dependencies
- Test all error paths
- Verify checksum validation

### Documentation
- Document all tools in metadata
- Include schema definitions
- Provide usage examples
- Keep FAQ updated

---

## Additional Resources

- **MCP Capabilities Reference**: `MCP_CAPABILITIES_REFERENCE.md`
- **Security Guide**: `MCP_SECURITY_GUIDE.md`
- **Developer Guide**: `MCP_DEVELOPER_GUIDE.md`
- **Implementation Summary**: `MCP_IMPLEMENTATION_SUMMARY.md`
- **100% Roadmap**: `MCP_100_PERCENT_ROADMAP.md`
- **Traversal Workflow**: `docs/Traversal_Workflow.md`
- **Usage Guide**: `docs/Usage_Guide.md`

---

## Contact

For questions or issues:
- Review audit results: `audit_artifacts/capabilities_scored.json`
- Check logs: `audit_run_manifest.json`
- Run explain: `audit_runner.py explain mcp-<capability>`
