# Follow-Up Prompt — PR #3496 Post-Merge
# Schedule repo-var-sync-agent + rust-error-validator 30-day observation

**Version:** 1.0.0
**Created:** 2026-03-05
**PR:** [#3496 — Schedule repo-var-sync-agent + rust-error-validator observation](https://github.com/Aries-Serpent/_codex_/pull/3496)
**Status file:** `docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3496.md`
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 112

---

## Session Restore Context

When you read this, PR #3496 has merged. This prompt defines your next session objectives.

### What PR #3496 delivered

| Item | Deliverable | Status |
|------|-------------|--------|
| W-109a | `repo-var-sync-schedule.yml` — daily cron (06:00 UTC) + workflow_dispatch; drift detection; auto-commit | ✅ |
| W-109b | `rust-error-validator-observation.yml` — weekly observation; historical evidence baseline; elapsed-day tracker | ✅ |
| W-109b | `AGENT_REGISTRY.yaml` v1.9.3 — `observation_started`, `observation_window_days`, `observation_baseline` added to rust-error-validator | ✅ |

### Critical State

```
AGENT_REGISTRY.yaml:          v1.9.3 (3 D_CAPABLE: ci-testing-agent rank 1, workflow-ci-fixer rank 13, rust-error-validator rank 20)
rust-error-validator observation: DAY 1 of 30 (started 2026-03-04, ends 2026-04-03)
rust-error-validator violations_30d: 0 (historical baseline confirmed)
repo-var-sync-schedule.yml:   ACTIVE — runs daily at 06:00 UTC
COGNITIVE_BRAIN_SESSION_NUMBER: 112
AUTO_PROMOTE_TIER_ENABLED:    true
CODEX_CLI_API_URL:            http://localhost:8765
```

---

## 🟢 Priority 1 — Routine (No Owner Action Required)

### P1.1 — Monitor rust-error-validator observation

**Status: 🔄 ONGOING — ends 2026-04-03**

The `rust-error-validator-observation.yml` workflow runs every Monday at 08:00 UTC.
- Check the workflow summary weekly for violations
- If `violations_30d` increases, a demotion review is required per D_CAPABLE protocol
- Window closes 2026-04-03 — generate promotion completion note at that time

### P1.2 — repo-var-sync drift monitoring

**Status: 🔄 ACTIVE — runs daily at 06:00 UTC**

`repo-var-sync-schedule.yml` auto-commits `.codex/agent_context.json` when drift detected.
- Monitor for any commit-push failures (token expiry)
- If `CODEX_MASTER_KEY` expires, manual sync needed

---

## 🟡 Priority 2 — Next D_CAPABLE Evaluation

### P2.1 — Fourth D_CAPABLE candidate

After rust-error-validator 30-day observation closes (2026-04-03):
1. Run demotion check on all 3 D_CAPABLE agents
2. Evaluate next GROUNDED candidate for fourth D_CAPABLE slot
3. Candidates: `owner-approval-guard`, `workflow-health-monitor` (both need rank + violations_30d set)

---

## Self-Review Checklist

```
[ ] Re-read: .codex/CODEBASE_AGENCY_POLICY.md
[ ] Re-read: .github/TEMPORARY_FILES_POLICY.md
[ ] Verify: all changed .py files compile-clean
[ ] Run: pytest for any modified Python modules
[ ] Wait: all in-progress CI jobs complete; read their logs
[ ] Call: code_review + codeql_checker before final commit
[ ] Update: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md (REQ-4)
[ ] Update: CHANGELOG.md (REQ-5)
[ ] Create: COGNITIVE_BRAIN_STATUS_PR{PR}.md
[ ] Create: FOLLOWUP_PROMPT_PR{PR+1}.md
```

---

## @copilot Activation Command

After merging PR #3496, post this comment on the next PR:

```
@copilot continue

Load context from `.codex/docs/FOLLOWUP_PROMPT_PR3496.md` and execute:
Priority 1: confirm repo-var-sync-schedule.yml is running daily without errors.
Priority 1: check rust-error-validator-observation.yml weekly report — violations still 0?
Priority 2: designate fourth D_CAPABLE candidate (after 2026-04-03 window closure).
Maintain REQ-4/REQ-5 compliance.
```

---

*Created: 2026-03-05 | Session 112 | Branch: copilot/schedule-repo-var-sync-agent → main | PR #3496*
*Author: copilot-swe-agent[bot]*
