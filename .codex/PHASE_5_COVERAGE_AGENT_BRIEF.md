# Phase 5: Coverage Work Stream Agent Brief

**Agent:** `unified-coverage-agent`  
**Campaign:** Phase 5 Coverage Quick Wins (CLI Modules)  
**Date:** 2026-06-25T23:56:00Z  
**Authority:** CAD-Mandate Phase 5 Coverage Stream  
**Status:** ✅ READY FOR DELEGATION

---

## 📋 Executive Summary

Execute comprehensive gap-fill testing campaign on CLI module zero-coverage areas to achieve **23.0% → 24.5%+ coverage gain** in Phase 5.

**Target Coverage Gain:** +1.5 percentage points  
**Primary Focus:** CLI modules with 0% baseline coverage (1,194+ lines)  
**Timeline:** 2026-06-26 through 2026-07-16 (3 weeks)  
**Effort Estimate:** 40 hours

---

## 🎯 Primary Objectives

### Objective 1: Cover Top 6 CLI Modules (16 hours)

**Week 1-2 Focus: These 6 quick-win modules**

| # | Module Path | Lines | Current Coverage | Target | Est. Hours | Priority |
|---|---|---|---|---|---|---|
| 1 | `src/cli.py` | 191 | 0% | >60% | 2.5h | 🔴 CRITICAL |
| 2 | `src/codex_ml/cli/repo_map.py` | 190 | 0% | >60% | 2.5h | 🔴 CRITICAL |
| 3 | `src/codex_ml/cli/hydra_audit.py` | 259 | 0% | >50% | 3.5h | 🔴 CRITICAL |
| 4 | `src/codex_ml/cli/feature_store.py` | 165 | 0% | >55% | 2.0h | 🔴 CRITICAL |
| 5 | `src/codex_cli/app.py` | 156 | 0% | >60% | 2.0h | 🟠 HIGH |
| 6 | `src/codex/utils/hash_table.py` | 233 | 0% | >50% | 3.5h | 🟠 HIGH |
| **TOTAL** | | **1,194** | | | **16h** | |

### Objective 2: Cover 4-6 Additional Modules (20+ hours)

**Week 2-3 Focus: Additional high-value modules**

- `src/codex_ml/plugins/plugin_sandbox.py` (208 lines, 0%, 3h)
- `src/codex_ml/integrations/har_integration.py` (230 lines, 0%, 3h)
- `src/codex/campaigns/orchestrator.py` (178 lines, 0%, 2.5h)
- Additional edge cases and utility modules (6h+)

### Objective 3: Validation & Documentation (4 hours)

- Coverage report generation
- Test fixture documentation
- Reusability assessment for future modules

---

## 📊 Current State (From Phase 4)

**Coverage Baseline:** 23.00% (24,572 covered lines / 106,817 total)  
**Pre-Merge Baseline:** 10.7%  
**Post-Merge Improvement:** +12.3pp ✅

**Zero-Coverage Modules:** 194 modules, 13,756 lines total  
**CLI Category Breakdown:**
- 6 target modules: 1,194 lines (100% zero-coverage)
- Additional 4-6 modules: ~800-1,000 lines (100% zero-coverage)

---

## 🔧 Implementation Strategy

### Phase 1: Analysis & Fixture Setup (Days 1-2)

1. **Analyze each target module:**
   - Map function signatures and entry points
   - Identify dependencies and mocking requirements
   - Determine test fixture scope

2. **Create reusable fixtures:**
   - CLI argument parsers (shared across modules)
   - Mock services and dependencies
   - Pytest plugin configurations

### Phase 2: Test Implementation (Days 3-14)

**Per-module approach:**

1. **src/cli.py** (2.5h)
   - Test main CLI entry point
   - Test argument parsing
   - Test help and version commands
   - Target: 60%+ coverage

2. **src/codex_ml/cli/repo_map.py** (2.5h)
   - Test repo mapping CLI commands
   - Test filtering and output formatting
   - Test error handling
   - Target: 60%+ coverage

3. **src/codex_ml/cli/hydra_audit.py** (3.5h)
   - Test Hydra configuration audit CLI
   - Test config validation
   - Test output generation
   - Target: 50%+ coverage

4. **src/codex_ml/cli/feature_store.py** (2.0h)
   - Test feature store CLI commands
   - Test data loading and querying
   - Target: 55%+ coverage

5. **src/codex_cli/app.py** (2.0h)
   - Test CLI app framework
   - Test command registration
   - Test app initialization
   - Target: 60%+ coverage

6. **src/codex/utils/hash_table.py** (3.5h)
   - Test hash table operations
   - Test insertion, deletion, lookup
   - Test collision handling
   - Target: 50%+ coverage

### Phase 3: Validation & Extension (Days 15-21)

1. **Run coverage reports:**
   - Execute `pytest --cov=src/ --cov-report=json,.codex/coverage_phase5.json`
   - Generate HTML coverage reports
   - Identify any gaps

2. **Additional module coverage (4-6 modules, ~15h):**
   - Follow same pattern as above
   - Prioritize highest-value modules
   - Achieve cumulative +1.5pp gain

3. **Documentation:**
   - Create fixture reusability guide
   - Document patterns for future coverage work
   - Create `.codex/PHASE_5_COVERAGE_FIXTURES.md`

---

## ✅ Success Criteria

### Coverage Targets
- ✅ `src/cli.py`: >60% coverage
- ✅ `src/codex_ml/cli/repo_map.py`: >60% coverage
- ✅ `src/codex_ml/cli/hydra_audit.py`: >50% coverage
- ✅ `src/codex_ml/cli/feature_store.py`: >55% coverage
- ✅ `src/codex_cli/app.py`: >60% coverage
- ✅ `src/codex/utils/hash_table.py`: >50% coverage
- ✅ 4-6 additional modules >50% coverage

### Overall Metrics
- ✅ **Overall coverage: 23.0% → 24.5%+** (minimum +1.5pp gain)
- ✅ **Lines covered: 24,572 → 26,100+** (minimum +1,528 new covered lines)
- ✅ **Modules improved: 10+ modules**
- ✅ **Zero new zero-coverage modules in CLI category**

### Deliverables
- ✅ Test suite with 100+ new test functions
- ✅ Coverage report: `.codex/PHASE_5_COVERAGE_RESULTS.json`
- ✅ Fixture documentation: `.codex/PHASE_5_COVERAGE_FIXTURES.md`
- ✅ Weekly checkpoints: `.codex/PHASE_5_WEEK{1,2,3}_CHECKPOINT.md`
- ✅ Final validation report: `.codex/PHASE_5_COVERAGE_VALIDATION.md`

### Code Quality
- ✅ All tests follow pytest conventions
- ✅ All fixtures are reusable and well-documented
- ✅ All test files pass linting (Ruff: E,F,I)
- ✅ All new code has docstrings
- ✅ No new security vulnerabilities introduced

---

## 🔄 Weekly Checkpoint Schedule

**Week 1 (Jun 26 - Jul 02):**
- Fixture setup complete
- Modules 1-4 initial tests
- Target: 10 hours effort, preliminary coverage increase
- Checkpoint: `.codex/PHASE_5_WEEK1_CHECKPOINT.md`

**Week 2 (Jul 03 - Jul 09):**
- Modules 5-8 tests complete
- Coverage validation
- Additional fixtures created
- Target: 10 hours effort, +0.8pp coverage gain
- Checkpoint: `.codex/PHASE_5_WEEK2_CHECKPOINT.md`

**Week 3 (Jul 10 - Jul 16):**
- Final validation and refinement
- Additional module coverage (optional)
- Documentation finalization
- Target: +0.7pp coverage gain (total +1.5pp)
- Checkpoint: `.codex/PHASE_5_WEEK3_CHECKPOINT.md`

---

## 📁 Artifact Locations

**All artifacts stored in repository-tracked `.codex/` directory:**
- `.codex/PHASE_5_COVERAGE_RESULTS.json` — Coverage metrics JSON
- `.codex/PHASE_5_COVERAGE_FIXTURES.md` — Reusable fixture documentation
- `.codex/PHASE_5_COVERAGE_VALIDATION.md` — Final validation report
- `.codex/PHASE_5_WEEK1_CHECKPOINT.md` — Week 1 progress
- `.codex/PHASE_5_WEEK2_CHECKPOINT.md` — Week 2 progress
- `.codex/PHASE_5_WEEK3_CHECKPOINT.md` — Week 3 progress

**Test files added to:** `tests/phase_5_coverage_cli/` (organized by module)

---

## 🎯 Known Constraints & Resources

### Constraints
- Python >=3.12 required (repository standard)
- All tests must pass existing test suite (no regressions)
- No breaking changes to public APIs
- Coverage must be achievable without major refactoring

### Available Resources
- Phase 4 coverage analysis: `.codex/PHASE_4_COVERAGE_GAP_ANALYSIS.md`
- Existing CLI test patterns in `tests/cli/`
- Existing fixture patterns in `tests/conftest.py`
- Mock service patterns in test suite

### Dependencies to Mock
- `hydra` (configuration framework)
- `Click` (CLI framework)
- External services and APIs (per existing patterns)

---

## 📞 Escalation & Blockers

**Blocker Escalation:** If any of these issues arise:
- Cannot import module due to unmet dependencies
- Module requires significant refactoring to test
- Test fixture complexity exceeds reasonable effort
- Architecture prevents comprehensive coverage

→ Escalate to @mbaetiong with detailed context

**Authority Level:** Full autonomy (D) to make implementation decisions

---

## 📝 Phase 4 Reference

From Phase 4 Coverage Gap Analysis:
- Top 15 critical zero-coverage modules identified
- 3-phase roadmap created (22% → 25% → 30%)
- CLI modules identified as quick-wins category
- Expected +1.5pp gain from CLI category

---

**Brief Created:** 2026-06-25T23:56:00Z  
**Status:** ✅ READY FOR AGENT EXECUTION  
**Next Step:** Launch unified-coverage-agent with this brief
