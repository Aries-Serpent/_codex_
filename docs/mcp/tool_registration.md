# MCP Tool Registration

The MCP server exposes tools via the in-memory `ToolRegistry` (`src/mcp/server/__init__.py`). Each tool stores a name and description; future iterations can add parameter schemas.

## Registering tools (Python/FastAPI)
```python
from mcp.server import MCPServer, Tool, ToolRegistry

registry = ToolRegistry()
registry.register(Tool(name="search", description="Run vector search"))
registry.register(Tool(name="context", description="Push or fetch context"))
server = MCPServer(tool_registry=registry)
```

## Registering tools (Node/Workers prototype)
For Cloudflare Workers, expose a `listTools` JSON-RPC response containing `{ "tools": [...] }` that mirrors the Python registry and aligns with `docs/mcp/api_schema.md`.

## Tests to run
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_server.py -q` (JSON-RPC registry behavior)
- `python scripts/validate_mcp.py --check-capability-map` (ensures registry docs/tests are mapped)
