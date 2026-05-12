# CodeQL Alert Inventory — PR #4427
**Generated**: 2026-05-12T21:07Z  
**Source**: Artifact run 25733097599  
**SHA256**: 87ec8de22896fccfbbad08e65fcb4210e8caf6d90407ec84ec6eabae5ec66c05

---

## 📊 EXECUTIVE SUMMARY

**Total Alerts**: 127 open  
**Last Fixed**: 1 (S967: Empty except in verify_living_files.py)  
**Remaining**: 126

### By Severity
| Severity | Count | Percentage |
|----------|-------|------------|
| **Error** | 9 | 7.1% |
| **Warning** | 57 | 44.9% |
| **Note** | 61 | 48.0% |

### By Category
| Category | Count | Percentage |
|----------|-------|------------|
| **Python Code Quality** | 66 | 52.0% |
| **GitHub Actions** | 58 | 45.7% |
| **Python Security** | 3 | 2.4% |

---

## 🎯 ALERT BREAKDOWN BY RULE

### 1. `py/unused-local-variable` (41 alerts) — Severity: note
**Description**: Unused local variable  
**Impact**: Code quality, maintainability  
**Fix Complexity**: Simple (remove or prefix with `_`)

**Top 10 Files**:
1. `tests/integration/test_training_pipeline_e2e.py:143` — Alert #13160
2. `tests/security/test_security_gating.py:260` — Alert #13159
3. `tests/auto_remediation/test_recovery_procedures.py:332` — Alert #13158
4. `tests/auto_remediation/test_recovery_procedures.py:197` — Alert #13157
5. `tests/rag/test_rag_monitoring_metrics.py:145` — Alert #13156
6. `tests/integration/test_phase3_performance_integration.py:640` — Alert #13155
7. `tests/integration/test_phase3_workflows_e2e.py:205` — Alert #13154
8. `tests/integration/test_phase3_edge_cases_coverage.py:423` — Alert #13153
9. `tests/integration/test_phase3_cross_module_coverage.py:445` — Alert #13152
10. `tests/agents/test_phase2_deep_coverage_batch5.py:523` — Alert #13151

**Fix Pattern**:
```python
# Before
def test_something():
    result = expensive_operation()  # Unused
    assert True

# After (Option 1: Remove)
def test_something():
    assert True

# After (Option 2: Use it)
def test_something():
    result = expensive_operation()
    assert result is not None

# After (Option 3: Mark as intentionally unused)
def test_something():
    _result = expensive_operation()  # Intentionally unused, validates no exception
    assert True
```

---

### 2. `actions/unpinned-tag` (33 alerts) — Severity: warning
**Description**: GitHub Actions using unpinned tags  
**Impact**: Security, reproducibility  
**Fix Complexity**: Simple (pin to SHA)

**Top 10 Files**:
1. `.github/workflows/validate.yml:296` — Alert #13240
2. `.github/workflows/test-rag.yml:136` — Alert #13239
3. `.github/workflows/rust_swarm_ci.yml:498` — Alert #13238
4. `.github/workflows/rust_swarm_ci.yml:465` — Alert #13237
5. `.github/workflows/rust_swarm_ci.yml:443` — Alert #13236
6. `.github/workflows/rust_swarm_ci.yml:440` — Alert #13235
7. `.github/workflows/rust_swarm_ci.yml:251` — Alert #13234
8. `.github/workflows/scheduled-dependency-audit.yml:188` — Alert #13233
9. `.github/workflows/scheduled-dependency-audit.yml:185` — Alert #13232
10. `.github/workflows/scheduled-dependency-audit.yml:145` — Alert #13231

**Fix Pattern**:
```yaml
# Before
- uses: actions/checkout@v4

# After
- uses: actions/checkout@v4  # v4.2.0
  # SHA: 93cb6efe18208431cddfb8368fd83d5badbf9bfd
```

**Note**: Repository memory shows approved SHAs for common actions. Use those.

---

### 3. `actions/missing-workflow-permissions` (22 alerts) — Severity: warning
**Description**: Workflow missing explicit permissions  
**Impact**: Security (principle of least privilege)  
**Fix Complexity**: Moderate (requires permission analysis)

**Top 10 Files**:
1. `.github/workflows/test-rag.yml:23` — Alert #13207
2. `.github/workflows/template_lint.yml:14` — Alert #13206
3. `.github/workflows/status_gate.yml:14` — Alert #13205
4. `.github/workflows/rust_swarm_ci.yml:478` — Alert #13204
5. `.github/workflows/rust_swarm_ci.yml:457` — Alert #13203
6. `.github/workflows/rust_swarm_ci.yml:432` — Alert #13202
7. `.github/workflows/rust_swarm_ci.yml:227` — Alert #13201
8. `.github/workflows/rust_swarm_ci.yml:168` — Alert #13200
9. `.github/workflows/rust_swarm_ci.yml:109` — Alert #13199
10. `.github/workflows/resilient_validation.yml:74` — Alert #13198

**Fix Pattern**:
```yaml
# Before
name: My Workflow
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

# After
name: My Workflow
on: [push]
permissions:
  contents: read
  pull-requests: write  # Only if needed
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]
```

---

### 4. `py/undefined-export` (8 alerts) — Severity: error ⚠️
**Description**: `__all__` references undefined names  
**Impact**: Import errors, API contract violation  
**Fix Complexity**: Simple (fix or remove from `__all__`)

**All Alerts** (in `src/codex/retrieval/__init__.py`):
1. Line 13 — Alert #13546
2. Line 12 — Alert #13545
3. Line 11 — Alert #13544
4. Line 10 — Alert #13543
5. Line 9 — Alert #13542
6. Line 8 — Alert #13541
7. Line 7 — Alert #13540
8. Line 6 — Alert #13539

**Fix Pattern**:
```python
# Before
__all__ = [
    "NonExistentClass",  # Error: not defined
    "AnotherMissing",
]

# After (Option 1: Remove from __all__)
__all__ = [
    # Removed undefined exports
]

# After (Option 2: Import the missing items)
from .module import NonExistentClass, AnotherMissing
__all__ = [
    "NonExistentClass",
    "AnotherMissing",
]
```

---

### 5. `py/unused-import` (8 alerts) — Severity: note
**Description**: Imported module not used  
**Impact**: Code quality, performance  
**Fix Complexity**: Simple (remove import)

**All Alerts**:
1. `tests/cognitive_brain/test_integration.py:13` — Alert #10983
2. `tests/cognitive_brain/quantum/test_ab_testing.py:13` — Alert #10980
3. `tests/cognitive_brain/quantum/test_ab_testing.py:12` — Alert #10979
4. `tests/cognitive_brain/quantum/test_ab_testing.py:11` — Alert #10978
5. `tests/cognitive_brain/quantum/test_ab_testing.py:10` — Alert #10977
6. `tests/cognitive_brain/quantum/test_ab_testing.py:9` — Alert #10976
7. `tests/cognitive_brain/quantum/test_ab_testing.py:8` — Alert #10975
8. `tests/cognitive_brain/quantum/test_ab_testing.py:7` — Alert #10974

**Fix Pattern**:
```python
# Before
import unused_module  # Not used anywhere

# After
# (removed)
```

---

### 6. `py/unused-global-variable` (6 alerts) — Severity: note
**Description**: Global variable defined but not used  
**Impact**: Code quality  
**Fix Complexity**: Simple (remove or use)

**All Alerts**:
1. `src/codex/retrieval/stores/__init__.py:9` — Alert #13547
2. `src/codex_ml/tracking/mlflow_guard.py:12` — Alert #13077
3. `src/codex_ml/tracking/mlflow_guard.py:11` — Alert #13076
4. `src/codex_ml/tracking/mlflow_guard.py:10` — Alert #13075
5. `src/codex_ml/tracking/mlflow_guard.py:9` — Alert #13074
6. `src/codex_ml/tracking/mlflow_guard.py:8` — Alert #13073

---

### 7. `py/import-and-import-from` (3 alerts) — Severity: note
**Description**: Module imported with both `import` and `from ... import`  
**Impact**: Code quality, clarity  
**Fix Complexity**: Simple (consolidate imports)

**All Alerts**:
1. `tests/test_logging_utils.py:12` — Alert #12726
2. `tests/tokenization/test_sentencepiece_contract.py:71` — Alert #12541
3. `tests/training/test_data_utils.py:267` — Alert #3751

**Fix Pattern**:
```python
# Before
import os
from os import path

# After (Option 1)
import os

# After (Option 2)
from os import path
```

---

### 8. `actions/untrusted-checkout/medium` (2 alerts) — Severity: warning ⚠️
**Description**: Checking out untrusted code  
**Impact**: Security (code injection risk)  
**Fix Complexity**: Moderate (requires workflow redesign)

**All Alerts**:
1. `.github/workflows/forward-sync-autogen.yml:71` — Alert #13242
2. `.github/workflows/app-package-download.yml:73` — Alert #13241

**Fix Pattern**:
```yaml
# Before
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha }}

# After
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha }}
    persist-credentials: false
# + Add explicit permission restrictions
# + Run in isolated environment
```

---

### 9. `py/ineffectual-statement` (2 alerts) — Severity: note
**Description**: Statement has no effect  
**Impact**: Code quality, likely bug  
**Fix Complexity**: Simple (remove or fix)

**All Alerts**:
1. `src/codex/rag/embeddings.py:50` — Alert #4557
2. `src/codex/rag/embeddings.py:46` — Alert #4556

**Fix Pattern**:
```python
# Before
def some_function():
    "This string does nothing"  # Ineffectual
    x = 5
    x  # Ineffectual
    return True

# After
def some_function():
    # Removed ineffectual statements
    x = 5
    return True
```

---

### 10. `py/uninitialized-local-variable` (1 alert) — Severity: error ⚠️
**Description**: Variable used before initialization  
**Impact**: Runtime error, logic bug  
**Fix Complexity**: Moderate (requires logic analysis)

**Alert**:
1. `tests/unit/test_peft_utils.py:29` — Alert #13430

**Fix Pattern**:
```python
# Before
def test_something():
    if condition:
        result = compute()
    return result  # Error: may be uninitialized

# After
def test_something():
    result = None  # Initialize
    if condition:
        result = compute()
    return result
```

---

### 11. `actions/syntax-error` (1 alert) — Severity: note
**Description**: Syntax error in action definition  
**Impact**: Action may not work correctly  
**Fix Complexity**: Simple (fix syntax)

**Alert**:
1. `.github/actions/doc-test-scribe-action/action.yml:201` — Alert #13292

---

## 🎯 REMEDIATION PRIORITY MATRIX

### Priority 1: CRITICAL (Fix First) — 9 alerts
**Severity**: Error  
**Impact**: High (runtime errors, API contract violations)

| Rule | Count | Files Affected |
|------|-------|----------------|
| `py/undefined-export` | 8 | `src/codex/retrieval/__init__.py` |
| `py/uninitialized-local-variable` | 1 | `tests/unit/test_peft_utils.py` |

**Estimated Time**: 1 session (S968)

---

### Priority 2: HIGH (Fix Second) — 57 alerts
**Severity**: Warning  
**Impact**: Medium (security, reproducibility)

| Rule | Count | Category |
|------|-------|----------|
| `actions/unpinned-tag` | 33 | GitHub Actions |
| `actions/missing-workflow-permissions` | 22 | GitHub Actions |
| `actions/untrusted-checkout/medium` | 2 | GitHub Actions |

**Estimated Time**: 2-3 sessions (S969-S971)

---

### Priority 3: MEDIUM (Fix Third) — 61 alerts
**Severity**: Note  
**Impact**: Low (code quality, maintainability)

| Rule | Count | Category |
|------|-------|----------|
| `py/unused-local-variable` | 41 | Python Quality |
| `py/unused-import` | 8 | Python Quality |
| `py/unused-global-variable` | 6 | Python Quality |
| `py/import-and-import-from` | 3 | Python Quality |
| `py/ineffectual-statement` | 2 | Python Quality |
| `actions/syntax-error` | 1 | GitHub Actions |

**Estimated Time**: 3-4 sessions (S972-S975)

---

## 📋 SESSION ALLOCATION

### Session S968 (Current): Priority 1 — Critical Errors
**Target**: 9 error-severity alerts  
**Focus**: `py/undefined-export` (8) + `py/uninitialized-local-variable` (1)  
**Files**: 2 files  
**Estimated Time**: 30-45 minutes

### Session S969: Priority 2A — Unpinned Tags (Part 1)
**Target**: 15-20 `actions/unpinned-tag` alerts  
**Files**: 10-15 workflow files  
**Estimated Time**: 45-60 minutes

### Session S970: Priority 2B — Unpinned Tags (Part 2)
**Target**: Remaining `actions/unpinned-tag` alerts  
**Files**: 10-15 workflow files  
**Estimated Time**: 45-60 minutes

### Session S971: Priority 2C — Workflow Permissions
**Target**: 22 `actions/missing-workflow-permissions` alerts  
**Files**: 15-20 workflow files  
**Estimated Time**: 60-75 minutes

### Session S972: Priority 2D — Untrusted Checkout
**Target**: 2 `actions/untrusted-checkout/medium` alerts  
**Files**: 2 workflow files  
**Estimated Time**: 30-45 minutes

### Session S973-S975: Priority 3 — Code Quality
**Target**: 61 note-severity alerts  
**Focus**: Unused variables, imports, ineffectual statements  
**Files**: 40-50 test files + 2-3 src files  
**Estimated Time**: 3 sessions × 60 minutes

### Session S976: Final Validation
**Target**: Verify 0 alerts, run full test suite  
**Estimated Time**: 30-45 minutes

---

## 📊 PROGRESS TRACKING

| Session | Target | Fixed | Remaining | Status |
|---------|--------|-------|-----------|--------|
| S967 | 1 | 1 | 126 | ✅ Complete |
| S968 | 9 | 0 | 126 | ⏳ In Progress |
| S969 | 15-20 | 0 | ~110 | ⏳ Pending |
| S970 | 13-18 | 0 | ~95 | ⏳ Pending |
| S971 | 22 | 0 | ~75 | ⏳ Pending |
| S972 | 2 | 0 | ~73 | ⏳ Pending |
| S973 | 20-25 | 0 | ~50 | ⏳ Pending |
| S974 | 20-25 | 0 | ~28 | ⏳ Pending |
| S975 | 15-20 | 0 | ~10 | ⏳ Pending |
| S976 | Validation | 0 | 0 | ⏳ Pending |

---

**Last Updated**: 2026-05-12T21:07Z  
**Next Update**: After S968 completion
