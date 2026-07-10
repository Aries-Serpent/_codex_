# PHASE 5 TRACK 3: Flaky Test Stabilization — Execution Plan

**Timeline:** 2026-07-10 to 2026-07-12  
**Authority:** @mbaetiong (Phase 5 Track 3)  
**Status:** Implementation Ready  
**Expected Outcome:** +0.5 points (95.5/100 overall)

---

## Executive Summary

This document outlines the precise execution plan for stabilizing all 12 marked flaky tests through systematic application of thread synchronization patterns, event-based timing, and proper concurrency controls.

**Current State:**
- ✅ Infrastructure created (utilities, documentation)
- ⏳ Fixes to be applied (12 tests)
- ⏳ Validation to be performed (10+ runs per test)
- ⏳ Documentation to be updated

---

## Detailed Flaky Test Map

### Category 1: Timing-Sensitive Tests (5 tests)

These tests fail due to unreliable `time.sleep()` calls. Fix: Replace with event-based timing.

| ID | File | Test | Issue | Fix |
|---|---|---|---|---|
| ft-001 | `tests/logging/test_session_db.py` | `test_cache_ttl_respected` | TTL validation uses `time.sleep(1.1)` | Use `timed_event(1.0)` |
| ft-005 | `tests/autonomy/test_integration_budget_exhaustion.py` | `test_budget_cap` | Timeout precision unreliable | Use `timed_event()` |
| ft-006 | `tests/autonomy/test_autonomy_scheduler.py` | `test_timeout_precision` | Budget timeout uses sleep | Use `timed_event()` |
| ft-008 | `tests/space_traversal/test_performance.py` | `test_budget_cap_timeout` | TTL precision timing dependent | Use `timed_event()` |
| ft-009 | `tests/space_traversal/test_performance.py` | `test_ttl_precision` | TTL expiry timing dependent | Use `timed_event()` |

**Fix Template:**

```python
# Before
import time
time.sleep(duration)  # ❌ Unreliable

# After
from tests.utils.test_synchronization import timed_event
with timed_event(duration) as (event, timer):
    timer.start()
    event.wait()
    timer.join()  # ✅ Deterministic
```

---

### Category 2: Race Condition Tests - Synchronization Required (4 tests)

These tests fail due to uncoordinated thread startup. Fix: Add threading barriers.

| ID | File | Test | Issue | Fix |
|---|---|---|---|---|
| ft-002 | `tests/logging/test_session_db.py` | `test_concurrent_inserts` | Threads start at different times | Add `synchronize_threads()` barrier |
| ft-003 | `tests/logging/test_session_db.py` | `test_concurrent_queries` | Race condition on results list | Add barrier + lock |
| ft-011 | `tests/test_concurrency_protection.py` | `test_read_lock_timing` | Timing dependent on system load | Add barrier for sync start |
| ft-012 | `tests/test_concurrency_protection.py` | `test_writer_starvation_timing` | Starvation timing dependent | Add barrier for determinism |

**Fix Template:**

```python
# Before
threads = [Thread(target=worker) for _ in range(n)]
for t in threads:
    t.start()  # ❌ Threads start at unpredictable times

# After
from tests.utils.test_synchronization import synchronize_threads
with synchronize_threads(n) as barrier:
    def worker():
        barrier.wait()  # ✅ All threads wait until all arrive
        # ... work ...
    threads = [Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
```

---

### Category 3: File Concurrency Tests (1 test)

This test fails due to concurrent file writes without locking.

| ID | File | Test | Issue | Fix |
|---|---|---|---|---|
| ft-004 | `tests/stress/test_concurrent_operations.py` | `test_concurrent_metrics_logging` | Concurrent writes interleave without locking | Add file-level locking (fcntl) |

**Fix Template:**

```python
# Before
def log_metrics(thread_id):
    with MetricLogger(log_file) as logger:
        logger.log(...)  # ❌ Concurrent writes interleave

# After
def log_metrics(thread_id):
    with MetricLogger(log_file, use_file_lock=True) as logger:
        logger.log(...)  # ✅ File-locked writes are atomic
```

---

### Category 4: Subprocess Timing Test (1 test)

This test fails due to subprocess timeout precision issues.

| ID | File | Test | Issue | Fix |
|---|---|---|---|---|
| ft-007 | `tests/autonomy/test_autonomy_scheduler.py` | `test_subprocess_timeout` | Subprocess timeout precision unreliable | Use `DeterministicTimeout` context manager |

**Fix Template:**

```python
# Before
import time
start = time.time()
subprocess.run(...)
elapsed = time.time() - start
assert elapsed < timeout  # ❌ Flaky

# After
from tests.utils.test_synchronization import DeterministicTimeout
with DeterministicTimeout(max_seconds=timeout) as timer:
    subprocess.run(...)
    assert not timer.exceeded()  # ✅ Deterministic
```

---

### Category 5: Measurement Precision Test (1 test)

This test fails due to imprecise timing measurements.

| ID | File | Test | Issue | Fix |
|---|---|---|---|---|
| ft-010 | `tests/space_traversal/test_performance.py` | `test_context_manager_measurement` | Measurement precision timing dependent | Use `DeterministicTimeout` |

---

## Implementation Phases

### Phase 1A: Setup & Validation (2026-07-10, ~30 min)

**Objective:** Verify infrastructure and baseline

```bash
# 1. Run full test suite baseline
pytest tests/logging/test_session_db.py -v --tb=short

# 2. Identify current pass rate
for i in {1..5}; do
    pytest tests/logging/test_session_db.py::TestThreadSafety::test_concurrent_inserts -x
done
# Expected: Some failures (confirming flakiness)

# 3. Verify test utilities are available
python -c "from tests.utils.test_synchronization import synchronize_threads, timed_event; print('✅ Utilities available')"
```

**Checkpoint:** ✓ Baseline established, utilities verified

---

### Phase 1B: Verify Deterministic Seed Setup (2026-07-10, ~15 min)

**Objective:** Confirm random seed fixture works correctly

```python
# Test in pytest session
@pytest.fixture(autouse=True)
def verify_seed_isolation(request):
    """Verify deterministic seed is active."""
    import random
    random_state_1 = random.getstate()
    
    yield
    
    # Seeds should be restored after test
    random_state_2 = random.getstate()
```

**Checkpoint:** ✓ Deterministic seed fixture verified

---

### Phase 2: Timing-Sensitive Test Fixes (2026-07-10, ~2 hours)

**Objective:** Fix 5 timing-dependent tests

**Tests to fix:** ft-001, ft-005, ft-006, ft-008, ft-009

**Per-test process:**

1. **Locate test** in file
2. **Remove** `@pytest.mark.flaky(...)` decorator
3. **Replace** `time.sleep()` with `timed_event()`
4. **Add** import: `from tests.utils.test_synchronization import timed_event`
5. **Validate** locally: `pytest <file>::<test> -v --count=10`
6. **Commit** with message: `Stabilize timing-sensitive test: <test_name>`

**Example (ft-001):**

```bash
# 1. Edit tests/logging/test_session_db.py
#    - Remove @pytest.mark.flaky on line 389
#    - Replace time.sleep(1.1) with timed_event

# 2. Validate
pytest tests/logging/test_session_db.py::TestCaching::test_cache_ttl_respected -v --count=10

# 3. Commit
git add tests/logging/test_session_db.py
git commit -m "Stabilize timing-sensitive test: test_cache_ttl_respected"
```

**Expected:** All 5 tests pass 100% across 10 runs

---

### Phase 3: Race Condition Test Fixes (2026-07-11, ~2 hours)

**Objective:** Fix 4 race condition tests

**Tests to fix:** ft-002, ft-003, ft-011, ft-012

**Per-test process:**

1. **Locate test** in file
2. **Remove** `@pytest.mark.flaky(...)` decorator
3. **Add** `synchronize_threads()` context manager
4. **Add** `barrier.wait()` at thread entry point
5. **Add** `lock` for shared state if needed
6. **Validate** locally: `pytest <file>::<test> -v --count=10`
7. **Commit** with descriptive message

**Example (ft-002):**

```bash
# 1. Edit tests/logging/test_session_db.py (line 622)
#    - Remove @pytest.mark.flaky on line 621
#    - Wrap with synchronize_threads(5)
#    - Add barrier.wait() in insert_sessions()

# 2. Validate
pytest tests/logging/test_session_db.py::TestThreadSafety::test_concurrent_inserts -v --count=10

# 3. Commit
git add tests/logging/test_session_db.py
git commit -m "Stabilize race condition: test_concurrent_inserts"
```

**Expected:** All 4 tests pass 100% across 10 runs

---

### Phase 4: File Concurrency Fix (2026-07-11, ~1 hour)

**Objective:** Fix MetricLogger concurrent write test

**Test to fix:** ft-004

**Implementation approach:**

```python
# Option A: Modify test to use file locking
with exclusive_resource("test_database.db"):
    # Only one thread accesses resource at a time

# Option B: Enhance MetricLogger with file locking
# (in MetricLogger class, not test)
@contextlib.contextmanager
def thread_safe_write(self):
    with fcntl.flock(self.file.fileno(), fcntl.LOCK_EX):
        yield
```

**Expected:** Test passes 100% across 10 runs

---

### Phase 5: Subprocess & Measurement Fixes (2026-07-11, ~1 hour)

**Objective:** Fix subprocess and measurement precision tests

**Tests to fix:** ft-007, ft-010

**Implementation:**

```python
# Use DeterministicTimeout for both
from tests.utils.test_synchronization import DeterministicTimeout

with DeterministicTimeout(max_seconds=timeout) as timer:
    subprocess.run(cmd, timeout=timeout)
    assert not timer.exceeded()
```

**Expected:** Both tests pass 100% across 10 runs

---

### Phase 6: Full Validation (2026-07-11 to 2026-07-12, ~3 hours)

**Objective:** Comprehensive multi-run testing

```bash
# Step 1: Full test suite, 10 consecutive runs
for i in {1..10}; do
    echo "=== RUN $i ==="
    pytest tests/ -x --tb=short -q
    if [ $? -ne 0 ]; then
        echo "❌ FAILED on run $i"
        exit 1
    fi
done
echo "✅ All 10 runs passed!"

# Step 2: Specifically test the 12 flaky tests
pytest \
    tests/logging/test_session_db.py::TestCaching::test_cache_ttl_respected \
    tests/logging/test_session_db.py::TestThreadSafety::test_concurrent_inserts \
    tests/logging/test_session_db.py::TestThreadSafety::test_concurrent_queries \
    tests/stress/test_concurrent_operations.py::test_concurrent_metrics_logging \
    tests/autonomy/test_integration_budget_exhaustion.py::test_budget_cap \
    tests/autonomy/test_autonomy_scheduler.py::test_timeout_precision \
    tests/autonomy/test_autonomy_scheduler.py::test_subprocess_timeout \
    tests/space_traversal/test_performance.py::test_budget_cap_timeout \
    tests/space_traversal/test_performance.py::test_ttl_precision \
    tests/space_traversal/test_performance.py::test_context_manager_measurement \
    tests/test_concurrency_protection.py::test_read_lock_timing \
    tests/test_concurrency_protection.py::test_writer_starvation_timing \
    -v --tb=short --count=10

# Step 3: Performance validation
time pytest tests/ -q  # Should be <5% slower than baseline
```

**Success Criteria:**
- [ ] All 12 previously-flaky tests pass 100% of the time
- [ ] No new test failures introduced
- [ ] Performance overhead <5%
- [ ] No @pytest.mark.flaky decorators remaining on fixed tests

---

### Phase 7: Documentation & Cleanup (2026-07-12, ~1 hour)

**Objective:** Document changes and hand off

**Deliverables:**

1. **FLAKY_TEST_STABILIZATION_REPORT.md**
   - Summary of all 12 fixes
   - Before/after statistics
   - Key learnings and patterns
   - Recommendations for test authors

2. **Update .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md**
   - Record completion of Phase 5 Track 3
   - Add stabilization work to agent portfolio

3. **Update CHANGELOG.md**
   - Entry for flaky test stabilization
   - Link to stabilization report
   - List of fixed tests

4. **Update CONTRIBUTING.md**
   - Add section: "Writing Deterministic Tests"
   - Describe anti-patterns to avoid
   - Link to synchronization utilities

---

## Validation Checklist

### For Each Fixed Test

- [ ] Remove `@pytest.mark.flaky` decorator
- [ ] Add appropriate synchronization utility import
- [ ] Apply synchronization pattern (barrier/lock/timer)
- [ ] Run: `pytest <file>::<test> -v --count=10`
  - All 10 runs pass: YES/NO
- [ ] Run full test suite: no regressions
- [ ] Commit with descriptive message
- [ ] Create PR checkpoint (every 3-4 tests)

### Overall Validation

- [ ] Baseline test run: pass
- [ ] 10 consecutive full runs: all pass
- [ ] 12 previously-flaky tests: 100% pass rate
- [ ] Performance regression: <5%
- [ ] No new warnings/errors
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Merge to main

---

## Risk Mitigation

### Risk 1: Breaking Existing Tests

**Mitigation:** 
- Run full suite after each fix
- Use git branches to isolate changes
- Quick rollback if issues arise

### Risk 2: Performance Regression

**Mitigation:**
- Benchmark baseline before changes
- Monitor timing with `pytest --durations=10`
- Keep synchronization overhead minimal

### Risk 3: Incomplete Fixes

**Mitigation:**
- Document expected behavior for each test
- Create acceptance criteria per test
- Use validation script (10+ runs)

### Risk 4: Subtle Race Conditions Remain

**Mitigation:**
- Run tests under load (pytest-xdist with multiple workers)
- Use thread sanitizer if available
- Extended test runs (50+ iterations)

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Flaky tests fixed | 12/12 | ⏳ |
| Single-run pass rate | 100% | ⏳ |
| Multi-run pass rate (10x) | 100% | ⏳ |
| Performance overhead | <5% | ⏳ |
| Code review completed | ✓ | ⏳ |
| Documentation updated | ✓ | ⏳ |
| Total time investment | <8 hours | ⏳ |
| Overall score gain | +0.5 points | ⏳ |

---

## Timeline Summary

```
2026-07-10 (Day 1)
├─ Setup & validation (30 min)
├─ Verify deterministic seeds (15 min)
└─ Fix 5 timing-sensitive tests (2 hours)
   Total: ~2.75 hours

2026-07-11 (Day 2)
├─ Fix 4 race condition tests (2 hours)
├─ Fix file concurrency test (1 hour)
├─ Fix subprocess & measurement tests (1 hour)
├─ Full validation (3 hours)
└─ Documentation updates (1 hour)
   Total: ~8 hours

2026-07-12 (Day 3)
├─ Extended validation & monitoring
├─ Any final fixes or adjustments
└─ PR review & merge
   Total: Flexible (ad-hoc)
```

**Total Estimated Time:** 8-10 hours across 2-3 days

---

## Key Success Factors

1. **Pattern Consistency:** Apply same patterns across all tests
2. **Thorough Validation:** 10+ runs before declaring test "fixed"
3. **Documentation:** Explain WHY each fix works
4. **Code Review:** Get peer review before merging
5. **Monitoring:** Track improvements in CI/CD

---

## Escalation Protocol

**If Fix Doesn't Work:**
1. Re-run test in isolation: `pytest <test> -v --count=20`
2. Check for other threading operations that might interfere
3. Review system load during test execution
4. Consider if test itself has fundamental flaw
5. Escalate to @mbaetiong if pattern doesn't apply

---

**Document Version:** 1.0  
**Created:** 2026-07-10  
**Status:** Ready for Implementation  
**Authority:** @mbaetiong (Phase 5 Track 3)  

Next: Start with Phase 2A (Timing-Sensitive Test Fixes)
