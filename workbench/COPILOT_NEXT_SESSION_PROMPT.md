# Follow-Up Prompt for GitHub Copilot Agent

## @copilot Coverage gate continuation — Gap 5 toward ≥35%

**Generated:** 2026-06-06T07:46Z  
**Branch:** `copilot/explore-codebase-and-create-plan`  
**PR:** #4792

---

## Context Lock — What Is Done

All 45 capability gaps ✅ implemented (Waves 0–4). This session completed:

- ✅ 10 open code-quality review threads fixed (commit `fix(quality): remediate 10 open review-bot issues`)
  - `feast_compat.py` lines 301, 305: `...` → `raise NotImplementedError` in Protocol stubs
  - `test_fuzz_api.py` lines 220, 273: empty except blocks now have explanatory comments
  - `test_fuzz_configs.py` lines 210, 243: same pattern fixed
  - `test_property_resilience.py` lines 195, 204, 228, 259: same pattern fixed
- ✅ 56 new direct coverage tests (jsonio, optional_dependencies, serialization, feedback_events, hf_revision, opt_import)
- ✅ `workbench/coverage/gap5_coverage_evidence.md` created with floor history + roadmap
- ✅ 4× unified-coverage-agent dispatched for: scalability, self_healing, stub_cleanup, continuous_learning
- ✅ REQ-4/REQ-5 compliant
- ✅ Replied to both `<comment_new>` blocking comments (4637828176, 4637834235)

`special_flags.needs_verification: []` — empty, no re-verification required.

---

## Primary Objective for Next Session

**Continue Gap 5 coverage gate**: current floor ~20–22% → roadmap target ≥35%.

---

## Task Sequence

### Task 1 — Integrate background agent results
Check if the 4 coverage agents completed:
- `coverage-scalability` → `tests/unit/test_scalability_utils.py`
- `coverage-self-healing` → `tests/unit/test_self_healing_utils.py`
- `coverage-stub-cleanup` → `tests/unit/test_stub_cleanup.py`
- `coverage-continuous-learning` → `tests/unit/test_eval_gate.py` + `tests/unit/test_retraining_trigger.py`

Run: `python3 -m pytest tests/unit/ --cov=src/codex_ml --cov-report=term-missing -q 2>&1 | tail -5`

### Task 2 — Raise pyproject.toml fail_under
Once coverage ≥ 22% confirmed in CI output, set `fail_under = 22` in `pyproject.toml` (line ~535).

### Task 3 — Advance toward ≥35%
Identify next 5 highest-line 0% modules from coverage report and dispatch 4 more unified-coverage-agents.

### Task 4 — parallel_validation gate
Run `parallel_validation` after all new tests committed. Address any HIGH/CRITICAL findings.

### Task 5 — REQ-4/REQ-5 compliance
```bash
python3 scripts/ci/session_wrapup_autofix.py --check --pr-number 4792
```

### Task 6 — Update living docs
- `workbench/coverage/gap5_coverage_evidence.md` — add session 4 row with new floor
- `workbench/gap_backlog_prioritized.md` — update gap 5 status with new floor %
- `workbench/wave_execution_control.md` — add session row

---

## Key Files Reference

| File | Purpose |
|---|---|
| `workbench/coverage/gap5_coverage_evidence.md` | Coverage gate evidence + roadmap |
| `workbench/gap_backlog_prioritized.md` | Gap 5 status tracker |
| `workbench/wave_execution_control.md` | Wave + session log |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | REQ-4 compliance |
| `CHANGELOG.md` | REQ-5 compliance |
| `pyproject.toml` line ~535 | `fail_under` threshold (currently 15) |

---

## Dispatch Constraints
- Max concurrent background agents: **4**
- All artifacts under `workbench/evidence/` (never `/tmp`)
- Pre-existing lint failures are NOT your responsibility unless introduced by your changes
- Do NOT modify `.github/workflows/copilot-setup-steps.yml` lines 141–147 (hardened YAML block)
- REQ-4/REQ-5: BOTH `CHANGELOG.md` AND `AGENT_ACCOUNTABILITY_REPORT.md` must appear in the **latest** commit

---

## Success Criteria
- [ ] All 4 agent results integrated
- [ ] Coverage floor ≥ 22% measured and recorded
- [ ] `pyproject.toml fail_under` raised to ≥22
- [ ] Progress toward ≥35% underway
- [ ] `session_wrapup_autofix --check` passes
- [ ] `parallel_validation` complete — 0 HIGH/CRITICAL issues
- [ ] Living docs updated
