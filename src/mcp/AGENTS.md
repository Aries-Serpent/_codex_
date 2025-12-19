# AGENTS — MCP Package Notes

Scope: src/mcp/**

## MCP Server
- FastAPI app is defined in `src/mcp/server/facade_fastapi.py` and must remain import-safe.
- Use `src/mcp/server/run.py` to start the server. Avoid calling `uvicorn.run` at import time.
- Health endpoints are registered via `register_health_routes` in `src/mcp/server/routes_health.py`.
- JSON-RPC routes are registered via `register_jsonrpc_routes` in `src/mcp/server/jsonrpc_adapter.py`.

## Adapter Loading
- `src/mcp/server/adapter_loader.py` provides lazy adapter loading with a mock fallback.
- When extending adapters, avoid network calls on import; connect in `lazy_connect_all` only.

## Packager
- The MCP packager lives in `src/mcp/packager/` and uses `docs/mcp_packager_template.yaml` for config.
- Keep templates deterministic and mock-first. Avoid adding heavy dependencies to the generator.

## Testing
- MCP tests are under `tests/mcp/` and should pass with mock-only defaults.
- Reset rate-limit state with `clear_buckets()` from `src/mcp/middleware/rate_limit_middleware.py` in tests.
