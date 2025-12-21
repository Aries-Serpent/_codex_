# Copilot MCP Integration Guide

This guide documents how to run, validate, and preview the Codex MCP server from Copilot Spaces and how to target low-cost hosting (Cloudflare Workers for edge previews, Fly.io for persistent workers). The reference branch for production readiness is **main**, with active development on `copilot/continue-high-maturity-achievement` (branched from `0D_base_`).

## Quick start (Copilot Spaces)
1. Copy `.copilot-space/mcp.example.json` into your Space configuration.
2. Set environment variables:
   - `CODEX_ITA_API_KEY` for ITA integration
   - `CODEX_MCP_API_KEY` (defaults to `dev-key` for local usage)
   - Optional: `MCP_OFFLINE=true` to bypass auth during offline dev
3. Launch the server using the bundled command: `python -m src.mcp.server.http --config codex_capability_map.yaml`.
4. Validate with `python scripts/validate_mcp.py --run-http-smoke`.

## Branch mapping
- **Production target**: `main`
- **Development snapshot**: `0D_base_`
- **Feature branch for MCP integration**: `copilot/continue-high-maturity-achievement`
- Keep PRs focused; rebase against `0D_base_` before opening against `main`.

## Hosting recommendations
- **Cloudflare Workers**: Use for stateless preview endpoints. Bridge `/mcp/*` routes to the FastAPI prototype or author a lightweight Worker (Node 18 runtime) using the `fetch` handler to mirror the FastAPI schema.
- **Fly.io**: Use for persistent containers and background embedding workers. Deploy using `fly launch` + `fly deploy`, keeping secrets in Fly Secrets. Run the FastAPI server and optional embedding worker in separate apps for isolation.
- **Vercel/Netlify**: Optional for PR previews; avoid long-running workers.

## Runtime options
- **Python/FastAPI prototype**: `src/mcp/server/http.py` provides `/mcp/v1/health`, `/mcp/v1/query`, `/mcp/v1/context` plus API-key auth and in-memory vector store. Use this for local previews and Fly.io deploys.
- **Node/TypeScript prototype (edge)**: Use a Workers-compatible handler with `fetch` and return JSON matching `docs/mcp/api_schema.md`. Recommended runtime: Node 18+ with the standard `Request`/`Response` APIs.

## Validation checklist
- `python scripts/validate_mcp.py --run-http-smoke` passes
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_http_server.py -q`
- Capability map includes MCP entries (`codex_capability_map.yaml`)
- Copilot Space config present (`.copilot-space/mcp.example.json`)
- No GitHub Actions workflows modified

## Security & secrets
- Never commit API keys. Use provider secret stores (Fly Secrets, Cloudflare Vars) or Copilot Space secrets.
- Enforce TLS on external endpoints and enable per-principal audit logging when moving beyond local previews.
