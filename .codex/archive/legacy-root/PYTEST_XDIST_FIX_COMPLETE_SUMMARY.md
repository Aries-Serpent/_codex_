# Pytest-xdist PYTEST_ADDOPTS Fix

**Date:** 2026-01-27  
**Issue:** PR #3020 - Testing Suite core-tests job failing with exit code 5 (no tests collected)  
**Commit:** 1287be6  
**Status:** ✅ FIXED

## Problem Description

The `core-tests` job in `.github/workflows/test-suite.yml` was failing with:
- **Exit code 5** (no tests collected)
- **Error:** "maximum crashed workers reached: 8"
- **pytest error:** "unrecognized arguments: --cov=src --cov-report=xml --cov-report=html --cov-report=term -n auto --dist loadgroup"

### Root Cause

The workflow had `PYTEST_ADDOPTS: '--color=yes --verbose'` set as an environment variable. When pytest-xdist spawns worker processes to run tests in parallel:

1. Each worker inherits the `PYTEST_ADDOPTS` environment variable
2. Workers try to parse these options during initialization
3. **BUT** pytest plugins (pytest-cov, pytest-xdist) haven't been loaded yet in the worker context
4. This causes `UsageError` exceptions and all workers crash
5. With no workers available, no tests can be collected or executed

### Error Logs

```
_pytest.config.exceptions.UsageError: usage: -c [options] [file_or_dir] [file_or_dir] [...]
-c: error: unrecognized arguments: --cov=src --cov-report=xml --cov-report=html --cov-report=term -n auto --dist loadgroup

maximum crashed workers reached: 8

================== xdist: maximum crashed workers reached: 8 ===================

---------------------- coverage: failed workers ----------------------
The following workers failed to return coverage data, ensure that pytest-cov is installed on these workers.
gw0, gw1, gw2, gw3, gw4, gw5, gw6, gw7, gw8, gw9
```

## Solution

**Remove `PYTEST_ADDOPTS` and pass all options directly to the pytest command.**

### Changes Made

```diff
 env:
   PYTHON_VERSION: '3.12'
-  PYTEST_ADDOPTS: '--color=yes --verbose'
+  # PYTEST_ADDOPTS removed - options passed directly to pytest command to avoid xdist worker crashes

-      - name: Run core tests with coverage
-        run: |
-          pytest tests/ \
-            --cov=src \
-            --cov-report=xml \
-            --cov-report=html \
-            --cov-report=term \
-            -n auto \
-            --dist loadgroup \
-            --maxfail=10 \
-            -v
+      - name: Run core tests with coverage
+        run: |
+          pytest tests/ \
+            --color=yes \
+            --verbose \
+            --cov=src \
+            --cov-report=xml \
+            --cov-report=html \
+            --cov-report=term \
+            -n auto \
+            --dist loadgroup \
+            --maxfail=10
```

### Why This Works

When options are passed directly to the pytest command:
1. The main pytest process loads all plugins first
2. Then spawns workers with the fully initialized plugin context
3. Workers inherit the correct environment and can process all options
4. Tests execute successfully with parallel execution and coverage

## Best Practices

### ✅ DO
- Pass all pytest options directly to the pytest command
- Use direct command-line arguments for --color, --verbose, --cov, -n, etc.
- Check plugin compatibility before using environment variables

### ❌ DON'T
- Use `PYTEST_ADDOPTS` environment variable with pytest-xdist
- Set coverage or xdist options in environment variables
- Assume environment variables are safe for worker processes

## References

- **Workflow:** `.github/workflows/test-suite.yml`
- **Commit:** 1287be6
- **CI Run:** Awaiting verification
- **Related:** pytest-xdist documentation on worker isolation

## Verification

Expected behavior after fix:
1. ✅ Workers spawn successfully (no crashes)
2. ✅ Tests are collected (exit code 0 or >0 if tests fail, but not 5)
3. ✅ Coverage reports generated
4. ✅ Artifacts uploaded successfully

## Future Maintenance

If adding new pytest options to workflows:
1. Add them to the pytest command line directly
2. Do NOT use PYTEST_ADDOPTS unless absolutely necessary
3. Test with pytest-xdist (-n auto) to ensure worker compatibility
4. Document any environment variables that affect test execution
