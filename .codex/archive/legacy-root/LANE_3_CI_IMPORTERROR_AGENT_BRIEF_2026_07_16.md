# Lane 3: Phase 6B - Test Error Remediation (Batch 2) — Agent Brief

**Prepared**: 2026-07-16T03:09:30Z  
**Target Agent**: `ci-importerror-agent`  
**Session**: CTEP-Phase4-6-Continuation-S2026_07_16  
**Authority**: @mbaetiong D-tier autonomous | wec:auto-approve enabled  

---

## 🎯 OBJECTIVE

Fix **40-50 import-specific test errors** from Phase 6 Batch 2 (sys.path issues, missing dependencies, import path errors) in parallel execution.

**Success Criteria**:
- ✅ 40-50 errors → 0 (100% batch resolution)
- ✅ Test suite passes green
- ✅ No new errors introduced
- ✅ No regressions
- ✅ Batch 2 confidence: 85-90%

---

## 📋 EXECUTION STEPS

### Step 1: Import Error Analysis

**Reference**: `.codex/PHASE_6_TEST_ERROR_ANALYSIS.md` (import error section)

From the 142 total test errors:
- **Your Batch**: Errors 61-110 (import-focused errors)
- **Error Categories** (your specialization):
  - `sys.path` issues (12-15): Incorrect path configuration
  - Missing dependencies (15-18): Dependency not installed, version mismatch
  - Import path errors (8-10): Wrong module path, typo in import
  - Dual-package shadowing (5-7): `src.*` vs `codex.*` confusion

**Analysis Command**:
```bash
python scripts/ci/ci_importerror_agent.py --batch 2 --errors 61-110 --analyze
```

### Step 2: sys.path Issue Remediation

**Pattern 1: sys.path.insert(0, 'src') anti-pattern**

```python
# WRONG (legacy, causes dual-package shadowing):
import sys
sys.path.insert(0, 'src')
from codex import something  # This imports src/codex/__init__.py

# CORRECT (use pytest.ini configuration):
# pytest.ini: pythonpath = [".", "src"]
# Then use:
from codex import something  # This imports the package correctly
```

**Fix Commands**:
```bash
# Find all sys.path.insert patterns in tests
grep -r "sys.path.insert" tests/ --include="*.py"

# For each occurrence:
# 1. Remove sys.path.insert line
# 2. Verify pytest.ini has pythonpath = [".", "src"]
# 3. Update import to use "from codex..." (no src prefix)
```

### Step 3: Missing Dependency Resolution

**Pattern 2: Dependencies not installed or version mismatches**

```python
# WRONG:
import hydra_core  # Never installed, or wrong version

# Proper approach:
try:
    import hydra_core
    HAS_HYDRA_CORE = True
except ImportError:
    HAS_HYDRA_CORE = False
    logger.warning("hydra-core not available")

# Then use:
if HAS_HYDRA_CORE:
    # Use hydra features
else:
    # Skip test or use mock
    pytest.skip("hydra-core not available")
```

**Dependency Check Command**:
```bash
# List installed packages with versions
pip list | grep -E "hydra|torch|transformers|mlflow"

# Install missing optional deps
pip install -r requirements-tests-optional.txt
```

### Step 4: Import Path Error Fixes

**Pattern 3: Incorrect module paths**

```python
# WRONG:
from src.codex.module import something  # src prefix causes dual-package shadowing

# CORRECT:
from codex.module import something

# WRONG:
from codex.cli import task  # Import not exported from __init__

# CORRECT (check __init__.py first):
from codex.cli.task_sequence import Task  # pragma: allowlist secret
```

**Path Validation Command**:
```bash
# Verify imports are correct
python -c "from codex.module import something; print('OK')"

# Check for src.* patterns (should be 0)
grep -r "from src\." tests/ --include="*.py" | wc -l
```

### Step 5: P19 Shadow Import Detection

**Pattern 4: Dual-package shadowing (P19 pattern)**

```python
# Symptom: Test works in IDE (uses src/) but fails in pytest (uses codex/)

# ROOT CAUSE: pytest.ini pythonpath includes both "." and "src"
# So "from codex..." resolves to BOTH:
#   1. src/codex/ (installed first in pythonpath)
#   2. codex/ (system package, if installed)

# DETECTION (P19 aware):
# If test imports codex but sys.modules['codex'].__file__ shows src/codex:
# Then you have a shadow import

import sys
if 'codex' in sys.modules:
    print(f"codex module location: {sys.modules['codex'].__file__}")
    # Expected: .../site-packages/codex/ or /repo/src/codex/
    # If inconsistent: P19 shadow detected
```

**P19 Remediation**:
```yaml
# pytest.ini — CORRECT configuration:
[pytest]
pythonpath = ["."]  # Only current dir, NOT "src"
testpaths = ["tests"]

# Then in tests:
from codex import module  # Always resolves correctly
```

### Step 6: Test Suite Validation

**Command**:
```bash
python -m pytest tests/ -v --tb=short -x
```

After each 5-10 fixes:
- ✅ Verify fixed tests pass
- ✅ Check for new errors
- ✅ Capture error reduction metrics

### Step 7: Error Count Tracking

**Progress Template**:
```
Batch 2 Progress (Errors 61-110):
- Start errors: 50
- Errors fixed (batch 1-10): 8 remaining → 42
- Errors fixed (batch 11-20): 9 remaining → 33
- Errors fixed (batch 21-30): 7 remaining → 26
- Errors fixed (batch 31-40): 8 remaining → 18
- Errors fixed (batch 41-50): 6 remaining → 12
- Final error count: [TARGET = 0]
- Success: ✅ [if 0] / ⚠️ [if >0]
```

---

## ⏱️ TIMELINE

- **Start**: 2026-07-16T03:12:00Z
- **Error Analysis**: 10 minutes
- **sys.path & Import Fixes**: 50 minutes
- **Dependency Resolution**: 15 minutes
- **Validation**: 10 minutes
- **Reporting**: 5 minutes
- **Total Estimate**: 90 minutes (1h 30m)
- **Target Completion**: 2026-07-16T04:42:00Z

---

## 📊 RESOURCES & REFERENCES

| Resource | Location | Purpose |
|----------|----------|---------|
| **Error Analysis** | `.codex/PHASE_6_TEST_ERROR_ANALYSIS.md` | Import error details |
| **Execution Plan** | `.codex/PHASE_6_EXECUTION_PLAN.md` | Fix templates |
| **pytest.ini** | `./pytest.ini` | Python path configuration |
| **Test Patterns** | `tests/test_*.py` | Example test patterns |

---

## 🚨 RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Dependency not available | Install from requirements-tests-optional.txt or mock |
| sys.path misconfiguration | Verify pytest.ini; test manually with `python -c` |
| Import path conflict | Check __init__.py exports; use absolute imports |
| P19 shadow detected | Fix pytest.ini pythonpath; re-run tests |

---

## ✅ HANDOFF CHECKLIST

Before completion, ensure:
- [ ] Import errors analyzed and categorized
- [ ] All sys.path issues fixed
- [ ] Missing dependencies installed or mocked
- [ ] Import paths corrected (no src.* patterns)
- [ ] P19 shadow imports resolved
- [ ] Test suite executes successfully
- [ ] Final error count = 0 (100% resolution)
- [ ] Execution report generated in `.codex/LANE_3_EXECUTION_REPORT_2026_07_16.md`
- [ ] AGENT_ACCOUNTABILITY_REPORT.md updated
- [ ] All files committed to branch

---

**Prepared by**: Copilot Task Agent  
**Authority**: @mbaetiong D-tier autonomous  
**Status**: READY FOR EXECUTION
