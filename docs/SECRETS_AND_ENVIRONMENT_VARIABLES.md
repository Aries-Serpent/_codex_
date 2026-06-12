# Secrets and Environment Variables Documentation

> **Last Full Audit**: 2026-06-03T17:39:00Z | **Auditor**: @mbaetiong
> **Total Tracked**: 113 (14 env vars · 76 repo vars · 3 env secrets · 7 repo secrets · 13 org secrets)
> **Current Pass Scope**: Variables only (secrets unchanged in this pass)
> **Next Review**: 2026-09-03 (quarterly)

## Overview

This document provides comprehensive documentation for all secrets and environment variables used in the Codex repository, covering authentication, CI/CD, cognitive-brain/agent orchestration, ML/AI pipeline, and runtime configuration.

---

## 📊 Full Inventory

### Environment Variables — `Aries_Serpent_codex_` Environment

These are injected into the Copilot agent sandbox via `copilot-setup-steps.yml`.

| Variable | Value | Purpose |
|----------|-------|---------|
| `CARGO_TERM_COLOR` | `always` | Enables color output for Cargo (Rust CI) |
| `CODEX_BRIDGE_DIR` | `/tmp/codex_secure_bridge` | Runtime tmpfs mount for IPC bridge (transient, not repo path) |
| `CODEX_BRIDGE_OWNER_ONLY` | `true` | Restricts bridge dir to owner UID only |
| `CODEX_DB_PATH` | `.codex/session_logs.db` | Repository default SQLite DB path; `copilot-setup-steps.yml` currently overrides it to `${GITHUB_WORKSPACE}/.codex/codex.db` inside Copilot sessions |
| `CODEX_ENV_GO_VERSION` | `1.21` | Go toolchain version for env setup |
| `CODEX_ENV_NODE_VERSION` | `22` | Node.js version for Copilot agent sandbox env setup (distinct from `NODE_JS_VERSION` repo var used by CI workflows) |
| `CODEX_ENV_PYTHON_VERSION` | `3.12` | Python version (must match `pyproject.toml requires-python`) |
| `CODEX_ENV_RUST_VERSION` | `1.92` | Rust toolchain version |
| `CODEX_ENV_SWIFT_VERSION` | `5.9` | Swift version for env setup |
| `CODEX_LOG_DB_PATH` | `.codex/session_logs.db` | Session log SQLite DB path used by logging/query tools |
| `CODEX_SQLITE_POOL` | `1` | Enable per-session SQLite connection pooling |
| `RUST_BACKTRACE` | `1` | Full backtraces for Rust panics |
| `RUST_TEST_THREADS` | `1` | Sequential test execution for determinism |

---

### Repository Variables

#### Agent & Autonomy Control

| Variable | Value | Purpose |
|----------|-------|---------|
| `AGENT_HANDOFF_TIMEOUT_SECONDS` | `120` | Seconds before a handoff is declared timed-out |
| `AGENT_KILL_SWITCH` | `0` | Emergency halt (`1` = halt all agents) |
| `AGENT_RUNNER_BUDGET_SECONDS` | `180` | Max wall-clock seconds per agent runner invocation |
| `AGENT_RUNNER_DRY_RUN` | `0` | If `1`, runner logs actions without executing |
| `AGENT_RUNNER_ITERATIONS` | `2` | Default max iterations per runner run |
| `AUTONOMY_BUDGET_SECONDS` | `90` | Per-task autonomy time budget |
| `AUTONOMY_DRY_RUN` | `0` | Dry-run flag for autonomous actions |
| `AUTONOMY_MAX_ITERATIONS` | `3` | Max autonomous iterations per decision loop |
| `AUTONOMOUS_ACTIONS_ENABLED` | `true` | Master switch for all autonomous agent actions |
| `AUTO_PROMOTE_TIER_ENABLED` | `true` | Allow agents to auto-promote tier on CI green |
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | Maximum autonomy level granted to Copilot agents |
| `UNCERTAINTY_BUDGET_SECONDS` | `20` | Time budget for uncertainty resolution before escalation |

#### CI/CD & Quality Gates

| Variable | Value | Purpose |
|----------|-------|---------|
| `AUDIT_RETENTION_DAYS` | `90` | Days to retain CI audit records |
| `CODEX_CACHE_VERSION` | `v2` | Cache coherency key across all workflows |
| `CODEX_CI_FAILURE_RATE` | `2.5:ok` | Live CI failure rate tracker (updated by CI agent) |
| `CODEX_CI_FAILURE_THRESHOLD` | `10.0` | Failure rate % that triggers CI health alert |
| `CODEX_CI_LAST_GREEN_SHA` | `8b5588da25a5d5f12ba8bd66cc37fa688fbc8e97` | Last commit SHA with all checks green |
| `CODEX_COVERAGE_THRESHOLD` | `80` | Minimum test coverage % for CI gate |
| `CODEX_LINT_STRICT` | `true` | Fail CI on any lint warning |
| `CODEX_TEST_PARALLELISM` | `auto` | Test sharding strategy |

#### Cognitive Brain & Session Management

| Variable | Value | Purpose |
|----------|-------|---------|
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]` | Actors allowed to write cognitive brain state |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | Enable session context injection at session start |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | `90` | Days to retain long-term memory |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `128000` | Max tokens for cognitive brain context window <!-- pragma: allowlist secret --> |
| `COGNITIVE_BRAIN_MEMORY_TIER` | `both` | Memory tiers (`stm`, `ltm`, or `both`) |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `0.75` | Minimum confidence to store a pattern |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | `1325` | Current session counter (auto-incremented) |

#### Copilot Agent Configuration

| Variable | Value | Purpose |
|----------|-------|---------|
| `COPILOT_ACTIVE_SESSION` | `4731\|1780503084\|26896743030` | Current active session ID triplet |
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | Require auth token for all agent write operations <!-- pragma: allowlist secret --> |
| `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | _(100+ domains)_ | Additional domains beyond GitHub defaults |
| `COPILOT_AGENT_FIREWALL_ENABLED` | `true` | Enable Copilot agent network firewall |
| `COPILOT_AGENT_PREFLIGHT_RULES` | _(JSON v2.0)_ | Pre-commit rules, mandatory loads, WEC rules |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | Restore prior session context on agent init |
| `COPILOT_BOT_COMMENT_KNOWN_ISSUES` | _(JSON)_ | Known bot comment issues (BCI-001 through BCI-003) |
| `COPILOT_CLI_BASE_URL` | `http://localhost:8765` | Copilot CLI API base URL |
| `COPILOT_CLI_ENABLED` | `true` | Enable Copilot CLI interface |
| `COPILOT_SESSION_QUEUE` | _(PR numbers)_ | Queue of pending PR sessions |
| `COPILOT_SESSION_TOOL_CAPABILITIES` | _(JSON)_ | Tool capability map for current session |
| `COPILOT_WEC_SELECTION_MATRIX` | _(JSON)_ | Workflow Execution Checklist trigger map |
| `COPILOT_WEC_TEMPLATE_DRIFT` | _(JSON)_ | Known WEC template drift items |

#### Infrastructure & Runtime

| Variable | Value | Purpose |
|----------|-------|---------|
| `CODEX_AGENT_NAME` | `ai_org_repo_admin` | Agent identity for audit trails |
| `CODEX_API_VERSION` | `2022-11-28` | GitHub API version used by agent tools |
| `CODEX_CLI_API_URL` | `http://localhost:8765` | CLI API gateway (Codespace/dev only) |
| `CODEX_D365_POLICIES_PATH` | `configs/deployment/d365/sla_policies.json` | Path to D365 SLA policy config |
| `CODEX_FORCE_CPU` | `0` | Force CPU-only execution (`1` = no GPU) |
| `CODEX_ISOLATED_PATH` | `/codex/network/isolated` | Network isolation path |
| `CODEX_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`/`INFO`/`WARNING`) |
| `CODEX_NETWORK_MODE` | `isolated` | Network mode for sandbox execution |
| `CODEX_OFFLINE` | `1` | Disable external network requests (`1` = offline) |
| `CODEX_ORG_NAME` | `Aries-Serpent` | GitHub organization name |
| `CODEX_PR_LIFECYCLE_VERSION` | _(JSON S293)_ | Current PR lifecycle spec version/metadata |
| `CODEX_PYTHON_VERSION` | `3.12` | Python version target (minor pinned, patch floating) |
| `CODEX_SANDBOX_TIMEOUT` | `60` | Seconds before sandbox task is killed |
| `CODEX_SESSION_ID` | `UUID v4` | Per-session unique identifier |
| `CODEX_SESSION_LOG_DIR` | `.codex/sessions` | Session log directory |
| `CODEX_ZENDESK_DOCS_ROOT` | `docs/vendors/zendesk` | Path to Zendesk documentation <!-- pragma: allowlist secret --> |
| `COMPOSE_DOCKER_CLI_BUILD` | `1` | Use Docker CLI for compose builds |
| `DOCKER_BUILDKIT` | `1` | Enable BuildKit for Docker builds |
| `EMBEDDING_INDEX_AUTO_REBUILD` | `true` | Auto-rebuild embedding index on change |
| `ENABLE_LIVE_TESTS` | `true` | Enable live integration tests in CI |
| `GENESIS_TIMESTAMP` | `2025-12-26T16:04:45Z` | Repository genesis timestamp |
| `GPU_OPT` | `--gpus all` | Docker GPU passthrough flag |
| `WEBHOOK_RECEIVER_URL` | `https://${CODESPACE_NAME}-8765.preview.app.github.dev/webhook/github` | Webhook receiver endpoint (Codespace) |

#### LLM & ML Pipeline

| Variable | Value | Purpose |
|----------|-------|---------|
| `CODEX_LLM_MODEL` | `gpt-4o` | Default LLM model identifier |
| `CODEX_LLM_RATE_LIMIT_DELAY` | `1.0` | Seconds between LLM API calls |
| `HF_HOME` | `~/.cache/huggingface` | HuggingFace cache directory |
| `MLFLOW_EXPERIMENT_NAME` | `saas_knowledge_training` | MLFlow experiment name |
| `TORCH_HOME` | `~/.cache/torch` | PyTorch model cache directory |
| `TRANSFORMERS_OFFLINE` | `1` | Force offline mode for HuggingFace Transformers |
| `WANDB_MODE` | `offline` | W&B logging mode |

#### Zendesk Integration

| Variable | Value | Purpose |
|----------|-------|---------|
| `ZENDESK_RATE_LIMIT` | `100` | Max Zendesk API requests per minute <!-- pragma: allowlist secret --> |
| `ZENDESK_SYNC_INTERVAL` | `3600` | Zendesk sync interval in seconds <!-- pragma: allowlist secret --> |

---

### Environment Secrets — `Aries_Serpent_codex_`

| Secret | Purpose | Rotation <!-- pragma: allowlist secret --> |
|--------|---------|---------|
| `CODEX_ENVIRONMENT_RUNNER` | Runner registration token for environment | On runner recycle <!-- pragma: allowlist secret --> |
| `CODEX_RUNNER_SHA256` | SHA256 checksum of runner binary | On binary update |
| `CODEX_RUNNER_TOKEN` | Auth token for self-hosted runner | Every 90 days <!-- pragma: allowlist secret --> |

---

### Repository Secrets

| Secret | Purpose | Security Level <!-- pragma: allowlist secret --> |
|--------|---------|----------------|
| `CODEX_GHP_TOKEN_BASE64` | GitHub PAT (Base64 encoded) | CRITICAL <!-- pragma: allowlist secret --> |
| `CODEX_GHP_TOKEN_HEX` | GitHub PAT (Hex encoded) | CRITICAL <!-- pragma: allowlist secret --> |
| `CODEX_GHP_TOKEN_SHA256` | GitHub PAT (SHA256 hash for verification) | CRITICAL <!-- pragma: allowlist secret --> |
| `CODEX_REPO_ID` | GitHub repository numeric ID | HIGH |
| `CODEX_WEBHOOK_SECRET` | HMAC secret for webhook signature validation | HIGH <!-- pragma: allowlist secret --> |
| `OPENAI_API_KEY` | OpenAI API key for LLM calls | CRITICAL <!-- pragma: allowlist secret --> |
| `_CODEX_BOT_RUNNER` | Bot runner auth token | HIGH <!-- pragma: allowlist secret --> |

---

### Organization Secrets

| Secret | Purpose | Security Level | Age <!-- pragma: allowlist secret --> |
|--------|---------|----------------|-----|
| `CODECOV_TOKEN` | Upload coverage reports to Codecov | MEDIUM | 5 months ⚠️ <!-- pragma: allowlist secret --> |
| `CODEX_ADMIN_KEY` | Admin-level operations key | CRITICAL | 3 months |
| `CODEX_BACKUP_KEY` | Fallback key for write operations | CRITICAL | 3 months |
| `CODEX_MASTER_KEY` | Master key for all token-chain write ops | CRITICAL | 3 months <!-- pragma: allowlist secret --> |
| `HF_TOKEN` | HuggingFace Hub access token | HIGH | 5 months ⚠️ <!-- pragma: allowlist secret --> |
| `NPM_TOKEN` | npm package publishing token | HIGH | 5 months ⚠️ <!-- pragma: allowlist secret --> |
| `PYPI_TOKEN` | PyPI package publishing token | HIGH | 5 months ⚠️ <!-- pragma: allowlist secret --> |
| `RAG_OPENAI_KEY` | Dedicated OpenAI key for RAG pipeline | HIGH | 4 months |
| `_CODEX_ACTION_RUNNER` | Actions runner registration token | HIGH | 5 months ⚠️ <!-- pragma: allowlist secret --> |
| `_GITHUB_APP_CLIENT_SECRET` | GitHub App OAuth client secret | CRITICAL | 3 months <!-- pragma: allowlist secret --> |
| `_GITHUB_APP_ID` | GitHub App identifier | HIGH | 3 months |
| `_GITHUB_APP_INSTALLATION_ID` | App installation identifier | HIGH | 3 months |
| `_GITHUB_APP_PRIVATE_KEY` | GitHub App private key (RSA) | CRITICAL | 3 months |

---

## 🔴 Gap Analysis — Variables Referenced in Code but NOT in Inventory

The following variables are referenced in source code, workflow files, or `.codex/` docs but **are not present** in the active repository/environment variable inventory. The maintainer should evaluate each for creation.

### Service API (`services/api/main.py`)

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `CODEX_AUTH_SECRET` | Repo Var | — | API service authentication secret <!-- pragma: allowlist secret --> |
| `CODEX_AUTH_MIDDLEWARE_ENABLED` | Repo Var | `true` | Enable auth middleware on API service |
| `CODEX_AUTH_RATE_LIMIT` | Repo Var | `100` | API rate limit (requests/minute) |
| `CODEX_ENV` | Workflow-exported env (repo-var fallback optional) | `copilot-agent` in `copilot-setup-steps.yml`, otherwise `development` fallback | Sandbox/runtime environment label used by security-aware components |
| `DISABLE_SECRET_FILTER` | Repo Var | `false` | **⚠️ DANGER — NEVER set to `true` in production.** Bypasses all secret redaction in API logs. Use ONLY in isolated local debugging sessions with no real credentials present. Any attempt to enable this in CI/CD should trigger an immediate security alert. <!-- pragma: allowlist secret --> |
| `ARTIFACTS_DIR` | Repo Var | `/tmp/artifacts` | API artifact output directory |

### Nox / ML Pipeline (`noxfile.py`, `scripts/`)

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `CODEX_CPU_MINIMAL` | Repo Var | `0` | Minimal CPU-only mode (skip heavy GPU sessions) |
| `CODEX_ABORT_ON_GPU_PULL` | Repo Var | `0` | Abort if GPU environment detected |
| `CODEX_ALLOW_TRITON_CPU` | Repo Var | `0` | Allow Triton CPU fallback |
| `CODEX_DEPENDENCY_EVIDENCE_PATH` | Repo Var | `.codex/evidence` | Path for dependency evidence artifacts |
| `CODEX_GIT_SHA` | Repo Var | — | Current git SHA injected at CI start |
| `CODEX_NET_ALLOWLIST` | Repo Var | — | Allowed network hosts (comma-separated) |
| `CODEX_NET_MODE` | Repo Var | `isolated` | Network mode alias for `CODEX_NETWORK_MODE` |
| `CODEX_NUM_THREADS` | Repo Var | `4` | Thread pool size for parallel operations |
| `CODEX_PIPELINE_STRICT` | Repo Var | `false` | Fail pipeline on any non-critical warning |
| `CODEX_SEED` | Repo Var | `42` | Random seed for deterministic ML runs |

### Cognitive Brain & Session (`.codex/CRITICAL_REPOSITORY_VARIABLES.md`)

| Variable | Type | Recommended Value | Purpose |
|----------|------|-------------------|---------|
| `SESSION_CONTEXT_AUTO_CAPTURE` | Repo Var | `true` | Auto-capture session context at start |
| `SESSION_CONTEXT_AUTO_INJECT` | Repo Var | `true` | Auto-inject prior context on agent init |
| `COGNITIVE_BRAIN_SESSION_RETENTION_HOURS` | Repo Var | `24` | Hours to retain session context |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | Repo Var | `5` | Self-healing agent rate limit |
| `CODEX_TELEMETRY_ENABLED` | Repo Var | `true` | Enable metrics collection |
| `METRICS_COLLECTION_INTERVAL_SECONDS` | Repo Var | `60` | Metrics sampling interval |
| `WORKFLOW_FAILURE_TRACKING_ENABLED` | Repo Var | `true` | Track all workflow failures |

### CI/CD Timeouts & Parallelism (`.codex/CRITICAL_REPOSITORY_VARIABLES.md`)

| Variable | Type | Recommended Value | Purpose |
|----------|------|-------------------|---------|
| `NODE_JS_VERSION` | Repo Var | `22` | Node.js LTS version for CI/workflows. **Scope note:** this is separate from environment variable `CODEX_ENV_NODE_VERSION` (sandbox runtime). `.github/workflows/copilot-setup-steps.yml` reads it as `NODE_VERSION: ${{ vars.NODE_JS_VERSION \|\| '22' }}`. |
| `CODEX_TEST_TIMEOUT_MINUTES` | Repo Var | `60` | Per-job test timeout |
| `CODEX_JOB_TIMEOUT_MINUTES` | Repo Var | `120` | Global job timeout |
| `CODEX_MAX_PARALLEL_JOBS` | Repo Var | `4` | Max concurrent jobs |
| `CODEX_SHARD_COUNT` | Repo Var | `4` | Test sharding count |

---

## 🔧 Token Chain

All write operations in this repository use the following fallback chain:

```
GH_TOKEN = CODEX_MASTER_KEY || CODEX_BACKUP_KEY || github.token  # pragma: allowlist secret
```

Defined in `COPILOT_AGENT_PREFLIGHT_RULES.token_rule`. Never use `git push` directly — always use `report_progress` tool.

---

## 🔄 Secret Rotation Schedule

| Secret | Rotation Frequency | Method | Due <!-- pragma: allowlist secret --> |
|--------|-------------------|--------|-----|
| `CODEX_MASTER_KEY` | Every 90 days | Manual → update org secret | 2026-06-28 <!-- pragma: allowlist secret --> |
| `CODEX_BACKUP_KEY` | Every 90 days | Manual → update org secret | 2026-06-28 <!-- pragma: allowlist secret --> |
| `CODEX_ADMIN_KEY` | Every 90 days | Manual → update org secret | 2026-06-28 <!-- pragma: allowlist secret --> |
| `_GITHUB_APP_PRIVATE_KEY` | Every 90 days | GitHub App → regenerate | 2026-06-03 |
| `_GITHUB_APP_CLIENT_SECRET` | Every 90 days | GitHub App → regenerate | 2026-06-04 <!-- pragma: allowlist secret --> |
| `CODEX_RUNNER_TOKEN` | Every 90 days | Runner recycle | 2026-06-04 <!-- pragma: allowlist secret --> |
| `OPENAI_API_KEY` | Every 90 days | OpenAI dashboard | 2026-06-03 <!-- pragma: allowlist secret --> |
| `CODECOV_TOKEN` | Annual | Codecov dashboard | ⚠️ OVERDUE (5 months) <!-- pragma: allowlist secret --> |
| `HF_TOKEN` | Annual | HuggingFace settings | ⚠️ OVERDUE (5 months) <!-- pragma: allowlist secret --> |
| `NPM_TOKEN` | Annual | npm settings | ⚠️ OVERDUE (5 months) <!-- pragma: allowlist secret --> |
| `PYPI_TOKEN` | Annual | PyPI account | ⚠️ OVERDUE (5 months) <!-- pragma: allowlist secret --> |
| `_CODEX_ACTION_RUNNER` | Annual | GitHub Actions runners | ⚠️ OVERDUE (5 months) |

---

## 🧩 `settings/variables/agents` — Recommended Additions

The Copilot agents settings page currently shows only the firewall defaults. The following variables **MUST or SHOULD** be added at `https://github.com/Aries-Serpent/_codex_/settings/variables/agents`:

| Variable | Value | Priority | Reason |
|----------|-------|----------|--------|
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | **MUST** | Controls maximum autonomy level granted to all Copilot coding agents |
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | **MUST** | Enforces auth token requirement for all agent write operations <!-- pragma: allowlist secret --> |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | **MUST** | Enables cognitive brain session restore on agent init |
| `COPILOT_AGENT_PREFLIGHT_RULES` | _(see repo var)_ | **MUST** | Pre-commit rules and mandatory doc loads; agents MUST read this at session start |
| `COPILOT_WEC_SELECTION_MATRIX` | _(see repo var)_ | **MUST** | Workflow Execution Checklist trigger map; agents must reference to select WEC items |
| `CODEX_LINT_STRICT` | `true` | **SHOULD** | Instructs agents to fail on any lint warning |
| `CODEX_COVERAGE_THRESHOLD` | `80` | **SHOULD** | Coverage gate threshold visible to agents |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | **SHOULD** | Confirms cognitive brain injection is active |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `128000` | **SHOULD** | Lets agents know their max context budget <!-- pragma: allowlist secret --> |

---

## Workflow Permissions Reference

| Workflow | Required Permissions |
|----------|---------------------|
| `auth-token-rotation.yml` | `contents: write`, `issues: write`, `secrets: write` <!-- pragma: allowlist secret --> |
| `auth-secret-rotation.yml` | `contents: write`, `secrets: write`, `issues: write` <!-- pragma: allowlist secret --> |
| `auth-compliance-report.yml` | `contents: read`, `issues: write` |
| `release.yml` | `contents: write`, `packages: write`, `id-token: write` <!-- pragma: allowlist secret --> |
| `cognitive-brain` writes | Uses `_GITHUB_APP_*` via `actions/create-github-app-token@v1` <!-- pragma: allowlist secret --> |

---

## 🗺️ Workflow & Agent Variable Usage Map

This section maps each key repository variable to the GitHub Actions workflows and custom agents that read it. Reference this when changing a variable value to understand downstream impact.

### Copilot Sandbox Bootstrap Surface (`.github/workflows/copilot-setup-steps.yml`)

| Variable | Surface | Current behavior | Downstream consumers |
|----------|---------|------------------|----------------------|
| `NODE_JS_VERSION` | Repository variable → workflow `env.NODE_VERSION` | Read as `${{ vars.NODE_JS_VERSION \|\| '22' }}` | Node/npm tools in the Copilot sandbox |
| `COPILOT_RUNNER_PROFILE` | Repository variable → `runs-on` | Read as `${{ vars.COPILOT_RUNNER_PROFILE \|\| 'ubuntu-latest' }}` | Runner sizing for Copilot sessions |
| `CODEX_CACHE_VERSION` | Repository variable → `setup-agent-env` input | Read as `${{ vars.CODEX_CACHE_VERSION \|\| 'v2' }}` | Agent venv/cache hierarchy and cache invalidation |
| `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY` | Organization secrets → job env → export step | Injected into the agent runtime for token-chain writes | `agent-auth-delegation`, variable sync, workflow dispatch <!-- pragma: allowlist secret --> |
| `CODEX_ENV` | Workflow-exported env | Explicitly set to `copilot-agent` | Security/compliance agents, runtime guards |
| `CODEX_LOG_LEVEL` | Workflow-exported env | Currently exported as `INFO` | Session diagnostics and troubleshooting |
| `CODEX_DB_PATH` | Workflow-exported env | Currently exported as `${GITHUB_WORKSPACE}/.codex/codex.db` | Cognitive brain / pattern-recorder DB consumers |
| `CODEX_LOG_DB_PATH` | Runtime default / optional env override | Defaults to `.codex/session_logs.db` | Logging, export, query, and viewer tools |

### Agents Settings Surface (`settings/variables/agents`)

| Variable | Surface | Current expectation | Primary consumers |
|----------|---------|---------------------|-------------------|
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | Agent variable | `D` ceiling | All Copilot/custom agents |
| `COPILOT_AGENT_AUTH_ENABLED` | Agent variable | `true` | Auth-gated write paths |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | Agent variable | `true` | `cognitive-brain-session-injector` |
| `COPILOT_AGENT_PREFLIGHT_RULES` | Agent + repo JSON | Mandatory load at session start | All Copilot/custom agents |
| `COPILOT_WEC_SELECTION_MATRIX` | Agent + repo JSON | Current routing matrix | Workflow/orchestration agents |
| `COPILOT_WEC_TEMPLATE_DRIFT` | Agent + repo JSON | Expected steady-state `count=0` after remediation | `workflow-compliance-guardian`, WEC-aware agents |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | Agent variable | `true` | Cognitive Brain session/bootstrap agents |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | Agent variable | `128000` | Cognitive/context-budget aware agents <!-- pragma: allowlist secret --> |

### Workflow Automation / CI Surface

| Variable | Verified workflow readers | Primary agent/process consumers |
|----------|---------------------------|---------------------------------|
| `CODEX_TEST_TIMEOUT_MINUTES` | `auth-tests.yml`, `coverage-with-timeout.yml`, `nox_gates.yml`, `test-rag.yml` | `ci-testing-agent`, `autonomous-test-healer-agent` |
| `CODEX_COVERAGE_THRESHOLD` | `ci-checkpoint-validation.yml`, `code-quality-coverage-suite.yml`, `copilot-agent-vars-bootstrap.yml` | `unified-coverage-agent`, `ci-testing-agent` |
| `CODEX_CI_FAILURE_RATE` | `copilot-agent-vars-bootstrap.yml`, `repo-var-sync-schedule.yml` | `ci-health-alert-agent`, `ci-triage-pipeline-agent` |
| `CODEX_CI_FAILURE_THRESHOLD` | `ci-health-monitor.yml`, `repo-var-sync-schedule.yml` | `ci-health-alert-agent` |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | `copilot-iterative-self-healing.yml`, `iterative-self-healing-ci.yml`, `self-healing.yml` | Self-healing agent family |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | `agent-auth-delegation.yml`, `chatops_copilot_trigger.yml`, `copilot-iterative-self-healing.yml`, `repo-var-sync-schedule.yml` | Session injection and orchestration agents |

### Runtime / Service Guard Surface

| Variable | Surface | Current expectation | Primary consumers |
|----------|---------|---------------------|-------------------|
| `CODEX_ENV` | Workflow-exported env or repo-var fallback | `copilot-agent` in Copilot sessions; `production` must trigger stricter guards | Security/compliance agents, service config |
| `DISABLE_SECRET_FILTER` | Repository variable | Must remain `false` outside isolated local debugging | `pii-scrubber`, `secret-detection-agent` <!-- pragma: allowlist secret --> |
| `CODEX_AUTH_MIDDLEWARE_ENABLED` | Repository variable | Default `true` | API/auth validation |
| `CODEX_AUTH_RATE_LIMIT` | Repository variable | Default `100` | API/auth validation |

---

### Variable Access Pattern in Workflows

All variables should be accessed using the safe fallback pattern:

```yaml
env:
  CODEX_CACHE_VERSION: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
  # NODE_VERSION is a workflow-level alias that reads vars.NODE_JS_VERSION:
  #   env: { NODE_VERSION: "${{ vars.NODE_JS_VERSION || '22' }}" }
  CODEX_TEST_TIMEOUT: ${{ vars.CODEX_TEST_TIMEOUT_MINUTES || '60' }}
  COGNITIVE_BRAIN_INJECTION_ENABLED: ${{ vars.COGNITIVE_BRAIN_INJECTION_ENABLED || 'true' }}
```

> **Note on Node.js version variables**:
> - `NODE_JS_VERSION` — **repo var** (create in GitHub UI → Settings → Actions → Variables). CI workflows (e.g., `copilot-setup-steps.yml`) read it as `env.NODE_VERSION: ${{ vars.NODE_JS_VERSION || '22' }}`.
> - `CODEX_ENV_NODE_VERSION` — **environment var** (Aries_Serpent_codex_ environment). Injected into the Copilot agent sandbox. These are two separate mechanisms serving different scopes.
> - `CODEX_ENV` — **runtime env value** exported by `copilot-setup-steps.yml` (`copilot-agent` today). This is distinct from any optional repository variable fallback used by services outside the Copilot sandbox.
> - `CODEX_DB_PATH` vs `CODEX_LOG_DB_PATH` — the setup workflow currently exports `CODEX_DB_PATH=${GITHUB_WORKSPACE}/.codex/codex.db` for cognitive/pattern state, while logging tools still default to `CODEX_LOG_DB_PATH=.codex/session_logs.db`.

For integer fields (e.g., `timeout-minutes`):
```yaml
timeout-minutes: ${{ fromJSON(vars.CODEX_TEST_TIMEOUT_MINUTES || '60') }}
```

For action inputs:
```yaml
- uses: ./.github/actions/setup-python-cached
  with:
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
- uses: actions/setup-node@v6
  with:
    node-version: ${{ vars.NODE_JS_VERSION || '22' }}
```

### Agent Variable Expectations

Every custom Copilot coding agent MUST:
1. Check `AGENT_KILL_SWITCH` (`vars.AGENT_KILL_SWITCH == '1'` → abort immediately)
2. Read `COPILOT_AGENT_PREFLIGHT_RULES` for pre-commit compliance rules
3. Reference `COPILOT_WEC_SELECTION_MATRIX` for WEC item routing
4. Respect `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` (ceiling: `D`)
5. Use token chain: `CODEX_MASTER_KEY || CODEX_BACKUP_KEY || github.token`

Every agent SHOULD:
6. Read `COGNITIVE_BRAIN_INJECTION_ENABLED` before calling cognitive brain APIs
7. Honor `CODEX_LINT_STRICT` when running linters
8. Respect `CODEX_COVERAGE_THRESHOLD` (default: `80`) for coverage gates
9. Check `CODEX_MAX_HEALER_RUNS_PER_HOUR` before triggering self-healing loops
10. Log telemetry if `CODEX_TELEMETRY_ENABLED` is `true`

Full per-agent variable expectations: [`agents/VARIABLE_EXPECTATIONS.md`](../agents/VARIABLE_EXPECTATIONS.md)

---

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Token chain for write ops**: `CODEX_MASTER_KEY` → `CODEX_BACKUP_KEY` → `github.token`
3. **Rotate compromised secrets immediately** — see `.codex/security/rotation_schedule.md`
4. **Use least privilege** for workflow permissions
5. **Audit secret access** via GitHub → Settings → Security → Audit log
6. **`DISABLE_SECRET_FILTER`** — must never be set to `true` in production
7. **`AGENT_KILL_SWITCH`** — set to `1` to immediately halt all autonomous agent activity

---

## Monitoring and Auditing

- **Audit Log**: Settings → Security → Audit log → Filter by "secret"
- **CI Failure Rate**: `CODEX_CI_FAILURE_RATE` (auto-updated by CI agent, thresholds via `CODEX_CI_FAILURE_THRESHOLD`)
- **Secret Access Patterns**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- **Usage Matrix**: `.codex/security/secrets_usage_matrix.json`

---

## What’s Next (After Variable Sync)

1. **Secrets pass (pending):** update/verify repo, environment, and org secrets inventory and rotation state.
2. **WEC drift verification:** keep `COPILOT_WEC_TEMPLATE_DRIFT` aligned with the remediated `_WEC_ITEMS` state (`count=0` expected after the 2026-06-03 update).
3. **Agent settings alignment:** verify `/settings/variables/agents` mirrors critical runtime variables (`COPILOT_AGENT_*`, `COPILOT_WEC_*`, `COGNITIVE_BRAIN_*`, `CODEX_LINT_STRICT`, `CODEX_COVERAGE_THRESHOLD`).
4. **`DISABLE_SECRET_FILTER` hardening:** keep default/effective value `false`, add explicit CI/policy guard to block any promotion flow that attempts `true`.
5. **Post-secrets refresh:** regenerate totals and audit timestamp once secrets are synchronized.

---

## References

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/)
- [PR Lifecycle Spec](ci/PR_LIFECYCLE.md) — referenced by `CODEX_PR_LIFECYCLE_VERSION`
- [Codebase Agency Policy](../.codex/CODEBASE_AGENCY_POLICY.md) — mandatory load per `COPILOT_AGENT_PREFLIGHT_RULES`

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-16 | Initial documentation created | @copilot |
| 2026-01-20 | Phase 22 Secrets Audit — added 11 undocumented secrets | @copilot <!-- pragma: allowlist secret --> |
| 2026-01-27 | Added GITLEAKS_LICENSE documentation | @copilot |
| 2026-06-03 | **Full inventory refresh** — added all 113 variables (14 env, 76 repo, 3 env secrets, 7 repo secrets, 13 org secrets); added gap analysis (30+ missing variables); added rotation schedule; added `settings/variables/agents` recommendations; updated token chain docs | @mbaetiong <!-- pragma: allowlist secret --> |
| 2026-06-03 | **Variable usage expansion** — updated `CODEX_ENV_NODE_VERSION` 18→22; added Workflow & Agent Variable Usage Map (CI/CD, autonomy, cognitive brain, self-healing, API categories); added agent variable access pattern reference; added per-agent MUST/SHOULD requirements | @mbaetiong |
| 2026-06-03 | **Variables-only sync pass** — updated totals to 113 tracked (14 env vars, 76 repo vars), updated `CODEX_CI_LAST_GREEN_SHA`, and added explicit next-step actions for pending secrets pass and WEC drift remediation | @mbaetiong <!-- pragma: allowlist secret --> |
| 2026-06-03 | **Workflow/agent reconciliation pass** — aligned cache defaults to `v2`, documented `COPILOT_RUNNER_PROFILE` safe fallback (`ubuntu-latest`), clarified `CODEX_ENV=copilot-agent`, and split `CODEX_DB_PATH` vs `CODEX_LOG_DB_PATH` by effective runtime surface | @copilot |

---

**Last Updated**: 2026-06-03T22:09:48Z
**Maintainer**: @mbaetiong
**Review Frequency**: Quarterly

#### `GITLEAKS_LICENSE`
- **Purpose**: License key for Gitleaks Pro/Enterprise for enhanced secret scanning capabilities
- **Format**: Gitleaks license key string
- **Used In**:
  - `security-suite.yml`
- **Generation**: Obtained from Gitleaks subscription (https://gitleaks.io)
- **Security Level**: LOW - Does not grant access to sensitive data, only enables scanning features
- **Required**: No (Gitleaks works without it in free mode with limited features)
- **Rotation**: As needed when subscription is renewed
- **Note**: Free version of Gitleaks works without this secret; this is only required for Pro/Enterprise features

#### `SESSION_ENCRYPTION_KEY`
- **Purpose**: Encrypt session data for secure storage
- **Format**: Base64-encoded Fernet key
- **Used In**: `auth-secret-rotation.yml`
- **Generation**: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- **Security Level**: HIGH - Rotate every 90 iterations
- **Required**: Yes (for session security features)

#### `ENABLE_LIVE_TESTS`
- **Purpose**: Feature flag to enable live integration tests
- **Format**: Boolean string ("true" or "false")
- **Used In**: `integration-gated.yml`
- **Security Level**: LOW (configuration flag)
- **Required**: No (defaults to false)

### Third-Party Integration Secrets

#### `NOTEBOOKLM_WEBHOOK_URL`
- **Purpose**: NotebookLM webhook URL for documentation sync
- **Format**: HTTPS webhook URL
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: LOW - Regenerate webhook as needed
- **Required**: No (sync skipped if not available)

#### `GOOGLE_CLIENT_SECRET`
- **Purpose**: Google OAuth client secret for API access
- **Format**: Google OAuth 2.0 client secret
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: MEDIUM - Rotate every 180 iterations
- **Required**: No (for Google Drive integration features)

#### `GDRIVE_SERVICE_ACCOUNT_JSON`
- **Purpose**: Google Drive service account credentials
- **Format**: JSON key file content (base64 or raw JSON)
- **Used In**: `notebooklm-sync.yml`
- **Security Level**: MEDIUM - Rotate annually
- **Required**: No (for automated Drive operations)

#### `GITHUB_OAUTH_CLIENT_ID`
- **Purpose**: GitHub OAuth app client ID (public identifier)
- **Format**: 20-character hex string
- **Used In**: `auth-oauth-app-sync.yml`
- **Security Level**: LOW (public identifier, not secret)
- **Required**: Yes (for OAuth flow)

#### `GITHUB_OAUTH_CLIENT_SECRET`
- **Purpose**: GitHub OAuth app client secret
- **Format**: 40-character hex string
- **Used In**:
  - `auth-oauth-app-sync.yml`
  - `auth-secret-rotation.yml`
- **Generation**: Via GitHub OAuth App settings
- **Security Level**: HIGH - Rotate every 180 iterations
- **Required**: Yes (for OAuth authentication)

### PyPI Publishing Secrets

#### `PYPI_API_TOKEN`
- **Purpose**: PyPI API token for publishing packages to production PyPI
- **Format**: `pypi-` prefixed token string from PyPI account settings
- **Used In**:
  - `pypi-publish.yml`
  - Package publishing workflows
- **Generation**: Via PyPI Account Settings → API tokens → Generate new token
- **Security Level**: HIGH - Rotate every 90 iterations or after each use
- **Required**: Yes (for production PyPI publishing)
- **Rotation**: Recommended after each release or every 90 iterations
- **Note**: Use with username `__token__` in Twine configuration

#### `TEST_PYPI_API_TOKEN`
- **Purpose**: TestPyPI API token for testing package uploads before production
- **Format**: `pypi-` prefixed token string from TestPyPI account settings
- **Used In**:
  - `pypi-publish.yml`
  - Pre-release testing workflows
- **Generation**: Via TestPyPI Account Settings → API tokens → Generate new token
- **Security Level**: MEDIUM - Rotate every 90 iterations
- **Required**: No (recommended for testing releases before production)
- **Rotation**: Recommended every 90 iterations
- **Note**: Separate token from production PYPI_API_TOKEN for security isolation

### AWS Integration Secrets

#### `AWS_ACCESS_KEY_ID`
- **Purpose**: AWS IAM access key ID (public identifier)
- **Format**: 20-character uppercase alphanumeric
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (public identifier, paired with SECRET)
- **Required**: Yes (for AWS S3/service access)

#### `AWS_SECRET_ACCESS_KEY`
- **Purpose**: AWS IAM secret access key
- **Format**: 40-character base64-encoded string
- **Used In**: `zendesk-knowledge-sync.yml`
- **Generation**: Via AWS IAM Console
- **Security Level**: HIGH - Rotate every 90 iterations
- **Required**: Yes (for AWS authentication)

### Zendesk Integration Secrets

#### `ZENDESK_TOKEN`
- **Purpose**: Zendesk API authentication token
- **Format**: Zendesk API token string
- **Used In**: `zendesk-knowledge-sync.yml`
- **Generation**: Via Zendesk Admin → API settings
- **Security Level**: MEDIUM - Rotate annually
- **Required**: Yes (for knowledge base sync)

#### `ZENDESK_USER`
- **Purpose**: Zendesk account email for API authentication
- **Format**: Email address
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (username, public)
- **Required**: Yes (paired with ZENDESK_TOKEN)

#### `ZENDESK_URL`
- **Purpose**: Zendesk instance URL
- **Format**: HTTPS URL (e.g., https://company.zendesk.com)
- **Used In**: `zendesk-knowledge-sync.yml`
- **Security Level**: LOW (public URL)
- **Required**: Yes (to specify Zendesk instance)

## Environment Variables

### Runtime Configuration

#### `CODEX_ENV_*`
- **Purpose**: Select language versions during environment setup
- **Variables**:
  - `CODEX_ENV_PYTHON_VERSION` (default: 3.12)
  - `CODEX_ENV_NODE_VERSION` (default: 22)
  - `CODEX_ENV_RUST_VERSION` (default: 1.92)
  - `CODEX_ENV_GO_VERSION` (default: 1.21)
  - `CODEX_ENV_SWIFT_VERSION` (default: 5.9)

#### `CODEX_SESSION_*`
- **Purpose**: Session management and logging
- **Variables**:
  - `CODEX_SESSION_ID`: Unique session identifier
  - `CODEX_SESSION_LOG_DIR`: Log directory (default: `.codex/sessions`)

#### `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH`
- **Purpose**: SQLite database path for logging
- **Default**: `CODEX_LOG_DB_PATH=.codex/session_logs.db`; `copilot-setup-steps.yml` currently overrides `CODEX_DB_PATH` to `${GITHUB_WORKSPACE}/.codex/codex.db`
- **Usage split**: Use `CODEX_LOG_DB_PATH` for session-log storage/query/export flows, and use `CODEX_DB_PATH` for cognitive-brain / pattern-recorder state when the Copilot sandbox override is active

#### `CODEX_SQLITE_POOL`
- **Purpose**: Enable per-session SQLite connection pooling
- **Values**: `1` (enabled) or `0` (disabled)
- **Default**: `0`

### CI/CD Environment Variables

#### `CARGO_TERM_COLOR`
- **Purpose**: Enable colored output in Cargo
- **Value**: `always`
- **Used In**: Rust CI workflows

#### `RUST_BACKTRACE`
- **Purpose**: Enable full backtraces for Rust panics
- **Value**: `1` or `full`
- **Used In**: Rust testing and debugging

#### `RUST_TEST_THREADS`
- **Purpose**: Control test parallelism
- **Value**: `1` (sequential) for deterministic tests
- **Used In**: `rust_swarm_ci.yml`

## Workflow Permissions

### Required Permissions by Workflow

#### `auth-token-rotation.yml`
```yaml
permissions:
  contents: write     # Read/write repository contents
  issues: write       # Create audit issues
  secrets: write      # Update GitHub secrets
```

#### `auth-secret-rotation.yml`
```yaml
permissions:
  contents: write     # Read/write repository contents
  secrets: write      # Rotate secrets
  issues: write       # Create audit trail
```

#### `auth-compliance-report.yml`
```yaml
permissions:
  contents: read      # Read repository data
  issues: write       # Post compliance reports
```

#### `phase10-automated-secrets-setup.yml`
```yaml
permissions:
  contents: read      # Read configuration
  actions: write      # Manage workflow state
  secrets: write      # Initialize secrets
```

## Security Best Practices

### Secret Rotation Schedule

Comprehensive rotation schedule with all 18 secrets: **.codex/security/rotation_schedule.md**

| Secret Category | Examples | Rotation Frequency | Method <!-- pragma: allowlist secret --> |
|----------------|----------|-------------------|--------|
| **Critical** | `CODEX_MASTER_KEY`, `TOKEN_SECRET_KEY` | Every 90 iterations (JWT: monthly) | Manual / Automated workflow <!-- pragma: allowlist secret --> |
| **High Priority** | `COMPLIANCE_REPORT_KEY`, `SESSION_ENCRYPTION_KEY`, `AWS_SECRET_ACCESS_KEY` | Every 90 iterations | Manual via service provider <!-- pragma: allowlist secret --> |
| **Medium Priority** | `CODECOV_TOKEN`, `ZENDESK_TOKEN`, `GOOGLE_CLIENT_SECRET` | Annually or as needed | Manual via service dashboard <!-- pragma: allowlist secret --> |
| **Config/Public IDs** | `GITHUB_TOKEN`, `AWS_ACCESS_KEY_ID`, `ZENDESK_URL`, `GITLEAKS_LICENSE` | N/A or with paired secret / On renewal | GitHub auto / Manual / Subscription renewal <!-- pragma: allowlist secret --> |

### Secrets Usage Matrix

Complete mapping of all secrets to workflows: **.codex/security/secrets_usage_matrix.json**

**Summary**:
- Total Secrets: 18
- Total Workflows: 86
- Secret References: 108
- Most Used: `GITHUB_TOKEN` (20 workflows)
- Newly Documented: `SESSION_ENCRYPTION_KEY`, `ENABLE_LIVE_TESTS`, `GITLEAKS_LICENSE`, AWS/Zendesk/Google integration secrets

### Secret Management Guidelines

1. **Never commit secrets** to the repository
2. **Use environment-specific secrets** for dev/staging/prod
3. **Rotate compromised secrets immediately** (see emergency procedures in https://github.com/Aries-Serpent/_codex_/blob/main/.codex/security/rotation_schedule.md)
4. **Audit secret access** via GitHub audit logs
5. **Use least privilege** for workflow permissions
6. **Document all secrets** in this file
7. **Test rotation procedures** regularly
8. **Review usage matrix** monthly for unauthorized secret sprawl

### MFA and Authentication

#### MFA Enrollment Process

The MFA enrollment automation (`scripts/mfa_enrollment_automation.py`) generates TOTP secrets and backup codes but **does not store or transmit them automatically**. In production:

1. Credentials must be delivered via secure, authenticated channels:
   - Encrypted email with PGP
   - SMS to verified numbers
   - Secure internal portal with authentication
   - Physical security keys

2. The current implementation is a **placeholder** - implement secure delivery before production use.

3. Never log or expose MFA secrets in plain text.

## Troubleshooting

### Missing Secret Errors

---

**Last Updated**: 2026-06-03T18:02:00Z
**Maintainer**: @mbaetiong
**Review Frequency**: Quarterly
