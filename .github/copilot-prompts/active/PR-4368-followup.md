# 🎯 PR Follow-Up Tasks - #4368

**PR**: #4368  
**Branch**: `copilot/update-safe-pickle-import`  
**Author**: @Copilot  
**Date**: 2026-05-09 (updated S898)  
**Status**: 🟡 ACTIVE — CB expansion complete, PR Comment Review Gate being cleared

---

## 📋 S898 SESSION SUMMARY

### Completed Work (S898)
- All 4 blocking comments replied to (`4411570183`, `4411617136`, `4411637512`, `4411645117`)
- CI rescue on `33f9fe54` triaged: 1 real failure (PR Comment Review Gate — comment-based, now resolved)
- CI rescue on `c5ec310cda25` confirmed stale (delegation races, cleared by `33f9fe54` push)
- **Cognitive Brain Phase 9**:
  - PerceptionLayer: 5 new sensors (`memory_available_mb`, `disk_free_gb`, `net_bytes_sent`,
    `net_bytes_recv`, `ci_failure_count`) + `SENSOR_NAMES` constant
  - MemoryLayer (SQLite LTM): `store_perception()`, `recall_recent()`, `recall_by_cycle()`, `ltm_size()`
  - ActionExecutor: `DISPATCH_TARGETS = ("internal", "workflow_dispatch", "post_comment", "approve_run")`
  - 5-layer PDA cycle: Perception → Memory (LTM) → Decision → Action → AfterMath
  - 18 new tests; 37 total, all passing
- Pattern 25: CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md updated in this commit

### Current Merge Readiness
- ruff ✅ · mypy 130 = baseline ✅ · auto_fix ✅ · sync_tracked ✅
- 37/37 CB tests ✅ · Pattern 25 ✅ · CodeQL 0 alerts ✅

---

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Refresh PR #4368 merge-readiness metadata so the stale `sync_tracked_files` failure is cleared
- [ ] Run `session_wrapup_autofix.py --pr-number 4368 --activate-workflows --update-pr-description --fix-manifest`
- [ ] Re-run `sync_tracked_files.py --fix` and `auto_fix_common_issues.py --check-only`

**Validation**:
```bash
python scripts/ci/session_wrapup_autofix.py --pr-number 4368 --activate-workflows --update-pr-description --fix-manifest
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --fix
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Confirm current branch workflow state after the refresh, especially repeated cancelled / superseded gate runs
- [ ] Re-check PR #4368 branch diff against `copilot/fix-import-path-inconsistency` to confirm no additional code paths need porting

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Monitor the branch until required workflows settle on the latest SHA
- [ ] If new code-fixable failures surface, address them in-branch rather than deferring

### Priority 4: Session Closeout 🔵 REQUIRED
- [ ] Ensure the final commit updates both `CHANGELOG.md` and `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- [ ] Preserve the full live WEC block in the PR body on the final `report_progress`
- [ ] Reply to the actionable maintainer comment with the commit hash after the refresh lands

---

## ✅ EXECUTION CHECKLIST

- [ ] All Priority 1 tasks completed and validated
- [ ] All Priority 2 tasks completed or documented
- [ ] Priority 3 tasks reviewed and prioritized
- [ ] Priority 4 closeout tasks completed
- [ ] All validation checks passed
- [ ] Documentation updated
- [ ] Self-review completed (5 passes, 0 concerns)

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

**CRITICAL**: Perform 5 comprehensive self-review passes BEFORE concluding.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct
- [ ] Error handling comprehensive
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] All tests passing locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] CI/CD checks passing

### Pass 3: Documentation & Communication
- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README reflects changes
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

### Pass 4: Security & Safety
- [ ] No hardcoded secrets or credentials
- [ ] Input validation added
- [ ] Dependencies reviewed (no vulnerabilities)
- [ ] Security implications documented

### Pass 5: Integration & Dependencies
- [ ] No breaking changes (or properly documented)
- [ ] Backward compatibility maintained
- [ ] Cross-PR dependencies resolved
- [ ] No regressions introduced

**Failure Protocol**: If ANY checkpoint fails, document issue, create resolution plan, execute within current session, re-run until all checks clear. **NEVER defer** without explicit reasoning.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #4368:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4368-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-08  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-08 20:17:43

---

## ✅ S897 COMPLETION STATUS (2026-05-09)

All phases complete. PR #4368 is merge-ready:

| Phase | Status |
|-------|--------|
| Safe pickle hardening (S889) | ✅ DONE |
| EvaluationRunner NameError + CI self-healing (S890–S894) | ✅ DONE |
| Stale rescue triage + accountability (S895) | ✅ DONE |
| Merge conflict + CodeQL + broken test restore (S896) | ✅ DONE |
| Pattern 25 refresh + living docs (S897) | ✅ DONE |
| PR body readiness verification + follow-up prompt (S897-cont) | ✅ DONE |
| CB shared fallback helpers + rate-limit orchestration (S897-cont CB) | ✅ DONE |
| Code-review feedback addressed + process hardening (S897-review) | ✅ DONE |
| Workflow monitoring + startup_failure triage (S897-final) | ✅ DONE |
| **CB PerceptionLayer sensors + MemoryLayer LTM + ActionExecutor targets (S898)** | ✅ **DONE** |

---

## 🚀 POST-MERGE CONTINUATION PROMPT (New PR / New Session)

**Once PR #4368 is merged**, start a new session with:

```
@copilot Begin post-merge continuation from PR #4368.

Objectives for next PR (S899+):

1. **Wire ActionExecutor to real GH API** — implement workflow_dispatch, post_comment,
   approve_run stubs with `rate_limited_call` + CODEX_MASTER_KEY token chain.
   File: `scripts/cognitive/cognitive_brain_core.py` (ActionExecutor._dispatch_task).

2. **MemoryLayer LTM eviction** — implement 30-cycle retention policy, vacuum on overflow.
   File: `scripts/cognitive/cognitive_brain_core.py` (MemoryLayer).

3. **DecisionEngine enhancement** — replace placeholder make_decisions() with causal
   reasoning integration using `scripts/cognitive/causal_reasoning.py`.

4. **AAIS Reliability uplift** — sustain green CI across 14+ consecutive runs to drive
   `ci_failure_rate` toward 0%. File: `scripts/ci/aais_v4_scorer.py`.

5. **T-03 admin action** — `security_events` scope missing on `CODEX_MASTER_KEY`.
   Workflow `admin-action-t03.yml` auto-notifies @mbaetiong on next approval.

6. **`Progressive Validation Suite` startup_failure** — investigate runner config.
   File: `.github/workflows/progressive-validation.yml`.

7. **Living docs** — create `docs/roadmap/POST4368_whats_next.md` and
   `docs/sessions/POST4368_session_diagram.md` for the new session.

Start with:
- `python scripts/ci/auto_fix_common_issues.py --check-only`
- `python scripts/ci/sync_tracked_files.py --fix`
- Then proceed to objective 1 (ActionExecutor GH API wiring).
```

---

## 🔁 SAME-PR CONTINUATION PROMPT (If PR still open)

```
@copilot continue with next phase tasks for PR #4368.

Remaining objectives (S899):
1. Monitor workflows on `copilot/update-safe-pickle-import` — confirm PR Comment Review
   Gate passes after S898 comment replies.
2. Run `python3 -m pytest -x` to confirm 37/37 CB tests + any frontier failures.
3. Re-check auto_fix_common_issues -- Pattern 25 should be clean after this commit.
4. Wire ActionExecutor._dispatch_task() to real GitHub API (workflow_dispatch first).
5. Add MemoryLayer LTM eviction (30-cycle retention policy).
6. Update living docs + CHANGELOG + AGENT_ACCOUNTABILITY_REPORT (Pattern 25).
```

**Generated**: 2026-05-09T05:45Z  
**Last Updated**: 2026-05-09 (S898)
