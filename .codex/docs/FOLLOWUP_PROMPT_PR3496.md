# Follow-Up Prompt — PR #3496 Post-Merge
# Schedule repo-var-sync-agent + rust-error-validator observation + Fourth D_CAPABLE designation

**Version:** 1.1.0
**Created:** 2026-03-05 | **Updated:** 2026-03-05 (W-110)
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
| W-110a | `ADR-20260305-fourth-d-capable-evaluation.md` — `workflow-health-monitor` designated 4th D_CAPABLE candidate; `owner-approval-guard` queued 5th | ✅ |
| W-110b | `AGENT_REGISTRY.yaml` v1.9.4 — `workflow-health-monitor` fields populated; `owner-approval-guard` has_tests/has_docs set | ✅ |

### Critical State

```
AGENT_REGISTRY.yaml:          v1.9.4 (3 D_CAPABLE: ci-testing-agent rank 1, workflow-ci-fixer rank 13, rust-error-validator rank 20)
4th D_CAPABLE candidate:      workflow-health-monitor (rank 21, DESIGNATED, observation started 2026-03-05)
rust-error-validator obs:     DAY 1 of 30 (started 2026-03-04, ends 2026-04-03)
workflow-health-monitor obs:  DAY 1 of 30 (started 2026-03-05, ends 2026-04-04)
repo-var-sync-schedule.yml:   ACTIVE — runs daily at 06:00 UTC
COGNITIVE_BRAIN_SESSION_NUMBER: 112
AUTO_PROMOTE_TIER_ENABLED:    true
CODEX_CLI_API_URL:            http://localhost:8765
```

---

## 🔴 Priority 1 — Owner Action Required

### P1.1 — C8 rank threshold sign-off for `workflow-health-monitor`

**Status: ⏳ PENDING @mbaetiong**

The current D_CAPABLE criterion C8 requires `activation_frequency_rank ≤ 20`. All ranks
1–20 are taken. `workflow-health-monitor` has been assigned rank 21.

**Required action:** @mbaetiong must sign off on one of:
- Option A: Relax C8 threshold from top-20 to top-25 for the fourth promotion
- Option B: Confirm rank-21 displaces an existing rank-11–20 agent based on actual invocation data

Without this sign-off, the fourth promotion remains deferred even after the observation window closes.

---

## 🟢 Priority 2 — Routine (No Owner Action Required)

### P2.1 — Monitor observation windows

Both observation workflows are running automatically:

| Workflow | Schedule | Window |
|----------|----------|--------|
| `rust-error-validator-observation.yml` | Weekly Mondays 08:00 UTC | 2026-03-04 → 2026-04-03 |
| `rust-error-validator-observation.yml` | Weekly Mondays 08:00 UTC | Covers rust-error-validator |

> Note: A separate `workflow-health-monitor-observation.yml` workflow can be created in a future PR if dedicated per-candidate tracking is needed. Currently, the `violations_30d` field in AGENT_REGISTRY.yaml is the canonical signal; the weekly `rust-error-validator-observation.yml` template can be extended or a new one created.

### P2.2 — repo-var-sync drift monitoring

`repo-var-sync-schedule.yml` auto-commits `.codex/agent_context.json` when drift detected.

---

## 🟡 Priority 3 — Fourth Promotion (Post 2026-04-04)

After observation window closes and @mbaetiong signs off on C8:

1. Run demotion check on all 3 D_CAPABLE agents
2. Verify `workflow-health-monitor` `violations_30d: 0` (still)
3. Create `docs/arch/ADR-20260305-workflow-health-monitor-d-capable-promotion.md`
4. Update `AGENT_REGISTRY.yaml` v1.9.5: `workflow-health-monitor` `autonomy_model: E` → `D_CAPABLE`
5. Regenerate `CODEX_MANIFEST.json`

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
Priority 1: confirm @mbaetiong has signed off on C8 rank threshold relaxation for workflow-health-monitor.
Priority 2: check both observation workflow weekly reports — violations still 0?
Priority 3 (after 2026-04-04 + P1 sign-off): promote workflow-health-monitor to D_CAPABLE.
Maintain REQ-4/REQ-5 compliance.
```

---

*Created: 2026-03-05 | Updated: 2026-03-05 (W-110) | Session 112 | Branch: copilot/schedule-repo-var-sync-agent → main | PR #3496*
*Author: copilot-swe-agent[bot]*
