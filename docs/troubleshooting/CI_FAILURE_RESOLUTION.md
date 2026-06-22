# 🚨 CI Failure Resolution Guide

> **Last Updated:** 2026-02-10
> **Status:** Active Reference Document

This guide documents common CI/CD pipeline failures and their resolutions, with a focus on the GitHub Actions workflows in the Aries-Serpent/_codex_ repository.

---

## Incident Report: Missing JSON Import (Job #61098313515)

### Problem Summary

| Field | Value |
|-------|-------|
| **Date** | 2026-01-22 |
| **Workflow** | `rust_swarm_ci.yml` |
| **Job** | `rust_tests` |
| **Error** | `NameError: name 'json' is not defined` |
| **Impact** | 5 jobs blocked, deployment halted |
| **Resolution** | Added missing `import json` statement |

### Symptoms

```
Traceback (most recent call last):
  File "scripts/ci/validate_cargo_features.py", line 71, in validate_cargo_features
    f"{k} = {json.dumps(v)}" if isinstance(v, list) else f"{k} = {v}"
NameError: name 'json' is not defined
```

### Root Cause Analysis

Line 71 in `scripts/ci/validate_cargo_features.py` used `json.dumps()` to serialize feature lists without importing the `json` module at the top of the file.

**Before (Broken):**
```python
import sys
import re
from pathlib import Path
from typing import List, Tuple

# json was NOT imported!
```

**After (Fixed):**
```python
import json  # ← Added this line
import re
import sys
from pathlib import Path
from typing import List, Tuple
```

## Cascading Failures

This single missing import caused a cascade of failures:

1. ❌ `rust_tests` - FAILED (script crashed)
2. ⏭️ `code_coverage` - SKIPPED (depends on rust_tests)
3. ⏭️ `python_integration` - SKIPPED (depends on rust_tests)
4. ❌ `status_check` - FAILED (depends on skipped jobs)
5. 🚫 **Deployment blocked**

### Solution Implemented

1. **Immediate Fix:** Added `import json` at line 12
2. **Code Quality:** Applied Black formatting and Ruff linting
3. **Testing:** Created 21 unit tests + 8 integration tests
4. **Prevention:** Documented in this troubleshooting guide

---

## Prevention Measures

### 1. Pre-commit Hooks

The repository uses pre-commit hooks that can catch missing imports:

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Specifically check for import issues
flake8 --select=F401,F811,F821 scripts/
```

## 2. Local Testing

Always test CI scripts locally before pushing:

```bash
# Run the validation script locally
python scripts/ci/validate_cargo_features.py

# Run the test suite
pytest tests/ci/test_validate_cargo_features.py -v
```

## 3. Integration Testing

Run integration tests that simulate the CI environment:

```bash
pytest tests/integration/test_ci_validation_workflow.py -v
```

---

## Troubleshooting Flowchart

```
CI Job Fails
     │
     ▼
Check Error Type
     │
     ├── NameError ──────────────► Missing Import
     │                                   │
     │                                   ▼
     │                            Add import statement
     │                                   │
     │                                   ▼
     │                            Run local validation
     │                                   │
     │                                   ▼
     │                            Execute unit tests
     │                                   │
     │                                   ▼
     │                            Push to feature branch
     │                                   │
     │                                   ▼
     │                            CI Passes? ─── No ──► Review logs, iterate
     │                                   │
     │                                  Yes
     │                                   │
     │                                   ▼
     │                              Merge PR
     │
     ├── ModuleNotFoundError ────► Missing Dependency
     │                                   │
     │                                   ▼
     │                            Add to requirements.txt
     │
     ├── SyntaxError ────────────► Code Syntax Issue
     │                                   │
     │                                   ▼
     │                            Run python -m py_compile
     │
     ├── unexpected cfg condition ─► Rust Feature Missing
     │                                   │
     │                                   ▼
     │                            Add feature to Cargo.toml
     │                                   │
     │                                   ▼
     │                            Run validation script
     │
     └── Other ──────────────────► Check workflow logs
                                         │
                                         ▼
                                   Analyze error message
```

---

## Common CI Failures and Solutions

### 1. Python Import Errors

**Symptom:** `NameError: name 'X' is not defined` or `ModuleNotFoundError`

**Solution:**
1. Check imports at the top of the file
2. Ensure all used modules are imported
3. Verify dependencies are in requirements.txt
4. Run `flake8 --select=F401,F811,F821` to detect issues

### 2. TOML Parsing Failures

**Symptom:** Script fails when parsing Cargo.toml or other TOML files

**Solution:**
1. Ensure `tomllib` (Python 3.12+) or `tomli` fallback is available
2. Check TOML syntax with `python -c "import tomllib; tomllib.load(open('file.toml', 'rb'))"`

### 3. Rust Build Failures

**Symptom:** `cargo build` or `cargo test` fails

**Solution:**
1. Check Cargo.toml for missing features
2. Run `cargo fmt --check` for formatting
3. Run `cargo clippy` for linting
4. Verify Cargo.lock is up to date

### 4. Rust Feature Configuration Errors

**Symptom:** `unexpected cfg condition value: "feature_name"` during clippy

**Solution:**
1. Add the missing feature to `Cargo.toml` `[features]` section
2. Run validation script: `python scripts/ci/validate_cargo_features.py`
3. Ensure feature dependencies are correct (e.g., `python = ["extension-module"]`)
4. For PyO3 projects, ensure `extension-module` depends on `pyo3/extension-module`

**Example Fix:**
```toml
[features]
default = []
python = ["extension-module"]
extension-module = ["pyo3/extension-module"]
```

### 5. Workflow Permission Issues

**Symptom:** `Resource not accessible by integration`

**Solution:**
1. Check workflow permissions block
2. Ensure proper `permissions:` configuration
3. See [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)

---

## Related Files

| File | Purpose |
|------|---------|
| `.github/workflows/rust_swarm_ci.yml` | Main Rust-Python CI workflow |
| `scripts/ci/validate_cargo_features.py` | Cargo.toml validation script |
| `tests/ci/test_validate_cargo_features.py` | Unit tests for validation |
| `tests/integration/test_ci_validation_workflow.py` | Integration tests |

---

## Support

If you encounter a CI failure not covered in this guide:

1. Check the workflow logs in GitHub Actions
2. Search existing issues for similar problems
3. Create a new issue with the `ci-failure` label
4. Include:
   - Workflow name and job name
   - Error message
   - Steps to reproduce
   - Any relevant logs

---

## Incident Report: Rust cfg Feature Validation Failure (Batch CI Triage #3106)

### Problem Summary

| Field | Value |
|-------|-------|
| **Date** | 2026-01-19 |
| **Batch Report** | Issue #3106 |
| **Workflow** | `rust_swarm_ci.yml` |
| **Job** | `rust_tests` |
| **Error** | `unexpected cfg condition value: "python"` |
| **Impact** | 10 CI failures across multiple issues |
| **Resolution** | Added proper Cargo.toml features configuration |

### Symptoms

```
error: unexpected `cfg` condition value: `python`
  --> src/lib.rs:47:7
   |
47 | #[cfg(feature = "python")]
   |       ^^^^^^^^^^^^^^^^^^
   |
   = note: expected values for `feature` are: `default`
   = help: consider adding `python` as a feature in `Cargo.toml`
```

### Root Cause Analysis

The Rust source code (`src/lib.rs`) used `#[cfg(feature = "python")]` conditional compilation attributes, but the `python` feature was not properly declared in `Cargo.toml`. When `cargo clippy --all-targets --all-features --locked -- -D warnings` ran in CI, the `-D warnings` flag promoted this warning to an error.

**Before (Broken):**
```toml
[features]
default = []
# python feature was missing!
```

**After (Fixed):**
```toml
[features]
default = []
python = ["extension-module"]
extension-module = ["pyo3/extension-module"]
```

## Affected Issues

The following 10 issues were part of the batch failure group:
- #2915, #2914, #2913, #2912, #2910, #2909, #2908, #2907, #2906, #2905

### Solution Implemented

1. **Immediate Fix:** Added `python` and `extension-module` features to `Cargo.toml`
2. **Prevention Script:** Created `scripts/ci/validate_cargo_features.py`
3. **CI Integration:** Added validation step to `rust_swarm_ci.yml`
4. **Testing:** Added comprehensive tests in `tests/ci/test_validate_cargo_features.py`

### Reusable Pattern: Feature Configuration Validation

This incident established a reusable pattern for preventing similar Rust feature configuration issues:

#### Pattern: Pre-flight Cargo.toml Validation

**Purpose:** Validate that all features used in Rust source code are declared in `Cargo.toml`

**Implementation:**
1. **Validation Script** (`scripts/ci/validate_cargo_features.py`):
   - Parses `Cargo.toml` to extract declared features
   - Scans `src/lib.rs` for `#[cfg(feature = "X")]` usages
   - Reports any undeclared features as errors

2. **CI Integration** (`.github/workflows/rust_swarm_ci.yml`):
   ```yaml
   - name: Validate Cargo.toml features
     run: python scripts/ci/validate_cargo_features.py
   ```

3. **Key Validations:**
   - `[features]` section exists
   - `python` feature declared (for PyO3 bindings)
   - `extension-module` feature depends on `pyo3/extension-module`
   - All `#[cfg(feature = "X")]` features in source code are declared

**When to Apply:**
- Any Rust project using conditional compilation
- PyO3 Python extensions
- Multi-feature library crates
- Projects running clippy with `-D warnings`

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1.0 | 2026-02-02 | Copilot | Added Rust cfg feature validation failure incident (#3106) |
| 1.0.0 | 2026-01-22 | Copilot | Initial creation after fixing json import issue |
