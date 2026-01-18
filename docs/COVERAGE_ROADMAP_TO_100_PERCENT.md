# Test Coverage Roadmap: Path from 0% to 100%

**Created:** 2026-01-18  
**Current Baseline:** ~27.5% (estimated 196 of 714 modules covered)  
**Target:** 100% test coverage  
**Status:** 🚧 Phase 14 Foundation - Coverage threshold temporarily at 0%

---

## Executive Summary

This roadmap provides a structured, phased approach to achieve 100% test coverage across the entire codebase. The plan is divided into phases with increasing coverage thresholds, prioritizing critical modules first.

**Current State:**
- Total source files: 714
- Files with tests: 196 (~27.5%)
- Files without tests: 518
- Coverage threshold: Temporarily at 0% (Phase 14 foundation)

---

## Phase Overview

| Phase | Target Coverage | Duration | Focus Area | Threshold Setting |
|-------|-----------------|----------|------------|-------------------|
| 14.0 (Current) | 0% → 30% | 2 weeks | Foundation & Infrastructure | `fail_under = 0` |
| 14.1 | 30% → 50% | 3 weeks | Core Modules (codex, codex_ml) | `fail_under = 30` |
| 14.2 | 50% → 70% | 4 weeks | Training, Agents, RAG | `fail_under = 50` |
| 14.3 | 70% → 85% | 3 weeks | Integration & Edge Cases | `fail_under = 70` |
| 14.4 | 85% → 100% | 3 weeks | Final Gaps & Branch Coverage | `fail_under = 85` |
| Post-14 | 100% | Ongoing | Maintenance & Regression | `fail_under = 100` |

**Total Estimated Duration:** 15 weeks

---

## Phase 14.0: Foundation (Current Phase)

**Goal:** Establish test infrastructure and baseline coverage  
**Duration:** 2 weeks  
**Threshold:** `fail_under = 0`

### Completed Items
- [x] Fix CI/CD pipeline issues
- [x] Align Python version matrix with project requirements (3.11+)
- [x] Fix pytest plugin discovery in xdist workers
- [x] Create coverage analysis baseline (`.codex/qa_walkthrough/coverage_analysis.json`)

### Remaining Items
- [ ] Fix all existing test failures
- [ ] Ensure all test infrastructure is working
- [ ] Document test patterns and conventions
- [ ] Set up coverage reporting to Codecov

### Exit Criteria
- All CI jobs passing
- Coverage baseline established
- Test infrastructure documented

---

## Phase 14.1: Core Modules (30% → 50%)

**Goal:** Cover high-impact core modules  
**Duration:** 3 weeks  
**Threshold:** `fail_under = 30`

### Priority Modules (High Impact)

| Module | Files | Current Tests | Target | Impact |
|--------|-------|---------------|--------|--------|
| `src/codex/logging/` | 8 | 2 | 8 | Critical - session logging |
| `src/codex/cli/` | 3 | 1 | 3 | Critical - entry points |
| `src/codex/utils/` | 5 | 1 | 5 | High - utility functions |
| `src/codex_ml/config/` | 3 | 0 | 3 | High - configuration |
| `src/codex_ml/cli/` | 25 | 3 | 15 | High - CLI commands |
| `src/codex_ml/data/` | 18 | 4 | 12 | High - data loading |

### Test Categories to Add

1. **Unit Tests for Core Functions** (~100 tests)
   - Configuration loading and validation
   - Data serialization/deserialization
   - CLI command parsing
   - Logging functionality

2. **Integration Tests** (~30 tests)
   - CLI end-to-end flows
   - Config → execution paths
   - Data pipeline integration

### Coverage Targets by Module Group

```
src/codex/logging/    → 80%
src/codex/cli/        → 70%
src/codex/utils/      → 70%
src/codex_ml/config/  → 80%
src/codex_ml/cli/     → 60%
src/codex_ml/data/    → 70%
```

### Exit Criteria
- Overall coverage ≥ 50%
- All priority modules have basic test coverage
- No critical paths untested

---

## Phase 14.2: Training, Agents & RAG (50% → 70%)

**Goal:** Cover ML training pipeline, agents, and RAG system  
**Duration:** 4 weeks  
**Threshold:** `fail_under = 50`

### Priority Modules

| Module | Files | Current Tests | Target | Impact |
|--------|-------|---------------|--------|--------|
| `src/codex_ml/training/` | 18 | 2 | 15 | Critical - training loop |
| `src/codex/rag/` | 24 | 4 | 20 | Critical - RAG system |
| `agents/` | 33 | 1 | 20 | High - agent framework |
| `training/` | 13 | 0 | 10 | High - training utils |
| `src/codex_ml/models/` | 10 | 2 | 8 | High - model loading |

### Test Categories to Add

1. **Training Pipeline Tests** (~80 tests)
   - Model initialization
   - Training loop execution
   - Checkpoint save/load
   - Early stopping logic
   - Distributed training mocks

2. **RAG System Tests** (~100 tests) 
   - See detailed plan in `docs/PLAN_100_PERCENT_COVERAGE.md`
   - Embeddings providers
   - Index building
   - Retrieval accuracy
   - Cache management

3. **Agent Tests** (~50 tests)
   - Agent initialization
   - Message handling
   - Memory management
   - Orchestrator logic

### Coverage Targets by Module Group

```
src/codex_ml/training/ → 80%
src/codex/rag/         → 90%
agents/                → 60%
training/              → 70%
src/codex_ml/models/   → 80%
```

### Exit Criteria
- Overall coverage ≥ 70%
- Training pipeline fully tested
- RAG system at 90%+ coverage
- Agent framework has basic coverage

---

## Phase 14.3: Integration & Edge Cases (70% → 85%)

**Goal:** Cover integration paths and edge cases  
**Duration:** 3 weeks  
**Threshold:** `fail_under = 70`

### Focus Areas

1. **Cross-Module Integration Tests** (~60 tests)
   - Config → Training → Evaluation flow
   - RAG → Agent → Response flow
   - CLI → Core → Output flow

2. **Error Handling & Edge Cases** (~80 tests)
   - Invalid inputs
   - Network failures
   - Resource exhaustion
   - Concurrent access
   - Platform-specific paths

3. **Remaining Module Coverage** (~100 tests)
   - `src/codex_ml/serving/`
   - `src/codex_ml/monitoring/`
   - `src/codex/security/`
   - `src/codex/quantum_orchestrator/`

### Coverage Targets by Module Group

```
src/codex_ml/serving/        → 80%
src/codex_ml/monitoring/     → 75%
src/codex/security/          → 90%
src/codex/quantum_orchestrator/ → 70%
```

### Exit Criteria
- Overall coverage ≥ 85%
- All critical error paths tested
- Integration tests passing
- No major modules below 60%

---

## Phase 14.4: Final Gaps & Branch Coverage (85% → 100%)

**Goal:** Achieve 100% line and branch coverage  
**Duration:** 3 weeks  
**Threshold:** `fail_under = 85`

### Strategy

1. **Coverage Gap Analysis**
   ```bash
   pytest --cov=src --cov-report=term-missing --cov-branch
   ```

2. **Targeted Test Generation**
   - Use coverage reports to identify uncovered lines
   - Add tests for each uncovered branch
   - Document any `# pragma: no cover` exclusions

3. **Documentation Example Tests**
   - Validate all code examples in docs
   - Add tests for README examples
   - Test CLI help examples

### Final Push Categories

| Category | Estimated Tests | Target |
|----------|-----------------|--------|
| Branch coverage gaps | 100 | 100% branch |
| Exception handlers | 50 | All exceptions tested |
| Documentation examples | 30 | All examples validated |
| Platform-specific code | 20 | Mocked appropriately |

### Exit Criteria
- Line coverage = 100%
- Branch coverage = 100%
- All documentation examples tested
- CI enforcing 100% threshold

---

## Implementation Guidelines

### Test File Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── conftest_shared.py           # Additional fixtures
├── unit/                        # Unit tests
│   ├── test_codex_ml/           # codex_ml module tests
│   ├── test_codex/              # codex module tests
│   └── test_agents/             # agents module tests
├── integration/                 # Integration tests
│   ├── test_cli_flows.py
│   ├── test_training_pipeline.py
│   └── test_rag_pipeline.py
├── e2e/                         # End-to-end tests
│   ├── test_full_workflow.py
│   └── test_cli_e2e.py
└── test_rag_*.py                # Existing RAG tests
```

### Test Naming Convention

```python
def test_<module>_<function>_<scenario>():
    """Test description."""
    pass

# Examples:
def test_indexer_chunk_text_empty_string():
def test_retriever_query_network_timeout():
def test_training_loop_early_stopping():
```

### Coverage Configuration

**pyproject.toml updates by phase:**

```toml
# Phase 14.0 (Current)
[tool.coverage.report]
fail_under = 0

# Phase 14.1
fail_under = 30

# Phase 14.2
fail_under = 50

# Phase 14.3
fail_under = 70

# Phase 14.4
fail_under = 85

# Post-14 (Final)
fail_under = 100
```

### Workflow Updates

Each phase should update the CI workflow thresholds:

```yaml
# .github/workflows/test-rag.yml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src \
      --cov-report=xml \
      --cov-report=html \
      --cov-fail-under=${PHASE_THRESHOLD}
```

---

## Priority Test Proposals

Based on `.codex/qa_walkthrough/coverage_analysis.json`:

### TP-001: Unit Tests for High-Priority Modules
- **Target:** 390 untested high-priority modules
- **Estimated Impact:** +20-30% coverage
- **Tests to Add:** ~400

### TP-002: Integration Tests for Cross-Module Interactions
- **Target:** Critical workflows
- **Estimated Impact:** +10-15% coverage
- **Tests to Add:** ~100

### TP-003: E2E Tests for Critical Workflows
- **Target:** User-facing features
- **Estimated Impact:** +5-10% coverage
- **Tests to Add:** ~50

---

## Monitoring & Tracking

### Coverage Dashboard

Track progress using:
1. **Codecov integration** - PR coverage diffs
2. **HTML reports** - Detailed line-by-line coverage
3. **CI badges** - Current coverage status

### Weekly Check-ins

| Week | Expected Coverage | Actual Coverage | Status |
|------|-------------------|-----------------|--------|
| 1 | 30% | - | |
| 2 | 35% | - | |
| 3 | 40% | - | |
| 4 | 50% | - | |
| ... | ... | ... | |
| 15 | 100% | - | |

---

## Risk Mitigation

### Common Blockers & Solutions

| Risk | Mitigation |
|------|------------|
| Flaky tests | Use `pytest-rerunfailures`, isolate external dependencies |
| Slow tests | Parallelize with `pytest-xdist`, use fixtures |
| Coverage plateaus | Focus on branch coverage, use mutation testing |
| External dependencies | Mock external services, use VCR cassettes |

### Exclusion Guidelines

Only exclude code with valid reasons:

```python
# Acceptable exclusions:
if TYPE_CHECKING:  # pragma: no cover
    ...

# Unacceptable exclusions:
if complex_condition:  # pragma: no cover  # ❌ Don't do this
    important_logic()
```

---

## Success Metrics

### Phase Completion Checklist

- [ ] **Phase 14.0**: Coverage infrastructure working, baseline established
- [ ] **Phase 14.1**: 50% coverage achieved, core modules tested
- [ ] **Phase 14.2**: 70% coverage achieved, ML pipeline tested
- [ ] **Phase 14.3**: 85% coverage achieved, integration tested
- [ ] **Phase 14.4**: 100% coverage achieved, all gaps closed

### Quality Indicators

| Metric | Target |
|--------|--------|
| Line Coverage | 100% |
| Branch Coverage | 100% |
| Test Count | 1000+ |
| Test Duration | < 10 min (parallel) |
| Flaky Test Rate | < 1% |

---

## References

- [RAG 100% Coverage Plan](./PLAN_100_PERCENT_COVERAGE.md)
- [Test Coverage Plan for RAG](./TEST_COVERAGE_PLAN_RAG.md)
- [Coverage Analysis JSON](../.codex/qa_walkthrough/coverage_analysis.json)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

## Next Steps

1. ✅ Fix current CI failures (xdist plugin discovery)
2. ⏳ Verify all existing tests pass
3. 📋 Begin Phase 14.1 - Core modules unit tests
4. 📋 Update coverage threshold to 30% after Phase 14.1

**Owner:** Phase 14 implementation team  
**Review Cadence:** Weekly coverage review
