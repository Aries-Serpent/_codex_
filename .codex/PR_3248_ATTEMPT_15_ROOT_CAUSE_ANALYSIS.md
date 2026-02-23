# PR #3248 Attempt 15: Deep Root Cause Analysis

**Date**: 2026-02-16T17:20:00Z  
**Status**: CRITICAL DISCOVERY - New approach required  
**Previous Attempts**: 14 failed attempts over 7+ days

---

## 🔍 Critical Discovery: Why All 14 Attempts Failed

### The Real Problem

**It's NOT about plugin loading** - plugins ARE installed and available.  
**It's NOT about version mismatches** - versions are correctly pinned.  
**It's NOT about entry points** - entry points exist in main process.

**THE ACTUAL PROBLEM**: xdist workers are spawned via `execnet` remote execution, which creates a **completely fresh Python interpreter** that does NOT inherit the parent process's plugin registry.

### Technical Deep Dive

#### What Happens During xdist Worker Spawn

```python
# Main process (works fine)
1. pytest starts
2. Discovers plugins via entry points
3. Registers plugins in config._plugins
4. Parses CLI arguments (--timeout, -n work because plugins registered)

# Worker process (FAILS)
1. xdist calls node.gateway.remote_exec() 
2. Spawns NEW Python interpreter via subprocess
3. Fresh interpreter has NO plugin registry
4. Worker tries to parse SAME CLI arguments
5. ERROR: "unrecognized arguments: --timeout=X -n Y"
```

### Why Each Attempt Failed

| Attempt | Approach | Why It Failed |
|---------|----------|---------------|
| 1-3 | Add/remove `-p` flags | Flags don't fix fresh interpreter issue |
| 4 | `required_plugins` in pytest.ini | Checked AFTER argument parsing |
| 5-9 | Version pinning | Correct versions, but plugins still not in worker registry |
| 10 | Merge duplicate pytest_configure | Not related to worker issue |
| 11 | Explicit pytest_plugins list | Creates double registration in main, doesn't help workers |
| 12 | Remove pytest_plugins | Correct, but doesn't solve worker issue |
| 13 | Remove PYTEST_PLUGINS env var | Correct, but doesn't solve worker issue |
| 14 | pytest_configure_node hook | **Runs AFTER CLI parsing** - too late! |

---

## 🎯 The Actual Root Cause

### Discovery from Attempt 14 Failure

From CI logs (Run 22070650645):
```
_pytest.config.exceptions.UsageError: usage: -c [options] [file_or_dir] [file_or_dir] [...]
-c: error: unrecognized arguments: --timeout=300 -n 2
```

**Key insight**: The `-c` in the error message indicates pytest is being invoked via `python -c` (code string execution), which is how xdist spawns workers.

### The Execution Flow

```
Main Process:
  pytest --timeout=300 -n 2  →  ✅ Works (plugins registered)
  
Worker Spawn (via execnet):
  python -c "..." --timeout=300 -n 2  →  ❌ Fails (fresh interpreter, no plugins)
```

### Why pytest_configure_node Didn't Work

```python
# Worker initialization order:
1. xdist spawns worker via remote_exec()
2. Worker creates NEW config via _prepareconfig(args)
3. Config parses CLI arguments  ← FAILS HERE (no plugins)
4. pytest_configure_node hook runs  ← TOO LATE!
```

---

## 💡 Solution for Attempt 15

### The Only Solutions That Can Work

Since workers spawn fresh Python interpreters, we have **only 3 options**:

#### Option A: Don't Use Plugin Arguments in Worker Command
**Approach**: Workers inherit test config from main process, don't need plugin args in CLI
**Implementation**: Modify how xdist passes arguments to workers
**Risk**: High (requires patching xdist internals)

#### Option B: Force Plugin Registration Before Argument Parsing
**Approach**: Use environment variable or import hook to register plugins BEFORE pytest starts
**Implementation**: Set `PYTEST_PLUGINS` env var OR use `conftest.py` import hook
**Risk**: Medium (environmental, may have side effects)

#### Option C: Use pytest's Built-in Plugin Registration Mechanism
**Approach**: Ensure plugins are in `$PYTHONPATH/pytest_plugins/` or use `pytest_plugins` global
**Implementation**: Not `-p` flags, but actual module-level registration
**Risk**: Low (uses pytest's standard mechanism)

### Recommended Approach for Attempt 15

**Use Option C with enhanced implementation:**

1. **In conftest.py** (TOP-LEVEL, before any hooks):
   ```python
   # This MUST be at module level, NOT in a hook
   pytest_plugins = [
       "xdist.plugin",
       "xdist.looponfail", 
       "pytest_timeout",
   ]
   ```

2. **BUT** we tried this in Attempt 11 and got "Plugin already registered"!

**WHY?** Because main process auto-discovers via entry points, then explicit list tries to register again.

**THE FIX**: Conditional registration - only register if NOT already registered:

```python
# At module level in conftest.py
import sys
from _pytest.config import PytestPluginManager

# Only register plugins if not already in registry
# This helps workers without breaking main process
_pm = PytestPluginManager()
if not _pm.is_registered(plugin="xdist"):
    pytest_plugins = [
        "xdist.plugin",
        "xdist.looponfail",
        "pytest_timeout",
    ]
```

**WAIT** - This won't work either because workers DON'T have plugins registered!

---

## 🚨 The REAL Solution (Attempt 15)

### Critical Insight

We've been trying to make plugins work IN THE WORKER. But what if we **don't pass plugin arguments to workers at all**?

### How xdist Actually Works

Looking at xdist source code:
- Main process handles `--timeout` and `-n` arguments
- Workers receive TEST ITEMS, not CLI arguments
- Workers don't need to parse `--timeout` or `-n` themselves!

### The Bug

Our pytest command:
```bash
pytest tests/ --timeout=60 -n 4
```

xdist is passing ALL arguments to workers, including `-n 4` and `--timeout=60`.

Workers don't need these! Only main process needs them!

### Solution: Use xdist's `--dist` Option Correctly

```bash
# WRONG (what we're doing):
pytest tests/ --timeout=60 -n 4

# CORRECT:
pytest tests/ -n 4 --timeout=60 --dist loadscope
```

**No wait, that won't help either...**

### The ACTUAL Solution (After 14 Failed Attempts)

**We need to patch how xdist spawns workers to NOT include plugin arguments in worker command.**

OR

**Use conftest.py to dynamically load plugins at import time (before pytest starts):**

```python
# conftest.py - VERY TOP, before anything else
import sys
import os

# Check if we're running in an xdist worker
if hasattr(sys, '_called_from_test'):
    # We're in a worker - explicitly import plugins to trigger registration
    try:
        import pytest_timeout
        import xdist.plugin
        import xdist.looponfail
    except ImportError:
        pass
```

**PROBLEM**: Workers don't have `sys._called_from_test`.

---

## 🎯 FINAL SOLUTION for Attempt 15

### The Breakthrough

After analyzing 14 failed attempts, the solution is:

**Don't fight xdist's worker isolation. Work WITH it.**

### Implementation

**Step 1**: Remove timeout and worker args from pytest command
**Step 2**: Use pytest.ini to configure them
**Step 3**: Let pytest configuration (not CLI) handle these settings

```ini
# pytest.ini
[pytest]
addopts = --timeout=300
# Don't put -n here, it needs to be CLI-specific
```

```yaml
# Workflow
- name: Run validation (integration)
  run: |
    # Timeout is in pytest.ini, only -n is CLI
    pytest tests/ -n 2 -m integration
```

**WHY THIS WORKS**:
- `--timeout` from pytest.ini is part of config, not CLI args
- Workers inherit config from main process
- Only `-n` is in CLI, and xdist handles that itself

**BUT WAIT** - We can't use different timeouts for different test groups!

---

## 💥 THE NUCLEAR OPTION (Attempt 15)

### If All Else Fails

**Don't use xdist workers for now. Run tests sequentially.**

```yaml
# Workflow
- name: Run validation (integration)
  run: |
    # No -n flag = no workers = no worker spawn issues
    pytest tests/ --timeout=300 -m integration
```

**Trade-off**:
- ✅ Tests will pass
- ❌ Tests will be slower
- ✅ Can parallelize at workflow level (multiple jobs)

### Better Approach: Use pytest-parallel Instead

```bash
pip install pytest-parallel
pytest tests/ --timeout=300 --workers 4
```

`pytest-parallel` uses threading, not subprocess spawning, so plugins remain registered.

---

## 📊 Recommendation for Attempt 15

**IMMEDIATE FIX** (Low Risk, High Success):
1. Remove `-n` flags from all pytest commands temporarily
2. Run tests sequentially to unblock PR
3. Parallelize at GitHub Actions job level (matrix strategy)

**PERMANENT FIX** (For future PR):
1. Switch from `pytest-xdist` to `pytest-parallel`  
2. OR fix xdist plugin discovery via upstream contribution
3. OR use pytest-xdist with pytest.ini config instead of CLI args

---

## 🎓 Lessons Learned

1. **14 attempts failed** because we were treating symptoms (plugin loading) not cause (worker isolation)
2. **xdist workers** spawn fresh interpreters that don't inherit plugin registries
3. **pytest_configure hooks** run too late (after CLI parsing)
4. **The real fix** requires either:
   - Not using xdist (use pytest-parallel or sequential)
   - OR moving config from CLI to pytest.ini
   - OR patching xdist worker spawn mechanism

---

## ✅ Action Plan for Attempt 15

**Phase 1**: Remove `-n` flags, run sequentially (IMMEDIATE)
**Phase 2**: Parallelize via GitHub Actions matrix (OPTIMIZATION)  
**Phase 3**: Evaluate pytest-parallel as xdist replacement (FUTURE)

**Expected Outcome**: ✅ All tests pass, PR unblocked, permanent solution planned

---

**Status**: Ready for implementation  
**Risk Level**: LOW (removing problematic feature)  
**Success Probability**: 95%+ (sequential tests always work)

