# Phase 6 Wave 1-2 Integrated Roadmap

**Status**: 📋 PLANNING PHASE  
**Timeline**: 5-7 days total (Wave 1: 2-3 days, Wave 2: 3-4 days)  
**Total Tests**: 142 new test cases (67 Wave 1 + 75 Wave 2)  
**Target Coverage**: 70%+ overall, 90%+ on critical modules

---

## Phase Structure Overview

```
Phase 6 Wave 1 (Days 1-3)          Phase 6 Wave 2 (Days 3-7)
├─ TIER-1 Unit Tests (35)          ├─ TIER-2 Unit Tests (32)
├─ TIER-1 Integration (25)         ├─ TIER-2 Integration (25)
├─ Error Path Tests (7)            ├─ Data Pipeline Tests (18)
└─ Coverage Report                 └─ Mutation Analysis

Parallel Execution Gates:
- PR #5111 validation workflows
- CodeQL security scan
- Continuous coverage monitoring
```

---

## Wave 1: TIER-1 Critical Path (Days 1-2)

### Execution Schedule

**Day 1 Morning (0-3 hours)**
```
1. Setup & Dependencies (30 min)
   └─ Install test libraries
   └─ Initialize test environment
   └─ Verify coverage baseline

2. Authentication & Lifecycle (90 min)
   └─ test_mcp_authentication.py (5 tests)
   └─ test_mcp_protocol_basics.py (10 tests)
   └─ test_service_initialization.py (8 tests)
   
Total: 23 tests, ~2-3 min execution
```

**Day 1 Afternoon (3-6 hours)**
```
3. Service Communication (2.5 hours)
   └─ test_service_communication.py (10 tests)
   └─ test_service_resilience.py (6 tests)
   └─ test_rpc_routing.py (8 tests)

4. Security Operations (1.5 hours)
   └─ test_crypto_operations.py (4 tests)
   └─ test_security_workflows.py (8 tests)
   
Total: 36 tests, ~4 min execution
```

**Day 2 Morning (6-9 hours)**
```
5. Codec & Utilities (3 hours)
   └─ test_codex_codecs.py (8 tests)
   └─ test_codex_serialization.py (10 tests)
   └─ test_utility_functions.py (12 tests)

Total: 30 tests, ~3 min execution
```

**Day 2 Afternoon (9-12 hours)**
```
6. Tool Registry & Execution (2 hours)
   └─ test_tool_registry.py (6 tests)
   └─ test_tool_execution.py (15 tests)

7. Error Path Coverage (1 hour)
   └─ test_mcp_errors.py (4 tests)
   └─ test_service_errors.py (3 tests)

Total: 28 tests, ~3 min execution
```

**Day 2 End (12 hours)**
```
8. Wave 1 Validation (1 hour)
   └─ Run full test suite with coverage
   └─ Generate coverage report
   └─ Validate 70%+ threshold met
   └─ Identify regressions

Wave 1 Total: 67 tests, ~12 min execution
```

---

## Wave 1 Module Coverage Targets

| Module | Current | Target | Wave 1 Target | Tests |
|--------|---------|--------|---------------|-------|
| `src/mcp` | 16.67% | 70% | 55% | 23 |
| `src/services` | 7.41% | 70% | 50% | 24 |
| `src/security` | 37.5% | 70% | 62% | 12 |
| `src/codex_utils` | 25.0% | 70% | 50% | 18 |
| `src/tools` | 20.0% | 70% | 55% | 21 |
| `src/utils` | 30.0% | 70% | 50% | 12 |
| **Wave 1 Subtotal** | **22.1%** | **70%** | **53%** | **67** |

---

## Wave 2: TIER-2 Completion (Days 3-7)

### TIER-2 Module Remediation

| Module | Current | Wave 1 After | Wave 2 Target | Tests | Priority |
|--------|---------|-------------|----------------|-------|----------|
| `src/agent` | 57.14% | ~65% | 72% | 11 | HIGH |
| `src/training` | 47.06% | ~55% | 75% | 19 | HIGH |
| `src/data` | 60.0% | ~65% | 75% | 8 | MEDIUM |
| `src/verification` | 50.0% | ~60% | 75% | 17 | MEDIUM |
| `src/tokenizer` | 50.0% | ~60% | 75% | 15 | MEDIUM |
| **Wave 2 Subtotal** | **52.8%** | ~61% | **74%** | **70** |

### Wave 2 Implementation Strategy

#### Phase 2A: Agent & Training Module Tests (Days 3-4)
```
test_agent_core.py (11 tests)
  ├─ Agent initialization
  ├─ Agent lifecycle (start/stop)
  ├─ Message routing
  └─ State management

test_training_pipeline.py (19 tests)
  ├─ Training job creation
  ├─ Dataset loading
  ├─ Model training flow
  ├─ Loss calculation
  ├─ Checkpoint management
  └─ Error recovery
```

#### Phase 2B: Data & Verification Tests (Days 4-5)
```
test_data_loading.py (8 tests)
  ├─ Data source initialization
  ├─ Data validation
  └─ Schema conformance

test_verification_workflows.py (17 tests)
  ├─ Model verification
  ├─ Output validation
  ├─ Performance checks
  └─ Result comparison
```

#### Phase 2C: Tokenization & Integration (Days 5-6)
```
test_tokenizer_encoding.py (10 tests)
  ├─ Token encoding
  ├─ Decoding verification
  ├─ Special tokens
  └─ Vocabulary operations

test_tokenizer_performance.py (5 tests)
  ├─ Batch processing
  ├─ Memory usage
  └─ Encoding speed
```

#### Phase 2D: Integration & Cross-Module Tests (Day 6-7)
```
test_full_pipeline.py (15 tests)
  ├─ End-to-end training
  ├─ Data → Training → Verification
  ├─ Error recovery
  └─ Performance validation

test_module_interactions.py (10 tests)
  ├─ Agent-Service communication
  ├─ Data-Training integration
  └─ Cross-module error handling
```

---

## Quality Gate Progression

### Wave 1 Exit Criteria (End of Day 2)

```python
# Code to verify Wave 1 completion
coverage_metrics = {
    "overall": 52.0,  # +20% from baseline
    "mcp": 55.0,      # +38% improvement
    "services": 50.0, # +42% improvement
    "security": 62.0, # +25% improvement
}

# Must satisfy:
assert coverage_metrics["overall"] >= 52.0
assert all(v >= 50.0 for v in coverage_metrics.values())
assert no_regressions()  # No previously covered code lost
assert mutation_score() >= 0.75  # 75% mutation kill rate
```

### Wave 2 Exit Criteria (End of Day 6)

```python
coverage_metrics = {
    "overall": 70.0,      # Target threshold
    "tier_1": 72.0,       # All critical paths covered
    "tier_2": 74.0,       # All important paths covered
    "security": 78.0,     # Max security coverage
    "services": 72.0,     # Max service coverage
}

# Must satisfy:
assert coverage_metrics["overall"] >= 70.0
assert all(v >= 70.0 for v in coverage_metrics.values())
assert no_regressions()
assert mutation_score() >= 0.80  # 80% mutation kill rate
assert flakiness_rate() == 0.0   # 100% reliable tests
```

---

## Resource Allocation

### Parallel Execution Strategy

```
┌─────────────────────────────────────┐
│ CI/CD Infrastructure (Continuous)   │
├─────────────────────────────────────┤
│ • Coverage monitoring active         │
│ • Regression detection enabled       │
│ • Performance baseline tracked       │
│ • Security scanning continuous       │
└─────────────────────────────────────┘
                  ↓
    ┌─────────────┬─────────────┐
    │   Wave 1    │   Wave 2    │
    │   Tests     │   Tests     │
    │  (67 tests) │  (75 tests) │
    └─────────────┴─────────────┘
            ↓           ↓
    ┌─────────────┬─────────────┐
    │ Unit Tests  │ Integration │
    │   (35)      │    (25)     │
    └─────────────┴─────────────┘
```

### Compute Requirements

| Phase | Tests | Est. Time | CPUs | Memory |
|-------|-------|-----------|------|--------|
| Wave 1 Unit | 35 | 3-4 min | 4 | 2GB |
| Wave 1 Integration | 25 | 5-6 min | 4 | 3GB |
| Wave 1 Error | 7 | 2 min | 2 | 1GB |
| Wave 2 (all) | 75 | 12-15 min | 4 | 4GB |

**Total Execution**: ~25-30 minutes (sequential), ~15 minutes (parallel)

---

## Duplication Extraction (Wave 3 - Post-Merge)

After Wave 2 completes, conduct analysis for test consolidation:

### 15 Identified Duplication Patterns

| Pattern | Files | Refactor Target | Consolidation |
|---------|-------|-----------------|----------------|
| Mock setup | 12 files | `conftest.py` | -8 tests |
| Async pattern | 8 files | `pytest_fixtures.py` | -6 tests |
| API validation | 15 files | `test_validators.py` | -12 tests |

**Wave 3 Impact**: 142 tests → 110 tests (22% consolidation, better maintainability)

---

## Success Metrics Dashboard

### Wave 1 Targets
- ✅ 67/67 tests implemented
- ✅ 52%+ overall coverage
- ✅ 0% regression
- ✅ 75%+ mutation score
- ✅ <15 min execution time

### Wave 2 Targets
- ✅ 75/75 tests implemented
- ✅ 70%+ overall coverage
- ✅ 72%+ TIER-1 coverage
- ✅ 74%+ TIER-2 coverage
- ✅ 0% flakiness
- ✅ 80%+ mutation score

### Post-Wave Consolidation
- ✅ 110-130 net tests (after DRY refactoring)
- ✅ 15+ TIER-1 patterns extracted
- ✅ 100% maintenance guide coverage

---

## Contingency Plans

### If Coverage Increase Falls Short

**Scenario**: Wave 1 tests reach only 48% instead of 52% target

**Response**:
1. Extend Wave 1 by 1 day to add 15-20 more tests
2. Focus on highest-priority uncovered paths
3. Defer TIER-2 to Wave 2
4. Update Wave 2 timeline accordingly

### If Tests Fail at High Rate (>10%)

**Scenario**: >10% of tests fail initial runs

**Response**:
1. Halt new test generation
2. Debug failing tests first
3. Verify mock/fixture setup
4. Check external dependencies
5. Resume generation once failure rate <5%

### If Regressions Detected

**Scenario**: Previously covered code now shows <70% coverage

**Response**:
1. Block PR #5111 merge
2. Identify regression root cause
3. Revert problematic changes
4. Re-run baseline tests
5. Provide root cause analysis to team

---

## Approval & Sign-Off

### Wave 1 Approval Gates

**Before Wave 1 Starts**:
- [ ] Team reviews and approves remediation plan
- [ ] Test environment validated
- [ ] Dependencies installed and verified
- [ ] Baseline coverage reported

**After Wave 1 Completes**:
- [ ] Coverage report reviewed
- [ ] All 67 tests passing
- [ ] Mutation score ≥75%
- [ ] No regressions detected
- [ ] Team sign-off on Wave 2 plan

### Wave 2 Approval Gates

**After Wave 2 Completes**:
- [ ] Coverage ≥70% overall
- [ ] All TIER-1 ≥70% coverage
- [ ] All TIER-2 ≥70% coverage
- [ ] Mutation score ≥80%
- [ ] Zero flaky tests
- [ ] Security approval (CodeQL)
- [ ] Ready for PR #5111 merge

---

## Next Steps

1. **Today (2026-06-27)**
   - [ ] Review & approve this roadmap
   - [ ] Confirm test environment ready
   - [ ] Identify test developers
   - [ ] Schedule Wave 1 kickoff

2. **Wave 1 Execution (2026-06-28 to 2026-06-30)**
   - [ ] Implement 67 TIER-1 tests
   - [ ] Run coverage report
   - [ ] Generate Wave 2 detailed plan

3. **Wave 2 Execution (2026-07-01 to 2026-07-04)**
   - [ ] Implement 75 TIER-2 tests
   - [ ] Validate 70%+ coverage
   - [ ] Security approval

4. **Post-Merge (2026-07-05+)**
   - [ ] PR #5111 merges with full coverage
   - [ ] Wave 3 duplication extraction (optional)
   - [ ] Activate continuous monitoring
   - [ ] Plan future coverage phases

---

*End of Phase 6 Wave 1-2 Integrated Roadmap*
