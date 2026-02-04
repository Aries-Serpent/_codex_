# CI Failure Investigation - Quick Reference

## Job Information
- **Workflow Run**: 21683424653
- **Job ID**: 62523872141
- **Job Name**: Core Tests (Python 3.12)
- **Failure**: Test collection timeout (exit code 2)

## Key Finding
**File**: `tests/framework/__init__.py` (line 9)  
**Issue**: Imports from `generator.py` at module level  
**Result**: Pytest collection hangs (62s timeout)

## Why It Fails
```
tests/framework/generator.py  ← has "test_" prefix
                ↓
       pytest tries to collect it
                ↓
    imports tests.framework package
                ↓
  __init__.py imports from generator.py
                ↓
         CIRCULAR DEPENDENCY
                ↓
         Collection HANGS
```

## The Fix (Choose One)

### Option 1: Rename (Fastest)
```bash
cd tests/framework/
git mv generator.py generator.py
sed -i 's/test_generator/generator_utils/' __init__.py
```

### Option 2: Move Out
```bash
mkdir -p tests/_utils/
git mv tests/framework/generator.py tests/_utils/
# Update imports in __init__.py
```

### Option 3: Remove Import
```python
# tests/framework/__init__.py
# Delete or comment out:
# from .test_generator import UnitTestGenerator, OrchestrationFlowSpec
```

## Verification
```bash
# Should complete in <5 seconds
timeout 30 python -m pytest tests/ --collect-only -q
```

## Related Files
- Analysis: `reports/ci_log_analysis_job_62523872141.md`
- Summary: `reports/ci_failure_summary.txt`
- Logs: `artifacts/ci_logs/job_62523872141_core_tests.log`
- Metadata: `artifacts/ci_logs/job_62523872141_metadata.json`

## Prevention
- ❌ Never name utility modules with `test_` prefix in `tests/`
- ❌ Avoid module-level imports in test package `__init__.py`
- ✅ Use lazy imports or pytest hooks for conditional imports
- ✅ Add collection timeout in CI: `timeout-minutes: 2`
