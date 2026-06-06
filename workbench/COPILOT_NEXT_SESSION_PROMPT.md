# Follow-Up Prompt for GitHub Copilot Agent

## @copilot Coverage gate continuation — Gap 5 toward ≥35%

**Generated:** 2026-06-06T08:15Z  
**Branch:** `copilot/explore-codebase-and-create-plan`  
**PR:** #4792

---

## Context Lock — What Is Done

All 45 capability gaps ✅ implemented (Waves 0–4). Session 3–4 completed:

- ✅ 10 open code-quality review threads fixed (commit `c6155a8fc`)
- ✅ 56 direct coverage tests for 6 zero-coverage modules (commit `5d5a372de`)
- ✅ 4× unified-coverage-agent completed: 257 tests total
  - `coverage-continuous-learning`: 46 tests — `eval_gate.py` + `trigger.py` (commit `c59f5062f`)
  - `coverage-scalability`: 77 tests — `scalability.py` (commit `67046c28`)
  - `coverage-stub-cleanup`: 78 tests — `stub_cleanup.py` (included in `c59f5062f`)
  - `coverage-self-healing`: 77 tests — `self_healing.py` + bug fix (current session)
- ✅ `pyproject.toml fail_under` raised from 15 → **20**
- ✅ Living docs updated (gap backlog, coverage evidence, wave control, this prompt)
- ✅ REQ-4/REQ-5 compliant

`special_flags.needs_verification: []` — empty, no re-verification required.

---

## Primary Objective for Next Session

**Advance Gap 5 coverage gate**: current floor ~20–22% → roadmap milestone ≥35%.

---

## Task Sequence

### Task 1 — Confirm CI coverage floor
Check CI for the latest coverage run on PR #4792. If ≥22% confirmed, raise `fail_under` from 20 → 22.

### Task 2 — Dispatch 4× unified-coverage-agent (≥35% batch)
Target the next 5 highest-line 0% modules. Suggested candidates:

| Module | Lines | Priority |
|--------|-------|----------|
| `src/codex_ml/utils/reproducibility_hardening.py` | 245 | HIGH |
| `src/codex_ml/workflow/track_c_workflow.py` | 150 | HIGH |
| `src/codex_ml/utils/safe_pickle.py` | 92 | MEDIUM |
| `src/codex_ml/utils/subproc.py` | 68 | MEDIUM |
| `src/codex_ml/utils/retention.py` | 87 | MEDIUM |

Dispatch prompt:
> *"Write unit tests for `<module_path>` targeting the uncovered lines listed below. All tests must pass. Do not modify source code. Commit tests with `test(coverage): ...`. Must include CHANGELOG.md and AGENT_ACCOUNTABILITY_REPORT.md in the commit (REQ-4/REQ-5)."*

### Task 3 — After agents complete: re-run coverage
```bash
python3 -m pytest tests/unit/ --cov=src/codex_ml --cov-report=term-missing -q 2>&1 | tail -10
```
Record new floor in `workbench/coverage/gap5_coverage_evidence.md`.

### Task 4 — Raise fail_under to new floor
Once ≥35% confirmed, update `pyproject.toml fail_under` to match.

### Task 5 — REQ-4/REQ-5 compliance
```bash
python3 scripts/ci/session_wrapup_autofix.py --check --pr-number 4792
```

### Task 6 — parallel_validation gate
Run `parallel_validation` after all tests committed. Address any HIGH/CRITICAL findings.

### Task 7 — Update living docs
- `workbench/coverage/gap5_coverage_evidence.md` — add session 4 row with new floor
- `workbench/gap_backlog_prioritized.md` — update gap 5 status with new floor %
- `workbench/wave_execution_control.md` — add session row
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
| `pyproject.toml` line ~535 | `fail_under` threshold (currently 20) |

---

## Dispatch Constraints
- Max concurrent background agents: **4**
- All artifacts under `workbench/evidence/` (never `/tmp`)
- Pre-existing lint failures are NOT your responsibility unless introduced by your changes
- Do NOT modify `.github/workflows/copilot-setup-steps.yml` lines 141–147 (hardened YAML block)
- REQ-4/REQ-5: BOTH `CHANGELOG.md` AND `AGENT_ACCOUNTABILITY_REPORT.md` must appear in the **latest** commit

---

## Success Criteria
- [ ] CI confirms coverage ≥ 22%
- [ ] `pyproject.toml fail_under` raised to ≥22 (then ≥35 once agents complete)
- [ ] 4 new agents dispatched for ≥35% target modules
- [ ] `session_wrapup_autofix --check` passes
- [ ] `parallel_validation` complete — 0 HIGH/CRITICAL issues
- [ ] Gap 5 status line in `gap_backlog_prioritized.md` updated with new floor
- [ ] `COPILOT_NEXT_SESSION_PROMPT.md` updated for next session
