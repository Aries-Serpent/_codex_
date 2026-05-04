# Automation Plan — Safe Agentic Enablement
> Generated: 2026-05-04T16:44:03Z | Repo: Aries-Serpent/_codex_ | HEAD: d2f849550ea512c30c81de8f68a22e1ea52bbe61

---

## Stage 0 — Read-Only Analysis (Current Stage ✅)

**Goal:** Discover and map all agentic surfaces without any mutations.

| Check | Status |
|---|---|
| Load CODEBASE_AGENCY_POLICY.md | ✅ |
| Manifest inventory produced | ✅ `.codex/agentic-enablement/manifest_inventory.md` |
| Evidence inventory produced | ✅ `.codex/agentic-enablement/evidence_inventory.ndjson` |
| Top-20 risks documented | ✅ `.codex/agentic-enablement/top_risks.md` |
| No repo mutations | ✅ All files written to `.codex/` only |

**Required before Stage 1:** Human operator review and sign-off on `change_signoff_template.md`.

---

## Stage 1 — Critical Hardening (Blocking — must complete before any autonomy)

**Goal:** Eliminate the 5 critical risks identified in Phase 5.

### 1a — Remove `agent_auth_session.json` and `agent_context.json` from git tracking
```bash
echo ".codex/agent_auth_session.json" >> .gitignore
echo ".codex/agent_context.json" >> .gitignore
git rm --cached .codex/agent_auth_session.json .codex/agent_context.json
```
- **Verification:** `git ls-files .codex/agent_auth_session.json` returns empty.
- **Effort:** S

### 1b — Set `autonomous_actions_enabled: false` in `.codex/autonomous_agent.yaml`
- **Verification:** `grep autonomous_actions_enabled .codex/autonomous_agent.yaml` shows `false`.
- **Effort:** S

### 1c — Disable `autonomous-agent.yml` schedule trigger
Add `if: false` to the scheduled job or convert to `workflow_dispatch` only.
- **Verification:** Workflow does not appear in scheduled runs list.
- **Effort:** S

### 1d — Set `COPILOT_AGENT_AUTH_BYPASS_TOOLS` to an explicit allowlist
Set repo variable to a narrow list (e.g., `"labeler,pr-checks"`) — never leave empty.
- **Verification:** `owner_approval_guard.sh` rejects autonomous-agent when not in allowlist.
- **Effort:** S

### 1e — Add `labeler.yml` rescue-comment job fork gate
```yaml
if: github.event.pull_request.head.repo.fork == false
```
- **Verification:** Fork PR does not trigger rescue-comment with CODEX_MASTER_KEY.
- **Effort:** S

**CI Checks for Stage 1:**
- `validate.yml` must pass (ruff, detect-secrets, sync-tracked)
- `codeql-analysis.yml` must show 0 new critical alerts
- Manual human review of each change required (see `change_signoff_template.md`)

**Rollback:** `git revert` each commit; re-set repo variables to previous values.

---

## Stage 2 — Simulation (Sandboxed — no network, no secrets)

**Goal:** Test agent behavior in an isolated environment before any privileged execution.

### Required before Stage 2:
- All Stage 1 items complete and verified
- Human sign-off on `change_signoff_template.md` (Stage 1 section)
- `AUTONOMY_DRY_RUN=1` enforced in all test runs

### Actions:
1. Create `test-autonomy-sandbox.yml` workflow — runs `autonomy_scheduler.py --dry-run` with `contents: read` only, no secrets, `AGENT_KILL_SWITCH` disabled.
2. Run `autonomy-phase-ci-matrix.yml` and confirm all phases pass with `AUTONOMY_DRY_RUN=1`.
3. Validate `agent_runner.py --dry-run --once` completes without writing files.

**Monitoring:** Workflow run logs only — no external SIEM required at this stage.
**Rollback:** Delete sandbox workflow; no state changes to revert.

---

## Stage 3 — Canary (Limited autonomy on non-protected branch, audit-logged)

**Goal:** Run limited automation on a designated canary branch with strict scopes.

### Prerequisites:
- Stages 1–2 complete
- `environment: agent-canary` created in GitHub with required reviewers
- Audit log forwarding configured (GitHub Audit Log API → `.codex/evidence/`)
- Kill-switch variable `AGENT_EMERGENCY_STOP` created (default: `false`)

### Scope restrictions:
- Only `monitor` mode (no `execute`)
- `contents: read` only — no write operations
- All agent actions must produce a PR for human review — no direct commits
- Maximum 1 autonomous PR per day

### Verification:
- Zero unreviewed direct commits from agent actors
- All PRs tagged `[CANARY]` and reviewed within 24h
- Kill-switch test: set `AGENT_EMERGENCY_STOP=true` → all autonomy scripts must halt within 60s

---

## Stage 4 — Controlled Autonomy (Limited write, human-gated escalation)

**Goal:** Gradually expand capabilities with policy enforcement and approval workflows.

### Prerequisites:
- Stage 3 canary runs for ≥2 weeks with no security incidents
- External security audit of top-risks.md items completed
- All OIDC migrations from Stage 4 complete (CODEX_MASTER_KEY usage ≤20 workflows)
- `autonomy_actions_enabled: false` → `true` with formal Genesis sign-off

### Controls:
- `environment: agent-controlled` with 2 required human reviewers
- OIDC tokens for all write operations (no long-lived PAT)
- Budget cap enforced: max 5 PRs/day, max 10 issues/day
- Full audit trail: every autonomous decision logged to `.codex/evidence/`

---

## Stage 5 — Operational Autonomy (Full D_CAPABLE, post-audit)

**Goal:** Full autonomous operations within guardrails, post all security gates.

### Prerequisites:
- All 20 risks in `top_risks.md` remediated (FIX or MIGRATE complete)
- External penetration test of agent workflows passed
- `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` re-assessed by human operator
- SLO defined: <1% false-positive autonomous action rate, <4h mean-time-to-detect anomaly

---

## Immediate Next Steps (Operator Action Required)

| Priority | Action | Owner | Effort |
|---|---|---|---|
| P0 | Review and sign `change_signoff_template.md` | @mbaetiong | 15 min |
| P0 | Set `COPILOT_AGENT_AUTH_BYPASS_TOOLS` repo variable | @mbaetiong | 5 min |
| P0 | Approve Stage 1 hardening PR | @mbaetiong | 30 min |
| P1 | Remove tracked credential files from git | Copilot | S |
| P1 | Disable autonomous-agent.yml schedule | Copilot | S |
| P1 | Migrate top-5 self-hosted runner workflows to ubuntu-latest | Copilot | M |
| P2 | Pin all 576 action invocations to SHA | Copilot | M |
| P2 | Add `permissions: contents: read` to 36 missing workflows | Copilot | M |
