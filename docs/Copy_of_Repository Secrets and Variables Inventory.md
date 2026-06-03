# Repository Secrets and Variables Inventory
> Generated: 2026-06-03T21:34:05Z | Author: mbaetiong
> Expanded by: Copilot Task Agent (2026-06-03T21:34:05Z)
> Variable Sync Pass: 2026-06-03T21:15:07Z (variables-only; secrets unchanged)
> Secrets/API Pass Attempt: 2026-06-03T21:32:23Z (**blocked**: GitHub Actions variables/secrets APIs returned `403 Resource not accessible by integration` for current token)

## 📊 Complete Inventory Tables

> This copy preserves the 2026-06-03 inventory baseline and is updated to the latest **variables-only** snapshot: **90 variables total** (14 environment + 76 repository). Secrets were not rotated/modified in this pass.

### Environment Variables (Aries_Serpent_codex_ Environment)

| Category | Count | Source Snapshot |
|---|---:|---|
| Environment Variables | 14 | 2026-06-03 variables refresh |

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
| Repository Variables | 76 | 2026-06-03 variables refresh |

#### Maintainer Add/Update Notes — Repository Variables

| Item | Expected Action | Target Value / Rule | Reason |
|---|---|---|---|
| `CODEX_CI_FAILURE_RATE` | UPDATE (automated) | `<float>:<status>` | Confirm CI monitor keeps this fresh (currently very recent). |
| `CODEX_CI_LAST_GREEN_SHA` | UPDATE (automated) | valid git SHA | Must track latest all-green commit for triage decisions. |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | UPDATE (automated) | incrementing integer | Must increment per session lifecycle. |
| `COPILOT_ACTIVE_SESSION` | UPDATE (automated) | current session tuple | Must reflect active session state. |
| `COPILOT_AGENT_PREFLIGHT_RULES` | VERIFY JSON freshness | version/date + mandatory rules | Critical governance source for agent operations. |
| `COPILOT_WEC_SELECTION_MATRIX` | VERIFY JSON freshness | workflow mapping current to repo reality | Prevent WEC drift and checklist mismatch. |
| `COPILOT_WEC_TEMPLATE_DRIFT` | VERIFY + SYNC | `count=0` template mapping gaps (normalized `auto-approve-workflows.yml` → `auto-approve-workflows`) | Drift was remediated in `_WEC_ITEMS`; keep the repo variable and agent settings copy aligned to the current zero-drift state. |
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
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]` | ADD/SYNC | SHOULD | Restricts who can update memory/session context. |
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
| **Environment Variables** | 14 |
| **Repository Variables** | 76 |
| **Environment Secrets** | 3 |
| **Repository Secrets** | 7 |
| **Organization Secrets** | 13 |
| **TOTAL** | **113** |

---

## 🧠 Key Observations

### Most Recently Updated (from source snapshot)
- `CODEX_CI_FAILURE_RATE`
- `CODEX_CI_LAST_GREEN_SHA` (`8b5588da25a5d5f12ba8bd66cc37fa688fbc8e97`)
- `COGNITIVE_BRAIN_ALLOWED_ACTORS`
- `COGNITIVE_BRAIN_SESSION_NUMBER`
- `COPILOT_ACTIVE_SESSION`
- `COPILOT_AGENT_AUTH_ENABLED`

### Oldest Items Requiring Rotation/Audit Attention
- `AUDIT_RETENTION_DAYS` (stale policy review)
- `CODEX_AGENT_NAME`, `CODEX_API_VERSION`, `CODEX_NETWORK_MODE` (long-lived static config; verify intentional)
- Aged org secrets: `CODECOV_TOKEN`, `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `_CODEX_ACTION_RUNNER`

---

## ▶️ What’s Next (Post Variables-Only Pass)

- [ ] Execute **secrets pass** (repo/env/org) and refresh secret ages/rotation status. _(Blocked in-session by `403 Resource not accessible by integration`; requires elevated token/API scope.)_
- [x] Resolve `COPILOT_WEC_TEMPLATE_DRIFT` by adding the missing workflows to `_WEC_ITEMS` in `/tmp/workspace/Aries-Serpent/_codex_/scripts/ci/session_wrapup_autofix.py` (`e-to-d-transition-gate.yml`, `d-capable-promotion-gate.yml`, `mcp-health.yml`).
- [ ] Re-run inventory export and replace all “placeholder JSON” references with the current exact values where required. _(Blocked in-session by the same API authorization limits.)_
- [ ] Reconcile `settings/variables/agents` against repo variables to ensure no drift between Actions Variables and Agents Variables pages. _(Blocked until repo/environment/org variable APIs are readable in-session.)_
- [ ] After secrets pass, regenerate summary totals and update this file’s timestamp block. _(Partially updated in this commit; full totals refresh pending successful secrets pass.)_

---

## ✅ Maintainer Execution Checklist

- [ ] Validate current inventory against live GitHub settings (repo/env/org)
- [ ] Apply **Agent Variables** table at `/settings/variables/agents`
- [ ] Apply **Agent Secrets** table at `/settings/secrets/agents`
- [ ] Rotate overdue secrets and record rotation timestamp
- [ ] Re-run inventory scan and refresh this document timestamp
- [ ] Link resulting verification issue/PR in this file
