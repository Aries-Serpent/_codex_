# Agent & Workflow Consolidation Planset — S174

**Last Updated:** 2026-06-22

> **Created:** 2026-03-21 (S173 / PR #3661)
> **Scope:** GitHub Actions workflows (128 active) + Custom Agents (203 files)
> **Goal:** Reduce operational surface, eliminate redundancy, lower CI-minutes cost
> **Next session:** Execute consolidations in priority order (P0 → P1 → P2)
> **Owner:** @copilot (next session) + @mbaetiong (approval)

---

## 📊 Current State

| Category | Count | Target | Reduction |
|----------|-------|--------|-----------|
| Workflows (`.github/workflows/*.yml`) | **128** | ≤ 80 | −38 (30%) |
| Agent files (`.github/agents/`) | **203** | ≤ 140 | −63 (31%) |
| Disabled workflows (`if: false`) | 0 | 0 | — |
| `Art_`-prefixed (legacy naming) | 6 | 0 | rename/consolidate |
| Deprecated agent stubs | ~15 | ≤ 5 | tombstone rest |

---

## 🔴 P0 — Must consolidate (duplicate triggers / race conditions)

### P0-1: Self-Healing CI Triad → Single canonical workflow

| File | Name | Trigger |
|------|------|---------|
| `self-healing.yml` | Self-Healing CI/CD | push, pull_request |
| `self_healing_ci.yml` | Self-Healing CI | push, pull_request |
| `iterative-self-healing-ci.yml` | Iterative Self-Healing CI | push, schedule |

**Problem:** Three workflows doing the same job fire on the same events — concurrent runs
create `.venv_ci` lock conflicts and inflated failure rates. `iterative-self-healing-ci.yml`
is the current canonical one (S172 cascade fix applied here). The other two are legacy.

**Action:**
1. Validate `iterative-self-healing-ci.yml` covers all triggers of the other two
2. Add a `schedule:` trigger to `iterative-self-healing-ci.yml` if not present
3. Delete `self-healing.yml` and `self_healing_ci.yml`
4. Update `SELF_HEALING_001` pattern in `ci_failure_patterns.yaml`

**Risk:** LOW — `iterative-self-healing-ci.yml` is already the most complete version

---

### P0-2: Validation Suite Explosion → Unified Validation Pipeline

| File | Name | Trigger |
|------|------|---------|
| `pre-flight-validation.yml` | Pre-Flight CI Validation | push, pull_request |
| `pre-merge-validation.yml` | Pre-Merge Validation | pull_request |
| `post-merge-validation-optimized.yml` | Post-Merge Validation | push |
| `progressive-validation.yml` | Progressive Validation Suite | pull_request |
| `resilient_validation.yml` | Resilient Validation Suite | pull_request |
| `validate.yml` | Validation Pipeline | pull_request |
| `optimized-ci.yml` | (CI optimized runner) | — |

**Problem:** 6–7 overlapping validation workflows run on the same events. This burns
~6× the required CI minutes and creates confusing "check" lists on every PR.

**Action:**
1. Inventory what each workflow uniquely tests (next session: read each file fully)
2. Identify the superset of tests across all 6
3. Consolidate into `unified-validation.yml` with job matrix:
   - `pre-flight` (fast, required) — runs on every PR push
   - `full-suite` (comprehensive, required) — runs on PR ready_for_review + merge to main
   - `post-merge` (smoke, required) — runs after merge to main
4. Archive the 6 source files to `.github/workflow-archive/`
5. Update any workflow that `needs:` these by name

**Risk:** MEDIUM — careful dependency mapping needed before deletion

---

### P0-3: `pr3178-pytest-execution.yml` — Stale PR-specific workflow

**Problem:** Workflow name contains a specific PR number (`pr3178`). PR #3178 is long
merged. This is dead code that still fires on `0D_base_ → main` PRs.

**Action:** Archive to `.github/workflow-archive/pr3178-pytest-execution.yml`

**Risk:** LOW — confirm no other workflow `needs:` it first

---

## 🟡 P1 — Should consolidate (redundant coverage / CI minutes waste)

### P1-1: Documentation Health → Unified Docs Monitor

| File | Purpose |
|------|---------|
| `doc-freshness-check.yml` | Check doc update timestamps |
| `docs-health.yml` | General docs health |
| `documentation-link-checker.yml` | Check broken links |
| `workflow-link-validation.yml` | Check workflow links |
| `pages-pre-merge-validation.yml` | Validate docs before merge |
| `pages-scheduled-validation.yml` | Scheduled docs validation |

**Action:** Consolidate into `docs-unified-health.yml` with 4 jobs:
`freshness`, `links`, `workflow-links`, `pages-preview`

---

### P1-2: Security Suite Consolidation

| File | Purpose |
|------|---------|
| `security-scanning-suite.yml` | Main security suite |
| `semgrep_sarif.yml` | Semgrep SAST |
| `codeql-analysis.yml` | CodeQL analysis |
| `nightly-codeql-alert-triage.yml` | CodeQL triage |
| `scan-secrets-variables.yml` | Secrets scan | <!-- pragma: allowlist secret -->
| `dependency-scan.yml` | Dependency vulnerabilities |
| `scheduled-dependency-audit.yml` | Scheduled dep audit |
| `security-alert-notification.yml` | Alert notifications |
| `security-tools-bootstrap.yml` | Tools setup |

**Action:** `security-scanning-suite.yml` already intended as the unified scanner.
Confirm it calls Semgrep + CodeQL + secrets + deps as job matrix. If so, the
individual files become redundant — archive after confirmation.

---

### P1-3: PR Check Duplication

| File | Purpose |
|------|---------|
| `pr-checks.yml` | PR validation |
| `pr-cost-check.yml` | Cost check |
| `cost-gate.yml` | Cost approval gate |
| `pr-followup-generator.yml` | Follow-up prompt |
| `pr-size-analyzer.yml` | PR size |
| `consolidated-pr-status.yml` | Status rollup |

**Action:** `consolidated-pr-status.yml` should be the single PR status source of truth.
Validate that `cost-gate.yml` is standalone (it is — it's an approval gate).
Consolidate `pr-checks.yml` + `pr-size-analyzer.yml` + `pr-cost-check.yml` into
`consolidated-pr-status.yml` jobs.

---

### P1-4: Copilot Session Workflow Audit

| File | Purpose |
|------|---------|
| `copilot-session-chain.yml` | Creates sub-PRs |
| `copilot-agent-session-done.yml` | Posts review after session |
| `copilot-pr-session-injector.yml` | Injects context on PR open |
| `copilot-review-responder.yml` | Posts apply-changes comment |
| `copilot-issue-triage.yml` | Triages issues |
| `copilot-agent-vars-bootstrap.yml` | Bootstrap vars |
| `copilot-evolution-suite.yml` | Evolution suite |
| `chatops_copilot_trigger.yml` | Chat-ops |
| `session-watchdog.yml` | Timebox enforcement |
| `session-incremental-summary-reminder.yml` | Summary reminder |

**Action:** These serve distinct purposes but can be rationalized:
- `copilot-agent-vars-bootstrap.yml` likely superseded by `copilot-setup-steps.yml`
- `copilot-evolution-suite.yml` — validate if still used (check last run date)
- `session-incremental-summary-reminder.yml` — merge into `session-watchdog.yml`

---

### P1-5: Coverage Agent Consolidation (already has `unified-coverage-agent`)

The AGENT_REGISTRY.yaml shows **5 active agents** all doing coverage work:
- `coverage-gapfill-agent`
- `coverage-maintenance-agent`
- `coverage-roadmap-agent`
- `test-coverage-agent`
- `test-coverage-monitor`

AND `unified-coverage-agent` was created to consolidate them. The 5 originals should
be **deprecated** in the registry and their `.md` files replaced with tombstone stubs.

**Action:**
1. Verify `unified-coverage-agent.md` covers all capabilities of the 5 originals
2. Set each original to `status: deprecated` in `AGENT_REGISTRY.yaml`
3. Replace each `.md` with a tombstone stub (50-line max) pointing to `unified-coverage-agent`

---

### P1-6: CI Agent Consolidation

**Overlapping agents in the CI/CD category:**

| Agent | Purpose |
|-------|---------|
| `ci-testing-agent.md` | Primary CI debugger (v4.1.0) |
| `ci-auto-healer-agent.md` | Auto-fix CI failures |
| `ci-emergency-response-agent.md` | Emergency CI fixes |
| `ci-resilience-emergency-response-agent.md` | Resilience fixes |
| `ci-triage-pipeline-agent.md` | Triage and routing |
| `ci-failure-resolution-agent.md` | **DEPRECATED** stub (5,813 chars) |
| `ci-log-retrieval-agent.md` | Log retrieval |
| `ci-importerror-agent.md` | ImportError fixes |
| `ci-docker-build-healer.md` | Docker build fixes |
| `ci-parameter-mismatch-healer.md` | Parameter mismatch |

**Action:** Audit each against `ci-testing-agent.md` v4.1.0. Deprecate those whose
capabilities are fully covered. Keep specialized ones (Docker, ImportError, Log Retrieval).

---

## 🟢 P2 — Nice to consolidate (reduce noise)

### P2-1: `Art_`-prefixed workflow renaming

These 6 workflows have `Art_` prefix in their `name:` field (legacy naming convention):
- `self-healing.yml` → delete (P0-1)
- `post-merge-validation-optimized.yml` → consolidate (P0-2)
- `validate.yml` → consolidate (P0-2)
- `agent-orchestration-unified.yml` → rename to remove `Art_`
- `audit-qa-suite.yml` → rename to remove `Art_`
- Others as found

**Action:** Remove `Art_` prefix from `name:` field in all surviving workflows

---

### P2-2: Stale archive docs in `.github/agents/`

**Files to tombstone or delete** (status docs, not agent definitions):
- `SESSION_SUMMARY_PHASE_8_7_COMPLETE.md` → move to `archive/sessions/`
- `AGENT_ECOSYSTEM_MAP.md` → verify if superseded by `AGENT_REGISTRY.yaml`
- `AI_AGENT_INTUITIVENESS_SCORE.md` → archive (snapshot, not an agent)
- `COGNITIVE_BRAIN_*` status docs → move to `.codex/docs/`
- `BATCH_SCAN_PROTOCOL.md` → move to `docs/ops/`
- `S101_CONTINUATION_PROMPT.md`, `S97_CONTINUATION_PROMPT.md` → move to `archive/`
- `QUANTUM_DETERMINISTIC_PLANNING.md` → validate still relevant or archive
- `SECRETS_CONFIGURATION.md` → move to `docs/admin/` (sensitive location)

**Action:** Move non-agent files out of `.github/agents/` to appropriate locations

---

### P2-3: Cognitive Brain workflow audit

| File | Purpose |
|------|---------|
| `cognitive-action-decision.yml` | OODA loop action |
| `cognitive-analysis-feed.yml` | Feed patterns |
| `cognitive-perception.yml` | Perception layer |
| `cognitive_brain_ci_feedback.yml` | CI feedback |
| `coherence-snapshot.yml` | Coherence snapshot |

**Action:** Verify each is needed for Phase 3 autonomy. Audit last run dates.
Consolidate `cognitive-perception.yml` + `cognitive-action-decision.yml` into
a unified OODA loop workflow if they form a chain.

---

## 📋 Execution Checklist (Next Session: S174)

```
Pre-session requirements:
- [ ] Read this planset fully
- [ ] Load .codex/CODEBASE_AGENCY_POLICY.md
- [ ] Check CI status on main (no active failures before starting)
- [ ] Run: gh workflow list --limit 200 | sort > /tmp/workflow_inventory.txt

P0 — Execute first (blocking):
- [ ] P0-1: Verify iterative-self-healing-ci.yml superset, archive self-healing.yml + self_healing_ci.yml
- [ ] P0-2: Map 6 validation workflows, build unified-validation.yml, archive originals
- [ ] P0-3: Archive pr3178-pytest-execution.yml

P1 — Execute next (significant savings):
- [ ] P1-1: Consolidate 6 doc health workflows → docs-unified-health.yml
- [ ] P1-2: Audit security-scanning-suite.yml, archive redundant security workflows
- [ ] P1-3: Consolidate PR check workflows into consolidated-pr-status.yml
- [ ] P1-4: Audit Copilot session workflows, deprecate copilot-agent-vars-bootstrap + evolution-suite
- [ ] P1-5: Deprecate 5 coverage agents in registry, tombstone .md files
- [ ] P1-6: Deprecate fully-covered CI agents in registry

P2 — Final polish:
- [ ] P2-1: Remove Art_ prefix from all surviving workflow names
- [ ] P2-2: Move stale non-agent docs out of .github/agents/
- [ ] P2-3: Audit cognitive brain workflows, consolidate perception + action-decision

Post-consolidation:
- [ ] Run: gh workflow list --limit 200 | sort > /tmp/workflow_inventory_after.txt
- [ ] Verify count reduction: wc -l /tmp/workflow_inventory_*.txt
- [ ] Update AGENTS.md workflow count (target: ≤ 80)
- [ ] Update .github/workflow-archive/PARITY_CHECKLIST.md
- [ ] Update CHANGELOG.md with consolidation summary
- [ ] Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
```

---

## 💡 Success Criteria

| Metric | Before | Target | Verification |
|--------|--------|--------|-------------|
| Workflow count | 128 | ≤ 80 | `ls .github/workflows/*.yml \| wc -l` |
| Agent files | 203 | ≤ 140 | `ls .github/agents/*.md \| wc -l` |
| Duplicate triggers on same event | ~12 pairs | 0 | Manual review |
| `Art_` prefixed workflows | 6 | 0 | `grep -l "^name: Art_"` |
| CI minutes / PR (estimated) | ~180 min | ≤ 100 min | Workflow analytics |
| AAIS Reliability score impact | ~+1.5 pts | — | `scripts/ci/aais_v4_scorer.py` |

---

## 🔗 References

- `.github/workflow-archive/PARITY_CHECKLIST.md` — existing parity record
- `.github/workflow-archive/ARTIFACT_CATALOG.md` — artifact catalog
- `.github/agents/AGENT_REGISTRY.yaml` — agent registry (source of truth)
- `AGENTS.md` — top-level agent documentation
- `.codex/CODEBASE_AGENCY_POLICY.md` — agency policy (§2: leave better than found)

---

*Auto-generated by copilot-swe-agent[bot] | S173 | 2026-03-21*
*To be executed in S174 — append `@copilot+claude-sonnet-4.6 Execute S174 consolidation planset from docs/ops/CONSOLIDATION_PLANSET_S174.md` to start the next session.*
