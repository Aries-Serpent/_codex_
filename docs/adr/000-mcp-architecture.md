# ADR 000: MCP Architecture & Hosting

## Status
Accepted (preview ready)

## Context
The Codex MCP stack needs a low-cost, reviewable path for Copilot Agents while remaining production-ready. The repo disallows new GitHub Actions by default, so deployment must rely on external triggers or manual flows.

## Decision
- **Runtime**: Python/FastAPI prototype (`src/mcp/server/http.py`) with JSON-RPC compatibility retained in `src/mcp/server/__init__.py`.
- **Edge option**: Node/TypeScript Worker sketch for Cloudflare Workers to mirror the FastAPI schema.
- **Hosting**: Cloudflare Workers for stateless previews; Fly.io for persistent containers and background embedding workers.
- **Data**: In-memory vector store for dev; Chroma container for local compose; external vector DB (Supabase/Pinecone) for production evaluation.
- **Config**: Copilot Spaces config stored at `.copilot-space/mcp.example.json`; capability map updated for MCP coverage.

## Consequences
- Fast local validation via `python scripts/validate_mcp.py --run-http-smoke` and `pytest tests/mcp/test_http_server.py -q`.
- Clear upgrade path to managed vector DBs without changing HTTP schema.
- Edge deployments must keep payloads JSON-only and avoid long-running connections.

## Follow-up
- Add OpenTelemetry exporters when observability SLOs are defined.
- Add real rate limiter storage (Durable Objects or Redis) before high-traffic rollout.
- Wire CI previews only if governance allows minimal workflows; otherwise, use manual Fly/Workers publishes.
