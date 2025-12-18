# Copilot Guidance: MCP Integration

> Generated: 2025-12-17 | Target Branch: main | Implementation Branch: copilot/continue-high-maturity-achievement

## Repository Context

High-maturity MLOps platform (75.2% Python) with MCP integration targeting **main** branch.

### MCP Capabilities (10 Total)

1. **mcp-protocol-surface** — JSON-RPC server (`src/mcp/server/`)
2. **mcp-schema-validation** — Config management (`src/mcp/config.py`)
3. **mcp-tooling-registry** — Tool discovery (`src/mcp/registry.py`)
4. **mcp-authz-authn** — Authentication/authorization (`src/mcp/auth.py`)
5. **mcp-rate-limiting** — Token bucket rate limiter (`src/mcp/rate_limit.py`)
6. **mcp-error-handling** — Error hierarchy (`src/mcp/errors.py`)
7. **mcp-lifecycle-management** — Server lifecycle (`src/mcp/lifecycle.py`)
8. **mcp-observability** — Metrics and tracing (`src/mcp/observability.py`)
9. **mcp-configuration** — Configuration validation (`src/mcp/config.py`)
10. **mcp-versioning-compat** — Protocol versioning (`src/mcp/versioning.py`)

## Integration Points

### Entry Points

```python
# Main MCP server entry
from src.mcp.server import MCPServer, Tool, ToolRegistry

# Configuration
from src.mcp.config import MCPConfig, load_config

# Authentication
from src.mcp.auth import MCPAuthenticator, APIKeyAuth, JWTAuth

# Rate limiting
from src.mcp.rate_limit import TokenBucketRateLimiter
```

### Transport Layer

The MCP server supports stdio transport for Copilot integration:

```python
from src.mcp.server.stdio import StdioTransport
from src.mcp.server.json_rpc import JsonRpcHandler
```

### Configuration

```yaml
# mcp-config.yaml
mcp:
  version: "1.0"
  server:
    name: "codex-mcp"
    transport: "stdio"
  auth:
    type: "api_key"
    header: "X-API-Key"
  rate_limit:
    requests_per_minute: 60
    burst_size: 10
```

## Testing

All MCP capabilities have comprehensive test coverage:

```bash
# Run MCP tests
pytest tests/mcp/ -v

# Run specific capability tests
pytest tests/mcp/test_server.py -v
pytest tests/mcp/test_auth.py -v
pytest tests/mcp/test_lifecycle.py -v
```

## Maturity Status

All 10 MCP capabilities are at HIGH maturity (≥0.85 score):

| Capability | Score | Status |
|------------|-------|--------|
| mcp-protocol-surface | 1.0+ | ✅ HIGH |
| mcp-schema-validation | 1.0+ | ✅ HIGH |
| mcp-tooling-registry | 1.0+ | ✅ HIGH |
| mcp-authz-authn | 1.0+ | ✅ HIGH |
| mcp-rate-limiting | 1.0+ | ✅ HIGH |
| mcp-error-handling | 1.0+ | ✅ HIGH |
| mcp-lifecycle-management | 1.0+ | ✅ HIGH |
| mcp-observability | 1.0+ | ✅ HIGH |
| mcp-configuration | 1.0+ | ✅ HIGH |
| mcp-versioning-compat | 1.0+ | ✅ HIGH |

## Related Documentation

- [MCP Server README](../src/mcp/server/README.md)
- [Operational Runbook](../docs/plans/operational_runbook.md)
- [Plan Status Dashboard](../docs/plans/PLAN_STATUS_DASHBOARD.md)
