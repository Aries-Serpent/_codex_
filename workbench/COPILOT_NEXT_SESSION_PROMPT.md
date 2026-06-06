# Follow-Up Prompt for GitHub Copilot Agent

## @copilot Coverage gate advancement + post-merge housekeeping

**Generated:** 2026-06-06T07:22Z  
**Branch:** `copilot/explore-codebase-and-create-plan`  
**PR:** #4792

---

## Context Lock — What Is Done

All 45 capability gaps are ✅ implemented (Waves 0–4). This session completed:

- ✅ CI regressions from Wave 3/4 fixed (pre-flight, action versions, Trivy scan)
- ✅ All 9 code-quality bot issues from review #4442009364 fixed (commit `93ddf17f5`)
- ✅ All 8 unanswered review comment threads replied to with resolving SHA
- ✅ 28 new coverage tests added (`test_check_workflow_yaml.py`, `test_validate_configs.py`)
- ✅ parallel_validation: CodeQL 0 alerts, code review 0 blocking issues
- ✅ REQ-4/REQ-5 compliant in every commit
- ✅ PR #4792 declared merge-ready

`special_flags.needs_verification: []` — empty, no re-verification required.

---

## Primary Objective for Next Session

**Advance Gap 5 coverage gate**: measured baseline 17.57% → roadmap target ≥80%.  
Immediate milestone: **≥22%** (close the +4.43 pp gap from baseline).

---

## Task Sequence

### Task 1 — Merge PR #4792 (if not yet merged)
Check if PR #4792 is already merged. If not, confirm CI is green and request merge.

### Task 2 — Measure current coverage (post-merge baseline)
```bash
python -m pytest --cov=src --cov=scripts --cov=agents --cov=training \
  --cov-report=term-missing -q 2>&1 | tail -40
```
Record the new baseline in `workbench/coverage/gap5_coverage_evidence.md`.

### Task 3 — Advance coverage floor (Gap 5)
Target: **≥22%** (then push toward ≥35% if time permits).

Approach:
1. Identify top 5 lowest-coverage modules with existing source code
2. Dispatch `unified-coverage-agent` for each (up to 4 concurrent):
   - Prompt: *"Write unit tests for `<module_path>` targeting the uncovered lines listed below. All tests must pass. Do not modify source code. Commit tests with `test(coverage): ...`"*
3. After agents complete: re-run coverage and record new floor
4. If ≥22% reached, raise `fail_under` in `pyproject.toml` to the new floor
5. Update `workbench/coverage/gap5_coverage_evidence.md` floor history table

### Task 4 — REQ-4/REQ-5 compliance
Each commit must include both `CHANGELOG.md` and `AGENT_ACCOUNTABILITY_REPORT.md`.
Run after every commit:
```bash
python3 scripts/ci/session_wrapup_autofix.py --check --pr-number 4792
```

### Task 5 — parallel_validation gate
Run `parallel_validation` after all coverage tests are committed. Address any HIGH/CRITICAL findings.

### Task 6 — Update living docs
- `workbench/coverage/gap5_coverage_evidence.md` — floor history + new actual
- `workbench/gap_backlog_prioritized.md` — gap 5 status line
- `workbench/wave_execution_control.md` — add coverage session row
- `workbench/COPILOT_NEXT_SESSION_PROMPT.md` — update for next continuation

---

## Key Files Reference

| File | Purpose |
|---|---|
| `workbench/coverage/gap5_coverage_evidence.md` | Coverage gate evidence + roadmap |
| `workbench/gap_backlog_prioritized.md` | Gap 5 status tracker |
| `workbench/wave_execution_control.md` | Wave + session log |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | REQ-4 compliance |
| `CHANGELOG.md` | REQ-5 compliance |
| `pyproject.toml` | `fail_under` threshold (currently 15) |

---

## Dispatch Constraints
- Max concurrent background agents: **4**
- All artifacts under `workbench/evidence/` (never `/tmp`)
- Pre-existing lint failures in `ruff check src/ tests/` are NOT your responsibility unless introduced by your changes
- Do NOT modify `.github/workflows/copilot-setup-steps.yml` lines 141–147 (hardened YAML block)
- REQ-4/REQ-5: BOTH `CHANGELOG.md` AND `AGENT_ACCOUNTABILITY_REPORT.md` must appear in the **latest** commit

---

## Success Criteria
- [ ] PR #4792 merged (or confirmed merge-ready)
- [ ] Coverage floor ≥ 22% measured in CI (from 17.57% baseline)
- [ ] `pyproject.toml fail_under` raised to match new floor
- [ ] `session_wrapup_autofix --check` passes
- [ ] `parallel_validation` complete — 0 HIGH/CRITICAL issues
- [ ] Gap 5 status line in `gap_backlog_prioritized.md` updated with new % floor
- [ ] `COPILOT_NEXT_SESSION_PROMPT.md` updated for next session
