# MCP Observability

Observability is built around FastAPI middleware and JSON-RPC logging hooks.

## Metrics and logs
- HTTP prototype exposes `status` payload via `/mcp/v1/health`.
- Add Prometheus scraping by mounting `/metrics` (placeholder in `src/mcp/server/http.py` ready for instrumentation hooks).
- JSON-RPC server logs unknown notifications and transport errors via `logging`.

## Tracing hooks
- Wrap `InMemoryVectorStore.query` with tracing decorators when enabling OpenTelemetry; keep disabled by default to stay offline-first.

## Validation
- `python scripts/validate_mcp.py --run-http-smoke` exercises health and query endpoints.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_http_server.py -q` ensures health payload shape is stable.
