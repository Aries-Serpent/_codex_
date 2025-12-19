# MCP Rate Limiting

Rate limiting protects the MCP server and upstream providers.

## Strategy
- **Token bucket** per API key with burst limits; future-proof by storing buckets in Durable Objects (Cloudflare) or Redis/SQLite (Fly.io).
- **Default limits**: 60 RPM read (`/mcp/v1/query`) and 30 RPM write (`/mcp/v1/context`) for previews.

## Configuration
| Variable | Purpose | Default |
| --- | --- | --- |
| `MCP_RATE_LIMIT_RPM_READ` | Queries per minute | `60` |
| `MCP_RATE_LIMIT_RPM_WRITE` | Context writes per minute | `30` |

## Implementation notes
- Hooks are stubbed in `src/mcp/server/http.py` (`_enforce_rate_limit`) so preview deployments can wire a limiter without changing the API.
- For Workers, reuse Durable Objects for counters; for Fly.io, run a lightweight Redis container or SQLite table.

## Tests
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/mcp/test_http_server.py -q` (ensures limiter hook returns 429 on forced failure)
