# Phase 26 Execution Plan: Coverage 70% → 75-80%

**Status**: 🔄 IN PROGRESS  
**Started**: 2026-01-24  
**Target Completion**: 4-6 Phases  
**Automation Level**: 100%  
**Policy**: AI Agency Policy v1.1.0 Compliant

---

## Executive Summary

**Goal**: Increase test coverage from 70% (Phase 25 baseline) to 75-80% through targeted edge case test generation.

**Approach**: Data-driven test generation focusing on:
1. Critical security paths (safety filters, auth middleware)
2. High-impact CLI modules (codex_cli, cli_rag)
3. Training pipeline components (engine_hf_trainer)
4. Zero-coverage modules with high priority scores

**Success Metrics**:
- ✅ 100-150 new edge case tests added
- ✅ Coverage increases to 75-80%
- ✅ All 14 quality gates pass
- ✅ Zero test failures
- ✅ Cognitive brain status updated

---

## Phase 1: Coverage Gap Analysis ✅

**Data Source**: `.codex/qa_walkthrough/coverage_analysis.json`

### Current State (Phase 25 Baseline)
- **Total Modules**: 262 source modules
- **Tested Modules**: 46 (17.6%)
- **Untested Modules**: 862 files
- **Current Coverage**: 70% (overall), 17.3% (file count)
- **Existing Tests**: 1,996 test files

### Critical Gaps Identified

#### Tier 1: Critical (0% Coverage, High Priority)
| Module | Lines | Priority | Risk |
|--------|-------|----------|------|
| src/codex/cli_rag.py | 821 | 100 | High (CLI entry point) |
| src/tokenization/cli.py | 596 | 100 | High (tokenization) |
| src/codex/archive/cli.py | 712 | 100 | High (data persistence) |
| src/codex/quantum_orchestrator/cli.py | 608 | 100 | High (orchestration) |
| src/codex_ml/cli/codex_cli.py | 846 | 100 | High (main CLI) |
| src/codex_ml/safety/filters.py | 1,027 | 95 | **CRITICAL** (security) |
| src/training/engine_hf_trainer.py | 1,357 | 90 | High (training core) |
| src/codex_ml/training/unified_training.py | 604 | 90 | High (training API) |
| src/codex_ml/training/legacy_api.py | 1,571 | 90 | High (backwards compat) |
| src/codex_ml/data/loaders.py | 659 | 90 | High (data loading) |
| src/codex_ml/config/__init__.py | 904 | 90 | High (configuration) |

**Total Tier 1**: 9,705 lines of untested critical code

#### Tier 2: Low Coverage (<30%)
- src/mcp: 11.67% coverage (60 files, 7 tested)
- src/context_management: 0% coverage (14 files)
- src/agent: 0% coverage (7 files)
- src/services: 7.41% coverage (27 files, 2 tested)
- src/codex_bridge: 0% coverage (2 files)
- src/tools: 20% coverage (5 files, 1 tested)
- src/utils: 30% coverage (10 files, 3 tested)
- src/cognitive_brain: 31.43% coverage (35 files, 11 tested)

---

## Phase 2: Test Generation Strategy 🔄

### Target Allocation (100-150 Tests)

#### Batch 1: Security & Safety (30 tests)
**Target**: `src/codex_ml/safety/filters.py` (1,027 lines)
- Content filtering edge cases (10 tests)
- Toxicity detection boundary conditions (10 tests)
- PII detection and scrubbing (10 tests)

**Files to Create**:
- `tests/codex_ml/safety/test_content_filters_edge_cases.py` (10 tests)
- `tests/codex_ml/safety/test_toxicity_boundaries.py` (10 tests)
- `tests/codex_ml/safety/test_pii_edge_cases.py` (10 tests)

#### Batch 2: CLI Entry Points (25 tests)
**Targets**:
- `src/codex_ml/cli/codex_cli.py` (846 lines)
- `src/codex/cli_rag.py` (821 lines)

- CLI argument parsing edge cases (10 tests)
- Error handling and validation (10 tests)
- Help text and documentation (5 tests)

**Files to Create**:
- `tests/codex_ml/cli/test_codex_cli_edge_cases.py` (15 tests)
- `tests/codex/test_cli_rag_edge_cases.py` (10 tests)

#### Batch 3: Training Pipeline (25 tests)
**Targets**:
- `src/training/engine_hf_trainer.py` (1,357 lines)
- `src/codex_ml/training/unified_training.py` (604 lines)

- Checkpoint loading/saving edge cases (10 tests)
- Optimizer state management (8 tests)
- Distributed training scenarios (7 tests)

**Files to Create**:
- `tests/training/test_engine_hf_trainer_edge_cases.py` (15 tests)
- `tests/codex_ml/training/test_unified_training_edge_cases.py` (10 tests)

#### Batch 4: Data Loading & Config (20 tests)
**Targets**:
- `src/codex_ml/data/loaders.py` (659 lines)
- `src/codex_ml/config/__init__.py` (904 lines)

- Data loader edge cases (corrupted files, empty datasets) (10 tests)
- Configuration validation and defaults (10 tests)

**Files to Create**:
- `tests/codex_ml/data/test_loaders_edge_cases.py` (10 tests)
- `tests/codex_ml/config/test_config_edge_cases.py` (10 tests)

#### Batch 5: Context & Agent Management (15 tests)
**Targets**:
- `src/context_management` (14 files, 0% coverage)
- `src/agent` (7 files, 0% coverage)

- Context window management edge cases (8 tests)
- Agent state transitions (7 tests)

**Files to Create**:
- `tests/context_management/test_context_edge_cases.py` (8 tests)
- `tests/agent/test_agent_edge_cases.py` (7 tests)

#### Batch 6: Utilities & Tools (15 tests)
**Targets**:
- `src/utils` (10 files, 30% coverage)
- `src/tools` (5 files, 20% coverage)

- Path utilities edge cases (8 tests)
- Tool integration edge cases (7 tests)

**Files to Create**:
- `tests/utils/test_utils_edge_cases.py` (8 tests)
- `tests/tools/test_tools_edge_cases.py` (7 tests)

#### Batch 7: Cognitive Brain & Services (15-20 tests)
**Targets**:
- `src/cognitive_brain` (35 files, 31.43% coverage)
- `src/services` (27 files, 7.41% coverage)

- Cognitive state management (8 tests)
- Service lifecycle and health checks (7-12 tests)

**Files to Create**:
- `tests/cognitive_brain/test_cognitive_edge_cases.py` (8 tests)
- `tests/services/test_service_edge_cases.py` (7-12 tests)

---

## Phase 3: Quality Gate Validation 📋

### 14 Quality Gates (from release-gate-agent)

#### Blocking Gates (7) - Must Pass
1. ✅ **Test Suite**: All tests pass
2. 🔄 **Coverage**: 75%+ coverage (target of Phase 26)
3. ✅ **Security Scan**: No high/critical vulnerabilities
4. ✅ **Documentation**: All public APIs documented
5. ✅ **Build**: Package builds successfully
6. ✅ **Compatibility**: Python 3.10+ support
7. ✅ **Changelog**: Changes documented

#### Warning Gates (4) - Should Pass
8. ⚠️ **Linting**: Code style compliant
9. ⚠️ **Type Checking**: Type annotations present
10. ⚠️ **Dependencies**: No deprecated dependencies
11. ⚠️ **Performance**: No performance regressions

#### Info Gates (3) - Nice to Have
12. ℹ️ **Code Complexity**: Cyclomatic complexity <10
13. ℹ️ **Documentation Coverage**: 80%+ docs coverage
14. ℹ️ **Test Performance**: Tests complete in <10 min

### Validation Commands
```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Security scan
bandit -r src/ -f json -o security_report.json

# Linting
ruff check src/

# Type checking
mypy src/ --strict

# Build package
python -m build
```

---

## Phase 4: Cognitive Brain Status Update 📊

### Files to Update
1. `.codex/cognitive_brain/PHASE_26_RELEASE_READINESS.md`
   - Mark Phase 26 as COMPLETE
   - Update coverage metrics (70% → 75-80%)
   - Document 100-150 new tests added

2. `.codex/cognitive_brain/PHASE_26_EXECUTION_PLAN.md` (this file)
   - Update status from IN PROGRESS → COMPLETE
   - Add execution summary with metrics

3. `.codex/qa_walkthrough/coverage_analysis_update.json`
   - New coverage statistics
   - Module-by-module improvements

---

## Execution Timeline

### Phase 2.1: Security Tests (Current)
**Duration**: 1 Phase  
**Output**: 30 tests for safety filters  
**Status**: 🔄 IN PROGRESS

### Phase 2.2: CLI Tests
**Duration**: 1 Phase  
**Output**: 25 tests for CLI entry points  
**Status**: ⏳ PENDING

### Phase 2.3: Training Tests
**Duration**: 1 Phase  
**Output**: 25 tests for training pipeline  
**Status**: ⏳ PENDING

### Phase 2.4: Data & Config Tests
**Duration**: 1 Phase  
**Output**: 20 tests for data/config  
**Status**: ⏳ PENDING

### Phase 2.5: Context & Agent Tests
**Duration**: 1 Phase  
**Output**: 15 tests for context/agent  
**Status**: ⏳ PENDING

### Phase 2.6: Utilities & Services Tests
**Duration**: 1 Phase  
**Output**: 30-35 tests for utilities/services  
**Status**: ⏳ PENDING

**Total Duration**: 4-6 Phases (policy compliant)

---

## Success Criteria Checklist

### Test Generation
- [ ] 100-150 edge case tests created
- [ ] All tests follow existing test patterns
- [ ] Tests use pytest fixtures and markers appropriately
- [ ] Tests include docstrings and clear descriptions

### Coverage Improvement
- [ ] Overall coverage: 75-80%
- [ ] Tier 1 critical modules: >50% coverage
- [ ] Security modules (safety filters): >70% coverage
- [ ] CLI modules: >60% coverage

### Quality Assurance
- [ ] All 14 quality gates validated
- [ ] 7 blocking gates: PASS
- [ ] 4 warning gates: PASS (or documented exceptions)
- [ ] 3 info gates: Monitored

### Documentation
- [ ] PHASE_26_RELEASE_READINESS.md updated
- [ ] coverage_analysis_update.json created
- [ ] Test documentation added to new test files
- [ ] Cognitive brain status reflects Phase 26 completion

---

## Risk Mitigation

### Potential Issues
1. **Test failures**: Use existing test patterns, mock external dependencies
2. **Import errors**: Conditional imports for optional dependencies
3. **Coverage measurement**: May need multiple test runs for accurate coverage
4. **Time constraints**: Prioritize Tier 1 critical modules

### Mitigation Strategies
- Use hypothesis for property-based testing
- Mock external APIs and services
- Skip tests requiring unavailable dependencies
- Focus on edge cases and boundary conditions

---

## Autonomous Execution Notes

**Policy Compliance**: AI Agency Policy v1.1.0
- ✅ No human intervention required
- ✅ Phase-based timeline (not time-based)
- ✅ Alternative approaches documented
- ✅ Best-effort iterations specified

**Automation Level**: 100%
- Test generation: Automated
- Coverage analysis: Automated
- Quality gate validation: Automated
- Documentation updates: Automated

---

**Last Updated**: 2026-01-24T01:44:44Z  
**Phase Status**: 🔄 IN PROGRESS  
**Next Update**: After Phase 2.1 completion
