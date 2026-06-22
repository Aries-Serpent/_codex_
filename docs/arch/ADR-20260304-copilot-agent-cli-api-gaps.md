# ADR-20260304-copilot-agent-cli-api-gaps

**Last Updated:** 2026-06-22

## Context

**Date:** 2026-03-04  
**PR:** #3495  
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 112  
**Status:** ACCEPTED — gaps resolved in this PR  

This ADR records the complete capability assessment of an active **GitHub Copilot Coding Agent**
using the **Cognitive Brain CLI API Client** (`cognitive_app/src/server/cli_api_server.py`),
identifies every gap discovered, and documents the targeted fixes applied.

---

## Investigation Method

Live interrogation performed during PR #3495 agent session (2026-03-04T22:00–22:30 UTC):

1. Attempted Playwright browser navigation to `https://aries-serpent.github.io/_codex_/cognitive_app/`
2. Attempted `web_fetch` of the same URL
3. Checked whether the FastAPI server was running on `localhost:8765`
4. Exercised every API endpoint with `curl` from within the agent `bash` tool
5. Cross-referenced `copilot-setup-steps.yml` startup logic
6. Cross-referenced `.codex/agent_context.json` existence and injection step
7. Verified `CODEX_MASTER_KEY` / `CODEX_BACKUP_KEY` env availability
8. Mapped every repo variable from the provided secrets/variables inventory

---

## Capability Matrix — Before This PR

| Capability | Status | Root Cause |
|-----------|--------|------------|
| `GET /api/health` | ✅ WORKS | Server auto-started by setup-steps |
| `POST /api/cli/run` | ✅ WORKS | No auth required |
| `GET /api/cli/history` | ✅ WORKS | No auth required |
| `DELETE /api/cli/history` | ✅ WORKS | No auth required |
| `POST /api/request` (HTTP proxy) | ✅ WORKS | No auth required; GitHub auto-inject via `CODEX_MASTER_KEY` skipped (key empty) |
| `GET /api/ooda/metrics` | ✅ WORKS | Returns empty (orchestrator not wired) |
| `POST /api/ooda/process` | ⚠️ PARTIAL | `cognitive_brain.base` import fails in CI |
| `GET /api/memory/state` | ❌ FAILS 503 | `CODEX_MASTER_KEY` not available in session |
| `GET /api/memory/search` | ❌ FAILS 503 | Same |
| `POST /api/memory/consolidate` | ❌ FAILS 503 | Same |
| `WebSocket /ws/cli` (PTY) | ⚠️ UNTESTED | No browser in agent sandbox; works if frontend is connected |
| GitHub Pages frontend URL | ❌ BLOCKED | Playwright sandbox network policy (`ERR_BLOCKED_BY_CLIENT`) |
| `web_fetch` of GitHub Pages | ✅ WORKS | Returns static HTML shell; React SPA requires JS runtime |
| `CODEX_CLI_API_URL` in agent env | ❌ MISSING | Not exported to `GITHUB_ENV` in setup steps |
| `COPILOT_CLI_BASE_URL` in agent env | ❌ MISSING | `.codex/agent_context.json` did not exist → injection step silently skipped |
| Repo variables injected as env vars | ❌ MISSING | **Same root cause: `.codex/agent_context.json` not present** |

---

## Root Causes

### RC-1 — `.codex/agent_context.json` missing (highest impact)

The "Inject repo variable context for agent" step in `copilot-setup-steps.yml` (line 118)
reads `.codex/agent_context.json` and writes every key-value pair into `GITHUB_ENV`.
**This file did not exist**, so every session since the step was introduced was silently
skipped. Consequence: none of the following reached the agent environment:

- `COPILOT_CLI_BASE_URL` = `http://localhost:8765`
- `COPILOT_CLI_ENABLED` = `true`
- `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` = `D`
- `AUTO_PROMOTE_TIER_ENABLED` = `true`
- `COGNITIVE_BRAIN_SESSION_NUMBER`
- `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE`
- All other `COGNITIVE_BRAIN_*` and `COPILOT_*` repo variables

**Fix (this PR):** Created `.codex/agent_context.json` from the full repo variables inventory.

### RC-2 — `CODEX_CLI_API_URL` never exported to `GITHUB_ENV`

The CLI server startup step exported `CLI_API_SERVER_PID` but not the server URL.
`BrainClient` and agent Python code had no standard way to discover the URL at runtime.

**Fix (this PR):**
- `copilot-setup-steps.yml` now exports `CODEX_CLI_API_URL=${COPILOT_CLI_BASE_URL:-http://localhost:8765}` to `GITHUB_ENV`
- `BrainClient.__init__` now checks `CODEX_CLI_API_URL` → `COPILOT_CLI_BASE_URL` → default

### RC-3 — No Python client wrapper for agent code

Agents had to manually construct `curl` commands or use raw `httpx`/`urllib` calls.
No standard, testable interface existed.

**Fix (this PR):** Created `src/codex/agents/brain_client.py` — `BrainClient` class with
typed methods for every server endpoint, convenience helpers (`git_status`, `git_log`,
`github_repo_info`, `github_workflow_runs`), and clean `BrainClientError` exception handling.

### RC-4 — `CODEX_MASTER_KEY` not available → memory endpoints blocked

`copilot-setup-steps.yml` references `secrets.CODEX_MASTER_KEY` and `secrets.CODEX_BACKUP_KEY`
in the job `env:` block (lines 86–87). In theory these should inject into the session.
In practice, the active session showed `CODEX_MASTER_KEY` empty.

**Likely cause:** The org secret `CODEX_MASTER_KEY` may have been rotated or its value is
empty. `CODEX_BACKUP_KEY` was updated 4 days ago (more recent) and may be valid.

**Partial fix (this PR):** `BrainClient._auth_header()` checks both `CODEX_MASTER_KEY`
and `CODEX_BACKUP_KEY` (preferred order). Memory endpoints fail gracefully with
`BrainClientError` when auth is not configured.

**Action required (@mbaetiong):** Verify `CODEX_MASTER_KEY` org secret value is not empty.
If empty, rotate it. The server's `_require_memory_auth()` rejects empty tokens.

### RC-5 — `httpx` not in CLI server startup pip install

The CLI server `api_proxy` endpoint uses `httpx` for outbound requests. The startup step
only installed `fastapi uvicorn ptyprocess`. If `httpx` was not pre-installed in the
environment, proxy requests would fail with `ImportError`.

**Fix (this PR):** Added `httpx` to the `pip install` line in the startup step.

### RC-6 — Browser (Playwright) cannot reach GitHub Pages frontend

The agent sandbox blocks outbound browser navigation to
`https://aries-serpent.github.io/_codex_/cognitive_app/` with `ERR_BLOCKED_BY_CLIENT`.

**Status:** **This is a sandbox network policy — cannot be changed within this PR.**
Agents should use `BrainClient` (Python) or `curl` (bash) against `localhost:8765` directly.
`web_fetch` CAN retrieve the static HTML shell of the GitHub Pages app but cannot execute
the React SPA (no JS runtime). The frontend is for human browser use; agent access is
via the REST/WebSocket server.

---

## Capability Matrix — After This PR

| Capability | Status | Notes |
|-----------|--------|-------|
| `GET /api/health` | ✅ WORKS | Unchanged |
| `POST /api/cli/run` | ✅ WORKS | Unchanged |
| `GET /api/cli/history` | ✅ WORKS | Unchanged |
| `DELETE /api/cli/history` | ✅ WORKS | Unchanged |
| `POST /api/request` (HTTP proxy) | ✅ WORKS | `httpx` now in startup install |
| `GET /api/ooda/metrics` | ✅ WORKS | Unchanged |
| `POST /api/ooda/process` | ⚠️ PARTIAL | Needs `cognitive_brain.base` installed |
| `GET /api/memory/state` | ⚠️ PENDING | Requires `CODEX_MASTER_KEY` rotation (RC-4) |
| `GET /api/memory/search` | ⚠️ PENDING | Same |
| `POST /api/memory/consolidate` | ⚠️ PENDING | Same |
| `WebSocket /ws/cli` (PTY) | ⚠️ HUMAN-ONLY | Accessible from browser frontend, not agent |
| GitHub Pages frontend | ❌ BLOCKED | Sandbox policy; use REST API directly |
| `CODEX_CLI_API_URL` in agent env | ✅ FIXED | Exported by startup step (this PR) |
| `COPILOT_CLI_BASE_URL` in agent env | ✅ FIXED | `agent_context.json` created (this PR) |
| All repo variables in agent env | ✅ FIXED | `agent_context.json` created (this PR) |
| `BrainClient` Python import | ✅ NEW | `from codex.agents.brain_client import BrainClient` |

---

## Variables — Added / Updated

| Variable | Type | Before | After | Action |
|----------|------|--------|-------|--------|
| `CODEX_CLI_API_URL` | Repo variable | ❌ Missing | `http://localhost:8765` | **Add to repo variables** |
| `agent_context.json` | File | ❌ Missing | Created with all repo vars | **Created (this PR)** |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | Repo variable | `110` | `112` | **Update in repo variables + agent_context.json** |
| `COPILOT_CLI_BASE_URL` | Repo variable | ✅ `http://localhost:8765` | Unchanged | Propagated via agent_context.json |
| `COPILOT_CLI_ENABLED` | Repo variable | ✅ `true` | Unchanged | Propagated via agent_context.json |
| `CODEX_MASTER_KEY` | Org secret | ⚠️ Possibly empty | **Verify & rotate** | Action for @mbaetiong |

---

## Action Items for @mbaetiong

| Priority | Action | Why |
|----------|--------|-----|
| P1 — IMMEDIATE | Verify `CODEX_MASTER_KEY` org secret value is not empty | Memory endpoints fail with 503 until rotated |
| P1 — IMMEDIATE | Add `CODEX_CLI_API_URL=http://localhost:8765` as repo variable | Canonical URL for `BrainClient` auto-discovery |
| P2 | Update `COGNITIVE_BRAIN_SESSION_NUMBER` repo variable to `112` | Tracks current session |
| P3 | Schedule `repo-var-sync-agent` to auto-update `agent_context.json` on repo variable changes | Prevent RC-1 regression |

---

## How Copilot Agents Should Use the CLI API

### From Python (preferred)

```python
from codex.agents.brain_client import BrainClient

brain = BrainClient()          # auto-discovers URL from CODEX_CLI_API_URL env var

# Check server is live
if brain.is_available():
    # Execute a shell command
    result = brain.run_command("python scripts/ci/generate_manifest.py")
    print(result["stdout"])

    # Proxy a GitHub API call
    runs = brain.github_workflow_runs(per_page=10)
    for run in runs:
        print(run["name"], run["conclusion"])

    # Quick helpers
    print(brain.git_status())
    print("\n".join(brain.git_log(5)))
```

## From bash (via curl)

```bash
# Health check
curl -sf http://localhost:8765/api/health | python3 -m json.tool

# Run a command
curl -sf -X POST http://localhost:8765/api/cli/run \
  -H "Content-Type: application/json" \
  -d '{"command": "git status --short", "timeout": 10}'

# Proxy a GitHub API call
curl -sf -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}'
```

---

*Created: 2026-03-04 | PR #3495 | Session 112 | Author: copilot-swe-agent[bot]*
