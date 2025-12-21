# MCP Authentication

This repository ships an MCP authentication baseline to keep previews lightweight while preserving production pathways.

## Supported methods
- **API key header**: `X-MCP-API-Key: <key>` (preferred) or `Authorization: Bearer <key>`.
- **Offline bypass**: set `MCP_OFFLINE=true` to disable API-key enforcement for local smoke tests.

## Environment variables
| Name | Purpose | Default |
| --- | --- | --- |
| `MCP_API_KEY` | Primary API key for HTTP endpoints | `dev-key` (development only) |
| `MCP_OFFLINE` | When `true`, disable auth checks (use only locally) | `false` |
| `CODEX_ITA_API_KEY` | Upstream ITA integration key (kept external) | unset |

## Recommended practices
- Keep keys in provider secret stores (Fly Secrets, Cloudflare Vars, Copilot Spaces secrets).
- Rotate keys when promoting from preview to production; use per-principal keys for auditability.
- Enforce TLS termination at the edge (Cloudflare) or load balancer (Fly.io). TLS is required for all production traffic.
- Add rate limiting alongside auth (see `docs/mcp/rate_limiting.md`).
