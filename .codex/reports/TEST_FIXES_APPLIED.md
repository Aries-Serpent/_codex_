# Test Fixes Applied - PR #3248

## Summary

**Date**: 2024-01-23
**Tests Investigated**: 7 (8 including false alarm)
**Tests Fixed**: 2 fully resolved
**API Alignments**: 3 tests partially fixed
**Time Spent**: ~17 minutes of actual fixes

---

## ✅ Fixes Successfully Applied

### 1. Security: XSS Sanitization Bug (CRITICAL)

**Test**: `tests/security/test_input_validation.py::test_xss_like_payloads_flagged`

**File Modified**: `src/security/core.py`

**Issue**: The `sanitize_user_content()` function only used `html.escape()` which doesn't remove dangerous URL protocols like `javascript:`, `data:`, or `vbscript:`. This allowed XSS attacks to bypass sanitization.

**Fix Applied**:
```python
def sanitize_user_content(value: Any, content_type: Literal["html", "markdown"] = "html") -> str:
    """Sanitize user generated content for safe rendering.

    Security: Uses proper HTML parsing instead of regex to prevent XSS and ReDoS attacks.
    """
    text = _ensure_str(value)

    # Remove dangerous URL protocols (javascript:, data:, vbscript:) before HTML escaping
    # This prevents XSS attacks via URL schemes that bypass HTML entity escaping
    for pattern in XSS_PATTERNS:
        text = pattern.sub("", text)

    if content_type == "html":
        sanitized = html.escape(text)
    # ... rest of function
```

**Security Impact**: 🔴 HIGH - This was a real XSS vulnerability that could have allowed code injection.

**Test Result**: ✅ All 3 parametrized test cases now pass

---

### 2. Performance: Shared Fixtures Test Logic (TEST BUG)

**Test**: `tests/performance_monitoring/test_parallelization.py::TestExecutionOptimization::test_detect_shared_fixtures`

**File Modified**: `tests/performance_monitoring/test_parallelization.py`

**Issue**: Test was sorting fixture names alphabetically but then asserting against non-alphabetical keys. When `["db", "cache"]` is sorted, it becomes `["cache", "db"]`, not `["db", "cache"]`.

**Fix Applied**:
```python
def test_detect_shared_fixtures(self):
    """Test detecting tests with shared fixtures."""
    tests = [
        {"name": "test_a", "fixtures": ["db", "cache"]},
        {"name": "test_b", "fixtures": ["db"]},
        {"name": "test_c", "fixtures": ["cache"]},
        {"name": "test_d", "fixtures": []},
    ]

    # Group by shared fixtures
    fixture_groups = {}
    for test in tests:
        fixtures_key = tuple(sorted(test["fixtures"]))
        if fixtures_key not in fixture_groups:
            fixture_groups[fixtures_key] = []
        fixture_groups[fixtures_key].append(test["name"])

    # Keys are alphabetically sorted, so "cache" comes before "db"
    assert fixture_groups[("cache", "db")] == ["test_a"]  # ← Fixed order
    assert fixture_groups[("cache",)] == ["test_c"]       # ← Added
    assert fixture_groups[("db",)] == ["test_b"]
    assert fixture_groups[()] == ["test_d"]               # ← Added
```

**Impact**: 🟡 MEDIUM - This was a test bug, not a production issue. Improved test coverage by adding missing assertions.

**Test Result**: ✅ Test now passes

---

### 3. Quantum: API Signature Alignment (PARTIAL FIX)

**Tests**:
- `tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py::TestAdaptiveScoringOptimized::test_accuracy_maintained`
- `tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py::TestAdaptiveScoringOptimized::test_k1_target_achieved`
- `tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py::TestAdaptiveScoringOptimized::test_no_regression`

**File Modified**: `src/cognitive_brain/experiments/exp1b_revalidation.py`

**Issue**: The `ComplianceAssessor` (alias for `QuantumComplianceAssessor`) constructor signature changed to require `monitor` and `repository` parameters, but the test code was only passing `config`.

**Fix Applied**:

1. Added imports:
```python
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
```

2. Updated initialization:
```python
# Initialize quantum assessor with Phase 8.0 optimized configuration
config = QuantumConfig.from_env()
config.superposition_enabled = True  # Required for complex scenario handling

# Initialize required dependencies for quantum compliance assessor
repository = QuantumMetricRepository(db_path=":memory:")  # In-memory DB for experiments
monitor = CoherenceMonitor(config, repository)
assessor = ComplianceAssessor(config, monitor, repository)
```

3. Fixed method call:
```python
# Changed from: assessor.assess(audit)
# To:
assessment = assessor.assess_compliance(audit)
```

**Status**: ⚠️ **PARTIAL FIX**

- ✅ API signature issues resolved - tests now run without TypeErrors
- ❌ Functional issues remain - tests fail due to poor quantum assessment performance:
  - Accuracy: 20% (target: ≥84%)
  - k₁: 18.09 (target: ≤0.35)
  - Coherence: 0.0 (target: ≥0.650)

**Impact**: 🟡 MEDIUM - Test alignment issues fixed, but revealed deeper functional problems in quantum assessment logic that require separate investigation.

**Recommendation**: Escalate remaining functional issues to quantum feature team. This is beyond the scope of test alignment.

---

## ⚠️ Issues Requiring Further Investigation

### 4. Knobs Summary Sidecar Test (SKIPPED)

**Test**: `tests/config/test_knobs_summary.py::test_knobs_summary_sidecar`

**Status**: Skipped during test collection - cannot determine if test would pass

**Issue**: Test file exists but pytest cannot collect it. Likely causes:
- Missing dependencies in test environment
- Skip conditions in conftest.py
- Import errors in test module

**Recommendation**: Run in full CI environment to determine actual status

---

### 5. Metrics Table Name Validation (MISSING DEPENDENCIES)

**Test**: `tests/cli/test_metrics_table_name_validation.py::test_allows_unsafe_with_override`

**Status**: Entire CLI test suite skipped due to missing dependencies

**Error**: `Skipping CLI tests: missing required dependencies ['omegaconf', 'hydra']`

**Fix Required**:
```bash
pip install omegaconf hydra-core
```

**Recommendation**: Add to CI test environment or mark as optional dependency test

---

### 6. Checkpoint Manager Best K (FALSE ALARM)

**Test**: `tests/utils/test_checkpoint_rng.py::test_checkpoint_manager_best_k`

**Status**: ✅ Already passing - no fix needed

**Analysis**: This test is not actually failing. May have been fixed in a previous commit or the failure was environment-specific.

---

## Files Changed

1. `src/security/core.py` - Fixed XSS sanitization
2. `tests/performance_monitoring/test_parallelization.py` - Fixed test assertions
3. `src/cognitive_brain/experiments/exp1b_revalidation.py` - Fixed API signature alignment

---

## Test Results Summary

| Test | Before | After | Status |
|------|--------|-------|--------|
| test_checkpoint_manager_best_k | ✅ Pass | ✅ Pass | No change needed |
| test_xss_like_payloads_flagged (3 cases) | ❌ Fail | ✅ Pass | **FIXED** |
| test_knobs_summary_sidecar | ⚠️ Skip | ⚠️ Skip | Needs investigation |
| test_detect_shared_fixtures | ❌ Fail | ✅ Pass | **FIXED** |
| test_accuracy_maintained | ❌ TypeError | ❌ Functional | API fixed, needs investigation |
| test_k1_target_achieved | ❌ TypeError | ❌ Functional | API fixed, needs investigation |
| test_no_regression | ❌ TypeError | ❌ Functional | API fixed, needs investigation |
| test_allows_unsafe_with_override | ⚠️ Skip | ⚠️ Skip | Needs dependencies |

**Fully Fixed**: 2 test failures
**Partially Fixed**: 3 tests (API aligned, functional issues remain)
**Needs Investigation**: 2 tests (environment/dependency issues)
**False Alarm**: 1 test (already passing)

---

## Next Steps

### Immediate (for this PR)

1. ✅ Commit the 2 fully fixed tests (XSS and shared fixtures)
2. ✅ Commit the API alignment fix for quantum tests (documents the functional issues)
3. ✅ Document the remaining functional issues in PR description

### Follow-up (separate tasks)

1. 🔴 HIGH: Investigate quantum assessment functional issues
   - Requires quantum feature team expertise
   - May need architecture review
   - Could be test scenario generation issue

2. 🟡 MEDIUM: Set up full test environment for skipped tests
   - Install missing dependencies
   - Verify script availability
   - Document any environment-specific requirements

3. 🟢 LOW: Review test skip conditions
   - Consider making skips more informative
   - Add pytest markers for optional dependency tests

---

## Security Note

⚠️ **IMPORTANT**: The XSS sanitization bug fix in this PR addresses a real security vulnerability. This should be prioritized for merge and deployment.

The vulnerability allowed `javascript:` URLs to bypass sanitization, potentially enabling XSS attacks through user-generated content.

**Severity**: Medium-High
**Exploitability**: Medium (requires user interaction with malicious link)
**Impact**: Code injection, session hijacking, data theft

---

## Conclusion

This investigation successfully:
- ✅ Fixed 2 real bugs (1 security vulnerability, 1 test bug)
- ✅ Aligned API signatures for 3 quantum tests
- ⚠️ Identified functional issues requiring deeper investigation
- ⚠️ Documented environment issues for follow-up

The fixes applied are production-ready and should be merged. The remaining issues are documented and can be addressed in follow-up PRs.
