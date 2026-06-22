# GitHub App ↔ cognitive_app CLI — Integration Mapping Guide

**Last Updated:** 2026-06-22

> **Status:** ✅ NEW (PR #3503 W-126, 2026-03-05)  
> **Audience:** Copilot Coding Agent sessions, integration engineers  
> **Related:** `docs/agent/COGNITIVE_APP_CONNECTION_GUIDE.md`, `src/codex/auth/github_app.py`,
> `cognitive_app/src/server/cli_api_server.py`, `src/codex/agents/brain_client.py`

---

## Overview

The `cognitive_app` CLI API server (`localhost:8765`) and the new GitHub App package
(`src/codex/auth/github_app.py`) serve complementary roles:

| Layer | Component | Responsibility |
|-------|-----------|---------------|
| **Inbound** | `WebhookVerifier` | Validates `X-Hub-Signature-256` on every GitHub delivery |
| **Outbound auth** | `GitHubApp.generate_jwt()` | RS256-signed JWT used to call the GitHub REST API as the App |
| **Outbound auth fallback** | `GitHubApp.pat_api_get()` | PAT-authenticated GET with automatic `CODEX_MASTER_KEY → CODEX_BACKUP_KEY` retry |
| **Proxy gateway** | `POST /api/request` (`BrainClient.proxy_request()`) | All external API calls from Copilot Agent sessions |
| **Memory + OODA** | `POST /api/ooda/process` | Routes GitHub event data through the cognitive loop |
| **Shell execution** | `POST /api/cli/run` | Runs follow-up git/gh commands in response to events |

```
GitHub → webhook delivery
         │
         ▼  X-Hub-Signature-256 verified
  ┌─────────────────────────────────┐
  │  WebhookVerifier.verify()       │  ← src/codex/auth/github_app.py
  └───────────────┬─────────────────┘
                  │ payload (bytes)
                  ▼
  ┌─────────────────────────────────┐
  │  POST /api/ooda/process         │  ← cli_api_server.py
  │  CognitiveAppMain.process()     │
  └───────────────┬─────────────────┘
                  │ ActionResult
                  ▼
  ┌─────────────────────────────────┐
  │  POST /api/cli/run              │  ← cli_api_server.py
  │  (e.g. gh pr comment, git push) │
  └─────────────────────────────────┘
                  │
                  ▼
  ┌─────────────────────────────────┐
  │  GitHubApp.pat_api_get()        │  ← github_app.py
  │  CODEX_MASTER_KEY               │
  │    └─ 401/403 → CODEX_BACKUP_KEY│
  └─────────────────────────────────┘
```

---

## Token Resolution — Unified Priority Chain

All components in the platform resolve GitHub tokens in the same order:

| Priority | Environment Variable | Scope | Where used |
|----------|---------------------|-------|-----------|
| 1 | `CODEX_MASTER_KEY` | Full PAT (`repo` scope) | `GitHubApp.pat_api_get()`, `BrainClient`, `VariableManager` |
| 2 | `CODEX_BACKUP_KEY` | Full PAT (fallback) | Same — tried automatically on 401/403 |
| 3 | `AGENT_GITHUB_TOKEN` | `GITHUB_TOKEN` alias | Same |
| 4 | `GITHUB_TOKEN` | Installation token | Last resort |

> **GitHub App JWT auth** (used by `GitHubApp.generate_jwt()` /
> `get_installation_token()`) is **separate** from PAT auth.  
> The RSA private key (`GITHUB_APP_PRIVATE_KEY` env var) is used exclusively
> for JWT signing — it never falls through to PAT tokens.

---

## Component Mapping

### 1 · Receiving Webhooks

```python
from codex.auth.github_app import WebhookVerifier

verifier = WebhookVerifier(secret=os.environ["WEBHOOK_SECRET"])

# In your HTTP handler (FastAPI / Flask / plain WSGI):
raw_body: bytes = await request.body()
sig_header: str  = request.headers["X-Hub-Signature-256"]

if not verifier.verify(raw_body, sig_header):
    raise HTTPException(status_code=401, detail="Invalid webhook signature")

event = json.loads(raw_body)
```

**Wire to the CLI server** — forward verified payloads into the OODA loop:

```python
from codex.agents.brain_client import BrainClient

brain = BrainClient()   # points to localhost:8765
result = brain.ooda_process(
    input_data={"event": event, "event_type": "pull_request"},
    context={"source": "github_webhook"},
)
```

Equivalent via curl (from within a CLI step):

```bash
curl -sf -X POST http://localhost:8765/api/ooda/process \
  -H "Content-Type: application/json" \
  -d "{\"input\": $(echo "$EVENT_JSON" | python3 -c \"import json,sys; print(json.dumps({'event': json.load(sys.stdin)}))\"), \"context\": {\"source\": \"github_webhook\"}}"
```

---

### 2 · Calling GitHub as the App (JWT auth)

```python
import os
from codex.auth.github_app import GitHubApp, GitHubAppConfig

config = GitHubAppConfig(
    app_id=int(os.environ["GITHUB_APP_ID"]),
    private_key_pem=os.environ["GITHUB_APP_PRIVATE_KEY"],
    webhook_secret=os.environ.get("WEBHOOK_SECRET"),
)
app = GitHubApp(config)

# Get an installation access token (cached, auto-refreshed)
token = app.get_installation_token(
    installation_id=int(os.environ["GITHUB_APP_INSTALLATION_ID"]),
    permissions={"contents": "read", "pull_requests": "write"},
)
print(token.token)          # ghs_xxxx — use as Bearer token
print(token.is_expired())   # False
```

Pass the installation token to `BrainClient` for the remainder of the session:

```python
# Override the auth header for this specific request
result = brain.proxy_request(
    "GET",
    "https://api.github.com/repos/Aries-Serpent/_codex_/pulls",
    headers={"Authorization": f"Bearer {token.token}"},
)
```

---

### 3 · Calling GitHub with PAT fallback (CODEX_MASTER_KEY → CODEX_BACKUP_KEY)

For endpoints that require PAT scope (e.g. Actions Variables API):

```python
# Automatic retry: tries CODEX_MASTER_KEY first, falls back to CODEX_BACKUP_KEY
# on 401/403, then AGENT_GITHUB_TOKEN, then GITHUB_TOKEN.
data = app.pat_api_get(
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables"
)
```

The same fallback is available through `BrainClient` (which already implements
the same chain internally):

```python
vars_resp = brain.proxy_request(
    "GET",
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
)
```

---

### 4 · App Manifest (one-click installation)

```python
from codex.auth.github_app import build_app_manifest
import json

manifest = build_app_manifest(
    name="codex-cognitive-bot",
    url="https://aries-serpent.github.io/_codex_/",
    webhook_url=os.environ.get("WEBHOOK_RECEIVER_URL",
                               "https://api.your-cognitive-brain-server.com/webhook/github"),
    description="Cognitive Brain CI feedback + OODA loop automation agent",
    callback_urls=["https://aries-serpent.github.io/_codex_/auth/callback"],
    default_events=[
        "push", "pull_request", "pull_request_review",
        "issue_comment", "workflow_run", "check_run",
    ],
    default_permissions={
        "contents": "read",
        "pull_requests": "write",
        "checks": "write",
        "statuses": "write",
        "issues": "write",
        "metadata": "read",
    },
    public=False,
)

# Embed in HTML form for the manifest flow:
print(json.dumps(manifest, indent=2))
```

---

### 5 · CLI ↔ GitHub App — Session Quick-Start

```bash
# 1. Verify CLI server is up
curl -sf http://localhost:8765/api/health

# 2. Confirm token chain (MASTER → BACKUP)
python3 - <<'EOF'
from codex.auth.github_app import _resolve_github_token
for val, name in _resolve_github_token():
    status = "✅ set" if val else "❌ missing"
    print(f"  {name}: {status}")
EOF

# 3. Test GitHub App JWT generation
python3 - <<'EOF'
import os
from codex.auth.github_app import GitHubApp, GitHubAppConfig
cfg = GitHubAppConfig(
    app_id=int(os.environ.get("GITHUB_APP_ID", "1")),
    private_key_pem=os.environ.get("GITHUB_APP_PRIVATE_KEY", ""),
)
app = GitHubApp(cfg)
jwt = app.generate_jwt()
print(f"JWT (first 40 chars): {jwt[:40]}...")
EOF

# 4. Test PAT fallback via proxy
curl -sf -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d['status_code'])"
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_APP_ID` | For App JWT | Numeric App ID from GitHub App settings |
| `GITHUB_APP_PRIVATE_KEY` | For App JWT | PEM-encoded RSA-2048 private key |
| `GITHUB_APP_INSTALLATION_ID` | For install tokens | Installation ID (from webhook payload or API) |
| `WEBHOOK_SECRET` | For webhook verify | Shared secret set on the GitHub webhook |
| `WEBHOOK_RECEIVER_URL` | For webhook delivery | URL where GitHub delivers webhook payloads |
| `CODEX_MASTER_KEY` | For PAT calls | Full-scope PAT (primary) |
| `CODEX_BACKUP_KEY` | For PAT calls | Full-scope PAT (fallback when master fails) |
| `CODEX_CLI_API_URL` | For BrainClient | CLI server URL (default: `http://localhost:8765`) |

---

## Error Handling

| Situation | Behaviour |
|-----------|-----------|
| `CODEX_MASTER_KEY` returns 401/403 | `pat_api_get()` automatically retries with `CODEX_BACKUP_KEY` |
| All PAT tokens fail | `AuthenticationError("All PAT tokens exhausted…")` raised |
| Invalid webhook signature | `verify()` returns `False` — caller should return HTTP 401 |
| GitHub App JWT > 10 min | `ValueError("expiry_seconds must be ≤ 600")` raised |
| Private network `api_base_url` | `ValueError("api_base_url must point to a remote GitHub endpoint")` |

---

## References

- `src/codex/auth/github_app.py` — GitHub App client, WebhookVerifier, manifest builder
- `src/codex/agents/brain_client.py` — CLI API proxy client
- `cognitive_app/src/server/cli_api_server.py` — FastAPI server (`:8765`)
- `docs/agent/COGNITIVE_APP_CONNECTION_GUIDE.md` — Full CLI server reference
- `docs/agent/COPILOT_TOKEN_GUIDE.md` — Token priority matrix
- `docs/ops/WEBHOOK_REGISTRY.md` — Live webhook registry
