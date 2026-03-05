# GitHub Variables & Secrets — Master Reference Guide

> **Version:** 1.0.0 (W-128, PR #3503, 2026-03-05)  
> **Owner:** @mbaetiong  
> **Status:** ✅ Current — reflects live state as of 2026-03-05  
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
| 2 | `CODEX_BACKUP_KEY` | ✅ Present | 4 days ago | Fallback GitHub PAT — auto-used on 401/403 from `CODEX_MASTER_KEY`. Same scope as master. | All auth-delegation workflows, `variable_manager.py`, `brain_client.py`, `github_app.py` |
| 3 | `CODEX_MASTER_KEY` | ⚠️ Present | 2 months ago | Primary full-scope GitHub PAT (classic, `repo` scope + `admin:repo_hook`). **Required for Variables API, Secrets API, Webhooks API.** | `agent-auth-delegation.yml`, `variable_manager.py`, `webhook_configurator.py`, `brain_client.py` |
| 4 | `HF_TOKEN` | ✅ Present | 2 months ago | HuggingFace API token for model downloads | ML training workflows |
| 5 | `NPM_TOKEN` | ✅ Present | 2 months ago | npm publish authentication | Node.js package publish workflows |
| 6 | `PYPI_TOKEN` | ✅ Present | 2 months ago | PyPI publish authentication | Python package publish workflows |
| 7 | `RAG_OPENAI_KEY` | ✅ Present | 3 weeks ago | OpenAI API key for RAG embeddings | RAG index build workflows |
| 8 | `_CODEX_ACTION_RUNNER` | ✅ Present | 2 months ago | Runner registration token for self-hosted Actions runners | Runner registration |
| — | `CODEX_ADMIN_KEY` | ❌ **Missing** | — | Fine-grained PAT (`Webhooks:write`). Needed for `webhook_configurator.py` least-privilege mode. Without it, `CODEX_MASTER_KEY` is used (less restrictive). | `apply-webhooks` job in `agent_infrastructure_manager.yml` |

### ⚠️ `CODEX_MASTER_KEY` — Rotation Alert

`CODEX_MASTER_KEY` was last updated **2 months ago**. The rotation runbook requires rotation every **90 days**.  
See [`docs/ops/secrets_rotation_runbook.md`](../ops/secrets_rotation_runbook.md) for the full rotation procedure.

**Token chain in code:** `CODEX_MASTER_KEY → CODEX_BACKUP_KEY → AGENT_GITHUB_TOKEN → GITHUB_TOKEN`  
This is enforced by `_resolve_github_token()` in `src/codex/auth/github_app.py` and `scripts/tools/variable_manager.py`.

---

## 4. Repository Secrets

> **Location:** [Settings → Secrets and variables → Actions → Secrets tab](https://github.com/Aries-Serpent/_codex_/settings/secrets/actions)  
> **Referenced in workflows as:** `${{ secrets.NAME }}`

| # | Secret Name | Status | Last Updated | Purpose | Notes |
|---|---|---|---|---|---|
| 1 | `CODEX_GHP_TOKEN_BASE64` | ✅ Present | 2 months ago | Base64-encoded GitHub token for copilot-with-mcp workflow | Decoder priority #3 in `copilot_token_decoder.py` |
| 2 | `CODEX_GHP_TOKEN_HEX` | ✅ Present | 2 months ago | Hex-encoded GitHub token (alternative encoding) | Decoder priority #4 |
| 3 | `CODEX_GHP_TOKEN_SHA256` | ✅ Present | 2 months ago | One-way SHA-256 hash of GHP token for integrity validation | Verification only — not a usable token |
| 4 | `CODEX_REPO_ID` | ✅ Present | 3 months ago | Repository numeric ID (GitHub internal) | Used in manifest generation |
| 5 | `CODEX_WEBHOOK_SECRET` | ✅ Present | 3 months ago | HMAC-SHA256 shared secret for incoming webhook verification | `WebhookVerifier` in `src/codex/auth/github_app.py` |
| 6 | `_CODEX_BOT_RUNNER` | ⚠️ Present | **7 months ago** | Bot runner registration token | Potentially stale — consider rotating. 90-day guideline exceeded. |

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
| 2 | `CODEX_ENV_NODE_VERSION` | ⚠️ **Wrong type** | Yesterday | `18` | **This is a non-sensitive version string stored as a secret. Should be converted to an Environment Variable instead.** See [§10](#10-known-issues--inconsistencies). |
| 3 | `CODEX_RUNNER_SHA256` | ✅ Present | 7 months ago | *(secret hash)* | May need rotation |
| 4 | `CODEX_RUNNER_TOKEN` | ⚠️ Present | **7 months ago** | *(secret)* | Potentially stale — runner tokens typically expire. Verify or rotate. |

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
| 4 | `CODEX_CI_FAILURE_RATE` | ✅ | `6.3:ok` (auto-updated) | Current CI failure rate — format: `<float>:<status>` where status ∈ `{ok, degraded, critical}`. Updated by `ci-health-monitor.yml`. |
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
| 10 | `CODEX_PYTHON_VERSION` | ⚠️ | `3.12` | Python version — **conflicts with env-level `CODEX_ENV_PYTHON_VERSION` (3.11)**. See §10. |
| 11 | `CODEX_SANDBOX_TIMEOUT` | ✅ | `60` | Sandbox operation timeout (seconds) |
| 12 | `CODEX_SESSION_LOG_DIR` | ✅ | `.codex/sessions` | Session log directory |
| 13 | `CODEX_TEST_PARALLELISM` | ✅ | `auto` | Pytest parallel execution mode |
| 14 | `CODEX_ZENDESK_DOCS_ROOT` | ✅ | `docs/vendors/zendesk` | Zendesk documentation root |
| 15 | `D365_SLA_POLICY_PATH` | ⚠️ | `configs/deployment/d365/sla_policies.json` | Duplicate of `CODEX_D365_POLICIES_PATH` — consider removing one |
| 16 | `ENABLE_LIVE_TESTS` | ✅ | `true` | Enable live/integration tests in CI |

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

### 6g. Webhook / Infra (Missing or incomplete)

| # | Variable | Status | Current Value | Purpose | Fix Required |
|---|---|---|---|---|---|
| 1 | `WEBHOOK_RECEIVER_URL` | ❌ **Missing** | — | Public URL for webhook delivery (Cognitive Brain API server). Required before webhooks can be activated (currently `active=false`). | Deploy Cognitive Brain API server, then set to its public URL. See [`docs/ops/WEBHOOK_REGISTRY.md`](../ops/WEBHOOK_REGISTRY.md). |

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
| 6 | `CODEX_ENV_NODE_VERSION` | ⚠️ | `18` | **Also set as an Env Secret!** | Duplicate — see [§10](#10-known-issues--inconsistencies) |
| 7 | `CODEX_ENV_PYTHON_VERSION` | ⚠️ | `3.11` | **Conflicts** with repo-level `CODEX_PYTHON_VERSION` (`3.12`) | Python 3.11 vs 3.12 discrepancy — see [§10](#10-known-issues--inconsistencies) |
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

| # | Secret Name | Status | Purpose | Where to Set |
|---|---|---|---|---|
| 1 | `CODEX_MASTER_KEY` | ❌ **Not confirmed** | Primary GitHub PAT for Variables API, Secrets API, Webhooks API | Org Codespace secrets **or** user secrets |
| 2 | `CODEX_BACKUP_KEY` | ❌ **Not confirmed** | Fallback PAT for 401/403 retries | Org Codespace secrets **or** user secrets |
| 3 | `CODEX_ADMIN_KEY` | ❌ **Not confirmed** | Fine-grained PAT (`Webhooks:write`) for webhook management | Org Codespace secrets **or** user secrets |
| 4 | `GITHUB_APP_ID` | ❌ **Not confirmed** | Numeric GitHub App ID for RS256 JWT auth | Org Codespace secrets |
| 5 | `GITHUB_APP_PRIVATE_KEY` | ❌ **Not confirmed** | PEM RSA-2048 private key for GitHub App | Org Codespace secrets (multi-line value) |
| 6 | `GITHUB_APP_INSTALLATION_ID` | ❌ **Not confirmed** | App installation ID for generating installation tokens | Org Codespace secrets |
| 7 | `WEBHOOK_SECRET` | ❌ **Not confirmed** | HMAC-SHA256 shared secret for webhook signature verification | Org Codespace secrets |
| 8 | `WEBHOOK_RECEIVER_URL` | ❌ **Not confirmed** | Public URL for webhook delivery (needed when activating webhooks) | Org Codespace secrets |

> **Note:** These Codespace secrets are declared in `.devcontainer/devcontainer.json` `"secrets"` block. They are **not** automatically mirrored from org Actions secrets — they must be set separately.  
> See [`docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md`](../agent/CODESPACE_COPILOT_AGENT_GUIDE.md) for detailed setup instructions.

---

## 9. Workflow-Defined `env:` Variables

These are **not** stored in GitHub Settings — they are defined inline in workflow files and can reference secrets/variables.

| Variable | Defined In | Value / Source | Purpose |
|---|---|---|---|
| `GITHUB_TOKEN` | Auto-injected by Actions | GitHub-provisioned short-lived token | Default token for all workflow steps |
| `AGENT_GITHUB_TOKEN` | `copilot-setup-steps.yml` Export step | `${{ env.GITHUB_TOKEN }}` | Stable alias for `GITHUB_TOKEN` written to `GITHUB_ENV` |
| `CODEX_SESSION_ID` | Runtime (auto-generated) | UUID v4 | Logical session identifier for log grouping |
| `CARGO_TERM_COLOR` | Rust workflows | `always` | Rust compiler coloured output |
| `RUST_BACKTRACE` | Rust workflows | `1` | Enable Rust backtraces on panic |

> **Reference:** [`docs/agent/COPILOT_TOKEN_GUIDE.md`](../agent/COPILOT_TOKEN_GUIDE.md) — complete token permission matrix.

---

## 10. Known Issues & Inconsistencies

### ❌ Issue 1 — `CODEX_ENV_NODE_VERSION` stored as a Secret (low severity)

| | Detail |
|---|---|
| **Problem** | `CODEX_ENV_NODE_VERSION` is stored as an **Environment Secret** with value `18`. Node.js version strings are not sensitive — storing them as secrets wastes secret slots and obscures the value from agents/logs. |
| **Impact** | Agents cannot read this value via the Variables API; it appears masked in logs. |
| **Fix** | Delete the env secret. Create an env variable with the same name and value `18`. |
| **Steps** | 1. [Settings → Environments → Aries_Serpent_codex_ → Secrets](https://github.com/Aries-Serpent/_codex_/settings/environments) → delete `CODEX_ENV_NODE_VERSION` · 2. Same page → Variables tab → Add `CODEX_ENV_NODE_VERSION` = `18` |

### ⚠️ Issue 2 — Python version conflict: `3.12` (repo var) vs `3.11` (env var)

| | Detail |
|---|---|
| **Problem** | `CODEX_PYTHON_VERSION` (repo variable) = `3.12` · `CODEX_ENV_PYTHON_VERSION` (env variable) = `3.11`. For jobs using the `Aries_Serpent_codex_` environment, the env-level value wins → Python 3.11 is used. Outside the environment, Python 3.12 is used. This silent inconsistency can cause test failures that differ between environment and non-environment jobs. |
| **Impact** | CI jobs using the Aries_Serpent_codex_ environment run Python 3.11; others run 3.12. |
| **Recommended fix** | Decide on one version (3.12 recommended per pyproject.toml). Update env variable `CODEX_ENV_PYTHON_VERSION` → `3.12`. |
| **Steps** | [Settings → Environments → Aries_Serpent_codex_ → Variables](https://github.com/Aries-Serpent/_codex_/settings/environments) → update `CODEX_ENV_PYTHON_VERSION` to `3.12` |

### ⚠️ Issue 3 — Duplicate path variable: `CODEX_D365_POLICIES_PATH` and `D365_SLA_POLICY_PATH`

| | Detail |
|---|---|
| **Problem** | Both variables point to `configs/deployment/d365/sla_policies.json`. |
| **Fix** | Audit which workflows use each. Delete the unused one to reduce clutter. |

### ⚠️ Issue 4 — Stale secrets (> 90-day rotation guideline)

| Secret | Age | Action |
|---|---|---|
| `CODEX_MASTER_KEY` | ~2 months (≤90 days OK, approaching) | Plan rotation before next 90-day mark |
| `_CODEX_BOT_RUNNER` | 7 months | Verify if still in use; rotate or delete |
| `CODEX_ENVIRONMENT_RUNNER` | 7 months | Verify if still in use; rotate or delete |
| `CODEX_RUNNER_TOKEN` | 7 months | Runner tokens often expire — verify or regenerate |
| `CODEX_RUNNER_SHA256` | 7 months | Regenerate after runner token rotation |

### ❌ Issue 5 — `CODEX_ADMIN_KEY` missing (low severity)

| | Detail |
|---|---|
| **Problem** | `webhook_configurator.py` prefers `CODEX_ADMIN_KEY` (fine-grained PAT, `Webhooks:write` only) for least-privilege webhook management. Without it, `CODEX_MASTER_KEY` is used, which has broader scope than necessary. |
| **Impact** | Webhooks still work (via `CODEX_MASTER_KEY`), but violates least-privilege principle. |
| **Fix** | Create a fine-grained PAT with only `Webhooks:read+write` scope. Add as org secret `CODEX_ADMIN_KEY`. |

### ❌ Issue 6 — `WEBHOOK_RECEIVER_URL` missing (blocks webhook activation)

| | Detail |
|---|---|
| **Problem** | 2 webhooks are configured in `.codex/webhook_config.json` but `active=false` because `WEBHOOK_RECEIVER_URL` is not set. |
| **Impact** | `workflow_run` and `pull_request` webhook events cannot be delivered to the Cognitive Brain API. The OODA loop and webhook-driven automation are inactive. |
| **Blocker** | Cognitive Brain API server must be deployed and have a public URL first. |
| **Fix** | Deploy Cognitive Brain API (`uvicorn` behind a tunnel or public host). Then set `WEBHOOK_RECEIVER_URL` as a repo variable. Run `apply-webhooks` job. |

### ❌ Issue 7 — Codespace secrets not confirmed present

| | Detail |
|---|---|
| **Problem** | The 8 Codespace secrets declared in `.devcontainer/devcontainer.json` have not been confirmed as set in org Codespace settings. |
| **Impact** | Codespace-based Copilot agent sessions will lack authentication tokens; `post-start.sh` will fail to start the CLI server. |
| **Fix** | Set all 8 secrets listed in [§8](#8-codespace-secrets) at the org Codespace level. |
| **Instructions** | See [`docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md`](../agent/CODESPACE_COPILOT_AGENT_GUIDE.md) — "Prerequisites — Admin Setup" section |

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
Cause:   CODEX_ENV_PYTHON_VERSION (env-level) = 3.11 overrides CODEX_PYTHON_VERSION (repo) = 3.12
Fix:     Update CODEX_ENV_PYTHON_VERSION in Aries_Serpent_codex_ environment to 3.12 (Issue 2, §10)
```

### "CODEX_ENV_NODE_VERSION appears as *** in logs"

```
Symptom: Node.js version appears masked in CI logs
Cause:   CODEX_ENV_NODE_VERSION is stored as a secret, not a variable
Fix:     Delete the env secret; recreate as env variable (Issue 1, §10)
```

### "Codespace starts but CLI API server not running"

```
Symptom: post-start.sh health check fails; uvicorn :8765 not reachable
Cause:   CODEX_MASTER_KEY or CODEX_BACKUP_KEY not set as Codespace secrets
Fix:     Set all 8 Codespace secrets per §8 at org level
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

## Summary Checklist

### 🔴 Action Required (Blockers)

- [ ] Set 8 Codespace secrets listed in §8 at org level (blocks Codespace agent sessions)
- [ ] Set `WEBHOOK_RECEIVER_URL` repo variable once Cognitive Brain API is deployed (blocks webhook activation)

### 🟡 Should Fix (Non-blocking)

- [ ] Fix Issue 1: Delete `CODEX_ENV_NODE_VERSION` env secret; recreate as env variable
- [ ] Fix Issue 2: Update `CODEX_ENV_PYTHON_VERSION` env variable from `3.11` → `3.12`
- [ ] Fix Issue 5: Create `CODEX_ADMIN_KEY` org secret (fine-grained PAT, `Webhooks:write`)
- [ ] Fix Issue 3: Remove duplicate `D365_SLA_POLICY_PATH` or `CODEX_D365_POLICIES_PATH`

### 🟢 Monitor / Maintenance

- [ ] Rotate `CODEX_MASTER_KEY` before 90-day mark (currently 2 months old — ~30 days remaining)
- [ ] Verify/rotate `_CODEX_BOT_RUNNER` (7 months old — exceeds 90-day guideline)
- [ ] Verify/rotate `CODEX_RUNNER_TOKEN` (7 months old — runner tokens often expire)
- [ ] Verify/rotate `CODEX_ENVIRONMENT_RUNNER` (7 months old)

---

*Supersedes: `.codex/runtime_variables.md` · `docs/security/CURRENT_EXPECTED_VARIABLES.md` · `.codex/QUICK_REFERENCE_TOKEN_STATUS.md`*  
*Maintained by: @mbaetiong · Last reviewed: 2026-03-05 (PR #3503 W-128)*
