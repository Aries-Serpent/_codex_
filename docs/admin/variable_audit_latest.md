# Variable / Secret Audit Report

## Table of Contents

- [Summary](#summary)
- [Layer: `org-secrets`](#layer-org-secrets)
- [Layer: `repo-secrets`](#layer-repo-secrets)
- [Layer: `env-secrets`](#layer-env-secrets)
- [Layer: `repo-vars`](#layer-repo-vars)
- [Layer: `env-vars`](#layer-env-vars)
- [Layer: `codespace`](#layer-codespace)

**Repository:** `Aries-Serpent/_codex_`  
**Generated:** `2026-03-20T06:16:37.803611+00:00`  
**Auth:** ❌ no token (expected-only mode)

## Summary

| Metric | Count |
|--------|-------|
| Total expected | 99 |
| ✅ Present | 0 |
| ❌ Absent (required) | 0 |
| ❓ Unknown (no API access) | 99 |
| ➕ Extra (not in guide) | 0 |


## Layer: `org-secrets`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `CODECOV_TOKEN` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ADMIN_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_BACKUP_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_MASTER_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `HF_TOKEN` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `NPM_TOKEN` | Publish | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `PYPI_TOKEN` | Publish | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `RAG_OPENAI_KEY` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_CODEX_ACTION_RUNNER` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_CLIENT_SECRET` 🔒 | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_ID` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_INSTALLATION_ID` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_PRIVATE_KEY` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |

## Layer: `repo-secrets`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `CODEX_GHP_TOKEN_BASE64` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_GHP_TOKEN_HEX` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_GHP_TOKEN_SHA256` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_REPO_ID` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_WEBHOOK_SECRET` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `OPENAI_API_KEY` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_CODEX_BOT_RUNNER` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |

## Layer: `env-secrets`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `CODEX_ENVIRONMENT_RUNNER` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_RUNNER_SHA256` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_RUNNER_TOKEN` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |

## Layer: `repo-vars`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `COGNITIVE_BRAIN_ALLOWED_ACTORS` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_INJECTION_ENABLED` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_MEMORY_TIER` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COGNITIVE_BRAIN_SESSION_NUMBER` | Cognitive Brain | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_AGENT_AUTH_ENABLED` 🔒 | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_AGENT_FIREWALL_ENABLED` 🔒 | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_CLI_BASE_URL` | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COPILOT_CLI_ENABLED` | Copilot Runtime | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AGENT_HANDOFF_TIMEOUT_SECONDS` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUTO_PROMOTE_TIER_ENABLED` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUTONOMOUS_ACTIONS_ENABLED` 🔒 | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_CI_FAILURE_RATE` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_CI_FAILURE_THRESHOLD` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_CI_LAST_GREEN_SHA` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `EMBEDDING_INDEX_AUTO_REBUILD` | CI/CD | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUDIT_RETENTION_DAYS` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_AGENT_NAME` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_API_VERSION` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ISOLATED_PATH` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_LOG_LEVEL` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_NETWORK_MODE` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ORG_NAME` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `GENESIS_TIMESTAMP` | Config | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_CACHE_VERSION` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_CLI_API_URL` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_COVERAGE_THRESHOLD` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_D365_POLICIES_PATH` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_FORCE_CPU` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_LINT_STRICT` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_LLM_MODEL` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_LLM_RATE_LIMIT_DELAY` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_OFFLINE` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_PYTHON_VERSION` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_SANDBOX_TIMEOUT` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_SESSION_ID` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_SESSION_LOG_DIR` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_TEST_PARALLELISM` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ZENDESK_DOCS_ROOT` | Build | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `ENABLE_LIVE_TESTS` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `COMPOSE_DOCKER_CLI_BUILD` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `DOCKER_BUILDKIT` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `GPU_OPT` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `HF_HOME` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `MLFLOW_EXPERIMENT_NAME` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `TORCH_HOME` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `TRANSFORMERS_OFFLINE` | ML | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `WANDB_MODE` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `ZENDESK_RATE_LIMIT` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `ZENDESK_SYNC_INTERVAL` | ML | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ACTIVE_CODESPACE` | Webhook/Infra | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `WEBHOOK_RECEIVER_URL` | Webhook/Infra | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AGENT_KILL_SWITCH` 🔒 | Autonomous Agent | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUTONOMY_BUDGET_SECONDS` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUTONOMY_MAX_ITERATIONS` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AUTONOMY_DRY_RUN` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AGENT_RUNNER_BUDGET_SECONDS` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AGENT_RUNNER_ITERATIONS` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `AGENT_RUNNER_DRY_RUN` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `UNCERTAINTY_BUDGET_SECONDS` | Autonomous Agent | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |

## Layer: `env-vars`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `CODEX_ENV_NODE_VERSION` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ENV_PYTHON_VERSION` | Build | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |

## Layer: `codespace`

| Status | Name | Category | Required | Notes |
|--------|------|----------|----------|-------|
| ❓ | `CODEX_MASTER_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_BACKUP_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `CODEX_ADMIN_KEY` | Auth | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_ID` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_PRIVATE_KEY` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_INSTALLATION_ID` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `_GITHUB_APP_CLIENT_SECRET` | GitHub App | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `WEBHOOK_SECRET` | Webhook/Infra | yes | No auth token — run with CODEX_MASTER_KEY set for live checks |
| ❓ | `WEBHOOK_RECEIVER_URL` | Webhook/Infra | optional | No auth token — run with CODEX_MASTER_KEY set for live checks |

---

_Generated by `scripts/tools/variable_audit_cli.py`._
