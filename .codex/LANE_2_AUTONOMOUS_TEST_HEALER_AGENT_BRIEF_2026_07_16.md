# Lane 2: Phase 6A - Test Error Remediation (Batch 1) — Agent Brief

**Prepared**: 2026-07-16T03:09:15Z  
**Target Agent**: `autonomous-test-healer-agent`  
**Session**: CTEP-Phase4-6-Continuation-S2026_07_16  
**Authority**: @mbaetiong D-tier autonomous | wec:auto-approve enabled  

---

## 🎯 OBJECTIVE

Fix **50-60 test errors** from Phase 6 Batch 1 (import errors, P19 shadow imports, flaky tests) in parallel execution.

**Success Criteria**:
- ✅ 50-60 errors → 0 (100% batch resolution)
- ✅ Test suite passes green
- ✅ No new errors introduced
- ✅ No regressions
- ✅ Batch 1 confidence: 85-90%

---

## 📋 EXECUTION STEPS

### Step 1: Error Analysis & Categorization

**Reference**: `.codex/PHASE_6_TEST_ERROR_ANALYSIS.md` (full analysis)

From the 142 total test errors:
- **Your Batch**: Errors 1-60 (prioritized by frequency)
- **Error Categories** (your batch):
  - Import errors (18-20): `ModuleNotFoundError`, `ImportError`
  - P19 shadow imports (8-10): Dual-package shadowing issues
  - Flaky tests (4-6): Timing, external service dependencies
  - Other (10-15): Type errors, assertion failures

**Categorization Command**:
```bash
python scripts/ci/analyze_test_errors.py --batch 1 --errors 50-60 --categorize
```

### Step 2: Fix Template Application

**Reference**: `.codex/PHASE_6_EXECUTION_PLAN.md` (fix templates per category)

**For Import Errors**:
```python
# Pattern 1: Missing dependency
# BEFORE: import mlflow
# AFTER: try/except with HAS_MLFLOW flag

# Pattern 2: sys.path issues
# BEFORE: sys.path.insert(0, 'src')
# AFTER: from codex... imports (no src prefix)

# Pattern 3: Circular imports
# BEFORE: from module_a import something that imports module_b
# AFTER: Refactor to remove circularity, use late imports if needed
```

**For P19 Shadow Imports**:
```python
# Pattern: Dual-package shadowing
# DETECTION: Import works in IDE but fails in pytest
# FIX: Use pytest.ini config: pythonpath = [".", "src"]
# And ensure no __init__.py in src that shadows package
```

**For Flaky Tests**:
```python
# Pattern: Timing-dependent tests
# FIX: Add pytest.mark.flaky(reruns=2, reruns_delay=1)
# Or use freezegun/time mocking for time-dependent tests

# Pattern: External service dependencies
# FIX: Use pytest-mock to mock external calls
# Or add pytest.mark.requires_network for integration tests
```

### Step 3: Test Suite Validation

**Command**:
```bash
python -m pytest tests/ -v --tb=short --x
```

Run after each batch of 5-10 fixes:
- ✅ Verify newly fixed tests pass
- ✅ Check for new errors introduced
- ✅ Capture error reduction metrics

**Tracking**:
```bash
# Before fixes
pytest tests/ --co -q | wc -l  # Total test count

# After each fix batch
pytest tests/ -v 2>&1 | grep -E "PASSED|FAILED|ERROR" | tee batch_results.txt
```

### Step 4: Error Count Tracking

**Progress Template**:
```
Batch 1 Progress (Errors 1-60):
- Start errors: 60
- Errors fixed (batch 1-10): 8 remaining → 52
- Errors fixed (batch 11-20): 7 remaining → 45
- Errors fixed (batch 21-30): 9 remaining → 36
- Errors fixed (batch 31-40): 6 remaining → 30
- Errors fixed (batch 41-50): 8 remaining → 22
- Errors fixed (batch 51-60): 5 remaining → 17
- Final error count: [TARGET = 0]
- Success: ✅ [if 0] / ⚠️ [if >0]
```

### Step 5: Escalation if Fix Fails

**Escalation Protocol**:
1. Document error details (type, stack trace, category)
2. If fix template doesn't work:
   - Try 2 alternative approaches
   - If both fail: Mark as "complex-requires-manual"
   - Post escalation brief with error details
3. Escalate to `ci-failure-resolution-agent` if needed

---

## 📊 ERROR BREAKDOWN (Batch 1 of 3)

**Reference**: `.codex/PHASE_6_TEST_ERROR_ANALYSIS.md`

| Error Category | Count | Estimated Fix Time | Complexity |
|---|---|---|---|
| Import Errors (ModuleNotFoundError) | 18 | 2-3 min each | Low |
| P19 Shadow Imports | 10 | 5 min each | Medium |
| Flaky Tests | 6 | 8 min each | Medium |
| Type Errors | 12 | 3-5 min each | Low |
| Assertion Failures | 10 | 5-10 min each | Medium |
| **Batch 1 Total** | **56** | **90 minutes** | **Mixed** |

---

## ⏱️ TIMELINE

- **Start**: 2026-07-16T03:12:00Z
- **Error Analysis**: 10 minutes
- **Fix Application**: 70 minutes
- **Validation**: 10 minutes
- **Reporting**: 5 minutes
- **Total Estimate**: 95 minutes (1h 35m)
- **Target Completion**: 2026-07-16T04:47:00Z

---

## 📢 EXECUTION NOTES

1. **Parallel execution** — work independently from Lanes 1, 3, 4, 5
2. **Error analysis is critical** — categorization determines fix approach
3. **All artifacts stored in `.codex/`** — never in /tmp
4. **Document every fix** — update AGENT_ACCOUNTABILITY_REPORT.md
5. **Preserve test isolation** — no shared state between tests

---

## 🚨 RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Fix template doesn't work | Try alternative patterns; escalate if needed |
| New errors introduced | Run full test suite after each 5-fix batch |
| Batch not fully resolved | Document complex errors; defer to Batch escalation |
| Timeout during validation | Split batch into sub-batches; parallelize validation |

---

## ✅ HANDOFF CHECKLIST

Before completion, ensure:
- [ ] Error analysis complete (50-60 errors categorized)
- [ ] Fix templates applied to all errors
- [ ] Test suite executes successfully
- [ ] Final error count = 0 (100% resolution)
- [ ] Execution report generated in `.codex/LANE_2_EXECUTION_REPORT_2026_07_16.md`
- [ ] Error reduction metrics captured
- [ ] AGENT_ACCOUNTABILITY_REPORT.md updated
- [ ] All files committed to branch

---

**Prepared by**: Copilot Task Agent  
**Authority**: @mbaetiong D-tier autonomous  
**Status**: READY FOR EXECUTION
