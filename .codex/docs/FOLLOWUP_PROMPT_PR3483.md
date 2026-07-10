# Follow-Up Prompt — PR #3483 Post-Merge
# Repo Variable Wiring + Cognitive Brain Continuity

**Version:** 1.0.0  
**Created:** 2026-03-03  
**PR:** [#3483 — actionlint-audit SC2016/SC2012 + repo variable expansion](https://github.com/Aries-Serpent/_codex_/pull/3483)  
**Status file:** `docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3483.md`  
**Last session:** COGNITIVE_BRAIN_SESSION_NUMBER 110+

---

## Session Restore Context

When you read this, PR #3483 has merged. This prompt defines your next session objectives.

### What PR #3483 delivered
1. ✅ `actionlint-audit.yml` SC2016/SC2012 fixed — Tier-1 gate passes
2. ✅ 13 new repo variables designed and documented (2 admin docs created)
3. ✅ Codebase-wide Mermaid audit — 9 stale "91 workflow" refs fixed to "96"
4. ✅ 3 agent files updated with current state and Mermaid diagrams
5. ✅ Cognitive brain status `COGNITIVE_BRAIN_STATUS_PR3483.md` created

### What still needs doing (your tasks)

---

## 🔴 Priority 1 — Immediate (complete first)

### P1.1 — Verify `actionlint-audit` CI gate passes
```bash
# Check the latest actionlint-audit workflow run
gh run list --workflow=actionlint-audit.yml --repo Aries-Serpent/_codex_ --limit 5
gh run view <RUN_ID> --repo Aries-Serpent/_codex_
```
Expected: ✅ green, `ERROR_COUNT = 0`.

### P1.2 — Confirm Human Admin created the 13 new variables
```bash
gh variable list --repo Aries-Serpent/_codex_ | sort | grep -E "COGNITIVE_BRAIN_MAX|COGNITIVE_BRAIN_LTM|COGNITIVE_BRAIN_PATTERN|COGNITIVE_BRAIN_MEMORY_TIER|COPILOT_CLI_BASE|COPILOT_CLI_ENABLED|COPILOT_AGENT_SESSION|COPILOT_AGENT_MAX_AUTONOMY|CODEX_CI_FAILURE_THRESHOLD|CODEX_CI_LAST_GREEN|AGENT_HANDOFF_TIMEOUT|EMBEDDING_INDEX_AUTO|AUTO_PROMOTE_TIER"
```
Expected: 13 lines. If any missing, direct admin to `docs/admin/HUMAN_ADMIN_REPO_VARIABLES_SETUP.md`.

---

## 🟡 Priority 2 — Wiring PRs (one PR per section)

### P2.1 — Wire `generate_manifest.py` to `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS`
**File:** `scripts/ci/generate_manifest.py:59`  
**Change:**
```python
# Before
CONTEXT_WINDOW_BUDGET: int = 32_000

# After
import os
CONTEXT_WINDOW_BUDGET: int = int(os.environ.get("COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS", 32_000))
```

### P2.2 — Wire `prune_corpus.py` to `COGNITIVE_BRAIN_LTM_RETENTION_DAYS`
**File:** `scripts/ci/prune_corpus.py`  
Find the retention_days constant and wire to env var.

### P2.3 — Wire `ci-health-monitor.yml` to `CODEX_CI_FAILURE_THRESHOLD`
**File:** `.github/workflows/ci-health-monitor.yml`  
Replace hardcoded `20%` / `0.2` threshold with `${{ vars.CODEX_CI_FAILURE_THRESHOLD }}`.

### P2.4 — Wire `agent-handoff-gate.yml` to `AGENT_HANDOFF_TIMEOUT_SECONDS`
**File:** `.github/workflows/agent-handoff-gate.yml`  
Replace hardcoded timeout with `${{ vars.AGENT_HANDOFF_TIMEOUT_SECONDS }}`.

### P2.5 — Add `COGNITIVE_BRAIN_SESSION_NUMBER` auto-increment to `chatops_copilot_trigger.yml`
Add the PATCH step from `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md §6`.

### P2.6 — Write `CODEX_CI_LAST_GREEN_SHA` on green CI runs
Add a post-success step to the main CI workflow that patches the variable.

---

## 🟢 Priority 3 — Enhancements (future scope)

### P3.1 — Add `.actionlintrc` for stronger compliance
```yaml
# .actionlintrc
shell-check:
  enable: true
ignore:
  - "^jobs\\.[^.]+\\.name: "  # allow job name expressions
```

### P3.2 — Evaluate `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` promotion E → D
Review `e-to-d-transition-gate.yml` output. Gate score is 5/5 ✅.
Only promote after owner review of full E→D transition implications.

### P3.3 — Evaluate `AUTO_PROMOTE_TIER_ENABLED` false → true
Review `scripts/ci/auto_promote_tier.py` logic end-to-end before enabling.

---

## Self-Review Checklist (complete before closing session)

- [ ] P1.1 actionlint-audit gate is green
- [ ] P1.2 all 13 variables confirmed present in repo
- [ ] Any wiring PR(s) created passes all CI gates
- [ ] REQ-4: `.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` updated in every commit
- [ ] REQ-5: `CHANGELOG.md` updated in every commit
- [ ] No new SC2012 / SC2016 patterns introduced
- [ ] Mermaid diagrams in changed files are accurate

---

## Activation Commands

```
# To trigger this session
@copilot continue with PR #3483 post-merge tasks

# To check CI status
@copilot Use the CI Testing Agent to verify actionlint-audit gate passes

# To check variable setup
@copilot Use the Repo Var Sync Agent to sync agent_context.json with repo variables

# To start wiring PR
@copilot Create a PR to wire generate_manifest.py to COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS

# For full cognitive brain status
@copilot Use the Cognitive Brain Manager to generate status report for PR #3483
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` | Technical wiring reference + all Mermaid diagrams |
| `docs/admin/HUMAN_ADMIN_REPO_VARIABLES_SETUP.md` | Admin action guide (checkboxes + CLI commands) |
| `docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3483.md` | This session's status |
| `.github/agents/repo-var-sync-agent.md` | Updated v1.1 with new prefix coverage |
| `.github/agents/cognitive-brain-manager.md` | Updated v2.0 with current metrics |
| `.github/agents/ci-health-alert-agent.md` | Updated with CODEX_CI_FAILURE_THRESHOLD wiring |
| `.codex/patterns/ci_failure_patterns.yaml` | CI pattern library |
