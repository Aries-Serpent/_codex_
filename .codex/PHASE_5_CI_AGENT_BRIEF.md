# Phase 5: CI Pattern Implementation Agent Brief

**Agent:** `ci-auto-healer-agent`  
**Campaign:** Phase 5 CI Pattern Enhancement (RP-031/032/033)  
**Date:** 2026-06-25T23:56:00Z  
**Authority:** CAD-Mandate Phase 5 CI Stream  
**Status:** ✅ READY FOR DELEGATION

---

## 📋 Executive Summary

Implement 3 new CI auto-fix patterns to achieve **37.5% → 40%+ auto-fix coverage** in Phase 5.

**Target Auto-Fix Coverage:** +2.5pp (from 37.5% to 40%+)  
**Primary Focus:** Assert messages, async timeouts, mock cleanup  
**Timeline:** 2026-06-26 through 2026-07-16 (3 weeks)  
**Effort Estimate:** 25 hours

---

## 🎯 Primary Objectives

### Implement 3 New CI Auto-Fix Patterns

#### Pattern 1: RP-031 — Assert Messages Without Context (8 hours)

**Problem:**
- Assertions without descriptive messages make debugging difficult
- Example: `assert len(result) >= 0` (always true, useless)
- Current Occurrences: 216 across test suite
- Auto-Fix Rate: 75% automatically fixable

**Detection Logic:**
```python
# Pattern to detect:
assert <simple_condition>  # without message or message is trivial

# Examples:
assert response
assert len(data) > 0
assert value is not None
```

**Auto-Fix Strategy:**
1. Extract surrounding context (variable names, function purpose)
2. Generate descriptive message from context
3. Inject message: `assert <condition>, "Descriptive message"`

**Manual Review Cases (54 edge cases):**
- Complex assertions requiring human judgment
- Assertions with conditional logic requiring context
- Legacy assertions that should be removed entirely

**Implementation Approach:**
1. Pattern detection in `scripts/ci/auto_fix_common_issues.py`
2. Add validator class: `AssertMessageValidator`
3. Add fixer class: `AssertMessageFixer`
4. Create test suite in `tests/ci/test_rp031_assert_messages.py`

**Expected Coverage Gain:** +0.5pp

---

#### Pattern 2: RP-032 — Async Tests Without Timeout ⭐ (6 hours)

**Problem:**
- Async tests can hang indefinitely without timeouts
- CI jobs get stuck, blocking all downstream tasks
- Common source of flaky CI behavior
- Current Occurrences: 72 across test suite
- Auto-Fix Rate: 90% automatically fixable

**Detection Logic:**
```python
# Pattern to detect:
@pytest.mark.asyncio
async def test_something():
    # No timeout configured

# Should be:
@pytest.mark.asyncio
@pytest.mark.timeout(30)  # or use pytest-asyncio fixture
async def test_something():
```

**Auto-Fix Strategy:**
1. Detect `@pytest.mark.asyncio` decorated functions
2. Check for timeout decorator or fixture
3. If missing, inject: `@pytest.mark.timeout(30)` (default 30s)
4. For pytest-asyncio: use fixture injection

**Manual Review Cases (7 edge cases):**
- Tests with intentionally long waits (network, DB operations)
- Tests requiring custom timeout values
- Tests using alternative async frameworks

**Implementation Approach:**
1. Pattern detection in `scripts/ci/auto_fix_common_issues.py`
2. Add validator class: `AsyncTimeoutValidator`
3. Add fixer class: `AsyncTimeoutFixer`
4. Create test suite in `tests/ci/test_rp032_async_timeout.py`

**Expected Coverage Gain:** +0.2pp

---

#### Pattern 3: RP-033 — Mock Object Cleanup Missing ⭐ (11 hours)

**Problem:**
- Mock objects not cleaned up cause test flakiness
- State leaks between tests
- Mock side effects persist across test runs
- Current Occurrences: 293 across test suite
- Auto-Fix Rate: 65% automatically fixable

**Detection Logic:**
```python
# Pattern to detect:
def test_something():
    mock_obj = Mock()
    # ... test code ...
    # Missing: mock_obj.reset_mock() or mock_obj.cleanup()

# Should be:
def test_something():
    mock_obj = Mock()
    try:
        # ... test code ...
    finally:
        mock_obj.reset_mock()
```

**Auto-Fix Strategy:**
1. Detect `Mock()` object creation
2. Check if cleanup called in test
3. If missing, inject cleanup in:
   - Explicit teardown method
   - Finally block
   - Pytest fixture cleanup

**Manual Review Cases (103 edge cases):**
- Mocks requiring custom cleanup logic
- Shared fixtures with multiple mocks
- Mocks with side effects requiring selective reset
- Context managers handling cleanup

**Implementation Approach:**
1. Pattern detection in `scripts/ci/auto_fix_common_issues.py`
2. Add validator class: `MockCleanupValidator`
3. Add fixer class: `MockCleanupFixer`
4. Create test suite in `tests/ci/test_rp033_mock_cleanup.py`

**Expected Coverage Gain:** +0.66pp

---

## 📊 Current State (From Phase 4)

**Auto-Fix Coverage Baseline:** 37.5% (confirmed)  
**Total Active Patterns:** 30 (RP-001 through RP-030)  
**Auto-Fixable Patterns:** 23 of 30 (76.7%)

**Phase 5 Coverage Projection:**
- Start: 37.5% (30 patterns active)
- After RP-031: 38.0% (Week 1-2)
- After RP-032: 38.2% (Week 2)
- After RP-033: 38.9% (Week 3)
- **Target: 40%+ achievable in 25 hours**

---

## 🔧 Implementation Strategy

### Phase 1: Pattern Design (Days 1-2)

1. **RP-031 Design:**
   - Finalize detection regex/AST patterns
   - Design message generation algorithm
   - Create test vectors (20+ test cases)

2. **RP-032 Design:**
   - Finalize async test detection patterns
   - Determine default timeout values (30s standard)
   - Design pytest fixture integration

3. **RP-033 Design:**
   - Finalize mock object detection patterns
   - Design cleanup injection locations (teardown, finally, fixtures)
   - Map mock types and cleanup methods

### Phase 2: Implementation (Days 3-14)

**All patterns integrated into:** `scripts/ci/auto_fix_common_issues.py`

1. **Add validator classes:**
   ```python
   class AssertMessageValidator(PatternValidator):
       """Detect assertions without messages"""
       pattern_id = "RP-031"
   
   class AsyncTimeoutValidator(PatternValidator):
       """Detect async tests without timeouts"""
       pattern_id = "RP-032"
   
   class MockCleanupValidator(PatternValidator):
       """Detect mock objects without cleanup"""
       pattern_id = "RP-033"
   ```

2. **Add fixer classes:**
   ```python
   class AssertMessageFixer(PatternFixer):
       """Fix assertions by adding messages"""
   
   class AsyncTimeoutFixer(PatternFixer):
       """Fix async tests by adding timeout decorators"""
   
   class MockCleanupFixer(PatternFixer):
       """Fix mock objects by adding cleanup"""
   ```

3. **Integration points:**
   - Add to `PATTERN_REGISTRY` in auto_fix_common_issues.py
   - Add to `--check-only` scan output
   - Add to `--fix` execution flow
   - Add to `--json-output` reporting

### Phase 3: Testing & Hardening (Days 15-21)

1. **Test coverage:**
   - 100+ test cases per pattern (detection + fixing)
   - Edge case handling
   - False positive prevention
   - Regression testing against existing patterns

2. **Integration testing:**
   - Run full `auto_fix_common_issues.py` test suite
   - Verify no conflicts with existing patterns
   - Test all 3 patterns together
   - Validate fix application order

3. **CI pipeline integration:**
   - Update `.github/workflows/auto-fix-pr-check.yml`
   - Enable new patterns in PR checks
   - Create diagnostic reports with new patterns
   - Document expected output format

---

## ✅ Success Criteria

### Pattern Implementation
- ✅ RP-031 (Assert Messages): Fully implemented and tested
- ✅ RP-032 (Async Timeout): Fully implemented and tested
- ✅ RP-033 (Mock Cleanup): Fully implemented and tested

### Detection & Fixing
- ✅ RP-031: Detects all 216 cases, fixes 75% (162 auto-fixed)
- ✅ RP-032: Detects all 72 cases, fixes 90% (65 auto-fixed)
- ✅ RP-033: Detects all 293 cases, fixes 65% (190 auto-fixed)
- ✅ **Total: 581 cases, 77% auto-fixed (447 automatic fixes)**

### Coverage Metrics
- ✅ **Auto-fix coverage: 37.5% → 38.9%+** (minimum +1.36pp)
- ✅ **Current issues: 5 existing → 0 (all auto-fixed)**
- ✅ **Pattern inventory: 30 → 33 patterns**
- ✅ **Auto-fixable rate: 76.7% → 78%+ (overall)**

### Code Quality
- ✅ All pattern classes follow existing architecture
- ✅ All validators inherit from `PatternValidator`
- ✅ All fixers inherit from `PatternFixer`
- ✅ Full docstrings on all new classes
- ✅ Type hints on all public methods
- ✅ No regressions in existing patterns

### Documentation
- ✅ Pattern documentation: `.codex/PHASE_5_CI_PATTERNS.md`
- ✅ Implementation guide: `.codex/PHASE_5_CI_IMPLEMENTATION.md`
- ✅ Test vectors: 100+ test cases per pattern
- ✅ Code examples: Real-world examples from codebase

### Deliverables
- ✅ Updated `scripts/ci/auto_fix_common_issues.py` (3 new patterns)
- ✅ Test suite: `tests/ci/test_rp031_*.py`, `test_rp032_*.py`, `test_rp033_*.py`
- ✅ Pattern documentation: `.codex/PHASE_5_CI_PATTERNS.md`
- ✅ Weekly checkpoints: `.codex/PHASE_5_WEEK{1,2,3}_CHECKPOINT.md`
- ✅ Final validation: `.codex/PHASE_5_CI_VALIDATION.md`

---

## 🔄 Weekly Checkpoint Schedule

**Week 1 (Jun 26 - Jul 02):**
- RP-031 design complete
- RP-031 validator + fixer implemented
- Initial RP-032 design
- Target: 8 hours effort
- Checkpoint: `.codex/PHASE_5_WEEK1_CHECKPOINT.md`

**Week 2 (Jul 03 - Jul 09):**
- RP-032 implementation complete
- RP-033 design complete
- Initial RP-033 implementation
- Testing for RP-031 and RP-032
- Target: 6 hours effort
- Checkpoint: `.codex/PHASE_5_WEEK2_CHECKPOINT.md`

**Week 3 (Jul 10 - Jul 16):**
- RP-033 implementation complete
- Full test suite for all 3 patterns
- Pipeline integration
- Documentation finalization
- Target: 11 hours effort
- Checkpoint: `.codex/PHASE_5_WEEK3_CHECKPOINT.md`

---

## 📁 Artifact Locations

**All artifacts stored in repository-tracked `.codex/` directory:**
- `.codex/PHASE_5_CI_PATTERNS.md` — Pattern documentation
- `.codex/PHASE_5_CI_IMPLEMENTATION.md` — Implementation details
- `.codex/PHASE_5_CI_VALIDATION.md` — Final validation report
- `.codex/PHASE_5_WEEK1_CHECKPOINT.md` — Week 1 progress
- `.codex/PHASE_5_WEEK2_CHECKPOINT.md` — Week 2 progress
- `.codex/PHASE_5_WEEK3_CHECKPOINT.md` — Week 3 progress

**Code locations:**
- Pattern implementation: `scripts/ci/auto_fix_common_issues.py`
- Test files: `tests/ci/test_rp031_*.py`, `test_rp032_*.py`, `test_rp033_*.py`

---

## 🎯 Known Constraints & Resources

### Constraints
- Must integrate with existing `auto_fix_common_issues.py` architecture
- Must not break existing 30 patterns (regression prevention)
- Must follow existing code style and conventions
- Must support both `--check-only` and `--fix` modes

### Available Resources
- Existing pattern implementations: `scripts/ci/auto_fix_common_issues.py`
- Test patterns: `tests/ci/` existing test suite
- Pattern registry: Look at RP-001 through RP-030 for reference

### Key Architecture Points
- `PatternValidator` base class: Validates against pattern
- `PatternFixer` base class: Applies automatic fixes
- `PATTERN_REGISTRY`: Central registry of all patterns
- JSON output: Used by Copilot agent for diagnostic reports

---

## 📞 Escalation & Blockers

**Blocker Escalation:** If any of these issues arise:
- Cannot integrate with existing pattern architecture
- New patterns conflict with existing patterns
- Testing coverage cannot reach 95%+ pass rate
- Pattern detection has >10% false positives

→ Escalate to @mbaetiong with detailed context and analysis

**Authority Level:** Full autonomy (D) to make implementation decisions

---

## 📝 Phase 4 Reference

From Phase 4 CI Pattern Enhancement:
- 30 total patterns identified and categorized
- 76.7% auto-fixable rate confirmed
- RP-031, RP-032, RP-033 identified as high-ROI patterns
- Total 25-hour effort estimate for Phase 5 implementation

---

**Brief Created:** 2026-06-25T23:56:00Z  
**Status:** ✅ READY FOR AGENT EXECUTION  
**Next Step:** Launch ci-auto-healer-agent with this brief
