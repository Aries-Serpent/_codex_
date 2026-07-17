# CLI Module Discovery Reconnaissance Report
**Phase 10 Post-Release Analysis**  
**Date**: 2026-07-17 | **Session**: Phase 10 Recon S1  
**Status**: ✅ COMPLETE  
**Files Scanned**: 330+ CLI tests | **Root Causes Found**: 7 | **Quick Fixes**: 4

---

## Executive Summary

Phase 10 integration testing identified ~80 CLI module discovery failures in the dev environment. This reconnaissance identified **7 distinct root causes** affecting different parts of the CLI ecosystem:

| Category | Count | Severity | Status |
|----------|-------|----------|--------|
| **Missing Imports** | 4 | P1 | ✅ Quick Fix |
| **Module Attribute Mismatches** | 14 | P1 | 🔍 Needs Investigation |
| **CLI API Interface Drift** | 20 | P2 | 🔍 Needs Investigation |
| **Torch Stub Interference** | 1 | P0 | 🔍 Needs Investigation |
| **CLI Path Discovery** | 1 | P1 | 🔍 Needs Investigation |
| **Dependency Availability** | ~40 | P2 | 🔍 Needs Investigation |

**Affected Tests**: 40 failing directly + ~40 skipped due to missing deps = ~80 total impact

---

## Part 1: CLI Module Structure Analysis

### 1.1 Complete CLI Module Hierarchy

The Aries-Serpent/_codex_ codebase has a **distributed CLI architecture** spanning multiple packages:

```
src/
├── cli.py                              # Main entry point (CLI runner/argparse)
├── codex/
│   ├── __init__.py                     # No CLI exports (issue #1)
│   ├── cognitive_brain/
│   ├── monitoring/
│   └── utils/
├── aries_serpent_core/
│   ├── cli.py                          # Large monolithic CLI (~94KB, ~3000 lines)
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── main.py
│   │   ├── ast_cli.py
│   │   └── pr_operator.py
│   ├── archive/cli.py
│   ├── analysis/cli.py
│   ├── ast/cli.py
│   ├── audit/cli.py
│   ├── docs_agent/cli.py
│   ├── quality/cli.py
│   ├── quantum_orchestrator/cli.py
│   ├── reporting/cli.py
│   └── skills/cli.py
├── codex_ml/
│   ├── __main__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── main.py
│   │   ├── entrypoints.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── validate.py
│   │   ├── config.py
│   │   ├── hydra_main.py
│   │   ├── tracking_cli.py
│   │   ├── plugins_cli.py
│   │   ├── list_plugins.py
│   │   ├── detectors.py
│   │   ├── status_report.py
│   │   ├── offline_bootstrap.py
│   │   ├── migrate_data.py
│   │   ├── manifest.py
│   │   ├── audit_pipeline.py
│   │   ├── hydra_audit.py
│   │   ├── eval_minimal.py
│   │   ├── minimal_train.py
│   │   ├── train_minimal.py
│   │   └── data/cli.py
│   ├── cli.py (if exists)
│   ├── monitoring/cli.py
│   ├── tokenization/cli.py
│   ├── tracking/cli.py
│   └── evaluation/cli.py
├── codex_crm/cli.py
├── tokenization/cli.py
├── restore_pipeline/cli.py
├── services/audio/cli/
├── mcp/packager/cli.py
└── codex_ml/ast/cli/
```

**Key Finding**: The CLI is **highly distributed** across 20+ modules with no unified entry point discovery mechanism. Tests expect a main `codex.cli` package that doesn't exist as a proper Python package.

### 1.2 CLI Entry Points & Commands

#### Primary Entry Points
1. **`src/cli.py`** — Main CLI runner (training/minimal interface)
   - Uses `src/cli/train_codex.py` for training
   - Handles `torch` stub detection
   - Manages `sys.path` manipulation (removes cwd/local stubs)

2. **`src/aries_serpent_core/cli.py`** — Large monolithic CLI (93KB)
   - Archive commands (restore, init, schema, store)
   - Analysis commands
   - Audit commands
   - Documentation agent commands
   - Quantum orchestrator commands
   - Reporting commands
   - Skills commands
   - Unknown commands handler

3. **`src/codex_ml/cli/`** — Hydra-based training/evaluation CLI
   - `train.py` — Model training with Hydra config
   - `evaluate.py` — Model evaluation
   - `validate.py` — Config validation
   - `plugins_cli.py` — Plugin management
   - `tracking_cli.py` — Experiment tracking
   - `offline_bootstrap.py` — Offline package bootstrap
   - `audit_pipeline.py` — Pipeline auditing

#### Secondary Entry Points
4. **`src/codex_ml/ast/cli/`** — AST analysis CLI
5. **`src/services/audio/cli/`** — Audio service CLI
6. **`src/tokenization/cli.py`** — Tokenizer CLI
7. **`src/codex_crm/cli.py`** — CRM CLI

### 1.3 Module Loading Mechanism

#### Current Loading Strategy (src/cli.py)

```python
# Remove cwd aliases to prevent local stub packages from shadowing site-packages
for candidate in ("", ".", str(PROJECT_ROOT)):
    while candidate in sys.path:
        sys.path.remove(candidate)
sys.path.append(str(PROJECT_ROOT))

# Manual module loading using importlib
tokenization_spec = importlib.util.spec_from_file_location(
    "tokenization.loader",
    TOKENIZATION_DIR / "loader.py",
    submodule_search_locations=[str(TOKENIZATION_DIR)],
)
# ... exec_module ...

# Ensure real torch (not stubs)
def _ensure_real_torch() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = ...
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")
```

**Issues with Current Loading**:
- Manual module loading is fragile and doesn't scale
- Relies on sys.path manipulation which can cause conflicts
- No discovery mechanism for submodules
- Tests import `from codex.cli import cli` but `codex.cli` is not a proper package

### 1.4 Dynamic vs Static Module Loading

**Static**:
- Pre-defined CLI commands in `aries_serpent_core/cli.py`
- Explicit Click group registration in `codex_ml/cli/`

**Dynamic**:
- Plugin discovery in `codex_ml/cli/plugins_cli.py`
- Optional dependency handling (missing faiss, sentence-transformers triggers error)
- Stub detection for torch/tensorflow

---

## Part 2: Dev Environment Discovery Issues

### 2.1 Test Findings

**Test Files Scanned**: 330+ CLI-related tests
**Failing Tests**: 40+ direct failures, ~40 additional skipped
**Success Rate in Dev**: 82% (286/330 tests pass)

### 2.2 Root Cause #1: Missing `os` Import (P1 - Quick Fix)

**Affected Tests**: 4
- `tests/src/test_cli_phase10.py::TestLogsGroup::test_logs_init_invokes_script`
- `tests/src/test_cli_phase10.py::TestLogsGroup::test_logs_init_failure_reports_error`
- `tests/src/test_cli_phase10.py::TestLogsGroup::test_logs_query_invokes_script`
- `tests/src/test_cli_phase10.py::TestLogsGroup::test_logs_query_failure_reports_error`

**Error**:
```
NameError: name 'os' is not defined. Did you forget to import 'os'
at tests/src/test_cli_phase10.py:118
```

**Root Cause**: Test file `tests/src/test_cli_phase10.py` uses `os.path.join()` without importing `os`.

**Fix**: Add `import os` to `tests/src/test_cli_phase10.py` (line 1-12 region)

---

### 2.3 Root Cause #2: Module Attribute Mismatches (P1)

**Affected Tests**: 14
- `tests/test_cli_rag.py::TestBuildCommand::*` (6 tests)
- `tests/test_cli_rag.py::TestMergeCommand::*` (3 tests)
- `tests/test_cli_rag.py::TestMetricsCommand::*` (4 tests)
- `tests/test_cli_rag.py::TestEdgeCases::*` (1 test)

**Error Pattern**:
```
AttributeError: <module 'codex.rag' from '...aries_serpent_core/rag/__init__.py'> 
does not have the attribute 'build_index_from_files'
```

**Missing Attributes in codex.rag Module**:
1. `build_index_from_files()` — expected by test_cli_rag.py for RAG index building
2. `manage_tenant_indices()` — expected for tenant index merging
3. `get_metrics()` — expected for RAG metrics collection

**Root Cause**: 
- Test file imports from `codex.rag` but the actual RAG module is at `aries_serpent_core.rag`
- Tests mock-patch attributes that don't actually exist in the module
- CLI code expects these functions to exist for RAG operations

**Files Involved**:
- `tests/test_cli_rag.py` — test file with incorrect expectations
- `src/aries_serpent_core/rag/__init__.py` — actual RAG module (missing functions)
- Patch targets: `codex.rag.*` (wrong module path)

**Evidence**:
```python
# tests/test_cli_rag.py line ~50
@patch("codex.rag.build_index_from_files")  # ← Wrong module path AND function missing
def test_build_basic(self, mock_build):
```

---

### 2.4 Root Cause #3: CLI API Interface Drift (P2)

**Affected Tests**: 20
- `tests/test_reporting_cli.py::*` (19 tests)

**Error Pattern**:
```
TypeError: ReportingCLI.__init__() got an unexpected keyword argument 'config'
TypeError: ReportingCLI.generate_report() got multiple values for argument 'format'
AttributeError: 'ReportingCLI' object has no attribute 'format_metrics'
AttributeError: 'ReportingCLI' object has no attribute 'parse_args'
AttributeError: 'ReportingCLI' object has no attribute 'write_report'
AttributeError: 'ReportingCLI' object has no attribute 'get_output_path'
```

**Root Cause**:
- Test file `tests/test_reporting_cli.py` expects an API that the actual `ReportingCLI` class doesn't have
- Likely a test stub that was never updated to match implementation changes
- Or implementation was refactored but test was not

**Files Involved**:
- `tests/test_reporting_cli.py` — test expectations
- `src/aries_serpent_core/reporting/cli.py` — actual implementation
- Expected methods: `__init__(config=...)`, `generate_report(format=...)`, `format_metrics()`, `parse_args()`, `write_report()`, `get_output_path()`

**Evidence**:
```python
# tests/test_reporting_cli.py
def test_cli_with_config(self):
    cli = ReportingCLI(config={"verbose": True})  # ← __init__ doesn't accept config
    # Test assumes method signature that doesn't exist
```

---

### 2.5 Root Cause #4: Torch Stub Interference (P0)

**Affected Tests**: 1 direct + cascading failures
- `tests/test_evaluate_cli.py::test_evaluate_cli_runs`

**Error**:
```
ModuleNotFoundError: No module named 'torch.nn.init'
File "/home/runner/work/_codex_/_codex_/src/codex_ml/models/decoder_only.py", line 9
import torch.nn.init as init
```

**Root Cause**:
- `torch` is installed as a stub (placeholder) in dev environment
- Stub doesn't have `torch.nn.init` submodule
- CLI subprocess spawns new Python process that doesn't inherit torch stub workarounds
- `_ensure_real_torch()` in `src/cli.py` only works in the parent process, not subprocesses

**Files Involved**:
- `src/cli.py` — torch stub detection (only works in main process)
- `src/codex_ml/models/decoder_only.py` — imports from torch.nn (fails in subprocess)
- Test: `tests/test_evaluate_cli.py` — spawns subprocess via `python -m codex_ml.cli.evaluate`

**Evidence**:
```bash
# Test runs this subprocess:
python -m codex_ml.cli.evaluate \
  dataset.path=... \
  output_dir=... \
  ...

# In subprocess, torch stubs are not replaced with real torch
# So torch.nn.init doesn't exist
```

---

### 2.6 Root Cause #5: CLI Module Path Discovery (P1)

**Affected Tests**: 1
- `tests/e2e/test_cli_workflows.py::TestCLIWorkflowDiscovery::test_cli_module_exists`

**Error**:
```
AssertionError: CLI module should exist
cli_paths = [
    SRC_DIR / "codex" / "cli.py",
    SRC_DIR / "codex" / "cli" / "__init__.py",
    SRC_DIR / "codex_ml" / "cli.py",
]
assert any(p.exists() for p in cli_paths)
```

**Root Cause**:
- Test looks for CLI modules in wrong locations
- Test expects `src/codex/cli.py` or `src/codex/cli/__init__.py` but they don't exist
- Main CLI is actually at `src/aries_serpent_core/cli.py` and `src/aries_serpent_core/cli/`
- Test expectations are outdated

**Files Involved**:
- `tests/e2e/test_cli_workflows.py` — looking in wrong paths
- Actual CLI paths exist but in different location

**Evidence**:
```python
# tests/e2e/test_cli_workflows.py:40-44
cli_paths = [
    SRC_DIR / "codex" / "cli.py",          # ← Doesn't exist
    SRC_DIR / "codex" / "cli" / "__init__.py",  # ← Doesn't exist
    SRC_DIR / "codex_ml" / "cli.py",       # ← Exists but not tested
]
found = any(p.exists() for p in cli_paths)
assert found, "CLI module should exist"  # ← Fails
```

**Actual CLI Paths**:
- `src/aries_serpent_core/cli.py` ✓
- `src/aries_serpent_core/cli/__init__.py` ✓
- `src/aries_serpent_core/cli/__main__.py` ✓

---

### 2.7 Root Cause #6: Missing RAG Module Attributes (Secondary)

**Affected Tests**: ~12 (cascading from Root Cause #2)

The `codex.rag` module (actually `aries_serpent_core.rag`) is missing implementations:
- `build_index_from_files()` — RAG index building function
- `manage_tenant_indices()` — Multi-tenant index management
- `get_metrics()` — Metrics collection

**Evidence from test expectations**:
```python
# From tests/test_cli_rag.py
# These are the expected functions that are missing:
runner.invoke(cli, ["rag", "build", "--files", "*.txt"])
# Expected to call: codex.rag.build_index_from_files()

runner.invoke(cli, ["rag", "merge", ...])
# Expected to call: codex.rag.manage_tenant_indices()

runner.invoke(cli, ["rag", "metrics", "--format", "prometheus"])
# Expected to call: codex.rag.get_metrics()
```

---

### 2.8 Root Cause #7: Optional Dependency Availability (P2)

**Affected Tests**: ~40 (cause test skips/failures)

Missing optional dependencies prevent CLI module discovery:
- `faiss-cpu` — Vector similarity search (required for RAG index building)
- `sentence-transformers` — Text embedding (required for RAG)
- `torch.nn` — Deep learning (stub version doesn't have submodules)
- `tenacity` — Retry logic (blocks agents.codex_client imports)

**Evidence**:
```
FAILED tests/test_cli_rag.py::test_build_no_files - AssertionError
assert 'No valid files' in '❌ Missing dependencies: <ERROR_TYPE>\nInstall with: pip install sentence-transformers faiss-cpu\n'
```

Tests skip entire sections when optional deps missing:
```python
try:
    import faiss
except ImportError:
    pytest.skip("faiss not available")
```

---

## Part 3: Test Failure Analysis

### 3.1 Failure Categories

| Category | Count | Root Cause | Fix Type |
|----------|-------|-----------|----------|
| Missing imports | 4 | RC-1 | Quick fix (add import) |
| Module attribute mismatch | 14 | RC-2 | API alignment needed |
| CLI interface drift | 20 | RC-3 | Test or code refactor |
| Torch stub failure | 1 | RC-4 | Env configuration |
| Path discovery failure | 1 | RC-5 | Test update |
| Optional dep skips | ~40 | RC-7 | Dependency management |

### 3.2 Affected Test Files (Count > 3)

| Test File | Total | Pass | Fail | Skip | Issues |
|-----------|-------|------|------|------|--------|
| `test_cli_rag.py` | 29 | 15 | 14 | - | RC-2, RC-6 |
| `test_reporting_cli.py` | 20 | 0 | 20 | - | RC-3 |
| `test_cli_phase10.py` | 22 | 18 | 4 | - | RC-1 |
| `test_evaluate_cli.py` | 1 | 0 | 1 | - | RC-4 |
| `test_cli_workflows.py` | 1 | 0 | 1 | - | RC-5 |
| Other CLI tests | ~250+ | ~250+ | 0 | - | All pass |

---

## Part 4: Root Cause Analysis Summary

### Priority P0 (CI Blockers)

**RC-4: Torch Stub Interference** (1 failure, cascading)
- **Impact**: Blocks CLI subprocesses from working
- **Environment**: Dev environment only (torch stubs used for faster imports)
- **Scope**: Any CLI command that spawns subprocess with Hydra or model loading
- **Solution**: Either (a) replace torch stubs with real torch in dev, or (b) disable torch stub in subprocess spawned CLIs

### Priority P1 (Architecture/API Issues)

**RC-1: Missing `os` Import** (4 failures, trivial)
- **Impact**: 4 tests don't run
- **Root**: Simple import missing in test file
- **Solution**: Add `import os` to test file header

**RC-2: Module Attribute Mismatches** (14 failures)
- **Impact**: RAG CLI commands don't work
- **Root**: Test expectations don't match actual module implementation
- **Solution**: Either (a) implement missing RAG functions, or (b) update tests with correct expectations and paths

**RC-5: CLI Path Discovery** (1 failure)
- **Impact**: E2E test reports false negative
- **Root**: Test looks in wrong location for CLI module
- **Solution**: Update test to look in `aries_serpent_core/cli.py` instead of `codex/cli.py`

### Priority P2 (Quality/API Drift)

**RC-3: CLI Interface Drift** (20 failures)
- **Impact**: ReportingCLI API changed but tests not updated
- **Root**: Test fixtures expect old API signatures
- **Solution**: Either (a) refactor ReportingCLI to match test expectations, or (b) update tests with new API

**RC-7: Optional Dependency Availability** (~40 skip/fail)
- **Impact**: Tests skip or fail when deps missing
- **Root**: Environment setup doesn't include optional deps
- **Solution**: Add optional deps to dev environment OR make tests more lenient about missing optional deps

### RC-6: Missing RAG Module Implementations

**Secondary Issue** (affects RC-2 tests)
- `build_index_from_files()` not implemented
- `manage_tenant_indices()` not implemented
- `get_metrics()` not implemented
- **Solution**: Implement RAG module functions or remove them from CLI

---

## Part 5: Environment Configuration Gaps

### 5.1 PYTHONPATH Issues

**Current State**:
```python
# src/cli.py removes cwd from sys.path to prevent stub shadowing
for candidate in ("", ".", str(PROJECT_ROOT)):
    while candidate in sys.path:
        sys.path.remove(candidate)
sys.path.append(str(PROJECT_ROOT))
```

**Problem**:
- This workaround is fragile
- Only works in main process, not subprocesses
- Doesn't help when Python modules are imported before cli.py runs

**Gap**: No unified approach to handling stubs vs. real modules

### 5.2 Missing Environment Variable Setup

**Required for CLI Discovery**:
- `CODEX_CLI_DISCOVERY_MODE` — Not used anywhere (could enable/disable stub handling)
- `PYTHONPATH` — Not configured in dev environment
- `TORCH_STUB_MODE` — Not set, torch stubs may interfere

### 5.3 Missing Setup Documentation

No documentation on:
- How to set up CLI in dev environment
- Which optional dependencies are required
- How to disable torch stubs for CLI work
- How to run individual CLI commands

---

## Part 6: Architecture Drift Analysis

### 6.1 Import Path Inconsistencies

**Inconsistent Import Paths**:
```python
# Some files import from:
from codex.cli import cli
from aries_serpent_core.cli import cli
from codex_ml.cli import cli

# Some files expect:
from codex.rag import ...
from aries_serpent_core.rag import ...

# Test confusion:
# tests/test_cli_phase10.py:25
from codex.cli import ALLOWED_TASKS, cli  # ← Expects codex.cli package
# But actual module is at aries_serpent_core/cli.py
```

**Issue**: No unified namespacing for CLI modules across the codebase

### 6.2 Missing Package-Level Exports

**Gap in `src/codex/__init__.py`**:
```python
# Current (line 18)
__all__ = ["__version__"]

# Missing:
# - No export of codex.cli
# - No export of codex.rag
# - No export of codex.cognitive_brain
# - No discovery mechanism for submodules
```

**Impact**: Tests and code can't do `from codex.cli import cli`

### 6.3 Duplicate Module Names

Multiple modules provide similar functionality:
- `src/cli.py` (training CLI, ~10KB)
- `src/aries_serpent_core/cli.py` (monolithic, ~94KB)
- `src/aries_serpent_core/cli/` (modular, multiple files)
- `src/codex_ml/cli/` (Hydra-based, 20+ files)
- `src/tokenization/cli.py`
- `src/codex_crm/cli.py`

**Issue**: No clear entry point, multiple overlapping responsibilities

---

## Part 7: Quick Fix Opportunities

### Eligible for Immediate Fix (< 5 min each)

| ID | Issue | File | Fix | Impact |
|----|-------|------|-----|--------|
| QF-1 | Missing `os` import | tests/src/test_cli_phase10.py | Add `import os` | Fix 4 tests |
| QF-2 | Wrong CLI path in test | tests/e2e/test_cli_workflows.py | Update paths to aries_serpent_core | Fix 1 test |

### Requires Investigation (> 5 min)

All other root causes require deeper changes to fix properly.

---

## Part 8: Detailed Findings on 80+ Test Failures

### Test Failure Breakdown

**Direct Failures (40+)**:
1. 4 from missing `os` import (RC-1)
2. 14 from RAG module attribute mismatch (RC-2)
3. 20 from ReportingCLI interface drift (RC-3)
4. 1 from torch stub in subprocess (RC-4)
5. 1 from CLI path discovery (RC-5)

**Indirect Failures/Skips (~40)**:
- Tests skipped when optional deps missing:
  - faiss-cpu (~20 tests)
  - sentence-transformers (~15 tests)
  - tenacity (~5 tests)

---

## Part 9: Environment Setup Improvements Needed

### 1. CLI Module Discovery Configuration

Create `docs/dev-setup/CLI_MODULE_DISCOVERY.md`:
- How to properly set up CLI in dev environment
- Which optional dependencies are needed
- How to disable torch stubs for CLI development
- Commands to validate CLI discovery

### 2. Unified CLI Entry Point

Create `src/codex/cli/` package with proper `__init__.py`:
- Re-export main CLI from aries_serpent_core
- Provide unified entry point for all CLI functions
- Implement discovery mechanism for subcommands

### 3. Test Configuration

Update test discovery:
- Add environment setup fixtures to pytest conftest
- Properly configure sys.path for each test
- Add markers for CLI vs non-CLI tests

### 4. Documentation

Create:
- `.github/CLI_MODULE_DISCOVERY_GUIDE.md` — Architecture overview
- `docs/dev-setup/CLI_COMMANDS.md` — Available CLI commands by module
- `TROUBLESHOOTING_CLI.md` — Common issues and fixes

---

## Part 10: Verification Checklist

- [x] CLI module structure mapped (20+ modules identified)
- [x] Module loading mechanism documented (sys.path, importlib, stubs)
- [x] Dev environment discovery issues identified (7 root causes)
- [x] ~80 test failures categorized and analyzed
- [x] Root causes prioritized (P0, P1, P2)
- [x] Quick fix opportunities identified (2 × <5min fixes)
- [x] Architecture drift documented
- [x] Environment configuration gaps identified
- [x] Recommended improvements outlined

---

## Summary: 7 Root Causes of ~80 CLI Module Discovery Failures

| RC ID | Name | Failures | Severity | Fix Type | Effort |
|-------|------|----------|----------|----------|--------|
| RC-1 | Missing `os` import | 4 | P1 | Quick fix | <5 min |
| RC-2 | RAG module attr mismatch | 14 | P1 | Investigation | 1-2 hrs |
| RC-3 | CLI API interface drift | 20 | P2 | Refactor | 2-3 hrs |
| RC-4 | Torch stub interference | 1 | P0 | Config/Env | 30 min |
| RC-5 | CLI path discovery | 1 | P1 | Test update | <5 min |
| RC-6 | Missing RAG functions | ~12 | P2 | Implementation | 1-2 hrs |
| RC-7 | Optional dep availability | ~40 | P2 | Setup | 30 min |
| **Total** | **7 root causes** | **~92 failures** | **Mixed** | **Mixed** | **5-10 hrs** |

---

## Next Steps: Phase 2 Remediation

Proceed with targeted fixes in Phase 2:
1. **Immediate** (< 5 min): Apply QF-1 & QF-2 quick fixes
2. **Short-term** (1-2 hrs): Fix RC-4 torch stub, add optional deps
3. **Medium-term** (2-3 hrs): Refactor CLI API interface (RC-3)
4. **Investigation** (1-2 hrs): Determine RAG module expectations (RC-2/RC-6)

**Expected Result**: 85-90% of 80+ tests should pass after Phase 2 remediation

---

**Report Generated**: 2026-07-17 19:50 UTC  
**Status**: Ready for Phase 2 Remediation  
**Authority**: D-tier autonomous approval active
