# [Report]: CI Failure Remediation Plan — Job 55143949728

## Summary
Coverage session failed during collection (15 errors) due to:
- Missing or broken critical dependencies (torch C extensions, transformers objects, hydra ConfigStore API differences).
- Absent libraries (requests, defusedxml, sentencepiece, transformers, accelerate).
- Unregistered markers (`cpu`) causing warning noise.
- Duplicate or shadowing modules (potential local `transformers/` or stale build artifacts).
- Hard import patterns in tests that assume full dependency presence.

## Remediation Applied

### 1. Dependency Normalization
**File**: `requirements-dev.txt`
- Added `transformers>=4.38.0` and `accelerate>=0.29.0`
- Pinned stable versions for all ML stack components
- Normalized versions to ensure compatibility

### 2. Marker Registration
**File**: `pytest.ini`
- Added `cpu` marker to eliminate warnings
- Standardized marker descriptions

### 3. Test Configuration Enhancement
**File**: `tests/conftest.py`
- Added dynamic skip logic for missing dependencies
- Implemented transformers import checking
- Added deterministic seeding with numpy and torch support

### 4. Hydra Compatibility
**File**: `src/codex_ml/utils/hydra_cs.py`
- Created `safe_exists()` helper for Hydra ConfigStore compatibility
- Supports both old (<1.3) and new (>=1.3) Hydra versions

### 5. CI Sanity Checking
**File**: `.github/scripts/ci_dependency_sanity.py`
- Pre-flight import validation for critical dependencies
- Catches broken wheels before pytest collection

### 6. Optional Dependency Management
**File**: `tools/testing/optional_deps.py`
- Updated probe list to include transformers
- Centralized dependency availability checking

## Verification Checklist
| Step | Status |
|------|--------|
| transformers added to requirements-dev.txt | ✅ |
| cpu marker registered in pytest.ini | ✅ |
| conftest.py updated with transformers skip logic | ✅ |
| Hydra compatibility shim created | ✅ |
| CI sanity script created | ✅ |
| optional_deps.py updated | ✅ |

## Next Steps
After merging:
```bash
# Local verification
python -m pip install -r requirements-dev.txt
python .github/scripts/ci_dependency_sanity.py
nox -s coverage
```

## Expected Outcomes
- Zero import errors during pytest collection
- All critical dependencies (torch, transformers, hydra) available
- Tests skip gracefully when optional deps missing
- Coverage session completes successfully
- artifacts/coverage.xml generated

— End —
