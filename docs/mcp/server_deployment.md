# MCP Server Deployment

This guide covers low/no-cost hosting for the MCP HTTP prototype and how to align with GitHub Copilot Agent flows.

## Targets
- **Cloudflare Workers (edge preview)**
  - Runtime: Node 18 Workers
  - Map `/mcp/*` to the FastAPI schema in `docs/mcp/api_schema.md`
  - Use Durable Objects or KV for lightweight rate-limit buckets
- **Fly.io (persistent container)**
  - Runtime: Python 3.11 (FastAPI `src/mcp/server/http.py`)
  - Recommended: separate apps for API and embedding worker
  - Commands: `fly launch --name codex-mcp`, `fly deploy`
- **Local Compose**
  - Use `docker-compose.yml` profile `mcp` to start FastAPI + Chroma sidecar

## Deployment steps (FastAPI on Fly.io)
<!-- pragma: allowlist secret -->
1. `fly launch --name codex-mcp --no-deploy`
2. `fly secrets set MCP_API_KEY=<prod-key> CODEX_ITA_API_KEY=<ita-key>`
   
   **⚠️ WARNING**: `<prod-key>` and `<ita-key>` are placeholders only. Replace them with your actual secret values. Real keys must be stored only as Fly secrets or in a secure secrets manager, never committed to code or documentation.

3. `fly deploy`
4. Smoke test: `curl -H "X-MCP-API-Key: <prod-key>" https://codex-mcp.fly.dev/mcp/v1/health`

## Deployment steps (Cloudflare Workers preview)
<!-- pragma: allowlist secret -->
1. Scaffold a Worker with `wrangler init codex-mcp-worker`
2. Add a `fetch` handler that routes `/mcp/v1/query` and `/mcp/v1/context` to the FastAPI-compatible schema
3. Configure secrets: `wrangler secret put MCP_API_KEY` <!-- pragma: allowlist secret -->
4. Publish: `wrangler publish --name codex-mcp-worker`

## Preview & PR flows
- Use Vercel or Netlify for PR previews if allowed by governance. Keep deployments stateless and read-only.
- Copilot Spaces can run the FastAPI prototype via `.copilot-space/mcp.example.json` for reviewers.
