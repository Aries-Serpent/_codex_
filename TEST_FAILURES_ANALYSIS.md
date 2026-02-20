# Test Failures Analysis for PR #3248

## Summary

Analysis of 7 test failures identified in PR #3248. Tests examined for root cause, whether they represent real bugs or test issues, and specific fix recommendations.

---

## 1. ✅ test_checkpoint_rng.py::test_checkpoint_manager_best_k

**Status**: PASSING (False Alarm)

**Location**: `tests/utils/test_checkpoint_rng.py:28-36`

**Test Details**:
- Tests CheckpointManager's `keep_best` functionality
- Saves 5 checkpoints with losses: [5, 3, 4, 2, 1]
- Expects best.json to contain top 2 (keep_best=2)
- Validates losses are sorted (ascending for lower-is-better)

**Result**: Test currently passes ✓

**Analysis**: This test is not failing. It may have been fixed in a previous commit or the failure was environment-specific.

**Recommendation**: No action needed. Test is working correctly.

---

## 2. ❌ test_input_validation.py::test_xss_like_payloads_flagged

**Status**: FAILING (Real Bug)

**Location**: `tests/security/test_input_validation.py:43-49`

**Test Details**:
```python
@pytest.mark.parametrize("payload", [
    "<script>alert(1)</script>",
    "javascript:alert(1)",  # ← This one fails
    "<img src=x onerror=alert(1)>",
])
def test_xss_like_payloads_flagged(payload):
    sanitize = getattr(core, "sanitize_user_content", None)
    if sanitize is None:
        pytest.skip("sanitize_user_content not found")
    out = sanitize(payload)
    # Expect scripts/handlers removed
    assert not re.search(r"<script|on\\w+\\s*=|javascript:", out, flags=re.IGNORECASE)
```

**Failure**:
```
AssertionError: assert not <re.Match object; span=(0, 11), match='javascript:'>
```

**Root Cause**: 
The `sanitize_user_content()` function in `src/security/core.py` uses `html.escape()` which only escapes HTML entities (`<`, `>`, `&`, `"`, `'`). It does NOT remove dangerous protocols like `javascript:`.

**Current Code** (`src/security/core.py:68-88`):
```python
def sanitize_user_content(value: Any, content_type: Literal["html", "markdown"] = "html") -> str:
    """Sanitize user generated content for safe rendering.
    
    Security: Uses proper HTML parsing instead of regex to prevent XSS and ReDoS attacks.
    """
    text = _ensure_str(value)

    if content_type == "html":
        # Use html.escape for HTML content (safe and efficient)
        sanitized = html.escape(text)  # ← Only escapes entities, doesn't remove javascript:
    elif content_type == "markdown":
        sanitized = html.escape(text)
    else:
        sanitized = text

    from .content_filters import sanitize_text

    return sanitize_text(sanitized)
```

**Bug Type**: Real security bug - XSS protection incomplete

**Fix Recommendation**:
Add explicit removal of dangerous URL protocols before HTML escaping:

```python
def sanitize_user_content(value: Any, content_type: Literal["html", "markdown"] = "html") -> str:
    """Sanitize user generated content for safe rendering.
    
    Security: Uses proper HTML parsing instead of regex to prevent XSS and ReDoS attacks.
    """
    text = _ensure_str(value)
    
    # Remove dangerous URL protocols (javascript:, data:, vbscript:)
    for pattern in XSS_PATTERNS:
        text = pattern.sub("", text)

    if content_type == "html":
        sanitized = html.escape(text)
    elif content_type == "markdown":
        sanitized = html.escape(text)
    else:
        sanitized = text

    from .content_filters import sanitize_text

    return sanitize_text(sanitized)
```

**Impact**: Medium - This is a real XSS vulnerability. Users could inject `javascript:` URLs that bypass sanitization.

---

## 3. ⚠️ test_knobs_summary.py::test_knobs_summary_sidecar

**Status**: SKIPPED (Environment Issue)

**Location**: `tests/config/test_knobs_summary.py:13-31`

**Test Details**:
- Runs `scripts/space_traversal/audit_runner.py` with SUMMARY_ENABLE=1
- Expects `audit_artifacts/knobs_effective.json` to be created
- Tests sidecar file generation for knobs configuration

**Result**: Test is skipped during collection - no actual test was run

**Root Cause**: Test file exists but pytest cannot collect it properly. Likely:
1. Missing dependencies in test environment
2. Import errors in the test module or its dependencies
3. Conftest.py skip conditions

**Analysis**: Cannot determine if this is a real bug without running the test. The test code looks correct.

**Fix Recommendation**:
1. Check if test is marked with skip conditions in conftest
2. Ensure `scripts/space_traversal/audit_runner.py` exists
3. Verify SUMMARY_ENABLE environment variable handling
4. Run test in CI environment with full dependencies

**Impact**: Unknown - need proper test execution to assess

**Note**: This appears to be a P5 (low priority) test based on docstring

---

## 4. ❌ test_parallelization.py::TestExecutionOptimization::test_detect_shared_fixtures

**Status**: FAILING (Test Bug)

**Location**: `tests/performance_monitoring/test_parallelization.py:257-276`

**Test Code**:
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

    assert fixture_groups[("db", "cache")] == ["test_a"]  # ← KeyError
    assert fixture_groups[("db",)] == ["test_b"]
```

**Failure**:
```
KeyError: ('db', 'cache')
```

**Root Cause**: 
The sorting creates `("cache", "db")` not `("db", "cache")`. When fixtures `["db", "cache"]` are sorted, they become `["cache", "db"]` (alphabetical order).

**Bug Type**: Test bug - incorrect assertion expectations

**Fix**:
```python
# Change assertions to use alphabetically sorted keys
assert fixture_groups[("cache", "db")] == ["test_a"]  # Changed order
assert fixture_groups[("db",)] == ["test_b"]
assert fixture_groups[("cache",)] == ["test_c"]  # Add this
assert fixture_groups[()] == ["test_d"]  # Add this
```

**Impact**: Low - This is a unit test for test parallelization logic, not production code. Simple fix.

---

## 5. ❌ test_adaptive_scoring_optimized.py (3 tests)

**Status**: PARTIALLY FIXED - API signature fixed, but functional issues remain

**Location**: `tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py`

**Failing Tests**:
1. `test_accuracy_maintained` (line 128-136)
2. `test_k1_target_achieved` (line 138-148)  
3. `test_no_regression` (line 149-171)

**Original Failure**:
```python
TypeError: QuantumComplianceAssessor.__init__() missing 2 required positional arguments: 'monitor' and 'repository'
```

**Fix Applied** ✅:
Updated `src/cognitive_brain/experiments/exp1b_revalidation.py`:
- Added imports for `CoherenceMonitor` and `QuantumMetricRepository`
- Initialized monitor and repository before creating assessor
- Changed `assessor.assess()` to `assessor.assess_compliance()`

**Current Status**:
API signature issue is **FIXED**, but tests still fail due to **functional problems**:
```
k₁ Process Factor:        18.0947 ❌ (target ≤ 0.35)
Accuracy:                 20.0% ❌ (target ≥ 84%)
Average Coherence:        0.000 ❌ (target ≥ 0.650)
```

**Root Cause of Remaining Failure**:
This is NOT a test alignment issue. The quantum compliance assessor is producing:
- Very low accuracy (20% vs 84% target)
- Extremely high k₁ (18.09 vs 0.35 target)
- Zero coherence (should be ≥0.650)

**Bug Type**: **Production code bug** - quantum assessment logic is broken or not properly initialized

**Impact**: High - Core quantum assessment functionality is not working correctly. This requires:
1. Debugging the quantum assessment decision logic
2. Investigating why coherence is zero
3. Checking if superposition engine is properly enabled
4. Reviewing the scenario generation and ground truth alignment

**Recommendation**: 
This is **beyond test alignment** - requires deep investigation of quantum compliance assessor implementation. Should be escalated to quantum feature team or deferred to separate investigation task.

**Test Alignment Fix Status**: ✅ Complete (API signature fixed)
**Functional Fix Status**: ❌ Requires further investigation

---

## 6. ⚠️ test_metrics_table_name_validation.py::test_allows_unsafe_with_override

**Status**: SKIPPED (Missing Dependencies)

**Location**: `tests/cli/test_metrics_table_name_validation.py:42-65`

**Test Details**:
```python
def test_allows_unsafe_with_override(tmp_path: Path) -> None:
    nd = tmp_path / "m.ndjson"
    nd.write_text('{"epoch":0,"loss":1.0}\n', encoding="utf-8")
    rc, out, err = run_cli([
        "ingest",
        "--input", str(nd),
        "--out-csv", str(tmp_path / "m.csv"),
        "--to-sqlite", str(tmp_path / "m.db"),
        "--table", "ok$name",
        "--allow-unsafe-table-name",  # ← Testing this flag
    ])
    assert rc == 0, f"Expected success with --allow-unsafe-table-name flag"
    payload = json.loads(out)
    assert payload["ok"] is True
```

**Failure**:
```python
Skipped: Skipping CLI tests: missing required dependencies ['omegaconf', 'hydra']
```

**Root Cause**: 
`tests/cli/conftest.py` line 51 skips entire CLI test suite if dependencies are missing.

**Analysis**: 
Cannot verify if test would pass without dependencies installed. This is an environment configuration issue, not a code bug.

**Fix Recommendation**:
1. Install test dependencies: `pip install omegaconf hydra-core`
2. Or mark test with `pytest.mark.skipif` for missing optional dependencies
3. Or use mock/stub for Hydra if testing CLI doesn't require real Hydra

**Impact**: Low - This is a CLI validation test that requires full environment

---

## Summary Table

| Test | Status | Type | Priority | Complexity | Fix Status |
|------|--------|------|----------|------------|------------|
| test_checkpoint_manager_best_k | ✅ Passing | N/A | None | N/A | N/A |
| test_xss_like_payloads_flagged | ✅ FIXED | **Real Bug** | **High** | Low | **✅ Fixed** |
| test_knobs_summary_sidecar | ⚠️ Skipped | Environment | Low | Medium | ⚠️ Needs investigation |
| test_detect_shared_fixtures | ✅ FIXED | Test Bug | Medium | **Very Low** | **✅ Fixed** |
| test_accuracy_maintained | ⚠️ API Fixed | Functional Bug | High | Complex | ⚠️ Needs investigation |
| test_k1_target_achieved | ⚠️ API Fixed | Functional Bug | High | Complex | ⚠️ Needs investigation |
| test_no_regression | ⚠️ API Fixed | Functional Bug | High | Complex | ⚠️ Needs investigation |
| test_allows_unsafe_with_override | ⚠️ Skipped | Environment | Low | Low | ⚠️ Needs dependencies |

---

## Recommendations by Priority

### ✅ COMPLETED - High Priority Fixes

**1. Fixed XSS Sanitization Bug** (`test_xss_like_payloads_flagged`)
- **File**: `src/security/core.py`
- **Function**: `sanitize_user_content()`
- **Change**: Added XSS pattern removal before HTML escaping
- **Status**: ✅ Fixed and verified - all 3 parametrized tests now pass
- **Risk**: Was a real security vulnerability - now resolved

**2. Fixed Shared Fixtures Test** (`test_detect_shared_fixtures`)
- **File**: `tests/performance_monitoring/test_parallelization.py`
- **Lines**: 274-277
- **Change**: Updated assertions to use alphabetically sorted keys and added missing assertions
- **Status**: ✅ Fixed and verified - test now passes

**3. Partially Fixed Quantum Assessor Tests** (3 tests in `test_adaptive_scoring_optimized.py`)
- **File**: `src/cognitive_brain/experiments/exp1b_revalidation.py`
- **Changes Made**:
  - Added imports for `CoherenceMonitor` and `QuantumMetricRepository`
  - Initialized monitor and repository before creating assessor  
  - Fixed method call from `assess()` to `assess_compliance()`
- **Status**: ⚠️ API signature fixed but functional issues remain
- **Remaining Issues**: Tests fail due to poor accuracy (20% vs 84%), high k₁ (18.09 vs 0.35), zero coherence

### 🔴 High Priority (Requires Further Investigation)

**4. Quantum Assessment Functional Issues**
- **Tests Affected**: `test_accuracy_maintained`, `test_k1_target_achieved`, `test_no_regression`
- **Problem**: Core quantum compliance assessment logic produces incorrect results
- **Symptoms**:
  - Accuracy: 20% (target: 84%)
  - k₁: 18.09 (target: ≤0.35)
  - Coherence: 0.0 (target: ≥0.650)
- **Investigation Needed**:
  1. Debug quantum decision-making logic
  2. Check if superposition engine is properly initialized
  3. Verify scenario generation and ground truth alignment
  4. Review adaptive scoring optimizer integration
- **Recommendation**: Escalate to quantum feature team - beyond scope of test alignment

### 🟢 Low Priority (Document/Defer)

**5. Investigate Skipped Tests**
- `test_knobs_summary_sidecar`: May need CI environment or script dependencies
- `test_allows_unsafe_with_override`: Needs Hydra dependencies (`pip install hydra-core omegaconf`)
- **Effort**: 30 minutes to investigate each

---

## Quick Wins Summary (COMPLETED ✅)

### Fixes Applied

1. **XSS Sanitization Bug** - ✅ FIXED (5 minutes)
   - Added XSS pattern removal in `sanitize_user_content()`
   - All 3 parametrized tests now pass
   
2. **Shared Fixtures Test** - ✅ FIXED (2 minutes)
   - Fixed alphabetical sorting expectations
   - Added missing assertions for complete test coverage

3. **Quantum Assessor API** - ⚠️ PARTIALLY FIXED (10 minutes)
   - Fixed API signature (monitor, repository parameters)
   - Fixed method name (`assess_compliance`)
   - Tests now run but fail due to functional issues (requires separate investigation)

**Total Quick Win Time**: ~17 minutes  
**Tests Fixed**: 2 fully fixed, 3 partially fixed (API aligned)

---

## Detailed Fix Summary

### ✅ Fully Fixed (2 test failures resolved)

1. **test_xss_like_payloads_flagged** - Security vulnerability fixed
2. **test_detect_shared_fixtures** - Test logic corrected

### ⚠️ Partially Fixed (API signature issues resolved, functional issues remain)

3. **test_accuracy_maintained** - API fixed, requires quantum logic investigation
4. **test_k1_target_achieved** - API fixed, requires quantum logic investigation  
5. **test_no_regression** - API fixed, requires quantum logic investigation

### ⚠️ Requires Investigation (not test alignment issues)

6. **test_knobs_summary_sidecar** - Skipped during collection (environment/dependencies)
7. **test_allows_unsafe_with_override** - Missing Hydra dependencies

### ✅ False Alarm (already passing)

8. **test_checkpoint_manager_best_k** - No action needed

---

## Next Steps

1. ✅ Apply quick wins first
2. Investigate quantum assessor initialization requirements
3. Set up proper test environment for skipped tests
4. Verify all fixes with full test suite run

