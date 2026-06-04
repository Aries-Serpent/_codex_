# Variable Visibility Audit (Pass 2) + Secrets Groundwork (Pass 3)

**Repository:** `Aries-Serpent/_codex_`  
**Date:** `2026-06-04`  
**Scope:** Variables only (pass 2), then secrets setup groundwork (pass 3 prep)

---

## 1) First-pass carry-over (from existing inventory)

From `/tmp/workspace/Aries-Serpent/_codex_/docs/Copy_of_Repository Secrets and Variables Inventory.md`:

- API verification is still blocked in-session (`403 Resource not accessible by integration`), so live read/write confirmation is still human-maintainer gated.
- The first-pass inventory already flagged 4 repository variables as missing for `copilot-setup-steps.yml`:
  - `CODEX_MAX_HEALER_RUNS_PER_HOUR`
  - `CODEX_SWEEP_SKIP_MAIN`
  - `CODEX_HEALER_SKIP_SKIPCI`
  - `COPILOT_AGENT_STATE`

---

## 2) Second-pass result: variable visibility validation (codebase-wide)

Second pass focused only on variable visibility drift between workflow usage and inventory coverage.

### 2.1 Validation method

- Enumerated `${{ vars.* }}` references in active workflows under `/tmp/workspace/Aries-Serpent/_codex_/.github/workflows/`.
- Compared those references against first-pass inventory documentation coverage.
- Cross-checked visibility surfaces already documented in repo docs:
  - Repo Actions Variables (`/settings/variables/actions`)
  - Agents Variables (`/settings/variables/agents`)
  - Org Actions Variables (`/organizations/.../settings/variables/actions`)

### 2.2 Findings summary

- **40** unique `${{ vars.* }}` workflow references found.
- **19** are not represented in first-pass inventory content and must be added/updated in the variable audit docs for visibility completeness.
- No new evidence that org-level variables are required yet; variables still appear repo-scoped in current workflow usage.

### 2.3 Missing visibility entries to add/update (second-pass backlog)

| Variable | Evidence (workflow) | Target surface | Required action |
|---|---|---|---|
| `AGENT_HANDOFF_TIMEOUT_SECONDS` | `.github/workflows/repo-var-sync-schedule.yml:114` | Repo Actions Variables | Add to inventory + verify value current |
| `AUTONOMOUS_ACTIONS_ENABLED` | `.github/workflows/chatops_copilot_trigger.yml:264`, `.github/workflows/admin_setup_verification.yml:220` | Repo Actions Variables + Agents Variables (governance) | Add/update visibility + human governance note |
| `AUTO_PROMOTE_TIER_ENABLED` | `.github/workflows/repo-var-sync-schedule.yml:116` | Repo Actions Variables | Add to inventory table |
| `CODEX_BACKUP_KEY_EXPIRY_DATE` | `.github/workflows/token-expiry-monitor.yml:43` | Repo Actions Variables | Add + document token-expiry monitor ownership |
| `CODEX_CLI_API_URL` | `.github/workflows/repo-var-sync-schedule.yml:106` | Repo Actions Variables | Add/update visibility entry |
| `CODEX_GROUNDED_TIER1_COUNT` | `.github/workflows/copilot-agent-vars-bootstrap.yml:74` | Repo Actions Variables | Add with bootstrap/automation ownership |
| `CODEX_GROUNDED_TIER2_COUNT` | `.github/workflows/copilot-agent-vars-bootstrap.yml:75` | Repo Actions Variables | Add with bootstrap/automation ownership |
| `CODEX_LAST_TELEMETRY_DATE` | `.github/workflows/copilot-agent-vars-bootstrap.yml:76` | Repo Actions Variables | Add with bootstrap/automation ownership |
| `CODEX_MASTER_KEY_EXPIRY_DATE` | `.github/workflows/token-expiry-monitor.yml:42` | Repo Actions Variables | Add + document token-expiry monitor ownership |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | `.github/workflows/repo-var-sync-schedule.yml:109` | Repo Actions Variables + Agents Variables | Add/update cross-surface sync expectation |
| `COGNITIVE_BRAIN_MEMORY_TIER` | `.github/workflows/repo-var-sync-schedule.yml:111` | Repo Actions Variables | Add/update inventory coverage |
| `COPILOT_AGENT_LAST_SESSION_ID` | `.github/workflows/copilot-agent-vars-bootstrap.yml:68` | Repo Actions Variables | Add + mark automated writer |
| `COPILOT_AGENT_SESSION_EXPIRES` | `.github/workflows/copilot-agent-vars-bootstrap.yml:67` | Repo Actions Variables | Add + mark automated writer |
| `COPILOT_CLI_BASE_URL` | `.github/workflows/repo-var-sync-schedule.yml:98` | Repo Actions Variables + Agents Variables | Add/update cross-surface visibility |
| `COPILOT_CLI_ENABLED` | `.github/workflows/repo-var-sync-schedule.yml:99` | Repo Actions Variables + Agents Variables | Add/update cross-surface visibility |
| `COPILOT_SESSION_TTL_SECONDS` | `.github/workflows/agent-auth-delegation.yml:1823` | Repo Actions Variables | Add/update inventory coverage |
| `DEPLOY_ENV` | `.github/workflows/copilot-agent-vars-bootstrap.yml:82` | Repo Actions Variables | Add to inventory + lifecycle note |
| `EMBEDDING_INDEX_AUTO_REBUILD` | `.github/workflows/repo-var-sync-schedule.yml:115` | Repo Actions Variables | Add/update inventory coverage |
| `WEBHOOK_RECEIVER_URL` | `.github/workflows/agent_infrastructure_manager.yml:199,274` | Repo Actions Variables | Add/update visibility + webhook ownership note |

---

## 3) Repo vs Org variable visibility (pass-2 decision)

### Current decision state

- Keep variables repo-scoped by default.
- Use org variables only when a variable must be shared across multiple repositories.
- If promoted to org scope, use **Selected repositories** visibility first and explicitly include `Aries-Serpent/_codex_`.

### Maintainer links

- Repo Actions Variables: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
- Agents Variables: https://github.com/Aries-Serpent/_codex_/settings/variables/agents
- Org Actions Variables: https://github.com/organizations/Aries-Serpent/settings/variables/actions

---

## 4) Third-pass groundwork (secrets-focused, human-maintainer navigation)

This section is the handoff foundation for pass 3 (secrets).

### 4.1 Primary secret management pages

- Repo Actions Secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
- Repo Agents Secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents
- Environment (`Aries_Serpent_codex_`): https://github.com/Aries-Serpent/_codex_/settings/environments/Aries_Serpent_codex_
- Org Actions Secrets: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
- Org Actions Variables (for access-policy checks tied to secret workflows): https://github.com/organizations/Aries-Serpent/settings/variables/actions

### 4.2 Workflow links maintainers should use during pass 3

- Copilot setup dependency check: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml
- Secrets/variables scanner: https://github.com/Aries-Serpent/_codex_/actions/workflows/scan-secrets-variables.yml
- Secrets baseline guard: https://github.com/Aries-Serpent/_codex_/actions/workflows/secrets-baseline-enforcer.yml
- Token expiry monitor (secret rotation metadata): https://github.com/Aries-Serpent/_codex_/actions/workflows/token-expiry-monitor.yml
- Repo variable sync (supports variable-side secret operations context): https://github.com/Aries-Serpent/_codex_/actions/workflows/repo-var-sync-schedule.yml

### 4.3 Human maintainer actions for pass 3

1. Confirm org secret access policy includes `Aries-Serpent/_codex_` where required.
2. Reconcile repo secrets vs agents secrets to avoid scope drift.
3. Execute/verify secret rotations due by age policy.
4. Run scanner and baseline workflows above; capture run URLs in audit notes.
5. Update inventory timestamps after secret pass completes (remove blocked markers when API access is restored).

---

## 5) Immediate next update targets

For documentation parity after this pass:

- Update `/tmp/workspace/Aries-Serpent/_codex_/docs/Copy_of_Repository Secrets and Variables Inventory.md` with the 19 second-pass visibility entries.
- Refresh `/tmp/workspace/Aries-Serpent/_codex_/docs/admin/variable_audit_latest.md` after a token-enabled audit run.
- Re-run pass 3 and append validated secret status using the workflow links in section 4.
