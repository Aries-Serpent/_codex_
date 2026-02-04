# MCP Server (Future-Ready)

This directory contains a skeleton Model Context Protocol (MCP) server that will expose the same capabilities as the Internal
Tools API. Constraints to observe when implementing the full server:

- Copilot coding agents currently support tool invocations only.
- Avoid OAuth for remote MCP access; issue short-lived API keys and reuse the ITA security primitives.
- Mirror the OpenAPI contract to keep Codex, Copilot, and MCP clients aligned.

## HTTP prototype
- `src/mcp/server/http.py` exposes `/mcp/v1/health`, `/mcp/v1/query`, and `/mcp/v1/context` using FastAPI.
- Auth: API key header (`X-MCP-API-Key`) or Bearer token. Set `MCP_OFFLINE=true` to disable auth for local smoke tests.
- Rate limiting: placeholder hook ready for Durable Objects/Redis integration.
- Local validation: `python scripts/validate_mcp.py --run-http-smoke` or `pytest tests/mcp/test_http_server.py -q`.
