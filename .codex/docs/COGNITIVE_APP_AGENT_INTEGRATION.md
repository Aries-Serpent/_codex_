# Cognitive App CLI Console — GitHub Coding Agent Integration Guide

**Status:** ✅ Production-ready (S155 — 2026-03-18)  
**URL:** https://aries-serpent.github.io/_codex_/cognitive_app/  
**Backend:** `cognitive_app/src/server/cli_api_server.py` (FastAPI, port 8765)  
**PR:** #3628 | Branch: `copilot/update-ci-failure-triage-report`

---

## How the App Works — API Mode Cascade

The cognitive_app `api-mode-selector.ts` uses a 4-level priority chain:

```
Priority 1: Live CLI server  (localhost:8765 or VITE_CLI_API_URL)
            → Full cognitive brain: memory, OODA, agent orchestration, CLI terminal
Priority 2: GitHub Public API (api.github.com — no auth needed)
            → Live repo data: workflow runs, stats, releases, branch status
Priority 3: HAR replay       (public/har-cache/api-demo.har — offline cache)
            → Recorded brain API responses served offline
Priority 4: Mock client      (built-in, zero network, deterministic)
            → Always works; unit tests and isolated dev
```

### Current GitHub Pages state (before this fix)

| Component | Before S155 | After S155 |
|-----------|-------------|------------|
| `VITE_API_MODE` at Pages build | not set → probe localhost → fail → `github` mode | `github` mode set explicitly (fast, no failed probe) |
| CLI terminal (WebSocket) | offline message | offline message (needs live server) |
| Workflow run data | ✅ (GitHub API) | ✅ (GitHub API) |
| CORS for aries-serpent.github.io | ❌ blocked (only localhost) | ✅ requires `CODEX_ALLOWED_ORIGINS` |

---

## Method 1: GitHub Codespaces (Recommended for Agent Sessions)

This is the primary path for making the **full CLI terminal + cognitive brain** available
from GitHub Pages during a GitHub Coding Agent session.

### How it works

When the GitHub Coding Agent runs, it executes inside a **GitHub Codespace**. Codespaces
automatically forward ports to a public HTTPS URL. If `cli_api_server.py` is started in
that Codespace, the forwarded port URL becomes the live backend for the GitHub Pages app.

### Human Admin Steps (one-time setup)

1. **Open the Codespace** for this repository:
   - Go to `https://github.com/Aries-Serpent/_codex_` → Code → Codespaces → New codespace

2. **Start the CLI API server** in the Codespace terminal:
   ```bash
   # Install deps
   pip install -e ".[dev]" --quiet
   pip install fastapi uvicorn websockets python-jose --quiet

   # Start server (background)
   uvicorn cognitive_app.src.server.cli_api_server:app \
     --host 0.0.0.0 --port 8765 --reload &

   # Confirm it's running
   curl http://localhost:8765/api/health
   # → {"status":"ok","version":"1.0.0","otel":false}
   ```

3. **Make port 8765 public** in the Codespace Ports panel:
   - In VS Code: View → Ports → right-click port 8765 → "Port Visibility" → Public
   - Or via CLI: `gh codespace ports forward 8765:8765 --codespace <name>`
   - Copy the forwarded URL: `https://<hash>-8765.app.github.dev`

4. **Set repo variable** `COGNITIVE_APP_API_URL` to the Codespace URL:
   ```bash
   gh variable set COGNITIVE_APP_API_URL \
     --body "https://<hash>-8765.app.github.dev" \
     --repo Aries-Serpent/_codex_
   ```

5. **Trigger a Pages redeploy** to bake the URL into the built JS:
   ```bash
   gh workflow run pages-mkdocs.yml --repo Aries-Serpent/_codex_
   ```
   Wait ~3 minutes for the build to complete.

6. **Open the app**: https://aries-serpent.github.io/_codex_/cognitive_app/  
   The mode indicator should show `🟢 Live — https://<hash>-8765.app.github.dev`

### Agent Auto-Steps (automated, no human needed if variables are set)

The Coding Agent can self-wire this when `COPILOT_AGENT_AUTH_ENABLED=true`:

```bash
# Step 1: Start server in background (agent runs this at session start)
uvicorn cognitive_app.src.server.cli_api_server:app \
  --host 0.0.0.0 --port 8765 --reload \
  --env-file .env.local &

# Step 2: Wait for server to be ready
until curl -s http://localhost:8765/api/health | grep -q '"ok"'; do sleep 1; done

# Step 3: Get Codespace forwarded URL
CODESPACE_URL=$(gh codespace ports view --json portNumber,browseUrl \
  | python3 -c "import json,sys; [print(p['browseUrl']) for p in json.load(sys.stdin) if p['portNumber']==8765]" 2>/dev/null || echo "")

# Step 4: Set repo variable via CODEX_MASTER_KEY
if [ -n "$CODESPACE_URL" ]; then
  gh variable set COGNITIVE_APP_API_URL --body "$CODESPACE_URL" \
    --repo Aries-Serpent/_codex_
fi
```

---

## Method 2: GitHub Actions Workflow Dispatch (No Codespace)

Use this when you want the CLI console to connect to a server spawned by a GitHub
Actions workflow run (ephemeral, for demo/test purposes).

**Note:** This method requires a tunnel (ngrok/cloudflared) since Actions runners
are not reachable from the browser without port forwarding.

### Setup

```yaml
# .github/workflows/start-cli-server-tunnel.yml
name: "Start CLI server with tunnel"
on:
  workflow_dispatch:
    inputs:
      duration_minutes:
        description: 'Keep server alive (minutes, max 30)'
        default: '15'

jobs:
  start-server:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Python deps
        run: pip install -e ".[dev]" fastapi uvicorn websockets --quiet

      - name: Install cloudflared tunnel
        run: |
          curl -L --output cloudflared.deb \
            https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
          dpkg -i cloudflared.deb

      - name: Start server + tunnel
        env:
          CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}
          CODEX_ALLOWED_ORIGINS: "https://aries-serpent.github.io"
        run: |
          uvicorn cognitive_app.src.server.cli_api_server:app \
            --host 0.0.0.0 --port 8765 &
          # Start tunnel and capture URL
          cloudflared tunnel --url http://localhost:8765 &
          sleep 5
          # The tunnel URL appears in cloudflared logs
          TUNNEL_URL=$(curl -s http://localhost:8765/api/health | python3 -c \
            "import json,sys; print('server ok')" 2>/dev/null && \
            journalctl -u cloudflared 2>/dev/null | grep "trycloudflare.com" | tail -1 | awk '{print $NF}' || echo "")
          if [ -n "$TUNNEL_URL" ]; then
            gh variable set COGNITIVE_APP_API_URL --body "$TUNNEL_URL" \
              --repo Aries-Serpent/_codex_
          fi
          # Keep alive
          sleep $(( ${{ inputs.duration_minutes }} * 60 ))
```

---

## Method 3: Direct REST API Calls (No Server Required)

For **read-only operations** from GitHub Pages (no CLI terminal), the app already
works in `github` mode. For **write operations** (posting comments, creating PRs,
triggering workflows), the GitHub Public API can be called directly with a token.

The `cli_api_server.py` exposes a `/api/request` HTTP proxy endpoint that
auto-injects `CODEX_MASTER_KEY` as `Authorization: Bearer` for `api.github.com` calls.
If the server is not running, the agent can call GitHub API directly:

```javascript
// From the browser console on https://aries-serpent.github.io/_codex_/cognitive_app/
const token = prompt("Enter GitHub PAT (CODEX_MASTER_KEY scope):");
const resp = await fetch("https://api.github.com/repos/Aries-Serpent/_codex_/pulls", {
  headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json" }
});
const prs = await resp.json();
console.log(prs.map(pr => `#${pr.number}: ${pr.title}`));
```

---

## Method 4: Copilot CLI + Hooks (Future)

The GitHub Copilot CLI (v1.0+) supports `hooks` in `.github/hooks/` that fire at
agent session lifecycle events. A `session-start` hook can:

1. Start `cli_api_server.py` on port 8765
2. Make port 8765 public (Codespace port forwarding)
3. Set `COGNITIVE_APP_API_URL` repo variable

**Hook file (`.github/hooks/session-start`):**
```bash
#!/usr/bin/env bash
# Auto-wire CLI server at session start (CB-INV-003 + Copilot CLI hooks)
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
LOG_DIR="${REPO_ROOT}/.codex/sessions"
mkdir -p "$LOG_DIR"

# Start CLI API server in background
uvicorn cognitive_app.src.server.cli_api_server:app \
  --host 0.0.0.0 --port 8765 --reload \
  > "$LOG_DIR/cli_api_server.log" 2>&1 &

echo "✅ CLI API server started on :8765 (PID $!)"
echo "   Log: $LOG_DIR/cli_api_server.log"

# Also run sync+new-work conflict prevention check
python scripts/ci/prevent_sync_commit_conflict.py --ci-mode || true
```

**Reference:** https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks

---

## Troubleshooting

### CLI terminal shows "⚠ CLI server offline"

**Cause:** The frontend cannot reach the server at `VITE_CLI_API_URL` (or the default
`http://localhost:8765`). The app has already fallen back to `github` or `har` mode.

**Fix (in priority order):**
1. Start the server in your Codespace and make port 8765 public (Method 1)
2. Set `COGNITIVE_APP_API_URL` repo variable to the forwarded URL
3. Retrigger Pages deployment: `gh workflow run pages-mkdocs.yml`

### CORS error in browser console

**Cause:** The server is running but `Access-Control-Allow-Origin` does not include
`https://aries-serpent.github.io`.

**Fix:** The server default CORS list is restricted to localhost for security
(``/api/cli/run`` executes shell commands; a remote web origin must be explicitly
enabled).  Set ``CODEX_ALLOWED_ORIGINS`` to include `https://aries-serpent.github.io`:
```bash
# Check what CORS origins the server is using
curl http://localhost:8765/api/health -v 2>&1 | grep -i "allow-origin"
```
Start the server with:
```bash
CODEX_ALLOWED_ORIGINS="http://localhost:5173,https://aries-serpent.github.io" \
  python cognitive_app/src/server/cli_api_server.py
```

### App shows mock data instead of live data

**Cause:** Server probe failed; app fell back to `mock` mode.

**Fix:** Check that `VITE_CLI_API_URL` resolves to a reachable server. Use browser
DevTools → Network to see if `/api/health` returns 200.

### GitHub Pages shows blank/broken page

**Cause:** Vite build failed silently (`continue-on-error: true` in workflow).

**Fix:**
```bash
cd cognitive_app && npm ci && npm run build
# Check for TypeScript errors or import failures
```

---

## Environment Variables Reference

| Variable | Where set | Default | Purpose |
|----------|-----------|---------|---------|
| `VITE_API_MODE` | Pages build env | `github` (S155 default) | Force API mode (`live`/`github`/`har`/`mock`) |
| `VITE_CLI_API_URL` | Pages build env / `.env.local` | `http://localhost:8765` | CLI server URL |
| `VITE_CODEX_KEY` | `.env.local` only | `demo-key` | Bearer token for `/api/memory/*` calls |
| `COGNITIVE_APP_API_URL` | Repo variable | not set | Overrides `VITE_CLI_API_URL` at Pages build |
| `COGNITIVE_APP_API_MODE` | Repo variable | `github` | Overrides `VITE_API_MODE` at Pages build |
| `CODEX_ALLOWED_ORIGINS` | Server env | `localhost:5173` (localhost-only) | CORS allowlist — add non-local origins here (e.g. `https://aries-serpent.github.io`) |
| `CODEX_MASTER_KEY` | Server env | not set | Auto-injected on `api.github.com` calls |

> **Note:** `VITE_GITHUB_TOKEN` has been removed. Any `VITE_*` variable is inlined into the
> static client bundle at build time, making it publicly readable. The Pages build uses the
> unauthenticated GitHub API (60 req/hr) instead. For higher rate limits, configure a
> server-side proxy via `COGNITIVE_APP_API_URL`.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ GitHub Pages: https://aries-serpent.github.io/_codex_/cognitive_app/│
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ api-mode-selector.ts                                         │    │
│  │   Priority 1: probe VITE_CLI_API_URL/api/health              │    │
│  │     → 200: mode=live (full brain)                            │    │
│  │     → fail: try HAR/GitHub modes                             │    │
│  │   Priority 2: GitHub Public API (api.github.com)             │    │
│  │   Priority 3: HAR replay (public/har-cache/)                 │    │
│  │   Priority 4: Mock client (always works)                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
          │ VITE_CLI_API_URL (when live server available)
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ cli_api_server.py  (FastAPI :8765)                                   │
│   Deployment options:                                                │
│   A. GitHub Codespace (port forwarded) ← recommended for agent use  │
│   B. Actions runner + cloudflared tunnel ← ephemeral/demo           │
│   C. Persistent deploy (Render/Railway/Fly.io) ← production         │
│                                                                       │
│  /api/health          → liveness                                     │
│  /api/request         → HTTP proxy (auto-injects CODEX_MASTER_KEY)  │
│  /api/cli/run         → one-shot command execution                   │
│  /ws/cli              → WebSocket PTY terminal                       │
│  /webhook/github      → inbound GitHub webhooks (HMAC-SHA256)       │
│  /api/webhooks/recent → recent event log                             │
└─────────────────────────────────────────────────────────────────────┘
          │ CODEX_MASTER_KEY bearer token
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GitHub REST API (api.github.com)                                     │
│   Auto-injected by /api/request proxy:                               │
│   • POST /repos/{owner}/{repo}/contents/{path} (create/update file) │
│   • POST /repos/{owner}/{repo}/pulls (create PR)                    │
│   • POST /repos/{owner}/{repo}/issues/{n}/comments (post comment)   │
│   • POST /repos/{owner}/{repo}/actions/workflows/{wf}/dispatches    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## CB-INV-001 Resolution (Playwright in Agent Sandbox)

The Playwright browser in the GitHub Coding Agent sandbox blocked `github.com` with
`ERR_BLOCKED_BY_CLIENT`. This is a **browser content filter**, not a firewall issue.

### Fix applied (S155)
The cognitive_app now uses `VITE_API_MODE=github` at Pages build time, bypassing the
Playwright-blocked localhost probe entirely. The app communicates with GitHub API
directly from the browser (not via Playwright).

### If Playwright web UI commits are needed in future

Configure the Playwright MCP server with `mcp.config.json` in the workspace root:
```json
{
  "playwrightServer": {
    "allowedOrigins": [
      "https://github.com",
      "https://*.github.com",
      "https://api.github.com"
    ]
  },
  "browser": {
    "launchOptions": {
      "headless": true,
      "args": [
        "--disable-extensions",
        "--no-sandbox",
        "--remote-allow-origins=*"
      ]
    }
  }
}
```

Known issue: Playwright MCP extension ID mismatches cause `ERR_BLOCKED_BY_CLIENT`
independent of extension configuration. See:
https://github.com/microsoft/playwright-mcp/issues/1402

---

*Created: S155 — 2026-03-18 | PR #3628*  
*See also: `.codex/docs/COMMIT_METHOD_FAILURES_S154.md` | `cognitive_app/src/server/cli_api_server.py` | `cognitive_app/src/lib/api-mode-selector.ts`*
