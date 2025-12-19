# MCP Version Negotiation

The server prefers MCP protocol version **1.0** and negotiates via `mcp.negotiateVersion` in the JSON-RPC surface.

## Flow
1. Client sends `supported` array (e.g., `["0.9", "1.0"]`).
2. Server picks the first overlapping version based on server preference order (`["1.0"]`).
3. If no overlap exists, server returns JSON-RPC error `-32602`.

## Tests
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_server.py -q`
- `python scripts/validate_mcp.py --check-capability-map` (ensures docs + tests mapped)
