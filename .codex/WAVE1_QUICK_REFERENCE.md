# Phase 7A Wave 1: Quick Reference Guide for Lane 1.3 & 1.4

**Generated**: December 19, 2024  
**For**: Lanes 1.3 (Gap-Filling) and 1.4 (Validation)

---

## 🎯 Mission Summary

- **Coverage Goal**: 7% → 25% (+18% gain)
- **Timeline**: Wave 1 (Days 1-30)
- **Strategy**: Test P1 modules first (codex_ml + codex), gain ~9%, then P2 modules for final push

---

## 📌 P1 MODULES: MUST TEST IN WAVE 1

### 1. **codex_ml** (469 files, 94K LOC)
- Current coverage: 20.3%
- Target: 25%+
- **What to test**: 
  - `train_loop.py` (core training) - **CRITICAL**
  - `utils/checkpointing.py` (checkpoint system) - **CRITICAL**
  - `tracking/writers.py` (experiment tracking)
  - Data loaders and processors
- **Effort**: 65 test functions, ~45 hours
- **Expected Gain**: +4-5%

### 2. **codex** (373 files, 92K LOC)
- Current coverage: 20.1%
- Target: 25%+
- **What to test**:
  - `github/mcp_poster.py` (GitHub integration) - **CRITICAL**
  - `cli.py` (CLI entry point) - **CRITICAL**
  - `cognitive/quantum_planset_engine.py` (cognitive engine)
  - `training.py` (training orchestration)
- **Effort**: 70 test functions, ~50 hours
- **Expected Gain**: +4-5%

---

## 🔥 TOP 10 HIGHEST-PRIORITY FUNCTIONS

### TIER A: TEST FIRST (Days 1-5)

| Rank | File | Function | LOC | Complexity | Why |
|------|------|----------|-----|-----------|-----|
| 1 | codex_ml/train_loop.py | Core training loop | 2,335 | HIGH | Core functionality |
| 2 | codex/github/mcp_poster.py | MCP poster | 2,612 | HIGH | Critical API |
| 3 | codex/cli.py | CLI handler | 1,893 | HIGH | User-facing |
| 4 | codex_ml/utils/checkpointing.py | Checkpoint manager | 1,662 | MEDIUM | Data persistence |
| 5 | codex/cognitive/quantum_planset_engine.py | Cognitive engine | 1,551 | HIGH | Core logic |

### TIER B: TEST NEXT (Days 6-15)

| 6 | codex_ml/utils/config_loader.py | Config parsing | 1,306 | MEDIUM | Used everywhere |
| 7 | codex_ml/reward_models/rlhf.py | RLHF model | 1,104 | HIGH | Advanced feature |
| 8 | codex/training.py | Training orchestrator | 1,296 | HIGH | Integration point |
| 9 | codex/archive/dal.py | Data access layer | 907 | MEDIUM | DB interactions |
| 10 | restore_pipeline/__init__.py | Pipeline orchestration | 1,119 | MEDIUM | Integration point |

---

## 🛠️ QUICK TEST IMPLEMENTATION CHECKLIST

### Phase 1: Quick Wins (Days 1-5) — 45-55 tests

- [ ] **bridge_protocol_v2.py** - 10 unit tests for message handling
- [ ] **logging_utils.py** - 8 unit tests for log formatting
- [ ] **config_loader.py** - 12 unit tests for parsing
- [ ] **codex_ml/train_loop.py** - 15 unit tests for core logic
- [ ] **codex/cli.py** - 10-15 unit tests for argument parsing

**Target Coverage Gain**: +2-3%

### Phase 2: Integration Tests (Days 6-15) — 45-60 tests

- [ ] **training pipeline** - 15-20 integration tests
- [ ] **GitHub API client** - 15-20 integration tests (with mocks)
- [ ] **checkpoint system** - 10-15 integration tests
- [ ] **context processing** - 5-10 integration tests

**Target Coverage Gain**: +4-5%

### Phase 3: Edge Cases & Parametrized (Days 16-25) — 55-75 tests

- [ ] **Error handling** - 30-40 parametrized tests
- [ ] **Boundary conditions** - 15-20 parametrized tests
- [ ] **Configuration variations** - 10-15 parametrized tests

**Target Coverage Gain**: +2-3%

---

## 📊 COVERAGE IMPACT MAPPING

### What tests drive the most coverage?

**High Impact (0.5% per test)**:
- Integration tests
- Parametrized tests with 3+ parameter combinations

**Medium Impact (0.2-0.4% per test)**:
- Unit tests for complex functions
- Mock-based API tests

**Low Impact (0.05-0.1% per test)**:
- Simple utility function tests
- Helper function tests

---

## 🔑 Key Testing Patterns

### Pattern 1: Configuration Parametrization

```python
@pytest.mark.parametrize("config,expected", [
    ({"learning_rate": 0.001}, True),
    ({"learning_rate": 0.0}, False),
    ({"learning_rate": 10.0}, False),
])
def test_training_configs(config, expected):
    ...
```

**Expected Impact**: +1-2% coverage per 10 tests

### Pattern 2: Error Scenario Mocking

```python
def test_github_api_error():
    with patch('github_client.post') as mock_post:
        mock_post.side_effect = APIError("403 Forbidden")
        assert handler() == "error_handled"
```

**Expected Impact**: +1-1.5% coverage per 10 tests

### Pattern 3: End-to-End Integration

```python
def test_training_pipeline(tmp_path):
    # Setup config
    # Run training
    # Verify checkpoint saved
    # Verify metrics logged
    ...
```

**Expected Impact**: +2-3% coverage per 10 tests

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't test library functions** - Focus on business logic
2. **Don't forget error cases** - 60% of gaps are error handling
3. **Don't skip integration tests** - They catch real bugs
4. **Don't test implementation details** - Test behavior instead
5. **Don't ignore parametrized tests** - They catch edge cases efficiently

---

## 📈 SUCCESS METRICS (Lane 1.4 Validation)

After implementing tests, verify:

| Metric | Success | Target |
|--------|---------|--------|
| Overall coverage | 7% → 15%+ | ≥ 15% |
| P1 modules | 20% → 25%+ | ≥ 25% |
| Test functions added | 130-145 | ✅ |
| Test pass rate | 100% | ✅ |
| No test pollution | 0 fixtures leaking | ✅ |
| Execution time | <5 min for quick suite | ✅ |

---

## 🎯 Daily Standup Template

**Lane 1.3 Leads** - Report daily:
- Functions tested today (count + LOC)
- Current measured coverage
- Blockers or questions
- Tomorrow's focus

**Lane 1.4 Leads** - Prepare for:
- Coverage measurement setup
- Failure analysis tools
- Regression detection
- Final reporting

---

## 📞 Escalation Path

**Question about a function?** → Check `.codex/PHASE_7A_WAVE1_LANE12_GAP_ANALYSIS.md`

**Need test pattern examples?** → See section "🛠️ Test Type Recommendations"

**Coverage not improving?** → Analyze with `pytest --cov --cov-report=term-missing`

**Need to reprioritize?** → Update this guide and notify both lanes

---

## 🚀 Success Formula

```
130-145 test functions × 30-45 min per function = 65-108 hours
÷ Team size (e.g., 3 developers) = 20-35 hours per developer
÷ 25 days = ~1-1.5 hours per developer per day
```

**Conclusion**: Wave 1 is achievable with focused effort on P1 modules

---

**Remember**: This is a **targeted gap-filling sprint**. Focus on:
1. High-impact functions first
2. Integration tests before edge cases
3. Parametrized tests for variations
4. Error handling paths (60% of gaps)

