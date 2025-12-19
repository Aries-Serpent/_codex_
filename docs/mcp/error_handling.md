# MCP Error Handling

The MCP server aligns JSON-RPC errors with clear codes and messages.

## JSON-RPC behavior
- Invalid request → `-32600`
- Method not found → `-32601`
- Invalid params → `-32602`
- Internal error → `-32603`

Handlers return structured errors via `JsonRpcError` (`src/mcp/server/__init__.py`) and raise `HTTPException` for HTTP endpoints (`src/mcp/server/http.py`).

## HTTP prototype
- Auth failure: `401 Unauthorized`
- Rate limit breach: `429 Too Many Requests` (placeholder hook ready)
- Validation error: `422 Unprocessable Entity` (pydantic-driven)

## Verification
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_http_server.py -q`
- `python scripts/validate_mcp.py --run-http-smoke`
