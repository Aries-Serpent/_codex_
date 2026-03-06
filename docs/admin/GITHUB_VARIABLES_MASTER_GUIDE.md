# GitHub Variables & Secrets — Master Reference Guide

> **Version:** 1.3.0 (W-135, 2026-03-06)  
> **Owner:** @mbaetiong  
> **Status:** ✅ Current — reflects live state as of 2026-03-06 (authoritative export from mbaetiong, second pass)  
> **Audience:** Human admins, Copilot agents, CI/CD authors  
> **Auto-synced by:** `repo-var-sync-schedule.yml` (daily 06:00 UTC → `.codex/agent_context.json`)

> ⚠️ **This is the single source of truth.** All other variable docs link here.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [How to Set Variables — Quick Links](#2-how-to-set-variables--quick-links)
3. [Organization Secrets](#3-organization-secrets)
4. [Repository Secrets](#4-repository-secrets)
5. [Environment Secrets (Aries_Serpent_codex_)](#5-environment-secrets-aries_serpent_codex_)
6. [Repository Variables](#6-repository-variables)
7. [Environment Variables (Aries_Serpent_codex_)](#7-environment-variables-aries_serpent_codex_)
8. [Codespace Secrets](#8-codespace-secrets)
9. [Workflow-Defined env: Variables](#9-workflow-defined-env-variables)
10. [Known Issues & Inconsistencies](#10-known-issues--inconsistencies)
11. [Troubleshooting](#11-troubleshooting)
12. [Related Documentation](#12-related-documentation)
13. [⛔ Still Missing — Variables/Secrets Not Yet Provided](#13--still-missing--variablessecrets-not-yet-provided)

---

## 1. Architecture Overview

GitHub provides **six distinct storage layers** for variables and secrets. Choosing the wrong layer is the most common misconfiguration.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Variable Storage Hierarchy                        │
│                                                                      │
│  🏢 ORGANIZATION LEVEL  (Aries-Serpent)                             │
│  ├─ Org Secrets       → shared across all repos in org              │
│  └─ Org Variables     → [none currently, use repo vars instead]     │
│                                                                      │
│  📦 REPOSITORY LEVEL  (Aries-Serpent/_codex_)                       │
│  ├─ Repo Secrets      → encrypted, not readable by agents           │
│  └─ Repo Variables    → readable plaintext, writable via API        │
│                                                                      │
│  🌍 ENVIRONMENT LEVEL  (Aries_Serpent_codex_ environment)           │
│  ├─ Env Secrets       → override repo secrets for this env          │
│  └─ Env Variables     → override repo variables for this env        │
│                                                                      │
│  💻 CODESPACE LEVEL  (org or user-scoped)                           │
│  └─ Codespace Secrets → injected into interactive Codespace only    │
└─────────────────────────────────────────────────────────────────────┘

Resolution order (GitHub Actions): Env > Repo > Org (most specific wins)
Token access:  CODEX_MASTER_KEY > CODEX_BACKUP_KEY > GITHUB_TOKEN
```

**Key constraints:**
- `GITHUB_TOKEN` **cannot** read/write the Variables API — requires `CODEX_MASTER_KEY` (classic PAT, `repo` scope).
- Secrets are **never** readable by agents or logs — only injected as env vars.
- Env-level values **silently override** repo-level values of the same name.

---

## 2. How to Set Variables — Quick Links

| Storage Type | GitHub UI Location | API / CLI |
|---|---|---|
| **Org Secrets** | [Settings → Security → Secrets → Actions](https://github.com/organizations/Aries-Serpent/settings/secrets/actions) | `gh secret set NAME --org Aries-Serpent` |
| **Org Variables** | [Settings → Security → Variables → Actions](https://github.com/organizations/Aries-Serpent/settings/variables/actions) | `gh variable set NAME --org Aries-Serpent` |
| **Repo Secrets** | [Settings → Secrets and variables → Actions → Secrets tab](https://github.com/Aries-Serpent/_codex_/settings/secrets/actions) | `gh secret set NAME --repo Aries-Serpent/_codex_` |
| **Repo Variables** | [Settings → Secrets and variables → Actions → Variables tab](https://github.com/Aries-Serpent/_codex_/settings/variables/actions) | `gh variable set NAME --body VALUE --repo Aries-Serpent/_codex_` |
| **Env Secrets** | [Settings → Environments → Aries_Serpent_codex_ → Secrets](https://github.com/Aries-Serpent/_codex_/settings/environments) | `gh secret set NAME --env Aries_Serpent_codex_ --repo Aries-Serpent/_codex_` |
| **Env Variables** | [Settings → Environments → Aries_Serpent_codex_ → Variables](https://github.com/Aries-Serpent/_codex_/settings/environments) | `gh variable set NAME --env Aries_Serpent_codex_ --repo Aries-Serpent/_codex_` |
| **Codespace Secrets (org)** | [Settings → Codespaces → Secrets](https://github.com/organizations/Aries-Serpent/settings/secrets/codespaces) | `gh secret set NAME --app codespaces --org Aries-Serpent` |
| **Codespace Secrets (user)** | [github.com/settings/secrets/codespaces](https://github.com/settings/secrets/codespaces) | `gh secret set NAME --app codespaces` |

---

## 3. Organization Secrets

> **Location:** [Aries-Serpent → Settings → Security → Secrets → Actions](https://github.com/organizations/Aries-Serpent/settings/secrets/actions)  
> **Referenced in workflows as:** `${{ secrets.NAME }}`  
> **Access via API:** Requires `CODEX_MASTER_KEY` or org-admin token

| # | Secret Name | Status | Last Updated | Purpose | Required By |
|---|---|---|---|---|---|
| 1 | `CODECOV_TOKEN` | ✅ Present | 2 months ago | Code coverage upload to codecov.io | `coverage*.yml` workflows |
| 2 | `CODEX_ADMIN_KEY` | ✅ Present | 3 hours ago | Fine-grained PAT (`Webhooks:write`). Used for `webhook_configurator.py` least-privilege mode. | `apply-webhooks` job in `agent_infrastructure_manager.yml` |
| 3 | `CODEX_BACKUP_KEY` | ✅ Present | 5 days ago | Fallback GitHub PAT — auto-used on 401/403 from `CODEX_MASTER_KEY`. Same scope as master. | All auth-delegation workflows, `variable_manager.py`, `brain_client.py`, `github_app.py` |
| 4 | `CODEX_MASTER_KEY` | ✅ Present | yesterday | Primary full-scope GitHub PAT (classic, `repo` scope + `admin:repo_hook`). **Required for Variables API, Secrets API, Webhooks API.** Recently rotated — next rotation due ~90 days from 2026-03-05. | `agent-auth-delegation.yml`, `variable_manager.py`, `webhook_configurator.py`, `brain_client.py` |
| 5 | `HF_TOKEN` | ✅ Present | 2 months ago | HuggingFace API token for model downloads | ML training workflows |
| 6 | `NPM_TOKEN` | ✅ Present | 2 months ago | npm publish authentication | Node.js package publish workflows |
| 7 | `PYPI_TOKEN` | ✅ Present | 2 months ago | PyPI publish authentication | Python package publish workflows |
| 8 | `RAG_OPENAI_KEY` | ✅ Present | 3 weeks ago | OpenAI API key for RAG embeddings | RAG index build workflows |
| 9 | `_CODEX_ACTION_RUNNER` | ✅ Present | 2 months ago | Runner registration token for self-hosted Actions runners | Runner registration |
| 10 | `_GITHUB_APP_CLIENT_SECRET` | ✅ Present | 1 hour ago | GitHub App OAuth client secret for web-flow App authentication | `github_app.py`, OAuth web-flow auth |
| 11 | `_GITHUB_APP_ID` | ✅ Present | 1 hour ago | Numeric GitHub App ID for RS256 JWT generation | `github_app.py`, App JWT auth flows |
| 12 | `_GITHUB_APP_INSTALLATION_ID` | ✅ Present | 1 hour ago | App installation ID for generating installation access tokens | `github_app.py`, installation token flows |
| 13 | `_GITHUB_APP_PRIVATE_KEY` | ✅ Present | 1 hour ago | RSA-2048 PEM private key for signing GitHub App JWTs | `github_app.py`, RS256 JWT signing |

> ✅ **`CODEX_MASTER_KEY` was rotated on 2026-03-05.** Next rotation due ~2026-06-03 (90-day cycle).  
> See [`docs/ops/secrets_rotation_runbook.md`](../ops/secrets_rotation_runbook.md) for the full rotation procedure.

**Token chain in code:** `CODEX_MASTER_KEY → CODEX_BACKUP_KEY → AGENT_GITHUB_TOKEN → GITHUB_TOKEN`  
This is enforced by `_resolve_github_token()` in `src/codex/auth/github_app.py` and `scripts/tools/variable_manager.py`.

### GitHub App Authentication Secrets (`_GITHUB_APP_*`)

The four `_GITHUB_APP_*` secrets were added 2026-03-06 to support GitHub App–based authentication
(RS256 JWT flow) as an alternative to PAT-based auth. They are consumed by `src/codex/auth/github_app.py`.

> **Codespace note:** These org Actions secrets are **separate** from Codespace secrets.
> Codespace-based agent sessions that need GitHub App auth must also have these values set at the
> Codespace level (see [§8](#8-codespace-secrets)). The naming convention (leading `_`) marks them
> as system/infrastructure secrets managed by the org admin.

---

## 4. Repository Secrets

> **Location:** [Settings → Secrets and variables → Actions → Secrets tab](https://github.com/Aries-Serpent/_codex_/settings/secrets/actions)  
> **Referenced in workflows as:** `${{ secrets.NAME }}`

| # | Secret Name | Status | Last Updated | Purpose | Notes |
|---|---|---|---|---|---|
| 1 | `CODEX_GHP_TOKEN_BASE64` | ✅ Present | 2 months ago | Base64-encoded GitHub token for copilot-with-mcp workflow | Decoder priority #3 in `copilot_token_decoder.py` |
| 2 | `CODEX_GHP_TOKEN_HEX` | ✅ Present | 2 months ago | Hex-encoded GitHub token (alternative encoding) | Decoder priority #4 |
| 3 | `CODEX_GHP_TOKEN_SHA256` | ✅ Present | 2 months ago | One-way SHA-256 hash of GHP token for integrity validation | Verification only — not a usable token |
| 4 | `CODEX_REPO_ID` | ✅ Present | 6 hours ago | Repository numeric ID (GitHub internal) | Used in manifest generation |
| 5 | `CODEX_WEBHOOK_SECRET` | ✅ Present | 12 minutes ago | HMAC-SHA256 shared secret for incoming webhook verification | `WebhookVerifier` in `src/codex/auth/github_app.py` |
| 6 | `OPENAI_API_KEY` | ✅ Present | 5 hours ago | OpenAI API key for LLM agent operations | Consumed by `brain_client.py` and LLM-based CI workflows |
| 7 | `_CODEX_BOT_RUNNER` | ⚠️ Present | **7 months ago** | Bot runner registration token | Potentially stale — consider rotating. 90-day guideline exceeded. |

### Token Decoder Priority Order

```
1. CODEX_GHP_TOKEN_CONFIG   (Combined AES — not currently set)
2. CODEX_GHP_TOKEN_BASE64   ✅ (present — simplest, recommended)
3. CODEX_GHP_TOKEN_HEX      ✅ (present — alternative)
4. GITHUB_TOKEN             (auto-provided by Actions)
```

---

## 5. Environment Secrets (`Aries_Serpent_codex_`)

> **Location:** [Settings → Environments → Aries_Serpent_codex_](https://github.com/Aries-Serpent/_codex_/settings/environments)  
> **Override scope:** These override org/repo secrets for jobs using `environment: Aries_Serpent_codex_`

| # | Secret Name | Status | Last Updated | Value | Issue |
|---|---|---|---|---|---|
| 1 | `CODEX_ENVIRONMENT_RUNNER` | ✅ Present | 7 months ago | *(secret)* | May need rotation |
| 2 | `CODEX_RUNNER_SHA256` | ✅ Present | 7 months ago | *(secret hash)* | May need rotation |
| 3 | `CODEX_RUNNER_TOKEN` | ⚠️ Present | **7 months ago** | *(secret)* | Potentially stale — runner tokens typically expire. Verify or rotate. |

> ✅ **Issue 1 resolved (2026-03-06):** `CODEX_ENV_NODE_VERSION` was previously stored here as an
> environment secret. It has been **deleted** from env secrets and **recreated** as an environment
> variable (see [§7](#7-environment-variables-aries_serpent_codex_)). Node.js version strings are
> non-sensitive and should be variables, not secrets.

---

## 6. Repository Variables

> **Location:** [Settings → Secrets and variables → Actions → Variables tab](https://github.com/Aries-Serpent/_codex_/settings/variables/actions)  
> **Referenced in workflows as:** `${{ vars.NAME }}`  
> **Readable by agents via:** `VariableManager` (requires `CODEX_MASTER_KEY`)  
> **Auto-synced to:** `.codex/agent_context.json` daily

Variables are grouped by subsystem. Human-governance flags must **never** be overwritten by automation without explicit owner approval.

### 6a. 🧠 Cognitive Brain

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `COGNITIVE_BRAIN_ALLOWED_ACTORS` | ✅ | `mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]` | Actors permitted to interact with cognitive brain memory |
| 2 | `COGNITIVE_BRAIN_INJECTION_ENABLED` | ✅ | `true` | Master switch for session context injection |
| 3 | `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | ✅ | `90` | Long-term memory retention in days |
| 4 | `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | ✅ | `128000` | Maximum tokens for context injection |
| 5 | `COGNITIVE_BRAIN_MEMORY_TIER` | ✅ | `both` | Memory tier: `stm`, `ltm`, or `both` |
| 6 | `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | ✅ | `0.75` | Minimum confidence to inject a pattern |
| 7 | `COGNITIVE_BRAIN_SESSION_NUMBER` | ✅ | `118` (auto-increments) | Current session number — auto-incremented by `agent-auth-delegation.yml` activate-delegation step |

### 6b. 🖥️ Copilot Agent Runtime

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `COPILOT_AGENT_AUTH_ENABLED` | ✅ | `true` | ⚠️ **Human governance flag** — gates token delegation workflow |
| 2 | `COPILOT_AGENT_FIREWALL_ENABLED` | ✅ | `true` | ⚠️ **Human governance flag** — network isolation control |
| 3 | `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | ✅ | *(long allowlist)* | Additional URLs allowed through Copilot firewall |
| 4 | `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | ✅ | `D` | Maximum D_CAPABLE autonomy level |
| 5 | `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | ✅ | `true` | Enable session context restoration |
| 6 | `COPILOT_CLI_BASE_URL` | ✅ | `http://localhost:8765` | Cognitive Brain CLI API URL (local server) |
| 7 | `COPILOT_CLI_ENABLED` | ✅ | `true` | Enable CLI API server integration |

### 6c. ⚙️ CI/CD Health

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `AGENT_HANDOFF_TIMEOUT_SECONDS` | ✅ | `120` | Timeout for agent handoff operations |
| 2 | `AUTO_PROMOTE_TIER_ENABLED` | ✅ | `true` | Auto-promotion tier for agent capabilities |
| 3 | `AUTONOMOUS_ACTIONS_ENABLED` | ✅ | `true` | ⚠️ **Human governance flag** — gates autonomous agent actions |
| 4 | `CODEX_CI_FAILURE_RATE` | ✅ | `6.5:ok` (auto-updated) | Current CI failure rate — format: `<float>:<status>` where status ∈ `{ok, degraded, critical}`. Updated by `ci-health-monitor.yml`. |
| 5 | `CODEX_CI_FAILURE_THRESHOLD` | ✅ | `10.0` | CI failure rate threshold for `degraded` state |
| 6 | `CODEX_CI_LAST_GREEN_SHA` | ✅ | *(sha)* (auto-updated) | Last commit SHA with all-green CI |
| 7 | `EMBEDDING_INDEX_AUTO_REBUILD` | ✅ | `true` | Auto-rebuild FAISS embedding index on changes |

### 6d. 🔒 Identity & Static Config

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `AUDIT_RETENTION_DAYS` | ✅ | `90` | Audit artifact retention period |
| 2 | `CODEX_AGENT_NAME` | ✅ | `ai_org_repo_admin` | Agent identity name |
| 3 | `CODEX_API_VERSION` | ✅ | `2022-11-28` | GitHub API version pin |
| 4 | `CODEX_ISOLATED_PATH` | ✅ | `/codex/network/isolated` | Network isolation path |
| 5 | `CODEX_LOG_LEVEL` | ✅ | `INFO` | Logging verbosity |
| 6 | `CODEX_NETWORK_MODE` | ✅ | `isolated` | Network mode policy |
| 7 | `CODEX_ORG_NAME` | ✅ | `Aries-Serpent` | Organization name constant |
| 8 | `GENESIS_TIMESTAMP` | ✅ | `2025-12-26T16:04:45Z` | Repository genesis timestamp (immutable) |

### 6e. 🐍 Runtime / Build Config

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `CODEX_CACHE_VERSION` | ✅ | `v2` | Cache-busting version for CI dependency caches |
| 2 | `CODEX_CLI_API_URL` | ✅ | `http://localhost:8765` | CLI API server URL |
| 3 | `CODEX_COVERAGE_THRESHOLD` | ✅ | `80` | Minimum test coverage % gate |
| 4 | `CODEX_D365_POLICIES_PATH` | ✅ | `configs/deployment/d365/sla_policies.json` | D365 SLA policies config path |
| 5 | `CODEX_FORCE_CPU` | ✅ | `0` | Force CPU-only torch (`0`=off, `1`=on) |
| 6 | `CODEX_LINT_STRICT` | ✅ | `true` | Enable strict Ruff/mypy linting |
| 7 | `CODEX_LLM_MODEL` | ✅ | `gpt-4o` | LLM model for agent operations |
| 8 | `CODEX_LLM_RATE_LIMIT_DELAY` | ✅ | `1.0` | Seconds between LLM requests |
| 9 | `CODEX_OFFLINE` | ✅ | `1` | Offline mode for CI (`1`=offline) |
| 10 | `CODEX_PYTHON_VERSION` | ✅ | `3.12` | Python version — aligned with env-level `CODEX_ENV_PYTHON_VERSION`. Issue 2 resolved. |
| 11 | `CODEX_SANDBOX_TIMEOUT` | ✅ | `60` | Sandbox operation timeout (seconds) |
| 12 | `CODEX_SESSION_ID` | ✅ | `UUID v4` (auto-set per session) | Current or most-recent logical session identifier. Written by `copilot-setup-steps.yml` on session start. Format: UUID v4 string. |
| 13 | `CODEX_SESSION_LOG_DIR` | ✅ | `.codex/sessions` | Session log directory |
| 14 | `CODEX_TEST_PARALLELISM` | ✅ | `auto` | Pytest parallel execution mode |
| 15 | `CODEX_ZENDESK_DOCS_ROOT` | ✅ | `docs/vendors/zendesk` | Zendesk documentation root |
| 16 | `D365_SLA_POLICY_PATH` | ⚠️ | `configs/deployment/d365/sla_policies.json` | Duplicate of `CODEX_D365_POLICIES_PATH` — pending deletion (see §13) |
| 17 | `ENABLE_LIVE_TESTS` | ✅ | `true` | Enable live/integration tests in CI |

### 6f. 🤖 ML / HuggingFace / Weights & Biases

| # | Variable | Status | Current Value | Purpose |
|---|---|---|---|---|
| 1 | `COMPOSE_DOCKER_CLI_BUILD` | ✅ | `1` | Enable BuildKit for Docker Compose |
| 2 | `DOCKER_BUILDKIT` | ✅ | `1` | Enable Docker BuildKit |
| 3 | `GPU_OPT` | ✅ | `--gpus all` | Docker GPU passthrough flag |
| 4 | `HF_HOME` | ✅ | `~/.cache/huggingface` | HuggingFace cache directory |
| 5 | `MLFLOW_EXPERIMENT_NAME` | ✅ | `saas_knowledge_training` | MLflow experiment name |
| 6 | `TORCH_HOME` | ✅ | `~/.cache/torch` | PyTorch cache directory |
| 7 | `TRANSFORMERS_OFFLINE` | ✅ | `1` | Run HF Transformers offline |
| 8 | `WANDB_MODE` | ✅ | `offline` | Weights & Biases run mode |
| 9 | `ZENDESK_RATE_LIMIT` | ✅ | `100` | Zendesk API rate limit |
| 10 | `ZENDESK_SYNC_INTERVAL` | ✅ | `3600` | Zendesk sync interval (seconds) |

### 6g. Webhook / Infra

| # | Variable | Status | Current Value | Purpose | Fix Required |
|---|---|---|---|---|---|
| 1 | `WEBHOOK_RECEIVER_URL` | ✅ **Auto-set by Codespace** | `https://${CODESPACE_NAME}-8765.app.github.dev/webhook/github` | Public URL for webhook delivery. Auto-updated on every Codespace start/resume via `post-start.sh`. | No manual action needed for Codespace sessions. For non-Codespace deployment, set manually: `gh variable set WEBHOOK_RECEIVER_URL --body "https://your-host/webhook/github" --repo Aries-Serpent/_codex_` |

---

## 7. Environment Variables (`Aries_Serpent_codex_`)

> **Location:** [Settings → Environments → Aries_Serpent_codex_](https://github.com/Aries-Serpent/_codex_/settings/environments)  
> **Override scope:** These **override** repository variables of the same name for jobs using `environment: Aries_Serpent_codex_`

| # | Variable | Status | Value | Env (overrides repo?) | Notes |
|---|---|---|---|---|---|
| 1 | `CARGO_TERM_COLOR` | ✅ | `always` | Overrides repo (`always`) | No conflict |
| 2 | `CODEX_BRIDGE_DIR` | ✅ | `/tmp/codex_secure_bridge` | New (not in repo-level) | IPC bridge directory for Codespace |
| 3 | `CODEX_BRIDGE_OWNER_ONLY` | ✅ | `true` | New (not in repo-level) | IPC bridge access control |
| 4 | `CODEX_DB_PATH` | ✅ | `.codex/logs.db` | Overrides repo (`.codex/logs.db`) | No conflict |
| 5 | `CODEX_ENV_GO_VERSION` | ✅ | `1.21` | Overrides repo (`1.21`) | No conflict |
| 6 | `CODEX_ENV_NODE_VERSION` | ✅ | `18` | Overrides repo — env variable only | ✅ **Issue 1 resolved (2026-03-06):** Previously stored as an env *secret*. Deleted from secrets; recreated as an env *variable*. |
| 7 | `CODEX_ENV_PYTHON_VERSION` | ✅ | `3.12` | Overrides repo (`3.12`) | ✅ **Issue 2 resolved (2026-03-06):** Updated from `3.11` to `3.12`. Now consistent with `CODEX_PYTHON_VERSION`. |
| 8 | `CODEX_ENV_RUST_VERSION` | ✅ | `1.92` | Overrides repo (`1.92`) | No conflict |
| 9 | `CODEX_ENV_SWIFT_VERSION` | ✅ | `5.9` | Overrides repo (`5.9`) | No conflict |
| 10 | `CODEX_LOG_DB_PATH` | ✅ | `.codex/logs.db` | Overrides repo (`.codex/logs.db`) | No conflict |
| 11 | `CODEX_SQLITE_POOL` | ✅ | `1` | Overrides repo (`1`) | No conflict |
| 12 | `RUST_BACKTRACE` | ✅ | `1` | Overrides repo (`1`) | No conflict |
| 13 | `RUST_TEST_THREADS` | ✅ | `1` | Overrides repo (`1`) | No conflict |

---

## 8. Codespace Secrets

> **Location (org):** [Settings → Codespaces → Secrets](https://github.com/organizations/Aries-Serpent/settings/secrets/codespaces)  
> **Location (user):** [github.com/settings/secrets/codespaces](https://github.com/settings/secrets/codespaces)  
> **Injected by:** `.devcontainer/devcontainer.json` `"secrets":` block  
> **When:** Only available inside an active GitHub Codespace session

These secrets mirror the Actions org secrets but are injected into Codespace containers for interactive agent sessions.

> ⚠️ **Codespace secrets are NOT automatically mirrored from org Actions secrets** — they must be set separately at the Codespace level even when the same secret exists as an Actions org secret.

| # | Secret Name | Status | Purpose | Where to Set | Actions Org Secret Equivalent |
|---|---|---|---|---|---|
| 1 | `CODEX_MASTER_KEY` | ❌ **Not confirmed** | Primary GitHub PAT for Variables API, Secrets API, Webhooks API | Org Codespace secrets **or** user secrets | `CODEX_MASTER_KEY` (org secret ✅) |
| 2 | `CODEX_BACKUP_KEY` | ❌ **Not confirmed** | Fallback PAT for 401/403 retries | Org Codespace secrets **or** user secrets | `CODEX_BACKUP_KEY` (org secret ✅) |
| 3 | `CODEX_ADMIN_KEY` | ❌ **Not confirmed** | Fine-grained PAT (`Webhooks:write`) for webhook management | Org Codespace secrets **or** user secrets | `CODEX_ADMIN_KEY` (org secret ✅) |
| 4 | `_GITHUB_APP_ID` | ❌ **Not confirmed** | Numeric GitHub App ID for RS256 JWT auth | Org Codespace secrets | `_GITHUB_APP_ID` (org secret ✅) |
| 5 | `_GITHUB_APP_PRIVATE_KEY` | ❌ **Not confirmed** | PEM RSA-2048 private key for GitHub App | Org Codespace secrets (multi-line value) | `_GITHUB_APP_PRIVATE_KEY` (org secret ✅) |
| 6 | `_GITHUB_APP_INSTALLATION_ID` | ❌ **Not confirmed** | App installation ID for generating installation tokens | Org Codespace secrets | `_GITHUB_APP_INSTALLATION_ID` (org secret ✅) |
| 7 | `_GITHUB_APP_CLIENT_SECRET` | ❌ **Not confirmed** | GitHub App OAuth client secret | Org Codespace secrets | `_GITHUB_APP_CLIENT_SECRET` (org secret ✅) |
| 8 | `WEBHOOK_SECRET` | ❌ **Not confirmed** | HMAC-SHA256 shared secret for webhook signature verification | Org Codespace secrets | `CODEX_WEBHOOK_SECRET` (repo secret ✅) |

> **Note:** Secrets 4–7 use the same `_GITHUB_APP_*` naming as the corresponding org Actions secrets (leading underscore is the standard convention for these system/infrastructure secrets).  
> See [`docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md`](../agent/CODESPACE_COPILOT_AGENT_GUIDE.md) for detailed setup instructions.

### ⚠️ How to set Codespace secrets (all 8 items above)

```bash
# Option A — GitHub CLI (requires admin scope)
gh secret set CODEX_MASTER_KEY             --app codespaces --org Aries-Serpent
gh secret set CODEX_BACKUP_KEY             --app codespaces --org Aries-Serpent
gh secret set CODEX_ADMIN_KEY              --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_ID              --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_PRIVATE_KEY     --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_INSTALLATION_ID --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_CLIENT_SECRET   --app codespaces --org Aries-Serpent
gh secret set WEBHOOK_SECRET               --app codespaces --org Aries-Serpent
```

```
# Option B — GitHub UI
https://github.com/organizations/Aries-Serpent/settings/secrets/codespaces
→ "New organization secret" for each item above
→ Set repository access to: Aries-Serpent/_codex_
```

---

## 9. Workflow-Defined `env:` Variables

These are **not** stored in GitHub Settings — they are defined inline in workflow files and can reference secrets/variables.

| Variable | Defined In | Value / Source | Purpose |
|---|---|---|---|
| `GITHUB_TOKEN` | Auto-injected by Actions | GitHub-provisioned short-lived token | Default token for all workflow steps |
| `AGENT_GITHUB_TOKEN` | `copilot-setup-steps.yml` Export step | `${{ env.GITHUB_TOKEN }}` | Stable alias for `GITHUB_TOKEN` written to `GITHUB_ENV` |
| `CODEX_SESSION_ID` | `copilot-setup-steps.yml` + repo variable | UUID v4 (written per session to repo var) | Logical session identifier for log grouping. Also persisted as repo variable (§6e). |
| `CARGO_TERM_COLOR` | Rust workflows | `always` | Rust compiler coloured output |
| `RUST_BACKTRACE` | Rust workflows | `1` | Enable Rust backtraces on panic |

> **Reference:** [`docs/agent/COPILOT_TOKEN_GUIDE.md`](../agent/COPILOT_TOKEN_GUIDE.md) — complete token permission matrix.

---

## 10. Known Issues & Inconsistencies

### ✅ Issue 1 — `CODEX_ENV_NODE_VERSION` stored as a Secret — **RESOLVED 2026-03-06**

| | Detail |
|---|---|
| ~~**Problem**~~ | ~~`CODEX_ENV_NODE_VERSION` is stored as an **Environment Secret** with value `18`.~~ |
| **Resolution** | `CODEX_ENV_NODE_VERSION` env secret has been **deleted**. A replacement env *variable* with value `18` now exists under `Aries_Serpent_codex_` (verified in 2026-03-06 export). Agents and logs can now read this value. |

### ✅ Issue 2 — Python version conflict: `3.12` vs `3.11` — **RESOLVED 2026-03-06**

| | Detail |
|---|---|
| ~~**Problem**~~ | ~~`CODEX_ENV_PYTHON_VERSION` (env variable) = `3.11` conflicted with `CODEX_PYTHON_VERSION` (repo variable) = `3.12`.~~ |
| **Resolution** | `CODEX_ENV_PYTHON_VERSION` updated to `3.12` (verified in 2026-03-06 export). Both layers now agree on Python 3.12. CI should no longer have version discrepancies between environment and non-environment jobs. |

### ⚠️ Issue 3 — Duplicate path variable: `CODEX_D365_POLICIES_PATH` and `D365_SLA_POLICY_PATH`

| | Detail |
|---|---|
| **Problem** | Both variables point to `configs/deployment/d365/sla_policies.json`. |
| **Recommendation** | Keep `CODEX_D365_POLICIES_PATH` (follows the `CODEX_` naming convention used across this codebase). Delete `D365_SLA_POLICY_PATH` (legacy name; no workflow or Python source file references it directly). |
| **Admin action** | `gh variable delete D365_SLA_POLICY_PATH --repo Aries-Serpent/_codex_` (see §13 for full command) |

### ⚠️ Issue 4 — Stale secrets (> 90-day rotation guideline)

| Secret | Age | Action |
|---|---|---|
| `CODEX_MASTER_KEY` | ✅ Rotated 2026-03-05 | Next rotation due ~2026-06-03 |
| `_CODEX_BOT_RUNNER` | 7 months | Verify if still in use; rotate or delete |
| `CODEX_ENVIRONMENT_RUNNER` | 7 months | Verify if still in use; rotate or delete |
| `CODEX_RUNNER_TOKEN` | 7 months | Runner tokens often expire — verify or regenerate |
| `CODEX_RUNNER_SHA256` | 7 months | Regenerate after runner token rotation |

### ✅ Issue 5 — `CODEX_ADMIN_KEY` missing — **RESOLVED 2026-03-06**

| | Detail |
|---|---|
| ~~**Problem**~~ | ~~`webhook_configurator.py` preferred `CODEX_ADMIN_KEY` but it was missing.~~ |
| **Resolution** | `CODEX_ADMIN_KEY` was added as an org secret (updated 3 hours before 2026-03-06 export). `webhook_configurator.py` can now use least-privilege webhook management without falling back to `CODEX_MASTER_KEY`. |

### ✅ Issue 6 — `WEBHOOK_RECEIVER_URL` missing — **RESOLVED 2026-03-06**

| | Detail |
|---|---|
| ~~**Problem**~~ | ~~2 webhooks configured but `active=false` because `WEBHOOK_RECEIVER_URL` not set.~~ |
| **Resolution** | `WEBHOOK_RECEIVER_URL` is now **auto-set** on every Codespace start/resume by `.devcontainer/scripts/post-start.sh`. The URL format is `https://${CODESPACE_NAME}-8765.app.github.dev/webhook/github`. The `POST /webhook/github` endpoint is now implemented in `cognitive_app/src/server/cli_api_server.py` with HMAC-SHA256 verification. For webhook delivery to work, port 8765 must be set to **public** visibility in the Codespace. |

### ⚠️ Issue 7 — Codespace secrets not confirmed present

| | Detail |
|---|---|
| **Problem** | The 8 Codespace secrets declared in `.devcontainer/devcontainer.json` have not been confirmed as set in org Codespace settings. |
| **Impact** | Codespace-based Copilot agent sessions will lack authentication tokens; `post-start.sh` will fail to start the CLI server. |
| **Fix** | Set all 8 secrets listed in [§8](#8-codespace-secrets) at the org Codespace level. |
| **Instructions** | See [§8 How to set Codespace secrets](#%EF%B8%8F-how-to-set-codespace-secrets-all-8-items-above) for the CLI/UI steps |

---

## 11. Troubleshooting

### "Variables API returns 403 / 404"

```
Symptom: VariableManager or brain_client raises AuthenticationError on variable read/write
Cause:   GITHUB_TOKEN used instead of CODEX_MASTER_KEY
Fix:
  1. Confirm CODEX_MASTER_KEY is set as an org secret (§3)
  2. Confirm copilot-setup-steps.yml "🔑 Export Auth Tokens" step is running
  3. In code, use: from scripts.tools.variable_manager import VariableManager; vm = VariableManager()
  Reference: docs/agent/COPILOT_TOKEN_GUIDE.md — Permission Matrix
```

### "Webhooks return 403 on create/update"

```
Symptom: webhook_configurator.py fails with HTTP 403 on webhook API calls
Cause:   GITHUB_TOKEN cannot manage webhooks; CODEX_ADMIN_KEY / CODEX_MASTER_KEY needed
Fix:
  1. Confirm CODEX_MASTER_KEY has admin:repo_hook scope, OR
  2. Create CODEX_ADMIN_KEY (fine-grained, Webhooks:write) and set as org secret
  Reference: docs/agent/COPILOT_TOKEN_GUIDE.md — Webhook operations section
```

### "Python version mismatch between jobs"

```
Symptom: Tests pass in some jobs, fail in others due to Python syntax/type differences
Status:  ✅ RESOLVED (2026-03-06) — CODEX_ENV_PYTHON_VERSION updated to 3.12 (Issue 2)
Both CODEX_PYTHON_VERSION (repo var) and CODEX_ENV_PYTHON_VERSION (env var) are now 3.12.
If you still see version mismatches, confirm no other variable overrides exist.
```

### "CODEX_ENV_NODE_VERSION appears as *** in logs"

```
Symptom: Node.js version appears masked in CI logs
Status:  ✅ RESOLVED (2026-03-06) — CODEX_ENV_NODE_VERSION deleted from env secrets and
         recreated as an env variable. Value is now readable in logs and by the Variables API.
```

### "Codespace starts but CLI API server not running"

```
Symptom: post-start.sh health check fails; uvicorn :8765 not reachable
Cause:   CODEX_MASTER_KEY or CODEX_BACKUP_KEY not set as Codespace secrets
Fix:     Set all 9 Codespace secrets per §8 and §13 at org level
         Reference: docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md
```

### "CODEX_CI_FAILURE_RATE shows stale value"

```
Symptom: CODEX_CI_FAILURE_RATE hasn't updated in > 24 hours
Cause:   ci-health-monitor.yml workflow not running, or CODEX_MASTER_KEY lacked write access
Fix:
  1. Check .github/workflows/ci-health-monitor.yml is enabled
  2. Verify CODEX_MASTER_KEY has variables:write permission
  Format: "<float>:<status>" — e.g. "6.3:ok", "15.2:degraded", "22.1:critical"
```

### "Secret rotation — CODEX_MASTER_KEY / CODEX_BACKUP_KEY"

```
Full runbook: docs/ops/secrets_rotation_runbook.md
Quick summary:
  1. Generate new 32-byte base64 key offline
  2. Copy current CODEX_MASTER_KEY → set as CODEX_BACKUP_KEY (opens grace window)
  3. Set new key as CODEX_MASTER_KEY
  4. Wait 48 hours (grace window) then verify
  5. Update CODEX_BACKUP_KEY to new value (closes grace window)
```

### "Incorrect variable format"

```
Variable: CODEX_CI_FAILURE_RATE
Required format: "<float>:<status>" (e.g. "6.3:ok")
Invalid examples: "6.3", "ok", "6.3-ok", "6.3 ok"
Fix: gh variable set CODEX_CI_FAILURE_RATE --body "6.3:ok" --repo Aries-Serpent/_codex_

Variable: COGNITIVE_BRAIN_SESSION_NUMBER
Required format: Integer (e.g. "118")
Invalid examples: "S118", "session-118", "118.0"
Fix: gh variable set COGNITIVE_BRAIN_SESSION_NUMBER --body "118" --repo Aries-Serpent/_codex_
```

---

## 12. Related Documentation

| Document | Scope | Notes |
|---|---|---|
| [`docs/agent/COPILOT_TOKEN_GUIDE.md`](../agent/COPILOT_TOKEN_GUIDE.md) | Token priority chain, permission matrix, how tokens reach agents | **Primary auth reference** |
| [`docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md`](./REPO_VARIABLES_IMPLEMENTATION_GUIDE.md) | Architecture, subsystem wiring, variable dependency map | Technical deep-dive |
| [`docs/admin/HUMAN_ADMIN_REPO_VARIABLES_SETUP.md`](./HUMAN_ADMIN_REPO_VARIABLES_SETUP.md) | Step-by-step CLI / UI setup for repo variables | Admin setup guide |
| [`docs/ops/secrets_rotation_runbook.md`](../ops/secrets_rotation_runbook.md) | Full rotation procedure for CODEX_MASTER_KEY / CODEX_BACKUP_KEY | **Required for 90-day rotation** |
| [`docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md`](../agent/CODESPACE_COPILOT_AGENT_GUIDE.md) | Codespace secrets, lifecycle hooks, environment parity with Actions | Codespace setup |
| [`docs/agent/GITHUB_APP_CLI_MAPPING.md`](../agent/GITHUB_APP_CLI_MAPPING.md) | GitHub App ID, private key, installation ID setup | GitHub App authentication |
| [`docs/ops/WEBHOOK_REGISTRY.md`](../ops/WEBHOOK_REGISTRY.md) | Webhook config, registry, apply procedure, CODEX_ADMIN_KEY | Webhook activation |
| [`.codex/runtime_variables.md`](../../.codex/runtime_variables.md) | Legacy env var catalog (pre-unification) | Superseded by this guide |
| [`docs/security/CURRENT_EXPECTED_VARIABLES.md`](../security/CURRENT_EXPECTED_VARIABLES.md) | Security-focused variable inventory (pre-unification) | Superseded by this guide |
| [`docs/security/secret_handling.md`](../security/secret_handling.md) | Secret handling best practices, never-log rules | Security policy |
| [`.codex/agent_context.json`](../../.codex/agent_context.json) | Live snapshot of repo variables (synced daily) | Machine-readable state |
| [`scripts/tools/variable_manager.py`](../../scripts/tools/variable_manager.py) | Python API for reading/writing repo variables | Code reference |
| [`src/codex/auth/github_app.py`](../../src/codex/auth/github_app.py) | `_resolve_github_token()` — token fallback chain implementation | Code reference |

---

## 13. ⛔ Still Missing — Variables/Secrets Not Yet Provided

The following entries are **not yet present** in the repository but are required for full functionality.
Each is grouped with clear instructions on how to provide the value.

> **Admin:** @mbaetiong — these require human action. Agents cannot create secrets or environment-level secrets.

---

### ✅ WEBHOOK_RECEIVER_URL (Repo Variable) — **RESOLVED 2026-03-06**

**Resolution:** `WEBHOOK_RECEIVER_URL` is now **auto-set** on every Codespace start/resume by
`.devcontainer/scripts/post-start.sh`. The URL format is:
`https://${CODESPACE_NAME}-8765.preview.app.github.dev/webhook/github`

The `POST /webhook/github` endpoint is implemented in `cognitive_app/src/server/cli_api_server.py`.
For webhook delivery to work, port 8765 must be set to **public** visibility in the Codespace Ports panel.

For non-Codespace deployment, set the variable manually:
```bash
gh variable set WEBHOOK_RECEIVER_URL \
  --body "https://your-deployed-url.com/webhook/github" \
  --repo Aries-Serpent/_codex_
```

---

### 🟡 Issue 3 — Delete duplicate `D365_SLA_POLICY_PATH` repo variable

**Action:** Delete the legacy duplicate variable. `CODEX_D365_POLICIES_PATH` is the preferred name (follows `CODEX_` convention) and points to the same file.  
**No code change needed:** Neither variable is referenced by any workflow YAML or Python source file.

```bash
gh variable delete D365_SLA_POLICY_PATH --repo Aries-Serpent/_codex_
```

---

### 🔴 Codespace Secrets (8 items) — blocks Codespace agent sessions

**What they are:** Secrets mirrored from Actions org secrets, required inside active Codespace containers.  
**Why they're missing:** Codespace secrets are not auto-mirrored from Actions secrets — they require a separate admin action.  
**Impact:** Any Copilot coding session running in a Codespace will fail to authenticate; `post-start.sh` cannot start the CLI server.

**How to set them:**

```bash
# Navigate to: https://github.com/organizations/Aries-Serpent/settings/secrets/codespaces
# OR use gh CLI (each command will prompt for the secret value):
gh secret set CODEX_MASTER_KEY             --app codespaces --org Aries-Serpent
gh secret set CODEX_BACKUP_KEY             --app codespaces --org Aries-Serpent
gh secret set CODEX_ADMIN_KEY              --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_ID              --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_PRIVATE_KEY     --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_INSTALLATION_ID --app codespaces --org Aries-Serpent
gh secret set _GITHUB_APP_CLIENT_SECRET   --app codespaces --org Aries-Serpent
gh secret set WEBHOOK_SECRET               --app codespaces --org Aries-Serpent
```

**Source values to copy from (all exist as Actions org/repo secrets):**

| Codespace Secret | Copy value from Actions Secret |
|---|---|
| `CODEX_MASTER_KEY` | Org secret: `CODEX_MASTER_KEY` |
| `CODEX_BACKUP_KEY` | Org secret: `CODEX_BACKUP_KEY` |
| `CODEX_ADMIN_KEY` | Org secret: `CODEX_ADMIN_KEY` |
| `_GITHUB_APP_ID` | Org secret: `_GITHUB_APP_ID` |
| `_GITHUB_APP_PRIVATE_KEY` | Org secret: `_GITHUB_APP_PRIVATE_KEY` |
| `_GITHUB_APP_INSTALLATION_ID` | Org secret: `_GITHUB_APP_INSTALLATION_ID` |
| `_GITHUB_APP_CLIENT_SECRET` | Org secret: `_GITHUB_APP_CLIENT_SECRET` |
| `WEBHOOK_SECRET` | Repo secret: `CODEX_WEBHOOK_SECRET` |

> After setting, confirm in `.devcontainer/devcontainer.json` that all secret names match
> the `"secrets"` array entries. Reference: `docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md`

---

## Summary Checklist

### 🔴 Action Required (Blockers)

- [ ] **Set 8 Codespace secrets** listed in [§8](#8-codespace-secrets) at org level — see [§13](#13--still-missing--variablessecrets-not-yet-provided) for CLI commands (blocks Codespace agent sessions)

### ✅ Resolved (Previously "Should Fix")

- [x] ~~Fix Issue 1: Delete `CODEX_ENV_NODE_VERSION` env secret; recreate as env variable~~ — **Done 2026-03-06**
- [x] ~~Fix Issue 2: Update `CODEX_ENV_PYTHON_VERSION` env variable from `3.11` → `3.12`~~ — **Done 2026-03-06**
- [x] ~~Fix Issue 5: Create `CODEX_ADMIN_KEY` org secret (fine-grained PAT, `Webhooks:write`)~~ — **Done 2026-03-06**
- [x] ~~Fix Issue 6: Set `WEBHOOK_RECEIVER_URL` repo variable~~ — **Done 2026-03-06** (auto-set by Codespace `post-start.sh`)

### 🟡 Should Fix (Non-blocking)

- [ ] Issue 3: Delete `D365_SLA_POLICY_PATH` repo variable (duplicate of `CODEX_D365_POLICIES_PATH`) — see [§13](#13--still-missing--variablessecrets-not-yet-provided) for delete command

### 🟢 Monitor / Maintenance

- [ ] Rotate `CODEX_MASTER_KEY` before 2026-06-03 (rotated 2026-03-05 — 90-day window opens)
- [ ] Verify/rotate `_CODEX_BOT_RUNNER` (7 months old — exceeds 90-day guideline)
- [ ] Verify/rotate `CODEX_RUNNER_TOKEN` (7 months old — runner tokens often expire)
- [ ] Verify/rotate `CODEX_ENVIRONMENT_RUNNER` (7 months old)

---

*Supersedes: `.codex/runtime_variables.md` · `docs/security/CURRENT_EXPECTED_VARIABLES.md` · `.codex/QUICK_REFERENCE_TOKEN_STATUS.md`*  
*Maintained by: @mbaetiong · Last reviewed: 2026-03-06 (W-130 — webhook endpoint + _GITHUB_APP_* naming + authoritative variable export)*
