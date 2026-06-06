# Gap 5 — Coverage Gate Evidence

**Gap ID:** 5  
**Title:** Establish CI coverage gate  
**Status:** 🟡 In Progress  
**Branch:** `copilot/explore-codebase-and-create-plan`  
**PR:** #4792  

---

## Coverage Floor History

| Session | Date | Tests Added | Module(s) | Coverage Floor | Notes |
|---------|------|-------------|-----------|----------------|-------|
| Baseline | 2026-05-01 | — | all | ~17.57% | Pre-Wave-3/4 baseline |
| Gap-5 session 1 | 2026-06-06T07:10Z | 28 | `scripts/ci/check_workflow_yaml.py`, `scripts/ci/validate_configs.py` | ~17.57% | First direct coverage tests |
| Gap-5 session 2 (agent) | 2026-06-06T07:32Z | 89 | `monitoring/drift_detection.py` (0→~86%), `experiments/ab_testing.py` stdlib (52→~97%) | ~18–20% | unified-coverage-agent batch |
| Gap-5 session 3 | 2026-06-06T07:46Z | 56 | `utils/jsonio.py`, `utils/optional_dependencies.py`, `utils/serialization.py`, `feedback/events.py`, `utils/hf_revision.py`, `utils/opt_import.py` | ~20–22% | Direct test writing (this session) |
| Gap-5 session 3 agents | 2026-06-06T08:15Z | 257 | `utils/scalability.py` (77 tests), `utils/self_healing.py` (77 tests), `utils/stub_cleanup.py` (78 tests), `continuous_learning/eval_gate.py`+`trigger.py` (46 tests) | ~22% | 4× unified-coverage-agent completed |

---

## Target Roadmap

| Milestone | Target % | Status |
|-----------|----------|--------|
| Phase 1 | ≥15% | ✅ Done (fail_under=15 in pyproject.toml) |
| Phase 2 | ≥20% | ✅ Done (fail_under=20 in pyproject.toml, 313 tests added session 3) |
| Phase 2b | ≥22% | 🟡 In Progress — confirm via CI |
| Phase 3 | ≥35% | ⬜ Planned |
| Phase 4 | ≥50% | ⬜ Planned |
| Phase 5 | ≥80% | ⬜ Roadmap target |

---

## Key 0% Modules Identified (Session 3)

From `python3 -m pytest tests/unit/test_continuous_learning.py tests/unit/test_data_drift.py tests/unit/test_ab_testing_stdlib.py --cov=src/codex_ml` (6.65% for that subset):

| Module | Lines | Coverage | Priority |
|--------|-------|----------|----------|
| `utils/scalability.py` | 290 | 0% | HIGH — dispatched to agent |
| `utils/reproducibility_hardening.py` | 245 | 0% | HIGH |
| `utils/self_healing.py` | 94 | 0% | HIGH — dispatched to agent |
| `utils/stub_cleanup.py` | 155 | 0% | HIGH — dispatched to agent |
| `workflow/track_c_workflow.py` | 150 | 0% | MEDIUM |
| `utils/safe_pickle.py` | 92 | 0% | MEDIUM |
| `utils/subproc.py` | 68 | 0% | MEDIUM |
| `utils/retention.py` | 87 | 0% | MEDIUM |
| `continuous_learning/eval_gate.py` | ~50 | 0% | HIGH — dispatched to agent |
| `continuous_learning/trigger.py` | ~50 | 0% | HIGH — dispatched to agent |

---

## Notes

- `fail_under` in `pyproject.toml` raised to **20** (session 3: 313 tests added across 8+ modules).
- 97 untested modules identified in `src/codex_ml` alone.
- Wave 3/4 contributions added 15+ new source modules; all starting at 0% coverage.
- Each coverage commit must include `CHANGELOG.md` + `AGENT_ACCOUNTABILITY_REPORT.md` (REQ-4/REQ-5).
