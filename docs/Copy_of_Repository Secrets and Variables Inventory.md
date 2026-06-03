# Repository Secrets and Variables Inventory
> Generated: 2026-06-03T17:39:00Z | Author: mbaetiong
> Expanded by: Copilot Task Agent (2026-06-03)

## 📊 Complete Inventory Tables

> This copy preserves the 2026-06-03 inventory snapshot (106 total items) and adds explicit maintainer action items for each section, including dedicated Copilot **Agent Variables** and **Agent Secrets** setup tables.

### Environment Variables (Aries_Serpent_codex_ Environment)

| Category | Count | Source Snapshot |
|---|---:|---|
| Environment Variables | 13 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Environment Variables

| Item | Expected Action | Target Value / Rule | Reason |
|---|---|---|---|
| `CODEX_ENV_NODE_VERSION` | **UPDATE** (if stale) | `22` (or approved current LTS) | Current docs indicate `22`; prior inventory showed `18`. Keep aligned with workflow/runtime expectations. |
| `CODEX_ENV_PYTHON_VERSION` | VERIFY | `3.12` | Must stay aligned with `pyproject.toml` (`requires-python >=3.12`). |
| `CODEX_DB_PATH` and `CODEX_LOG_DB_PATH` | VERIFY | `.codex/logs.db` | Keep paths consistent to avoid split logging behavior. |
| `RUST_TEST_THREADS` | VERIFY | `1` | Deterministic Rust test behavior in CI/sandbox. |

---

### Repository Variables

| Category | Count | Source Snapshot |
|---|---:|---|
| Repository Variables | 70 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Repository Variables

| Item | Expected Action | Target Value / Rule | Reason |
|---|---|---|---|
| `CODEX_CI_FAILURE_RATE` | UPDATE (automated) | `<float>:<status>` | Confirm CI monitor keeps this fresh (currently very recent). |
| `CODEX_CI_LAST_GREEN_SHA` | UPDATE (automated) | valid git SHA | Must track latest all-green commit for triage decisions. |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | UPDATE (automated) | incrementing integer | Must increment per session lifecycle. |
| `COPILOT_ACTIVE_SESSION` | UPDATE (automated) | current session tuple | Must reflect active session state. |
| `COPILOT_AGENT_PREFLIGHT_RULES` | VERIFY JSON freshness | version/date + mandatory rules | Critical governance source for agent operations. |
| `COPILOT_WEC_SELECTION_MATRIX` | VERIFY JSON freshness | workflow mapping current to repo reality | Prevent WEC drift and checklist mismatch. |
| `COPILOT_WEC_TEMPLATE_DRIFT` | UPDATE after WEC changes | drift count/details current | Ensures session wrapup checker remains accurate. |
| `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | REVIEW/PRUNE/UPDATE | approved domains only | Large allowlist should be periodically pruned and normalized. |

---

### Environment Secrets (Aries_Serpent_codex_ Environment)

| Category | Count | Source Snapshot |
|---|---:|---|
| Environment Secrets | 3 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Environment Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `CODEX_ENVIRONMENT_RUNNER` | ROTATE/VERIFY | 90-day cadence | Environment runner auth hardening. |
| `CODEX_RUNNER_SHA256` | UPDATE on runner change | must match active runner binary | Integrity verification for runner payload. |
| `CODEX_RUNNER_TOKEN` | ROTATE | 90-day cadence or on exposure | Limit long-lived runner token risk. |

---

### Repository Secrets

| Category | Count | Source Snapshot |
|---|---:|---|
| Repository Secrets | 7 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Repository Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `OPENAI_API_KEY` | ROTATE/VERIFY | 90-day cadence | LLM runtime secret hygiene. |
| `CODEX_WEBHOOK_SECRET` | ROTATE/VERIFY | on webhook infra change or 90-day | Protect webhook signature validation. |
| `_CODEX_BOT_RUNNER` | ROTATE/VERIFY | 90-day cadence | Bot runner token should not remain static. |
| `CODEX_GHP_TOKEN_BASE64` / `CODEX_GHP_TOKEN_HEX` | REVIEW necessity | keep one preferred encoding path | Reduce duplicate token encodings unless required for compatibility. |
| `CODEX_REPO_ID` | VERIFY | numeric repo ID current | Keep internal ID references consistent. |

---

### Organization Secrets

| Category | Count | Source Snapshot |
|---|---:|---|
| Organization Secrets | 13 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Organization Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `CODEX_MASTER_KEY` | **ROTATE/VERIFY PRIORITY** | 90-day cadence | Primary write token in auth chain. |
| `CODEX_BACKUP_KEY` | ROTATE/VERIFY | 90-day cadence | Fallback write token; must remain valid. |
| `CODEX_ADMIN_KEY` | ROTATE/VERIFY | 90-day cadence | Elevated operations token. |
| `_GITHUB_APP_PRIVATE_KEY` | ROTATE/VERIFY | app key rotation policy | Required for GitHub App JWT auth. |
| `_GITHUB_APP_CLIENT_SECRET` | ROTATE/VERIFY | app secret rotation policy | OAuth/App exchange integrity. |
| `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `_CODEX_ACTION_RUNNER`, `CODECOV_TOKEN` | REVIEW AGE + ROTATE as needed | follow provider policy | Aging secrets should be refreshed on schedule. |

---

## 🤖 Maintainer Required Additions — Agent Variables and Secrets

> Target UI for variables: https://github.com/Aries-Serpent/_codex_/settings/variables/agents  
> Target UI for secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents

### Agent Variables (Copilot Agent Settings)

| Variable Name | Expected Value / Source | Action | Priority | Notes |
|---|---|---|---|---|
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | ADD/VERIFY | MUST | Governs max autonomy for coding agent. |
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | ADD/VERIFY | MUST | Enforces auth-gated writes. |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | ADD/VERIFY | MUST | Enables context/session restore. |
| `COPILOT_AGENT_FIREWALL_ENABLED` | `true` | ADD/VERIFY | MUST | Enforces network boundary controls. |
| `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | repo-var current value | ADD/SYNC | MUST | Keep agent allowlist aligned with repo policy. |
| `COPILOT_AGENT_PREFLIGHT_RULES` | repo-var JSON | ADD/SYNC | MUST | Mandatory preflight, token, and WEC rules. |
| `COPILOT_WEC_SELECTION_MATRIX` | repo-var JSON | ADD/SYNC | MUST | Required for WEC workflow selection logic. |
| `COPILOT_WEC_TEMPLATE_DRIFT` | repo-var JSON | ADD/SYNC | SHOULD | Keeps agent aware of known template drift. |
| `COPILOT_SESSION_TOOL_CAPABILITIES` | repo-var JSON | ADD/SYNC | SHOULD | Agent capability map for guarded behavior. |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | ADD/VERIFY | SHOULD | Enables cognitive brain injection controls. |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `128000` | ADD/VERIFY | SHOULD | Context budget awareness for agents. |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `0.75` | ADD/VERIFY | SHOULD | Pattern injection threshold consistency. |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | current actor list | ADD/SYNC | SHOULD | Restricts who can update memory/session context. |
| `CODEX_COVERAGE_THRESHOLD` | `80` | ADD/VERIFY | SHOULD | Useful for agent remediation decisions. |
| `CODEX_LINT_STRICT` | `true` | ADD/VERIFY | SHOULD | Keeps agent behavior aligned with strict lint policy. |
| `CODEX_CI_FAILURE_THRESHOLD` | `10.0` | ADD/VERIFY | SHOULD | Supports CI health triage logic. |
| `CODEX_PYTHON_VERSION` | `3.12` | ADD/VERIFY | SHOULD | Keeps agent runtime assumptions aligned. |
| `CODEX_LOG_LEVEL` | `INFO` | ADD/VERIFY | MAY | Optional but useful for consistent diagnostics. |

### Agent Secrets (Copilot Agent Settings)

| Secret Name | Source of Truth | Action | Priority | Notes |
|---|---|---|---|---|
| `CODEX_MASTER_KEY` | Org secret | ADD/GRANT/VERIFY | MUST | Primary write/auth token for agent operations. |
| `CODEX_BACKUP_KEY` | Org secret | ADD/GRANT/VERIFY | MUST | Required fallback in token chain. |
| `CODEX_ADMIN_KEY` | Org secret | ADD/GRANT/VERIFY | SHOULD | Needed for elevated admin workflows. |
| `OPENAI_API_KEY` | Repo secret | ADD/GRANT/VERIFY | SHOULD | Needed for LLM-backed tasks where applicable. |
| `RAG_OPENAI_KEY` | Org secret | ADD/GRANT/VERIFY | MAY | Needed for RAG-specific agent operations. |
| `CODEX_WEBHOOK_SECRET` | Repo secret | ADD/GRANT/VERIFY | MAY | Needed only for webhook-managing agent flows. |
| `_GITHUB_APP_ID` | Org secret | ADD/GRANT/VERIFY | SHOULD | GitHub App auth bundle member. |
| `_GITHUB_APP_INSTALLATION_ID` | Org secret | ADD/GRANT/VERIFY | SHOULD | GitHub App installation token flow. |
| `_GITHUB_APP_PRIVATE_KEY` | Org secret | ADD/GRANT/VERIFY | SHOULD | JWT signing for App auth. |
| `_GITHUB_APP_CLIENT_SECRET` | Org secret | ADD/GRANT/VERIFY | SHOULD | OAuth/App client secret requirements. |
| `_CODEX_BOT_RUNNER` | Repo secret | ADD/GRANT/VERIFY | MAY | Needed only for runner-management tasks. |

---

## 📈 Summary Statistics

| Category | Count |
|----------|-------|
| **Environment Variables** | 13 |
| **Repository Variables** | 70 |
| **Environment Secrets** | 3 |
| **Repository Secrets** | 7 |
| **Organization Secrets** | 13 |
| **TOTAL** | **106** |

---

## 🧠 Key Observations

### Most Recently Updated (from source snapshot)
- `CODEX_CI_FAILURE_RATE`
- `CODEX_CI_LAST_GREEN_SHA`
- `COGNITIVE_BRAIN_ALLOWED_ACTORS`
- `COGNITIVE_BRAIN_SESSION_NUMBER`
- `COPILOT_ACTIVE_SESSION`
- `COPILOT_AGENT_AUTH_ENABLED`

### Oldest Items Requiring Rotation/Audit Attention
- `AUDIT_RETENTION_DAYS` (stale policy review)
- `CODEX_AGENT_NAME`, `CODEX_API_VERSION`, `CODEX_NETWORK_MODE` (long-lived static config; verify intentional)
- Aged org secrets: `CODECOV_TOKEN`, `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `_CODEX_ACTION_RUNNER`

---

## ✅ Maintainer Execution Checklist

- [ ] Validate current inventory against live GitHub settings (repo/env/org)
- [ ] Apply **Agent Variables** table at `/settings/variables/agents`
- [ ] Apply **Agent Secrets** table at `/settings/secrets/agents`
- [ ] Rotate overdue secrets and record rotation timestamp
- [ ] Re-run inventory scan and refresh this document timestamp
- [ ] Link resulting verification issue/PR in this file
