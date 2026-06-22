# Cognitive App CLI — Copilot Agent Connection Guide

**Last Updated:** 2026-06-22

> **Status:** ✅ VERIFIED 2026-03-05 (PR #3497 W-114 audit)
> **Server:** `http://localhost:8765` (FastAPI — auto-started by `copilot-setup-steps.yml`)
> **Frontend:** `https://aries-serpent.github.io/_codex_/cognitive_app` (GitHub Pages SPA)
> **Source:** `cognitive_app/src/server/cli_api_server.py`
> **Python client:** `src/codex/agents/brain_client.py` (`BrainClient`)

---

## Agent API Request Priority Hierarchy

Copilot Coding Agent sessions should use the following priority order for all
external API calls:

| Priority | Mechanism | When to use |
|----------|-----------|-------------|
| **1 — Primary** | **MCP Server + Playwright** (`github-mcp-server-*` tools, browser tools) | Always try first — richest auth, structured responses, no server dependency |
| **2 — Secondary** | **CLI API Client** (`BrainClient.proxy_request()` / `POST /api/request`) | When MCP/Playwright unavailable or insufficient; provides auto-auth + audit logging |
| **3 — Fallback** | Direct `urllib` / `requests` / `httpx` | Last resort only — when neither MCP nor the CLI server is available |

### Secondary mechanism — CLI API Client pattern

```python
from codex.agents.brain_client import BrainClient

brain = BrainClient()
assert brain.is_available(), "Start server before session (or fall back to MCP/urllib)"

# GitHub API — auth auto-injected via CODEX_MASTER_KEY
repo  = brain.proxy_request("GET", "https://api.github.com/repos/Aries-Serpent/_codex_")
runs  = brain.proxy_request("GET",
          "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs",
          params={"per_page": "5"})

# Create / update a repo variable
brain.proxy_request(
    "POST",
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
    body={"name": "COPILOT_TEST_VAR", "value": "hello_from_agent"},
)
```

```bash
# Equivalent via curl (bash tool) — same auto-auth behaviour
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}'
```

---

## Quick-Start Checklist (Every Session)

Run these four lines at the start of every Copilot Coding Agent session to confirm connectivity:

```bash
# 1 — Server alive?
curl -sf http://localhost:8765/api/health && echo " ✅ server up"

# 2 — GitHub API proxy working?
curl -sf -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); b=d.get('body',{}); print('✅ repo:', b.get('full_name'), '| status:', d.get('status_code'))"

# 3 — History DB accessible?
curl -sf http://localhost:8765/api/cli/history?limit=1 \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ history total:', d['total'])"

# 4 — Env vars injected?
echo "CODEX_CLI_API_URL=${CODEX_CLI_API_URL:-NOT SET}"
echo "COPILOT_CLI_BASE_URL=${COPILOT_CLI_BASE_URL:-NOT SET}"
```

Expected output:
```
{"status":"ok",...} ✅ server up
✅ repo: Aries-Serpent/_codex_ | status: 200
✅ history total: 0
CODEX_CLI_API_URL=http://localhost:8765
COPILOT_CLI_BASE_URL=http://localhost:8765
```

---

## API Endpoint Reference

All endpoints are on `http://localhost:8765`. The server requires **no authentication** for
local calls. GitHub API calls auto-inject `Authorization: Bearer $CODEX_MASTER_KEY` when
the key is available.

### 1. Brain Health — `GET /api/health`

```bash
curl -s http://localhost:8765/api/health | python3 -m json.tool
```

**Response:**
```json
{
  "status": "ok",
  "repo_root": "/home/runner/work/_codex_/_codex_",
  "timestamp": "2026-03-05T04:25:08.069819",
  "history_db": "/home/runner/work/_codex_/_codex_/.codex/codex.db"
}
```

**Expected HTTP:** `200`  
**Failure:** If this returns connection refused, the server is not running — see
[Troubleshooting](#troubleshooting) section.

---

### 2. Run Command — `POST /api/cli/run`

Execute any shell command from the repo root and capture stdout/stderr.

```bash
curl -s -X POST http://localhost:8765/api/cli/run \
  -H "Content-Type: application/json" \
  -d '{"command":"git log --oneline -3"}'
```

**Payload schema:**
```json
{
  "command": "string",       // required — shell command to run
  "cwd":     "string",       // optional — working directory (default: repo root)
  "timeout": 30              // optional — seconds (default: 30)
}
```

**Response:**
```json
{
  "command":     "git log --oneline -3",
  "stdout":      "b65212b fix: correct detect-secrets...\n",
  "stderr":      "",
  "returncode":  0,
  "duration_ms": 5.8,
  "cwd":         "/home/runner/work/_codex_/_codex_",
  "timestamp":   "2026-03-05T04:25:08.123485"
}
```

**Expected HTTP:** `200`

---

### 3. CLI History — `GET /api/cli/history`

Retrieve recent command history from SQLite.

```bash
curl -s "http://localhost:8765/api/cli/history?limit=5"
```

**Query params:** `limit` (int, default 50), `offset` (int, default 0)

**Response:**
```json
{
  "items": [
    { "command": "git log ...", "stdout": "...", "returncode": 0, "timestamp": "..." }
  ],
  "total": 42
}
```

**Expected HTTP:** `200`

---

### 4. Clear History — `DELETE /api/cli/history`

Wipe all command history from SQLite.

```bash
curl -s -X DELETE http://localhost:8765/api/cli/history
```

**Response:**
```json
{ "cleared": true }
```

**Expected HTTP:** `200`

---

### 5. HTTP Proxy / GitHub API — `POST /api/request`

Proxy **any** HTTP method (GET · POST · PUT · PATCH · DELETE · HEAD · OPTIONS) to any URL.
When the target URL starts with `https://api.github.com/`, `Authorization: Bearer $CODEX_MASTER_KEY`
is auto-injected if the env var is set.

**Payload schema (`ApiProxyRequest`):**
```json
{
  "method":   "GET",                   // required: GET POST PUT PATCH DELETE HEAD OPTIONS
  "url":      "https://...",           // required: full URL or path (resolved against base_url)
  "headers":  { "key": "value" },     // optional
  "params":   { "key": "value" },     // optional — appended to URL as query string
  "body":     { "any": "json" },      // optional — request body (auto Content-Type: application/json)
  "base_url": "https://...",          // optional — prefix for relative urls
  "timeout":  30                       // optional — seconds
}
```

**Response schema (`ApiProxyResponse`):**
```json
{
  "status_code": 200,
  "headers":     { "content-type": "application/json" },
  "body":        { "...": "..." },
  "error":       null
}
```

#### GET GH Repo

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}'
```

**Live result (2026-03-05):**
```
id: 1040037790  |  full_name: Aries-Serpent/_codex_
language: Python  |  default_branch: main
visibility: public  |  HTTP status: 200
```

#### GET GH Runs

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs?per_page=1"}'
```

**Live result (2026-03-05):**
```
total_count: 40000  |  latest run: 22702237122
name: Iterative Self-Healing CI  |  status: completed  |  HTTP status: 200
```

#### POST example

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"POST","url":"https://httpbin.org/post","body":{"hello":"world"}}'
```

#### PUT example

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"PUT","url":"https://httpbin.org/put","body":{"key":"value"}}'
```

#### PATCH example

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"PATCH","url":"https://httpbin.org/patch","body":{"field":"patched"}}'
```

#### DELETE example

```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"DELETE","url":"https://httpbin.org/delete"}'
```

**Expected HTTP for all proxy calls:** `200` (outer) with `status_code` reflecting upstream.

---

### 6. Memory State — `GET /api/memory/state`

```bash
curl -s http://localhost:8765/api/memory/state
```

**⚠️ Requires `CODEX_MASTER_KEY` env var.** Returns `503` when the key is absent (expected in CI).
See RC-4 in `docs/arch/ADR-20260304-copilot-agent-cli-api-gaps.md`.

---

### 7. OODA Metrics — `GET /api/ooda/metrics`

```bash
curl -s http://localhost:8765/api/ooda/metrics | python3 -m json.tool
```

Returns orchestrator cycle counts and loop timings. Always reachable (no auth).

---

## Python Client (`BrainClient`)

Use `BrainClient` from `src/codex/agents/brain_client.py` for typed access:

```python
from codex.agents.brain_client import BrainClient

# Auto-discovers URL from CODEX_CLI_API_URL → COPILOT_CLI_BASE_URL → http://localhost:8765
client = BrainClient()

# Check server is up
if not client.is_available():
    raise RuntimeError("Cognitive brain server not running")

# Run a shell command
result = client.run_command("git log --oneline -3")
print(result["stdout"])

# Proxy an HTTP request
resp = client.proxy_request(
    method="GET",
    url="https://api.github.com/repos/Aries-Serpent/_codex_",
)
print(resp["body"]["full_name"])   # Aries-Serpent/_codex_

# Get repo info (convenience wrapper)
info = client.github_repo_info("Aries-Serpent", "_codex_")
print(info["language"])            # Python

# Get workflow runs
runs = client.github_workflow_runs("Aries-Serpent", "_codex_", per_page=1)
print(runs["total_count"])         # 40000

# Git status
print(client.git_status())

# Command history
history = client.memory_state()    # ⚠️ needs CODEX_MASTER_KEY
```

---

## GitHub Pages Frontend

| Property | Value |
|----------|-------|
| URL | `https://aries-serpent.github.io/_codex_/cognitive_app` |
| `web_fetch` | ✅ Returns static HTML shell |
| Playwright browser | ❌ Blocked — `ERR_BLOCKED_BY_CLIENT` (sandbox network policy) |
| Agent direct use | Via `curl`/`BrainClient` — full functionality available |

The GitHub Pages frontend is a React SPA. It communicates with the same `http://localhost:8765`
API. Because the Copilot sandbox blocks GitHub Pages domains via network policy, the frontend
**cannot be loaded in the agent Playwright browser**. Use `curl` or `BrainClient` directly.

This is a **permanent sandbox constraint** (RC-6 in ADR-20260304). It does not affect agent
capability — all operations the frontend performs are available via the REST API.

---

## Full Audit Results (2026-03-05 PR #3497 W-114)

| # | Operation | Method | Endpoint | HTTP | Result |
|---|-----------|--------|----------|------|--------|
| 1 | Brain Health | `GET` | `/api/health` | **200** | ✅ `status: ok` |
| 2 | Run cmd | `POST` | `/api/cli/run` | **200** | ✅ `returncode: 0`, git log returned 3 commits |
| 3 | CLI History | `GET` | `/api/cli/history` | **200** | ✅ `total: 3` after 3 prior commands |
| 4 | Clear History | `DELETE` | `/api/cli/history` | **200** | ✅ `{"cleared": true}`, history = 0 after |
| 5 | GET GH Repo | `POST→GET` | `/api/request` → `api.github.com/repos/…` | **200** | ✅ `full_name: Aries-Serpent/_codex_`, `language: Python` |
| 6 | GET GH Runs | `POST→GET` | `/api/request` → `api.github.com/…/actions/runs?per_page=1` | **200** | ✅ `total_count: 40000`, latest run 22702237122 |
| 7 | PUT proxy | `POST→PUT` | `/api/request` → `httpbin.org/put` | **200** | ✅ body echoed correctly |
| 8 | PATCH proxy | `POST→PATCH` | `/api/request` → `httpbin.org/patch` | **200** | ✅ body echoed correctly |
| 9 | GitHub Pages | browser | `https://aries-serpent.github.io/_codex_/cognitive_app` | ❌ | `ERR_BLOCKED_BY_CLIENT` — permanent sandbox constraint (RC-6) |

**Overall: 8/8 API operations successful. 1 known permanent limitation (browser blocked).**

---

## GitHub Variables Management

The CLI API Client can create and update **repo**, **environment**, and **org** variables
via the GitHub Actions Variables REST API. All calls auto-inject `Authorization: Bearer $CODEX_MASTER_KEY`.

### Repo Variables

```bash
# List repo variables
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables"}'

# Create a repo variable (POST — name must not already exist)
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url":    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
    "body":   {"name": "COPILOT_TEST_VAR", "value": "hello_from_agent"}
  }'

# Update an existing repo variable (PATCH)
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "PATCH",
    "url":    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables/COPILOT_TEST_VAR",
    "body":   {"name": "COPILOT_TEST_VAR", "value": "updated_value"}
  }'

# Delete a repo variable
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"DELETE","url":"https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables/COPILOT_TEST_VAR"}'
```

**Python (`BrainClient`):**

```python
brain = BrainClient()

# Create
brain.proxy_request(
    "POST",
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
    body={"name": "COPILOT_TEST_VAR", "value": "hello_from_agent"},
)

# Update
brain.proxy_request(
    "PATCH",
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables/COPILOT_TEST_VAR",
    body={"name": "COPILOT_TEST_VAR", "value": "updated_value"},
)
```

### Environment Variables

```bash
# List environment variables (environment name: "production")
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_/environments/production/variables"}'

# Create an environment variable
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url":    "https://api.github.com/repos/Aries-Serpent/_codex_/environments/production/variables",
    "body":   {"name": "COPILOT_ENV_TEST", "value": "env_value"}
  }'
```

### Org Variables

```bash
# List org variables
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/orgs/Aries-Serpent/actions/variables"}'

# Create an org variable (visibility: "all" | "private" | "selected")
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url":    "https://api.github.com/orgs/Aries-Serpent/actions/variables",
    "body":   {"name": "COPILOT_ORG_TEST", "value": "org_value", "visibility": "all"}
  }'
```

### Live Test Results (2026-03-05 PR #3497 W-117)

**Hierarchy demonstration — same operation via each tier:**

| Tier | Mechanism | Operation | Result |
|------|-----------|-----------|--------|
| **1 — Primary** | `github-mcp-server-search_repositories` MCP tool | GET repo info | ✅ `200` full response, admin perms confirmed |
| **2 — Secondary** | `POST /api/request` → `GET /repos/…/actions/variables` | List repo vars | ✅ `200` outer; upstream `401` when `CODEX_MASTER_KEY` absent (expected — key not injected into sandbox process env); `200` with full list when key is set |
| **3 — Fallback** | `urllib.request` direct | (not tested — MCP was sufficient) | N/A |

**Variable management (when `CODEX_MASTER_KEY` is set in server env):**

| Operation | GitHub API | Expected upstream HTTP |
|-----------|-----------|----------------------|
| List repo vars | `GET /repos/…/actions/variables` | 200 |
| Create repo var | `POST /repos/…/actions/variables` | 201 |
| Update repo var | `PATCH /repos/…/actions/variables/{name}` | 204 |
| Delete repo var | `DELETE /repos/…/actions/variables/{name}` | 204 |
| List env vars | `GET /repos/…/environments/{env}/variables` | 200 |
| Create env var | `POST /repos/…/environments/{env}/variables` | 201 |
| List org vars | `GET /orgs/Aries-Serpent/actions/variables` | 200 |
| Create org var | `POST /orgs/Aries-Serpent/actions/variables` | 201 |

> **Note:** The outer `/api/request` response wrapper always returns HTTP `200` to the caller.
> The actual GitHub API status code is in `response["status_code"]`. Check that field, not the
> outer HTTP code, to determine whether the operation succeeded.

> **Auth note:** `CODEX_MASTER_KEY` must be injected into the **server process environment**
> (via `copilot-setup-steps.yml` `GITHUB_ENV` export) for auto-inject to work. If it is set
> as a repo variable only — not a secret exported to the runner — the server will see an empty
> key and GitHub will return 401. Verify with: `curl http://localhost:8765/api/health` then
> check that `CODEX_MASTER_KEY` appears in the server's process environment.

---

## Troubleshooting

### Server not running (`Connection refused`)

```bash
# Check if process is alive
curl -sf http://localhost:8765/api/health || echo "SERVER DOWN"

# Start manually
cd /home/runner/work/_codex_/_codex_
python cognitive_app/src/server/cli_api_server.py &
sleep 2
curl -sf http://localhost:8765/api/health
```

The server is normally auto-started by `copilot-setup-steps.yml`. If it failed:
1. Check `$COGNITIVE_BRAIN_SERVER_LOG` for startup errors
2. Verify `httpx`, `fastapi`, `uvicorn` are installed: `pip install fastapi uvicorn httpx`

### Env vars not set

```bash
# Manual injection fallback
export CODEX_CLI_API_URL=http://localhost:8765
export COPILOT_CLI_BASE_URL=http://localhost:8765
```

Root cause: `.codex/agent_context.json` missing or `copilot-setup-steps.yml` injection step
skipped. See RC-1/RC-2 in `docs/arch/ADR-20260304-copilot-agent-cli-api-gaps.md`.

### Memory endpoints return 503

```
{"detail": "Memory server unavailable: CODEX_MASTER_KEY not set"}
```

`CODEX_MASTER_KEY` must be set as a repo/org secret and passed to the session. Contact
`@mbaetiong` to verify the secret is current. See RC-4 in the ADR.

### `/api/request` returns `error` field

```json
{ "status_code": null, "body": null, "error": "Connection timeout after 30s" }
```

The target URL is unreachable from the CI runner. GitHub API (`api.github.com`) and
`httpbin.org` are always reachable. Custom internal URLs may be blocked.

### `/api/request` returns `401` for GitHub API calls

```
{ "status_code": 401, "body": {"message": "Requires authentication"} }
```

`CODEX_MASTER_KEY` must be exported to `GITHUB_ENV` by `copilot-setup-steps.yml` so that
the CLI API server process inherits it. If it is only a **repo variable** (not a secret
exported to the runner), the server process env will not have it and auto-inject silently
skips. Verify:

```bash
# Check if key reached the server process
curl -s http://localhost:8765/api/health | python3 -m json.tool
# Then check your runner env:
echo "CODEX_MASTER_KEY length: ${#CODEX_MASTER_KEY}"
```

For authenticated variable management, use the **primary mechanism** (MCP tools) instead
when `CODEX_MASTER_KEY` is not available in the process env. The MCP tools carry their own
credentials independently of this server.

### detect-secrets baseline fails after touching `agent-auth-delegation.yml`

Run the targeted scan (never full-repo scan):
```bash
detect-secrets scan .github/workflows/agent-auth-delegation.yml CODEX_MANIFEST.json \
  --baseline .secrets.baseline
# Exit 0 = baseline now matches file; commit .secrets.baseline
```

See pattern `DETECT_SECRETS_002` in `.codex/patterns/ci_failure_patterns.yaml`.

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/arch/ADR-20260304-copilot-agent-cli-api-gaps.md` | Full root-cause analysis of all gaps found in PR #3495 |
| `src/codex/agents/brain_client.py` | Typed Python client — annotated source |
| `tests/agents/test_brain_client.py` | 35 unit tests covering every BrainClient method |
| `cognitive_app/src/server/cli_api_server.py` | FastAPI server source (all route handlers) |
| `.codex/agent_context.json` | Repo variable snapshot injected into every session |
| `.codex/patterns/ci_failure_patterns.yaml` | CI failure pattern library (23 patterns) |
| `docs/agent/OPERATIONAL_GUIDELINES.md` | Full agent operational framework |

---

*Last verified: 2026-03-05T04:25:08Z — PR #3497 W-114 audit | All 8 API operations confirmed ✅*
