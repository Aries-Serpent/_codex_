# PHASE 3.1 PRIORITIZED FIX LIST & EXECUTION PLAN

**Status:** Ready for Implementation  
**Generated:** 2026-07-03T15:45 UTC  
**Target Completion:** 2026-07-04 (4 days)

---

## Executive Summary

This document provides the actionable fix list extracted from the comprehensive audit report. It is organized by priority, execution order, and estimated time.

**Total Issues:** 25+  
**Critical (P0):** 2  
**High (P1):** 1  
**Medium (P2):** 1  

**Estimated Total Time:** 18-22 hours (can be parallelized)

---

## Quick Reference: Priority Summary

| Phase | Task | Est. Time | Owner | Status |
|-------|------|-----------|-------|--------|
| **A** | Fix prometheus_client import | 2 hrs | TBD | 🔴 Blocked |
| **A** | Fix charset_normalizer import | 2 hrs | TBD | 🔴 Blocked |
| **B** | Add pytest.importorskip() guards | 4-6 hrs | TBD | 🟡 Waiting |
| **C** | Add missing conftest.py files | 2-3 hrs | TBD | 🟢 Ready |
| **D** | Full validation & testing | 2-3 hrs | TBD | 🟢 Ready |

---

## PHASE A: CRITICAL FIXES (Day 1 - 4 hours)

### A1: Fix prometheus_client Import Chain

**Severity:** 🔴 P0 - BLOCKS COLLECTION  
**Status:** Identified & Ready to Fix  
**Effort:** 2 hours  
**Files:** 1  
**Tests Unblocked:** 12+

#### Root Cause Analysis

```
Import chain:
test_file.py
  → codex_utils/__init__.py
    → mlflow_offline.py
      → src/codex_ml/tracking/__init__.py
        → init_experiment.py
          → ndjson_logger.py
            → session_logger.py
              → moderation.py (LINE 63)
                → prometheus_client.Counter (FAILS HERE)
```

#### Current Code (BROKEN)

```python
# File: src/codex_ml/safety/moderation.py:52-63

def _make_moderation_counter():
    from prometheus_client import Counter
    return Counter(
        "moderation_decisions_total",
        "Total moderation decisions",
        labelnames=["decision_type"]
    )

_moderation_decisions_total = _make_moderation_counter()  # ← CALLED AT MODULE IMPORT TIME
```

**Problem:** prometheus_client imported unconditionally at module level

#### Fix #1 (RECOMMENDED): Lazy Import + Fallback

```python
# File: src/codex_ml/safety/moderation.py:52-75

def _make_moderation_counter():
    """Create counter with fallback to no-op if prometheus_client unavailable."""
    try:
        from prometheus_client import Counter
        return Counter(
            "moderation_decisions_total",
            "Total moderation decisions",
            labelnames=["decision_type"]
        )
    except ImportError:
        # Return no-op counter that does nothing
        class NoOpCounter:
            def inc(self, *args, **kwargs):
                pass
        return NoOpCounter()

# Only create once, lazily
_moderation_decisions_total = None

def _get_moderation_counter():
    """Get or create the moderation counter."""
    global _moderation_decisions_total
    if _moderation_decisions_total is None:
        _moderation_decisions_total = _make_moderation_counter()
    return _moderation_decisions_total

# Update all usages:
# OLD: _moderation_decisions_total.inc(...)
# NEW: _get_moderation_counter().inc(...)
```

#### Fix #2: Move to Optional Dependencies

```toml
# File: pyproject.toml

[project.optional-dependencies]
monitoring = [
    "prometheus-client>=0.19.0",
]
```

**Then in setup/CI:**
```bash
pip install -e ".[monitoring]"  # For environments that need metrics
pip install -e "."              # For minimal install (skip metrics)
```

#### Implementation Checklist

- [ ] **Step 1:** Edit `src/codex_ml/safety/moderation.py`
  - Implement lazy import pattern (above)
  - Find all usages of `_moderation_decisions_total`
  - Replace with `_get_moderation_counter()`
  
- [ ] **Step 2:** Find all usages
  ```bash
  grep -r "_moderation_decisions_total" src/
  # Expected: Find ~5-10 usages
  ```
  
- [ ] **Step 3:** Update usages
  ```python
  # Find-replace pattern:
  OLD: _moderation_decisions_total.inc(
  NEW: _get_moderation_counter().inc(
  ```
  
- [ ] **Step 4:** Test import safety
  ```bash
  python3 -c "from src.codex_ml.safety import moderation; print('✓ Import OK')"
  ```
  
- [ ] **Step 5:** Validate with collection
  ```bash
  pytest tests/phase6_wave1/ --collect-only -q 2>&1 | grep -i error
  # Expected: 0 errors for this module
  ```

#### Testing

```bash
# Test with prometheus_client NOT installed (main scenario)
python3 -c "
from unittest.mock import patch
import sys

# Remove prometheus_client from sys.modules if present
if 'prometheus_client' in sys.modules:
    del sys.modules['prometheus_client']

# Mock import to fail
with patch.dict(sys.modules, {'prometheus_client': None}):
    from src.codex_ml.safety import moderation
    counter = moderation._get_moderation_counter()
    counter.inc()  # Should not raise
    print('✓ No-op counter works')
"

# Test with prometheus_client installed (optional scenario)
if python3 -c "import prometheus_client" 2>/dev/null; then
    python3 -c "
    from src.codex_ml.safety import moderation
    counter = moderation._get_moderation_counter()
    counter.inc()  # Should work
    print('✓ Real counter works')
    "
fi
```

#### Estimated Time Breakdown
- Code analysis: 20 min
- Implementation: 30 min
- Testing: 40 min
- Code review: 30 min
- **Total: 2 hours**

#### Success Criteria
- [ ] Import succeeds without prometheus_client
- [ ] Import succeeds with prometheus_client
- [ ] tests/phase6_wave1/test_cache_and_utils.py collects without error
- [ ] tests/phase6_wave1/test_codex_ml_core.py collects without error
- [ ] tests/phase6_wave1/test_codex_utils_core.py collects without error

---

### A2: Fix charset_normalizer Import Chain

**Severity:** 🔴 P0 - BLOCKS COLLECTION  
**Status:** Identified & Ready to Fix  
**Effort:** 2 hours  
**Files:** 1  
**Tests Unblocked:** 13+

#### Root Cause Analysis

**File:** `src/ingestion/encoding_detect.py:34`

```python
from charset_normalizer import from_path  # ← FAILS HERE
```

#### Current Code (BROKEN)

```python
# File: src/ingestion/encoding_detect.py:30-40

def detect_encoding(file_path: str) -> str:
    """Detect file encoding using charset_normalizer."""
    from charset_normalizer import from_path
    result = from_path(file_path).best()
    return result.encoding if result else 'utf-8'
```

**Problem:** charset_normalizer imported at function level (better than module level, but still fails if missing)

#### Fix: Try-Except with Fallback

```python
# File: src/ingestion/encoding_detect.py:30-50

def detect_encoding(file_path: str) -> str:
    """Detect file encoding using charset_normalizer with fallback."""
    try:
        from charset_normalizer import from_path
        result = from_path(file_path).best()
        return result.encoding if result else 'utf-8'
    except ImportError:
        # Fallback: use built-in chardet or default to utf-8
        try:
            import chardet
            raw_data = open(file_path, 'rb').read(100000)
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') if result else 'utf-8'
        except (ImportError, FileNotFoundError):
            # Final fallback: assume utf-8
            return 'utf-8'
```

#### Implementation Checklist

- [ ] **Step 1:** Edit `src/ingestion/encoding_detect.py`
  - Wrap in try-except
  - Add chardet fallback
  - Add final utf-8 fallback
  
- [ ] **Step 2:** Find all usages of `detect_encoding`
  ```bash
  grep -r "detect_encoding" tests/ src/
  ```
  
- [ ] **Step 3:** Test with missing dependency
  ```bash
  python3 -c "
  from src.ingestion.encoding_detect import detect_encoding
  result = detect_encoding('README.md')
  print(f'✓ Encoding detected: {result}')
  "
  ```
  
- [ ] **Step 4:** Validate with collection
  ```bash
  pytest tests/ --collect-only -q 2>&1 | grep -i "charset_normalizer"
  # Expected: 0 errors
  ```

#### Testing

```bash
# Test with charset_normalizer NOT installed
python3 -c "
from src.ingestion.encoding_detect import detect_encoding
result = detect_encoding('README.md')
print(f'✓ Fallback works: {result}')
"

# Test with a binary file
touch /tmp/test_binary
echo -e '\x80\x81\x82' > /tmp/test_binary
python3 -c "
from src.ingestion.encoding_detect import detect_encoding
result = detect_encoding('/tmp/test_binary')
print(f'✓ Binary file handled: {result}')
"
```

#### Estimated Time Breakdown
- Code analysis: 15 min
- Implementation: 30 min
- Testing: 45 min
- Code review: 30 min
- **Total: 2 hours**

#### Success Criteria
- [ ] Function works without charset_normalizer
- [ ] Function works with charset_normalizer
- [ ] All ingestion tests collect without error
- [ ] tests/phase6_wave1/test_batch_1_unit_tests.py passes
- [ ] tests/phase6_wave1/test_batch_3_error_paths.py passes

---

## PHASE B: HIGH-PRIORITY FIXES (Days 2-3, 4-6 hours)

### B1: Add pytest.importorskip() Guards to 122 Files

**Severity:** 🟡 P1 - STABILITY  
**Status:** Identified & Ready to Fix  
**Effort:** 4-6 hours (can parallelize)  
**Files Affected:** 122  
**Dependencies:** After A1, A2

#### Problem: Unguarded Optional Imports

**Current State (BAD):**
```python
# File: tests/rag/test_vector_search.py

import faiss  # ← Will fail if faiss not installed
from sentence_transformers import SentenceTransformer  # ← Same

def test_vector_search():
    # Test is hard-failed if deps missing
```

**Required State (GOOD):**
```python
# File: tests/rag/test_vector_search.py

import pytest

pytest.importorskip('faiss')
pytest.importorskip('sentence_transformers')

import faiss
from sentence_transformers import SentenceTransformer

def test_vector_search():
    # Test gracefully skipped if deps missing
```

#### List of 122 Affected Files

**By Package:**

| Package | Count | Example Files |
|---------|-------|----------------|
| faiss | 3 | test_cli_rag_offline.py, test_rag_end_to_end_pipeline.py |
| sentence_transformers | 2 | test_cli_rag_offline.py, test_rag_end_to_end_pipeline.py |
| mlflow | 4+ | test_app.py, test_cli_config_sweep.py, test_codex_logging.py |
| wandb | 2+ | test_cli_offline_bootstrap.py, test_codex_logging_degraded_warning.py |
| torch.distributed | 1 | test_readiness_remaining_modules.py |
| torch.profiler | 1+ | (various) |

#### Implementation Script

```bash
#!/bin/bash
# scripts/fix_import_guards.sh

# Function to add guards to a test file
add_guards() {
    local file=$1
    local deps=$2  # comma-separated: "faiss,sentence_transformers"
    
    # Read file into variable
    content=$(cat "$file")
    
    # Check if guards already present
    if echo "$content" | grep -q "pytest.importorskip"; then
        echo "  [SKIP] $file already has guards"
        return 0
    fi
    
    # Build guard statements
    guards=""
    IFS=',' read -ra arr <<< "$deps"
    for dep in "${arr[@]}"; do
        guards="$guards"$'\n'"pytest.importorskip('$dep')"
    done
    
    # Insert after imports
    updated=$(cat "$file" | awk -v guards="$guards" '
        BEGIN { printed = 0 }
        /^import / && !printed { print guards ""; printed = 1 }
        /^from / && !printed { print guards ""; printed = 1 }
        { print }
    ')
    
    echo "$updated" > "$file"
    echo "  [FIXED] $file"
}

# Example usage:
add_guards "tests/rag/test_vector_search.py" "faiss,sentence_transformers"
add_guards "tests/tracking/test_mlflow.py" "mlflow"
```

#### Manual Fix Template

For each affected file:

1. **Identify missing dependencies:**
   ```bash
   grep -E "^import |^from " tests/rag/test_vector_search.py
   # Output:
   # import faiss
   # from sentence_transformers import SentenceTransformer
   ```

2. **Add guards at top of file:**
   ```python
   import pytest
   
   pytest.importorskip('faiss')
   pytest.importorskip('sentence_transformers')
   
   # Then continue with normal imports
   import faiss
   from sentence_transformers import SentenceTransformer
   ```

3. **Test the change:**
   ```bash
   pytest tests/rag/test_vector_search.py --collect-only -v
   # Expected: Test collected (may be skipped if deps missing, but no error)
   ```

#### List of All Affected Files (122 total)

**Partial List (can be extracted from audit):**
```
tests/api/test_api_docs_build.py (wandb)
tests/api/test_app.py (mlflow)
tests/artifacts/test_attach_artifacts.py (mlflow)
tests/cli/test_cli_config_sweep.py (mlflow)
tests/cli/test_cli_offline_bootstrap.py (mlflow, wandb)
tests/rag/test_cli_rag_offline.py (faiss, sentence_transformers)
tests/codex/test_codex_best_effort.py (mlflow)
tests/logging/test_codex_logging.py (mlflow)
tests/logging/test_codex_logging_cfg.py (mlflow, wandb)
tests/logging/test_codex_logging_degraded_warning.py (mlflow, wandb)
tests/readiness/test_codex_ml_readiness_imports.py (mlflow, wandb)
tests/readiness/test_readiness_remaining_modules.py (faiss, mlflow, wandb, torch.distributed)
tests/rag/test_rag_end_to_end_pipeline.py (faiss, sentence_transformers)
... (109 more files)
```

#### Automated Fix Generation

```bash
#!/bin/bash
# Find all test files using optional imports and generate fixes

for package in "faiss" "sentence_transformers" "mlflow" "wandb"; do
    echo "=== Files using $package ==="
    grep -r "^import $package\|^from $package" tests/ --files-with-matches | while read file; do
        if ! grep -q "pytest.importorskip.*$package" "$file"; then
            echo "  $file"
        fi
    done
done
```

#### Validation

```bash
# After applying all fixes:

# 1. Check all guards present
python3 -c "
import ast
import pathlib

files_without_guards = []
for f in pathlib.Path('tests').rglob('*.py'):
    if f.name.startswith('test_'):
        with open(f) as fp:
            try:
                tree = ast.parse(fp.read())
                # Check for pytest.importorskip in first 10 lines
                # ...
            except:
                pass

print(f'Files still missing guards: {len(files_without_guards)}')
for f in files_without_guards:
    print(f'  {f}')
"

# 2. Verify graceful skip works
pytest tests/rag/ --collect-only -v 2>&1 | grep -c "SKIP"
# Expected: >0 (some tests should skip if deps missing)

# 3. Run with deps to ensure tests still work
pytest tests/rag/ -x --tb=short 2>&1 | tail -10
```

#### Estimated Time Breakdown
- Automated generation of guard statements: 1 hour
- Manual review & application: 2-3 hours
- Testing & validation: 1-2 hours
- Code review: 30 min
- **Total: 4-6 hours**

#### Parallelization Strategy
- Assign ~12 files per developer
- Each developer adds guards + tests their set
- Merge in batches to avoid conflicts

---

## PHASE C: STRUCTURAL IMPROVEMENTS (Day 3-4, 2-3 hours)

### C1: Add conftest.py to 261 Directories

**Severity:** 🟠 P2 - STRUCTURE  
**Status:** Identified & Ready to Fix  
**Effort:** 2-3 hours (scripted)  
**Directories Affected:** 261  
**Dependencies:** None (can run in parallel)

#### Problem: Incomplete Fixture Configuration

**Current State:** Only 35/295 directories have `conftest.py` (12% coverage)

**Impact:**
- Fixtures not inherited in child directories
- Inconsistent setup/teardown
- Missing pytest hooks

#### Solution: Template conftest.py

```python
# Template: tests/<subdir>/conftest.py

"""Pytest configuration for this test module.

This conftest.py provides:
- Fixture inheritance from parent directories
- Test-specific setup/teardown
- Module-specific pytest hooks
"""

import pytest
import sys
from pathlib import Path

# Inherit fixtures from parent conftest files
# (pytest automatically discovers these)
pytest_plugins = []
```

#### Implementation Script

```bash
#!/bin/bash
# scripts/add_conftest_files.sh

TEMPLATE='"""Pytest configuration for this test module."""
import pytest
'

# Find all directories with test files but no conftest.py
find tests -type f -name "test_*.py" -exec dirname {} \; | sort -u | while read dir; do
    if [ ! -f "$dir/conftest.py" ]; then
        echo "Creating conftest.py in $dir"
        cat > "$dir/conftest.py" << 'EOF'
"""Pytest configuration for this test module.

Provides:
- Fixture inheritance from parent directories
- Test-specific setup/teardown hooks
"""

import pytest
EOF
    fi
done
```

#### Implementation Checklist

- [ ] **Step 1:** Generate list of directories
  ```bash
  find tests -type f -name "test_*.py" -exec dirname {} \; | sort -u > /tmp/test_dirs.txt
  wc -l /tmp/test_dirs.txt  # Should be ~295
  ```

- [ ] **Step 2:** Create template conftest.py for each
  ```bash
  bash scripts/add_conftest_files.sh
  ```

- [ ] **Step 3:** Verify creation
  ```bash
  find tests -name "conftest.py" | wc -l
  # Expected: ~295 (up from 35)
  ```

- [ ] **Step 4:** Test fixture inheritance
  ```bash
  pytest tests/ --collect-only -q 2>&1 | tail -5
  # Expected: All tests still collect
  ```

#### Validation

```bash
# Check fixture inheritance works
pytest tests/unit/codex_ml/ -v --fixtures 2>&1 | head -20
# Expected: Fixtures from parent conftest available

# Run sample tests from multiple subdirectories
pytest tests/unit/ -x --tb=short
pytest tests/integration/ -x --tb=short
pytest tests/security/ -x --tb=short
```

#### Estimated Time Breakdown
- Generate directory list: 10 min
- Create template conftest files: 20 min (scripted)
- Verify & test: 30 min
- Code review: 20 min
- **Total: 1.5-2 hours**

#### Alternative: Minimal conftest

If template conftest causes issues, use minimal version:

```python
"""Test configuration."""
```

(Empty conftest still enables fixture inheritance from parent directories)

---

## PHASE D: VALIDATION & TESTING (Day 4, 2-3 hours)

### D1: Complete Collection Validation

**Effort:** 30 min - 1 hour

```bash
# D1.1: Collection baseline
echo "=== D1.1: Collection Baseline ==="
pytest tests/ --collect-only -q 2>&1 | tail -3
# Expected: "2714 tests collected" or similar

# D1.2: Error count
echo "=== D1.2: Error Count ==="
pytest tests/ --collect-only -q 2>&1 | grep -c "error"
# Expected: 0

# D1.3: Phase 6 Wave 1 collection
echo "=== D1.3: Phase 6 Wave 1 Collection ==="
pytest tests/phase6_wave1/ --collect-only -q 2>&1 | tail -3
# Expected: No errors, 10+ tests

# D1.4: Import safety check
echo "=== D1.4: Import Safety ==="
python3 -c "
from src.codex_ml.safety import moderation
from src.ingestion import encoding_detect
print('✓ All imports working')
"
```

### D2: Sample Test Execution

**Effort:** 1-2 hours

```bash
# D2.1: Unit tests
echo "=== D2.1: Unit Tests ==="
pytest tests/unit/ -x --tb=short -q 2>&1 | tail -10

# D2.2: Integration tests
echo "=== D2.2: Integration Tests ==="
pytest tests/integration/ -x --tb=short -q 2>&1 | tail -10

# D2.3: Security tests
echo "=== D2.3: Security Tests ==="
pytest tests/security/ -x --tb=short -q 2>&1 | tail -10

# D2.4: RAG tests (with graceful skip)
echo "=== D2.4: RAG Tests (Optional) ==="
pytest tests/rag/ --tb=short -v 2>&1 | grep -E "PASSED|SKIPPED|FAILED" | head -20
```

### D3: Regression Check

**Effort:** 30 min

```bash
# Compare with baseline
pytest tests/ --co -q > /tmp/final_collect.txt
diff /tmp/baseline_collect.txt /tmp/final_collect.txt
# Expected: No significant differences (may have fewer errors)
```

---

## Timeline & Schedule

### Recommended Timeline

```
Day 1 (Wednesday, 4 hours):
  08:00 - 08:30: Task A1 analysis
  08:30 - 09:30: Task A1 implementation
  09:30 - 10:00: Task A1 testing
  10:00 - 10:30: Task A2 analysis
  10:30 - 11:30: Task A2 implementation
  11:30 - 12:00: Task A2 testing
  12:00 - 12:30: Validation of A1+A2
  12:30 - 13:00: Code review & fixes

Day 2 (Thursday, 6 hours):
  09:00 - 10:00: Task B1 setup (identify all files)
  10:00 - 12:00: Batch 1 fixes (40 files)
  12:00 - 13:00: Testing batch 1
  13:00 - 14:00: Batch 2 fixes (40 files)
  14:00 - 15:00: Testing batch 2
  15:00 - 16:00: Batch 3 fixes (42 files) + testing

Day 3 (Friday, 3 hours):
  09:00 - 09:30: Task C1 setup
  09:30 - 10:00: Generate conftest files
  10:00 - 10:30: Verify creation
  10:30 - 11:00: Testing
  11:00 - 12:00: Documentation & review

Day 4 (Monday, 3 hours):
  09:00 - 10:30: Full validation suite (D1 + D2 + D3)
  10:30 - 11:00: Fix any issues found
  11:00 - 12:00: Final testing & documentation
```

---

## Success Criteria Summary

### Phase A (Critical)
- [ ] pytest test collection succeeds (0 errors)
- [ ] All tests in phase6_wave1 collect without import errors
- [ ] prometheus_client import chain fixed
- [ ] charset_normalizer import chain fixed

### Phase B (High Priority)
- [ ] All 122 files have pytest.importorskip() guards
- [ ] Tests gracefully skip when optional deps missing
- [ ] No hard failures on missing optional packages

### Phase C (Structural)
- [ ] 261 directories now have conftest.py files
- [ ] Total conftest.py count: ~295 (was 35)
- [ ] Fixture inheritance working correctly

### Phase D (Validation)
- [ ] Full test collection: 2,714 tests collected
- [ ] Zero collection errors
- [ ] Sample test runs pass (unit, integration, security)
- [ ] No regressions vs baseline

---

## Resource Requirements

### Personnel
- **Task A1-A2:** 1 developer (4 hours)
- **Task B1:** 2-3 developers (4-6 hours, parallelizable)
- **Task C1:** 1 developer (2-3 hours, highly scripted)
- **Task D1-D3:** 1 developer (2-3 hours)

**Total Person-Hours:** 18-22 hours  
**Parallel Days:** 4 days (with 2-3 devs on B1)

### Infrastructure
- Python 3.12+ environment
- pytest 9.0.3+
- Git repository access
- Basic bash scripting

---

## Risk Mitigation

### Risk 1: Lazy Import Breaking Something
**Likelihood:** Low | **Impact:** Medium  
**Mitigation:**
- Test both with and without prometheus_client installed
- Run full test suite after merge
- Keep original code backed up

### Risk 2: pytest.importorskip() Not Working
**Likelihood:** Very Low | **Impact:** Low  
**Mitigation:**
- Validate with sample file first
- Check pytest version (9.0.3+ required)
- Review pytest documentation

### Risk 3: Circular Import After Lazy Import
**Likelihood:** Low | **Impact:** High  
**Mitigation:**
- Run full import test suite
- Check for import cycles: `python3 -m py_compile src/codex_ml/safety/moderation.py`
- Profile import times

### Risk 4: Missing Conftest Breaking Fixtures
**Likelihood:** Medium | **Impact:** Low  
**Mitigation:**
- Use template conftest (minimal, just enables inheritance)
- Test in small batches
- Keep original conftest setup as fallback

---

## Appendix: Quick Command Reference

```bash
# Collect all test files
find tests -name "test_*.py" | wc -l

# Find unguarded imports
grep -r "^import faiss\|^import mlflow\|^import wandb" tests/ | \
  grep -v "pytest.importorskip"

# List directories without conftest
find tests -type f -name "test_*.py" -exec dirname {} \; | sort -u | \
  while read d; do [ ! -f "$d/conftest.py" ] && echo "$d"; done | wc -l

# Validate fixes
pytest tests/phase6_wave1/ --collect-only -q 2>&1 | tail -3
python3 -c "from src.codex_ml.safety import moderation; print('✓')"
python3 -c "from src.ingestion import encoding_detect; print('✓')"

# Full validation
pytest tests/ --collect-only -q 2>&1 | tail -1
```

---

*End of Prioritized Fix List*
