# GitHub Codespace — Copilot Agent Configuration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

> **Status:** NEW (PR #3503 W-126, 2026-03-05)
> **Session:** S114
> **Audience:** Copilot Coding Agents, repository maintainers
> **Related:** `.devcontainer/devcontainer.json`, `copilot-setup-steps.yml`,
> `docs/agent/COPILOT_TOKEN_GUIDE.md`, `docs/agent/GITHUB_APP_CLI_MAPPING.md`

---

## Existing remote VS Code workspace

The tracked [workspace settings](../../.vscode/settings.json),
[extension recommendations](../../.vscode/extensions.json),
[tasks](../../.vscode/tasks.json) and [debug configurations](../../.vscode/launch.json)
also support an already-running remote VS Code window without rebuilding a
container or running lifecycle scripts. The remaining guide describes the
devcontainer/service setup, not proof those facilities exist in this session
or prerequisites for ordinary local agent work. Native editing, tests and
debugging do not require administrative PATs or webhook activation.

1. Open the repository in the existing remote window. Install recommended
   extensions only when needed and permitted; recommendations are not evidence
   they are installed. Select **Python: Select Interpreter** and choose the
   existing supported Python 3.12 validation environment.
2. Use **Tasks: Run Task**. `Codex: inspect worktree` is dependency-free apart
   from Git. Python tasks prompt for the existing interpreter executable;
   process tasks pass it as an executable, not interpolated shell code.
   This choice is environment configuration, not renewed owner consent.
   Copilot's native `runTask` tool uses type-qualified IDs such as
   `process: Codex: inspect worktree`; the bare label can return "Task not found".
   `Codex: native runtime diagnostics` reports Python/workspace, presence of
   terminal/Git IPC and tool availability without exposing environment values.
   These are observed capabilities, not proof of signing or GitHub access.
   `Codex: native VS Code version` checks whether the CLI is actually usable
   in that terminal context; command presence alone is insufficient.
3. `Codex: validate CDX catalog` is read-only. It does not regenerate startup
   timestamps or invoke the unsupported `scripts.ci.cdx_context` module as a CLI.
4. `Codex: CDX focused tests` isolates the archive conftest and can skip five
   optional adapter integrations if no adapter is supplied. It is not full
   real-adapter validation. `Codex: CDX tests with real adapter` prompts for the
   authenticated adapter executable and the authenticated executable directories
   prepended to Linux PATH. Include the validation environment's `bin` directory
   for detect-secrets and the directory containing pinned Gitleaks; selecting a
   Python executable alone does not put its scanner launchers on PATH.
   Do not leave required paths empty. Invalid paths must fail,
   not be treated as a pass. Both use the five maintained CDX test files.
5. `Codex: offline Go adapter tests` requires a previously authenticated Go
   executable (selected by its task prompt) and populated verified module cache;
   it disables online fetching.
   `Codex: Rust advisory check` requires Cargo/cargo-deny. The frontend typecheck
   task requires the installed cognitive_app dependencies. Missing tools are
   explicit environment failures; restore only what the selected validation
   actually needs, through approved authenticated distribution.
6. F5 uses debugpy and the selected Python interpreter. Debug current development
   source or the fixed CDX context-test launch, never untrusted archived source.
   Use the Testing panel for selected tests, Problems for diagnostics, and
   Pylance/Rust Analyzer/Go for supported symbol navigation. Full pytest discovery
   is not the workspace default: the Testing panel starts with the five CDX
   files and does not rediscover on save. Configure the test paths for another
   owning-area task explicitly, or use its smallest CLI selector.
7. Use GitHub PR/Actions extensions or available authenticated tools for actual
   feedback and check evidence. Source Control uses real account/signing
   facilities; workspace settings grant no credentials or platform rights.
8. For custom agents, use **Chat: Open Customizations**, inspect the Agents entry
   and source, choose the intended Session Target and **CDX Archive Lifecycle**.
   An already-exposed agent tool is another candidate to reconcile, not proof of
   source binding or hosted activation. Record actual selection/invocation.

These files intentionally contain no session-specific interpreter paths,
credentials, blanket auto-approvals, automatic startup tasks or profile copies.
Other machine-local `.vscode/` data stays ignored. Configuration and extension
recommendations are reusable repository data, not a claim of hosted selection.

If a native task/terminal tool is unavailable to the current Copilot host, use
the same task command/arguments in the existing integrated terminal or authorized
CLI environment and report that limitation. The remote CLI needs its genuine
VS Code terminal IPC context; an error printed with exit zero is still failure.
Do not guess IPC values, launch another server or rewrite global PATH.
See the [human continuation plan](../../site/plans/cdx_archive_scanner_preflight_recovery/human_continuation_plan.md)
for minimal account/UI/administrative handbacks and the unchanged archive gates.

## Overview

A GitHub Codespace for this repository gives a Copilot agent the **same
environment** it gets inside GitHub Actions (`copilot-setup-steps.yml`), but
running interactively in the browser or VS Code. Every configuration file,
lifecycle script, and environment variable mirrors the Actions workflow exactly.

```
GitHub Actions (CI) GitHub Codespace (interactive)
 
copilot-setup-steps.yml .devcontainer/devcontainer.json
 Phase 1+2: system deps ≡ on-create.sh
 Phase 3+4: pip install ≡ update-content.sh
 Phase 5+6: env vars + auth ≡ post-create.sh
 Phase 7: start CLI server ≡ post-start.sh
 (attach) ≡ post-attach.sh (banner)
```

---

## File Structure

```
.devcontainer/
 devcontainer.json Master configuration
 scripts/
 on-create.sh Phase 1+2: system deps (runs once)
 update-content.sh Phase 3+4: pip install (re-runs on rebuild)
 post-create.sh Phase 5+6: env vars + auth report (once)
 post-start.sh Phase 7: start CLI API server (every start)
 post-attach.sh Banner + health check (every attach)
```

---

## Prerequisites — Admin Setup

Before any Copilot agent can use the Codespace, an org admin must configure
these **Codespace secrets** (Settings Codespaces Secrets):

| Secret | Required | Purpose |
|--------|----------|---------|
| `CODEX_MASTER_KEY` | **Yes** | Primary GitHub PAT (`repo` scope). Enables Variables API, Secrets API, Webhooks API. |
| `CODEX_BACKUP_KEY` | **Yes** | Fallback PAT — used automatically when master returns 401/403. |
| `CODEX_ADMIN_KEY` | For webhooks | Fine-grained PAT (Webhooks:write). Webhook management only. |
| `_GITHUB_APP_ID` | For GitHub App | Numeric App ID from github.com/settings/apps. |
| `_GITHUB_APP_PRIVATE_KEY` | For GitHub App | PEM RSA-2048 private key. Multi-line — paste as-is. |
| `_GITHUB_APP_INSTALLATION_ID` | For install tokens | Get from `GET /app/installations`. |
| `WEBHOOK_SECRET` | For webhook verify | Shared HMAC secret set on the GitHub webhook. |
| `WEBHOOK_RECEIVER_URL` | For activation | Public URL for webhook delivery. |

> Secrets set at the **org level** (Settings Codespaces Secrets select
> `Aries-Serpent/_codex_`) are automatically available to all Codespaces in the
> repository without per-user configuration.

---

## Lifecycle Execution Order

Codespaces runs devcontainer lifecycle hooks in this exact order:

```
Container pulled / built
 
 ① onCreateCommand
 on-create.sh
 • apt-get system packages
 • git lfs install --skip-smudge
 • mkdir .codex/sessions, artifacts
 
 ② updateContentCommand (re-runs on branch switch)
 update-content.sh
 • pip install pytest, ruff, black, mypy, ...
 • pip install -e .[dev]
 • pip install fastapi uvicorn httpx cryptography
 • npm ci (if package.json)
 • cargo build (if Cargo.toml)
 • pre-commit install
 
 ③ postCreateCommand (after first updateContent)
 post-create.sh
 • write ~/.codex_env (all CODEX_* vars)
 • auth token status report
 • write .codex/codespace_auth_status.json
 • load agent_context.json (repo variables)
 • validate python / gh / ruff / imports
 
 ④ postStartCommand (every container start)
 post-start.sh
 • kill stale CLI API server
 • nohup uvicorn ... :8765 (with auth token forwarding)
 • retry health-check × 5
 • verify GitHub App JWT generation
 
 ⑤ postAttachCommand (every terminal attach)
 post-attach.sh
 • print Copilot agent banner
 • show service status
 • show token status
 • print quick-start commands
```

---

## Environment Variables — Full Reference

These are set in `devcontainer.json containerEnv` (static) and
`post-create.sh ~/.codex_env` (dynamic). They match `copilot-setup-steps.yml`
exactly.

### Core Codex Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `CODEX_ENV` | `codespace-copilot-agent` | Environment tag |
| `CODEX_FORCE_CPU` | `1` | Disable GPU, use CPU-only PyTorch |
| `RAG_EMBEDDING_PROVIDER` | `tfidf` | Lightweight embeddings (no GPU needed) |
| `CODEX_LOG_LEVEL` | `INFO` | Log verbosity |
| `CODEX_DB_PATH` | `/workspaces/_codex_/.codex/codex.db` | SQLite history DB |
| `CODEX_SESSION_LOG_DIR` | `/workspaces/_codex_/.codex/sessions` | Session logs |
| `PYTHONPATH` | `/workspaces/_codex_/src` | Editable package path |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout/stderr |
| `GIT_LFS_SKIP_SMUDGE` | `1` | Skip LFS blobs on checkout |

### CLI API Server Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `CODEX_CLI_API_URL` | `http://localhost:8765` | `BrainClient` server URL |
| `COPILOT_CLI_BASE_URL` | `http://localhost:8765` | Legacy alias |
| `GITHUB_COPILOT_AGENT` | `true` | Copilot identity flag |

### Auth Token Variables (from Codespace secrets)

| Variable | Source | Notes |
|----------|--------|-------|
| `CODEX_MASTER_KEY` | Codespace secret | Primary PAT — auto-injected by Codespaces |
| `CODEX_BACKUP_KEY` | Codespace secret | Fallback — tried on 401/403 |
| `CODEX_ADMIN_KEY` | Codespace secret | Webhook operations only |
| `_GITHUB_APP_ID` | Codespace secret | Numeric App ID |
| `_GITHUB_APP_PRIVATE_KEY` | Codespace secret | PEM key (multi-line OK) |
| `_GITHUB_APP_INSTALLATION_ID` | Codespace secret | Installation ID |
| `WEBHOOK_SECRET` | Codespace secret | HMAC secret |

---

## Token Resolution Chain (Codespace vs Actions)

Both environments use the **same priority chain**:

```
 GitHub Actions Codespace
 
1 (primary) job env: CODEX_MASTER_KEY ≡ Codespace secret env var
2 (backup) job env: CODEX_BACKUP_KEY ≡ Codespace secret env var
3 (alias) AGENT_GITHUB_TOKEN ≡ GITHUB_TOKEN (auto-provided)
4 (fallback) GITHUB_TOKEN ≡ GITHUB_TOKEN (auto-provided)
```

In Codespaces, `GITHUB_TOKEN` is **automatically provided** by GitHub with
`contents:read` scope. It cannot access the Variables API — use
`CODEX_MASTER_KEY` for that.

The `GitHubApp.pat_api_get()` method and `BrainClient.proxy_request()` both
implement this chain automatically — no manual header construction needed.

---

## CLI API Server

The Cognitive Brain CLI API server starts automatically via `post-start.sh`.

```bash
# Verify it is running
curl -s http://localhost:8765/api/health

# Use BrainClient (Python)
from codex.agents.brain_client import BrainClient
brain = BrainClient() # auto-discovers CODEX_CLI_API_URL
brain.is_available() # True when server is up

# Proxy a GitHub API call (auto-injects CODEX_MASTER_KEY CODEX_BACKUP_KEY)
resp = brain.proxy_request("GET",
 "https://api.github.com/repos/Aries-Serpent/_codex_")

# Run a shell command
result = brain.run_command("git log --oneline -5")
print(result["stdout"])

# Server logs
tail -f .codex/cli_api_server.log
```

If the server crashes:

```bash
# Restart it
bash .devcontainer/scripts/post-start.sh

# Or manually
nohup uvicorn cognitive_app.src.server.cli_api_server:app \
 --host 0.0.0.0 --port 8765 --log-level warning \
 > .codex/cli_api_server.log 2>&1 &
```

---

## GitHub App in Codespace

```python
import os
from codex.auth.github_app import GitHubApp, GitHubAppConfig, _resolve_github_token

# 1. Check token chain 
for val, name in _resolve_github_token():
 status = "" if val else ""
 print(f" {status} {name}")

# 2. Generate App JWT (needs _GITHUB_APP_ID + _GITHUB_APP_PRIVATE_KEY) 
cfg = GitHubAppConfig(
 app_id=int(os.environ["_GITHUB_APP_ID"]),
 private_key_pem=os.environ["_GITHUB_APP_PRIVATE_KEY"],
 webhook_secret=os.environ.get("WEBHOOK_SECRET"),
)
app = GitHubApp(cfg)
jwt = app.generate_jwt()

# 3. Get installation token 
token = app.get_installation_token(
 installation_id=int(os.environ["_GITHUB_APP_INSTALLATION_ID"]),
)
print(token.token) # ghs_xxxx
print(token.is_expired()) # False

# 4. PAT fallback (auto MASTER_KEY BACKUP_KEY) 
data = app.pat_api_get(
 "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables"
)
```

---

## Webhook Verification in Codespace

```python
from codex.auth.github_app import WebhookVerifier
import os

verifier = WebhookVerifier(secret=os.environ["WEBHOOK_SECRET"])

# Verify a payload (e.g., from a test script)
payload = b'{"action":"opened","number":42}'
sig = verifier.compute_signature(payload) # "sha256=abc123..."
assert verifier.verify(payload, sig) is True # 

# Forward to OODA loop via CLI server
from codex.agents.brain_client import BrainClient
import json

brain = BrainClient()
result = brain.ooda_process(
 input_data={"event": json.loads(payload), "event_type": "pull_request"},
 context={"source": "webhook"},
)
```

---

## Ports

| Port | Service | Auto-forward |
|------|---------|-------------|
| `8765` | Cognitive Brain CLI API | `notify` — click to open |
| `8766` | GitHub App webhook receiver | `silent` |
| `3000` | React frontend (cognitive_app) | `openPreview` |

All ports are defined in `devcontainer.json forwardPorts` and are accessible
from the Codespace public URL when forwarded.

---

## VS Code Extensions (pre-installed)

| Extension | Purpose |
|-----------|---------|
| `github.copilot` | **Required** — Copilot agent core |
| `github.copilot-chat` | Chat interface for agent |
| `github.vscode-pull-request-github` | PR management |
| `github.vscode-github-actions` | Workflow editing + run status |
| `ms-python.python` | Python language support |
| `charliermarsh.ruff` | Fast Python linter + formatter |
| `ms-python.mypy-type-checker` | Type checking |
| `ms-azuretools.vscode-docker` | Docker (Dockerfile.preview) |
| `redhat.vscode-yaml` | YAML validation (workflows) |

---

## Troubleshooting

### Server not starting
```bash
cat .codex/cli_api_server.log # check startup errors
bash .devcontainer/scripts/post-start.sh # restart
```

### Token not available
```bash
# Check which secrets are set
python3 -c "
from codex.auth.github_app import _resolve_github_token
for val, name in _resolve_github_token():
 print(f'{\"\" if val else \"\"} {name}')
"
# If missing: Settings Codespaces Secrets add the secret
```

## Import errors
```bash
bash .devcontainer/scripts/update-content.sh # re-install deps
```

### GitHub App JWT fails
```bash
# Check _GITHUB_APP_PRIVATE_KEY is in PEM format
echo "$_GITHUB_APP_PRIVATE_KEY" | head -1 # should be "-----BEGIN RSA PRIVATE KEY-----" <!-- pragma: allowlist secret -->
```

---

## Parity Matrix — Codespace vs GitHub Actions

| copilot-setup-steps.yml step | devcontainer equivalent | Status |
|------------------------------|------------------------|--------|
| Phase 1: checkout + git lfs | `on-create.sh` | |
| Phase 2: system deps (apt) | `on-create.sh` | |
| Phase 3: Python venv + pip | `update-content.sh` | |
| Phase 4: Node + Rust | `update-content.sh` | |
| Phase 5: Rust build | `update-content.sh` | |
| Phase 6: Set Codex env vars | `post-create.sh` `~/.codex_env` | |
| Phase 6: Export auth tokens | Codespace secrets env vars | |
| Phase 6: Load agent config | `post-create.sh` | |
| Phase 7: Start CLI server | `post-start.sh` | |
| Phase 7: Health-check retry | `post-start.sh` | |
| Phase 7: Auth token banner | `post-attach.sh` | |
| `COPILOT_RUNNER_PROFILE` | `hostRequirements` (4 CPU / 8 GB) | |

---

## References

- `.devcontainer/devcontainer.json` — master Codespace config
- `.devcontainer/scripts/` — lifecycle scripts
- `.github/workflows/copilot-setup-steps.yml` — Actions equivalent
- `docs/agent/COPILOT_TOKEN_GUIDE.md` — full token reference
- `docs/agent/GITHUB_APP_CLI_MAPPING.md` — GitHub App CLI mapping
- `docs/plans/custom-preview-image.md` — GHCR preview image plan
- `src/codex/auth/github_app.py` — GitHub App package
- `src/codex/agents/brain_client.py` — CLI API client
