# Façade (FastAPI) — Cloud Run & Local Run Notes

Overview
- The MCP Façade exposes a JSON-RPC endpoint and health endpoints. It loads an adapter at startup via the `ADAPTER_CLASS` env var (defaults to the in-repo mock backend).

Configuration env vars
- ADAPTER_CLASS (optional): Python import path to adapter class (e.g. `src.mcp.backends.mock_backend.InMemoryMockBackend`).
- ENABLE_LIVE_TESTS: default "false". Must be set to "true" to allow any code path that would call live provider APIs.
- AUTH / RATE LIMIT:
  - DEV_API_KEY: sample dev key used by APIKeyAuthMiddleware (default `dev-key-1`).
  - RATE_LIMIT_RATE: tokens/second (default 5)
  - RATE_LIMIT_BURST: burst capacity (default 10)
- Tracing:
  - OTEL_EXPORTER_OTLP_ENDPOINT: if set and OTel packages present, OTel will attempt to export traces.

Local run (quick)
```bash
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn pytest
# Run the façade locally (loads mock backend by default)
uvicorn src.mcp.server.facade_fastapi:APP --host 127.0.0.1 --port 8080
```

Run unit tests (mocked)
```bash
. .venv/bin/activate
pip install -U pip
pip install pytest
pytest tests/mcp -q
```

Gated integration tests
- Integration tests that call live providers must be gated behind:
  - `ENABLE_LIVE_TESTS=true` AND repository secrets set (e.g., PINECONE_API_KEY).
- A template workflow exists: `.github/workflows/integration-gated.yml`.
- Do not enable this workflow until operational and security guards are reviewed.

Auth & rate-limit notes
- For local development the APIKeyAuthMiddleware reads `DEV_API_KEY`. Production should plug in a secrets manager.
- The RateLimitMiddleware is an in-memory scaffold — replace with Redis-backed implementation for multi-instance deployments.

Safety
- Live-provider calls must always check `src.mcp.server.safety_checks.live_tests_enabled()` before invoking network operations.

Notes for reviewers
- Ensure no provider secrets are present in this PR.
- Validate that tests run locally and in CI without network access.
