# Copilot Coding Agent — Token & Authentication Guide

**Last Updated:** 2026-06-22

> **Status:** ✅ CURRENT (PR #3499 W-125, 2026-03-05 — webhook token requirements added)
> **Audience:** Copilot Coding Agent sessions, CI/CD pipeline authors
> **Related:** `docs/agent/COGNITIVE_APP_CONNECTION_GUIDE.md`, `scripts/tools/variable_manager.py`

---

## Overview

Every Copilot Coding Agent session has access to **up to four authentication tokens**.
Each token has a different scope and capability. This guide explains what each token is,
how it reaches your session, how to use it, and what it can and cannot do.

---

## Token Priority & Availability

| Priority | Token | Set in workflow | Exported to `GITHUB_ENV` | Scope / Capability |
|----------|-------|----------------|--------------------------|-------------------|
| **1** | `CODEX_MASTER_KEY` | Job `env:` → `secrets.CODEX_MASTER_KEY` | ✅ "🔑 Export Auth Tokens" step | Full PAT (classic) — `repo` scope. Can read/write **all** GitHub API resources including **variables**, secrets, and settings. **Required for variables API.** |
| **2** | `CODEX_BACKUP_KEY` | Job `env:` → `secrets.CODEX_BACKUP_KEY` | ✅ same step | Fallback PAT — same capability as above, used when master key is absent. |
| **3** | `AGENT_GITHUB_TOKEN` | Derived from `GITHUB_TOKEN` | ✅ same step | Alias for `GITHUB_TOKEN`; stable env var name for agent code. **Cannot access variables API.** |
| **4** | `GITHUB_TOKEN` | Auto-provided by GitHub Actions | Already in env | Scoped installation token. Can push code, comment on PRs, dispatch workflows. **Cannot access the Actions Variables API** (requires PAT `repo` scope). |

> **Webhook operations also accept `CODEX_ADMIN_KEY`** (a fine-grained PAT with Webhooks:write)
> as the highest-priority auth source. `webhook_configurator.py` resolves tokens in the order:
> `CODEX_ADMIN_KEY` → `CODEX_MASTER_KEY`. `GITHUB_TOKEN` **cannot** manage webhooks.

All four tokens are resolved automatically by `BrainClient._auth_header()` and
`VariableManager._resolve_token()` — **no manual header construction needed**.

---

## How Tokens Reach the Agent Session

```
copilot-setup-steps.yml
│
├── job env: block
│   ├── CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}   ← job-level only
│   └── CODEX_BACKUP_KEY: ${{ secrets.CODEX_BACKUP_KEY }}   ← job-level only
│
├── "🔑 Export Auth Tokens to Agent Environment" step
│   ├── echo "CODEX_MASTER_KEY=..."   >> $GITHUB_ENV   ← persists to agent
│   ├── echo "CODEX_BACKUP_KEY=..."   >> $GITHUB_ENV   ← persists to agent
│   └── echo "AGENT_GITHUB_TOKEN=..."  >> $GITHUB_ENV  ← persists to agent
│
├── "💻 Start CLI API Server" step
│   ├── export CODEX_MASTER_KEY="${CODEX_MASTER_KEY:-}"   ← forwarded to uvicorn
│   ├── export CODEX_BACKUP_KEY="${CODEX_BACKUP_KEY:-}"
│   └── export AGENT_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
│
└── Copilot Agent process inherits GITHUB_ENV → all four tokens available
```

> **Why two steps?** Job-level `env:` values are available to setup steps but
> are **not automatically added to `GITHUB_ENV`**. The "🔑 Export Auth Tokens"
> step bridges this gap by explicitly writing the values to the GITHUB_ENV file
> that the agent process reads.

---

## Permission Matrix

| API Operation | `CODEX_MASTER_KEY` | `CODEX_BACKUP_KEY` | `AGENT_GITHUB_TOKEN` / `GITHUB_TOKEN` |
|---------------|:-----------------:|:-----------------:|:-------------------------------------:|
| **Repo variables** — list | ✅ | ✅ | ❌ requires PAT `repo` scope |
| **Repo variables** — create/update/delete | ✅ | ✅ | ❌ requires PAT `repo` scope |
| **Environment variables** — list | ✅ | ✅ | ❌ requires PAT `repo` scope |
| **Environment variables** — create/update/delete | ✅ | ✅ | ❌ requires PAT `repo` scope |
| **Org variables** — list | ✅ | ✅ | ❌ |
| **Org variables** — create/update/delete | ✅ | ✅ | ❌ |
| **Repo secrets** — read/write | ✅ | ✅ | ❌ |
| **Org secrets** — read/write | ✅ (if org admin) | ✅ (if org admin) | ❌ |
| **Code push / commits** | ✅ | ✅ | ✅ (contents:write) |
| **Issues / PRs** | ✅ | ✅ | ✅ (issues/pull-requests:write) |
| **Workflow dispatch** | ✅ | ✅ | ✅ (actions:write) |
| **GitHub API (read-only)** — repos, runs, PRs | ✅ | ✅ | ✅ |
| **Webhooks** — list | ✅ (`admin:repo_hook`) | ✅ (`admin:repo_hook`) | ❌ 403 — requires PAT with `admin:repo_hook` or fine-grained Webhooks:read |
| **Webhooks** — create/update/delete | ✅ (`admin:repo_hook`) | ✅ (`admin:repo_hook`) | ❌ 403 — requires `CODEX_ADMIN_KEY` (Webhooks:write) or `CODEX_MASTER_KEY` (`admin:repo_hook`) |

> **Key constraint:** GitHub's Actions Variables API requires a classic PAT with `repo` scope
> OR a fine-grained PAT with `Variables: read/write`. **`GITHUB_TOKEN` cannot access
> the variables API** regardless of the `actions:` permission level in the workflow.
> `CODEX_MASTER_KEY` is the only token in this chain that can manage variables.

> **Summary:** Use `CODEX_MASTER_KEY` for any GitHub API call. Use `GITHUB_TOKEN`
> / `AGENT_GITHUB_TOKEN` as a fallback for repo/env variable management only.

> **Webhook operations (scripts/ci/webhook_configurator.py)** use a dedicated token hierarchy:
> 1. `CODEX_ADMIN_KEY` — fine-grained PAT with **Webhooks: write** scope (preferred for least-privilege)
> 2. `CODEX_MASTER_KEY` — classic PAT with `admin:repo_hook` scope (fallback)
>
> `GITHUB_TOKEN` returns HTTP 403 for all webhook API calls — this is expected and correct.
> Set `CODEX_ADMIN_KEY` as a repo/org secret with only Webhooks:read+write to follow least-privilege.
> The `apply-webhooks` job in `agent_infrastructure_manager.yml` also accepts `WEBHOOK_RECEIVER_URL`
> as a repo variable (not a secret) to override the placeholder URL without editing config files.

---

## Using Tokens in Agent Code

### 1 — Automatic (recommended)

```python
from codex.agents.brain_client import BrainClient

brain = BrainClient()
# Auth is auto-injected from CODEX_MASTER_KEY → GITHUB_TOKEN priority chain
resp = brain.proxy_request("GET",
    "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables")
```

## 2 — VariableManager (repo / env / org variables)

```python
from scripts.tools.variable_manager import VariableManager

vm = VariableManager()   # auto-resolves best available token

# Repo variables
vm.create_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR", "hello_agent")
vm.update_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR", "updated_val")
vm.list_repo_vars("Aries-Serpent", "_codex_")
vm.delete_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR")

# Environment variables
vm.create_env_var("Aries-Serpent", "_codex_", "production", "MY_ENV_VAR", "val")

# Org variables
vm.create_org_var("Aries-Serpent", "COPILOT_ORG_VAR", "val", visibility="all")

# Live test (create → verify → update → verify → delete)
vm.run_live_test("Aries-Serpent", "_codex_")
```

## 3 — CLI (bash tool / shell scripts)

```bash
# List repo variables
python scripts/tools/variable_manager.py list repo Aries-Serpent _codex_

# Create a test variable
python scripts/tools/variable_manager.py create repo Aries-Serpent _codex_ \
  COPILOT_TEST_VAR "hello_from_agent"

# Update it
python scripts/tools/variable_manager.py update repo Aries-Serpent _codex_ \
  COPILOT_TEST_VAR "updated_value"

# Delete it
python scripts/tools/variable_manager.py delete repo Aries-Serpent _codex_ \
  COPILOT_TEST_VAR

# Full live test
python scripts/tools/variable_manager.py test

# Environment variables
python scripts/tools/variable_manager.py list env Aries-Serpent _codex_ production

# Org variables
python scripts/tools/variable_manager.py list org Aries-Serpent
```

## 4 — Direct curl via CLI API Server

```bash
# Auto-injects CODEX_MASTER_KEY (or GITHUB_TOKEN fallback) from server env
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
    "body": {"name": "COPILOT_TEST_VAR", "value": "hello_from_agent"}
  }'
```

## 5 — Check which token is active

```bash
python3 -c "
import os
priority = ['CODEX_MASTER_KEY','CODEX_BACKUP_KEY','AGENT_GITHUB_TOKEN','GITHUB_TOKEN']
for k in priority:
    v = os.environ.get(k, '')
    if v:
        print(f'Active token: {k} ({len(v)} chars)')
        break
else:
    print('⚠️  No auth token found in environment')
"
```

---

## Agent Token Delegation

When a PR has **Agent Token Delegation** enabled (checkbox ticked in PR description)
and the owner approves the workflow run, the delegation workflow:

1. Sets `COPILOT_AGENT_AUTH_ENABLED=true` repo variable
2. Writes `.codex/agent_auth_session.json` with provenance metadata
3. Updates `COGNITIVE_BRAIN_ALLOWED_ACTORS` with the delegated actors list

```json
{
  "issued_at": "2026-03-05T04:44:23Z",
  "expires_at": 1772700263,
  "issued_by": "agent-auth-delegation",
  "run_id": "22702507580",
  "pr_number": "3497",
  "note": "Provenance-chain token. Allows all agent sessions to bypass owner_approval_guard within TTL."
}
```

The delegation **does not change which auth tokens are available** — it changes
what the agent is **authorised to do** with those tokens (bypasses the
`owner_approval_guard` gate within the TTL).

Check delegation status:

```python
import json, os, time
session = json.load(open(".codex/agent_auth_session.json"))
expired = int(time.time()) > session.get("expires_at", 0)
print(f"Delegation active: {not expired}")
print(f"Issued by: {session['issued_by']} on {session['issued_at']}")
```

---

## Troubleshooting

### `403 Resource not accessible by integration`

```
Token source    → GITHUB_TOKEN (no repo scope)
Affected APIs   → secrets, org variables, some advanced settings
Fix             → Use CODEX_MASTER_KEY (must be set as org secret)
```

### `401 Bad credentials`

```
Token source    → Token is expired or invalid
Fix             → Re-trigger agent-auth-delegation workflow to refresh session
                  Or: rotate CODEX_MASTER_KEY org secret
```

### `CODEX_MASTER_KEY` not in agent process env

```
Symptom         → python3 -c "import os; print(os.environ.get('CODEX_MASTER_KEY','MISSING'))"
                  → MISSING
Cause           → "🔑 Export Auth Tokens" step was not executed or secret is empty
Fix             → Verify secrets.CODEX_MASTER_KEY is set in org/repo secrets
                  Check copilot-setup-steps.yml step "🔑 Export Auth Tokens to Agent Environment"
```

### CLI API Server returns `401` for GitHub API calls

```
Symptom         → POST /api/request → {"status_code": 401, ...}
Cause           → Server process doesn't have CODEX_MASTER_KEY in its env
                  (setup steps forwarded it to GITHUB_ENV but server started before that step)
Fix             → Verify step order: "🔑 Export Auth Tokens" MUST run BEFORE
                  "💻 Start CLI API Server".
                  The server startup step also runs:
                    export CODEX_MASTER_KEY="${CODEX_MASTER_KEY:-}"
                  to explicitly forward the key to the uvicorn process.
```

### `X-OAuth-Scopes: ` (empty scopes on GITHUB_TOKEN)

```
Symptom         → curl -sI -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/ |
                  grep X-OAuth-Scopes
                  → X-OAuth-Scopes:
Explanation     → GITHUB_TOKEN is a GitHub Apps installation token, NOT a classic OAuth token.
                  It has no "scopes" — its permissions come from the workflow permissions: block.
                  This is NORMAL. The token is valid; empty scopes ≠ no permissions.
Fix             → Ensure workflow has `actions: write` in permissions: block.
```

---

## Quick Verification Script

Run at the start of every agent session to confirm all tokens and the CLI server
are functioning:

```bash
python3 - <<'EOF'
import os, sys, json, urllib.request, urllib.error

print("=" * 55)
print(" Copilot Agent Token & CLI Server Verification")
print("=" * 55)

# 1. Token inventory
priority = [
    ("CODEX_MASTER_KEY",   "Full PAT (repo scope)"),
    ("CODEX_BACKUP_KEY",   "Fallback PAT"),
    ("AGENT_GITHUB_TOKEN", "GITHUB_TOKEN alias"),
    ("GITHUB_TOKEN",       "Actions installation token"),
]
active_token = ""
active_name  = ""
for name, desc in priority:
    val = os.environ.get(name, "")
    status = f"✅ {len(val)} chars" if val else "❌ NOT SET"
    print(f"  {name:<25} {status:>15}  ({desc})")
    if val and not active_token:
        active_token, active_name = val, name

print(f"\n  Active token: {active_name or 'NONE'}")

# 2. GitHub API test
if active_token:
    req = urllib.request.Request(
        "https://api.github.com/repos/Aries-Serpent/_codex_",
        headers={
            "Authorization": f"Bearer {active_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec
            d = json.loads(resp.read())
            print(f"  GitHub API (repo info):     ✅ {d['full_name']}")
    except urllib.error.HTTPError as e:
        print(f"  GitHub API (repo info):     ❌ HTTP {e.code}")
    except Exception as e:
        print(f"  GitHub API (repo info):     ❌ {e}")

# 3. CLI API server
try:
    req = urllib.request.Request("http://localhost:8765/api/health")
    with urllib.request.urlopen(req, timeout=3) as resp:  # nosec
        h = json.loads(resp.read())
        print(f"  CLI API server (:8765):     ✅ status={h.get('status')}")
except Exception as e:
    print(f"  CLI API server (:8765):     ❌ {e}")

# 4. Delegation status
try:
    sess = json.load(open(".codex/agent_auth_session.json"))
    import time
    expired = int(time.time()) > sess.get("expires_at", 0)
    flag = "❌ EXPIRED" if expired else "✅ ACTIVE"
    print(f"  Agent token delegation:     {flag} (issued {sess.get('issued_at','')})")
except Exception:
    print("  Agent token delegation:     ⚠️  session file not found")

print("=" * 55)
EOF
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/agent/COGNITIVE_APP_CONNECTION_GUIDE.md` | CLI API Server full reference + variable management |
| `scripts/tools/variable_manager.py` | CRUD tool — repo/env/org variables |
| `tests/agents/test_variable_management.py` | Unit test suite for variable manager |
| `src/codex/agents/brain_client.py` | BrainClient — typed Python client |
| `.github/workflows/copilot-setup-steps.yml` | Setup steps — token export implementation |
| `.github/workflows/agent-auth-delegation.yml` | Delegation workflow — session token issuance |
| `.codex/agent_auth_session.json` | Active delegation session metadata |
