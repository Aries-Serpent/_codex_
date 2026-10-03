# Campaign Implementation Plan: codex-ml v0.1.0 Installation Gap Resolution

**Campaign ID:** INSTALL_FIX_v0.1.0  
**Start Date:** 2026-07-10T18:06:00Z  
**Target Completion:** 2026-07-10 (same day)  
**Status:** 📋 PLANNING PHASE  
**Authority:** D-Tier Autonomous (full delegation approved)

---

## Executive Overview

This campaign resolves 6 identified gaps in the `codex-ml==0.1.0` installation process:
- **3 Critical issues** blocking CLI functionality
- **2 Medium issues** affecting usability  
- **1 Low issue** affecting documentation

**Execution Model:** Phased delivery with staged profile fixes:
1. **Phase 1 (Core):** Resolve all gaps for base + `[core]` profile (4 days)
2. **Phase 2 (Runtime):** Prepare `[runtime]` profile (pending Phase 1 completion)
3. **Phase 3 (Full):** Prepare `[full]` profile (pending Phase 2 completion)

---

## Campaign Scope & Objectives

### In Scope ✅
- **pyproject.toml modifications:** Dependencies, profiles, entry points
- **Package structure validation:** setuptools configuration audit
- **CLI module refactoring:** Decouple from `codex.logging` or include it
- **Entry point audit:** Verify all 27 entry points reference bundled modules
- **Test coverage:** Add smoke tests for installation validation
- **Documentation:** Profile comparisons, troubleshooting guides

### Out of Scope ❌
- PyTorch/transformers feature development (handled in Phase 2)
- Full test suite execution (handled separately)
- Release workflow changes (only publication readiness)

---

## Critical Issues Deep Dive

### 🔴 Issue 1: Missing `click` in Base Dependencies

**Priority:** CRITICAL  
**Location:** `pyproject.toml:31-58` (dependencies section)  
**Current State:** `click>=8.1` only in `[core]` profile (line 95)  
**Required State:** Must be in base dependencies

**Why It's Critical:**
- `codex_ml.cli.main:cli` directly imports `click`
- Entry point `codex-ml` tries to initialize without it
- Affects all CLI-dependent entry points

**Resolution:**
```
File: pyproject.toml
Location: Line 40 (after typer>=0.12)
Action: Add "click>=8.1" to dependencies list
Expected: CLI tools import successfully

Diff:
 [project]
 dependencies = [
     # ...CLI support
     "typer>=0.12",
+    "click>=8.1",
     # Code analysis (core feature)
     "libcst>=1.0.0",
```

**Verification:**
```bash
python -c "from codex_ml.cli.main import cli; print('✅ click dependency resolved')"
```

**Estimated Effort:** 5 minutes (1 line change + test)

---

### 🔴 Issue 2: Missing `codex.logging` Module in Wheel

**Priority:** CRITICAL  
**Location:** Package structure in `src/codex/`  
**Current State:** Wheel contains only `codex_ml.*` packages  
**Required State:** Either include `codex.logging` OR refactor imports

**Why It's Critical:**
- 3 entry points import from `codex.logging` directly:
  - `codex-ml` → `codex_ml.cli.main:cli` imports `codex.logging.adapter`
  - `codex-train` → `codex_ml.cli.entrypoints:train_main`
  - `codex-eval` → `codex_ml.cli.entrypoints:eval_main`
- All fail at import time if module unavailable

**Root Cause Analysis:**
```
setuptools.package-dir configuration (lines 327-343):
  "" = "src"           # Default: packages in src/
  codex_ml = ...       # codex_ml explicitly mapped
  # BUT no mapping for codex/ base packages

setuptools.packages.find include list (lines 350-374):
  "codex_ml*",         # Included
  "codex*",            # TOO BROAD - but codex.logging may not match
  # Ambiguity: does "codex*" pattern include src/codex/?
```

**Option A: Bundle `codex.logging` (Recommended)**
- **Pros:** Maintains existing API, no refactoring needed
- **Cons:** Larger wheel size, shared module complexity
- **Effort:** 2 hours (audit + fix + test)
- **Steps:**
  1. Verify `src/codex/logging/` exists and is complete
  2. Add explicit mapping: `codex = "src/codex"` to package-dir
  3. Verify setuptools finds it: `python -m setuptools find_packages`
  4. Rebuild wheel and test import
  5. Add smoke test to `tests/smoke/`

**Option B: Refactor to Use Only `codex_ml.*` (Alternative)**
- **Pros:** Cleaner separation, smaller wheel
- **Cons:** Code refactoring, breaking change risk
- **Effort:** 4 hours (refactoring + testing)
- **Steps:**
  1. Move `codex.logging` → `codex_ml.logging`
  2. Update all imports across CLI modules
  3. Update entry point targets
  4. Test all CLI tools

**Option C: Make Logging Optional (Not Recommended)**
- Creates hard-to-debug import errors
- Violates principle of least surprise

**Recommended Path:** Option A (Option B requires refactoring time)

**Verification:**
```bash
python -c "from codex.logging.adapter import get_default_logger; print('✅ codex.logging resolved')"
```

---

### 🔴 Issue 3: Entry Points Reference Non-Existent Modules

**Priority:** CRITICAL  
**Location:** `pyproject.toml:237-289` (project.scripts section)  
**Current State:** 27 entry points declared; 0 functional  
**Required State:** All entry points reference modules in the wheel

**Entry Point Audit:**

| Category | Status | Entry Points | Action |
|----------|--------|--------------|--------|
| ✅ Core (`codex_ml.*`) | FIXABLE | `codex-ml`, `codex-train`, `codex-eval`, ... | Fix with Issue 1+2 |
| ❌ Missing (`codex.*`) | REMOVE | `codex`, `codex-setup`, `codex-audit-runner` | Remove or refactor |
| ❌ Missing (`tokenization.*`) | REMOVE | `codex-tokenizer` | Remove or include module |
| ❌ Missing (`tools.*`) | REMOVE | `fence-check`, `docs-*` | Remove or include modules |
| ❌ Missing (`cli.*`) | REMOVE | `codex-patch-runner`, `codex-task-sequence` | Remove or include modules |
| ❌ Missing (`hhg_logistics.*`) | REMOVE | `hhg-train`, `hhg-serve` | Remove or include modules |

**Resolution Strategy:**

1. **Audit which modules are bundled:**
   ```bash
   python -c "import setuptools; print(setuptools.find_packages('src'))"
   ```

2. **For each entry point:**
   - If target module IS in wheel → OK (will be fixed by Issue 1+2)
   - If target module NOT in wheel → Mark for removal
   - If critical functionality → Move to `[runtime]` or `[full]` profile

3. **Remove non-bundled entry points:**
   ```toml
   # Remove these lines from [project.scripts]:
   codex-setup = "cli.setup:main"              # cli not bundled
   codex-tokenizer = "tokenization.cli:app"    # tokenization not bundled
   fence-check = "tools.validate_fences:main"  # tools not bundled
   hhg-train = "hhg_logistics.main:main"       # hhg_logistics not bundled
   # ... etc
   ```

4. **Create separate entry point groups:**
   - Base entry points (only if bundled)
   - Runtime entry points (if `[runtime]` tools exist)
   - Full entry points (if `[full]` tools exist)

**Verification:**
```bash
for ep in codex-ml codex-train codex-eval; do
  $ep --help 2>/dev/null && echo "✅ $ep works" || echo "❌ $ep failed"
done
```

---

### 🟡 Issue 4: Incorrect Package Discovery in setuptools

**Priority:** MEDIUM  
**Location:** `pyproject.toml:325-404` (tool.setuptools section)  
**Current State:** Conflicting package-dir mappings, ambiguous includes  
**Required State:** Clear, tested package discovery

**Configuration Issues:**

```toml
[tool.setuptools.package-dir]
"" = "src"                    # Default: all packages in src/
agents = "agents"             # Override: agents at ROOT (not src/agents!)
config = "src/config"         # Override: config in src/
codex_bridge = "src/codex_bridge"
# ... 10 more overrides

[tool.setuptools.packages.find]
where = [".", "src"]          # Search both root and src/
include = [
    "agents*",                # Will include ROOT/agents/
    "codex_ml*",              # Will include src/codex_ml/
    "cli*",                   # AMBIGUOUS: could match src/cli or ROOT/cli
    # ... 20+ more patterns
]
exclude = [...]
```

**Problems:**
1. `agents = "agents"` points to ROOT, not `src/agents` → duplicate if both exist
2. Multiple include patterns create ambiguity
3. No clarity on which packages are actually bundled

**Resolution:**

1. **Clarify intent with setuptools:**
   ```bash
   python -c "
   from setuptools import find_packages
   packages = find_packages('src', include=['codex*'])
   print('Discovered packages:', packages)
   "
   ```

2. **Standardize package locations:**
   ```toml
   [tool.setuptools.package-dir]
   "" = "src"                    # All packages in src/

   [tool.setuptools.packages.find]
   where = ["src"]               # Search only src/
   include = [
       "codex_ml*",              # Core package
       "codex*",                 # Include codex.logging, etc
   ]
   ```

3. **Document the mapping:**
   ```markdown
   # Package Structure
   - src/codex_ml/     → codex_ml (main ML framework)
   - src/codex/        → codex (shared utilities)
   - src/training/     → training (training configs)
   - src/tokenization/ → tokenization (tokenizer tools)
   ```

**Verification:**
```bash
python setup.py --name --version --packages
```

---

### 🟡 Issue 5: hydra-core[hydra_plugins] Extra Not Available

**Priority:** MEDIUM (non-blocking)  
**Location:** `pyproject.toml:85, 143`  
**Current State:** Specifies invalid extra that generates warning  
**Required State:** Use base `hydra-core` without extra

**Issue:**
```
WARNING: hydra-core 1.3.2 does not provide the extra 'hydra-plugins'
```

**Resolution:**
```toml
# Before
"hydra-core[hydra_plugins]==1.3.2",

# After
"hydra-core==1.3.2",
```

**Files to update:**
- Line 85: Core profile dependencies
- Line 143: Full profile dependencies

**Effort:** 5 minutes (2 line removals + test)

---

### 🟢 Issue 6: No Post-Install Verification

**Priority:** LOW  
**Location:** New file `tests/smoke/test_install.py`  
**Current State:** No verification after installation  
**Required State:** Smoke tests validate core functionality

**Resolution:**

Create `tests/smoke/test_install.py`:
```python
"""Smoke tests for installation verification."""
import subprocess
import sys

def test_codex_ml_imports():
    """Verify core module imports work."""
    code = "import codex_ml; print('✅ codex_ml imports')"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, f"Import failed: {result.stderr.decode()}"

def test_codex_logging_imports():
    """Verify codex.logging is available."""
    code = "from codex.logging.adapter import get_default_logger; print('✅ codex.logging imports')"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, f"Import failed: {result.stderr.decode()}"

def test_click_installed():
    """Verify click dependency."""
    code = "import click; print('✅ click installed')"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, f"Click not found: {result.stderr.decode()}"

def test_cli_entry_point():
    """Verify CLI entry point works."""
    result = subprocess.run(["codex-ml", "--help"], capture_output=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr.decode()}"
```

**Verification command:**
```bash
pytest tests/smoke/test_install.py -v
```

---

## Campaign Execution Plan

### Phase 1: Core Profile Resolution

**Duration:** ~4 hours  
**Objective:** Resolve all 6 gaps for base + `[core]` profile  
**Completion Criteria:** All gaps resolved, 0 failures

#### Wave 1: Critical Issues (Parallel Execution)

**Lane 1.1: Fix Missing `click` Dependency** (Agent: code-review + manual)
- **Time:** 15 minutes
- **Tasks:**
  - [ ] Add `click>=8.1` to `dependencies` in pyproject.toml:40
  - [ ] Rebuild wheel: `pip install -e .`
  - [ ] Verify import: `python -c "from click import *; print('✅')"`
  - [ ] Commit: `fix(deps): Add missing click dependency to base`

**Lane 1.2: Resolve `codex.logging` Module** (Agent: general-purpose)
- **Time:** 2 hours
- **Tasks:**
  - [ ] Verify `src/codex/logging/` exists and completeness
  - [ ] Add explicit package mapping: `codex = "src/codex"` to pyproject.toml:333
  - [ ] Test package discovery: `python -m setuptools find_packages`
  - [ ] Rebuild wheel: `pip install -e .`
  - [ ] Verify import: `python -c "from codex.logging.adapter import *; print('✅')"`
  - [ ] Commit: `fix(packaging): Include codex.logging in wheel`

**Lane 1.3: Audit & Fix Entry Points** (Agent: code-analysis-agent)
- **Time:** 1 hour
- **Tasks:**
  - [ ] Audit all 27 entry points for bundled modules
  - [ ] Categorize as: Keep/Remove/Conditional
  - [ ] Remove non-bundled entries from pyproject.toml:237-289
  - [ ] Document removed entries with rationale
  - [ ] Verify remaining entry points work: `for ep in codex-ml ...; do $ep --help; done`
  - [ ] Commit: `fix(entry-points): Remove references to non-bundled modules`

#### Wave 2: Medium Issues (Sequential)

**Lane 2.1: Fix hydra-plugins Extra** (Agent: code-review)
- **Time:** 10 minutes
- **Tasks:**
  - [ ] Remove `[hydra_plugins]` from line 85 (core profile)
  - [ ] Remove `[hydra_plugins]` from line 143 (full profile)
  - [ ] Rebuild wheel: `pip install -e .`
  - [ ] Verify no warnings: `pip install --dry-run .`
  - [ ] Commit: `fix(hydra): Remove invalid hydra_plugins extra`

**Lane 2.2: Clarify setuptools Configuration** (Agent: general-purpose)
- **Time:** 30 minutes
- **Tasks:**
  - [ ] Test current package discovery: `python -c "import setuptools; print(setuptools.find_packages('src'))"`
  - [ ] Simplify package-dir mapping if needed
  - [ ] Document package structure in pyproject.toml comments
  - [ ] Verify all packages discovered correctly
  - [ ] Commit: `refactor(setuptools): Clarify package discovery configuration`

#### Wave 3: Low-Priority Issues (Parallel)

**Lane 3.1: Add Smoke Tests** (Agent: test-pattern-guardian)
- **Time:** 30 minutes
- **Tasks:**
  - [ ] Create `tests/smoke/test_install.py`
  - [ ] Add import verification tests
  - [ ] Add CLI entry point tests
  - [ ] Run: `pytest tests/smoke/ -v`
  - [ ] Commit: `test(smoke): Add post-install verification tests`

**Lane 3.2: Create Installation Guide** (Agent: documentation-quality-agent)
- **Time:** 30 minutes
- **Tasks:**
  - [ ] Create/update `.codex/archive/misc/INSTALL.md`
  - [ ] Document [core], [runtime], [full] profiles
  - [ ] Add profile comparison table
  - [ ] Add troubleshooting section
  - [ ] Link from README.md
  - [ ] Commit: `docs(install): Add comprehensive installation guide`

### Phase 1 Integration & Validation

**Duration:** ~30 minutes  
**Objective:** Verify all fixes work together

**Integration Tasks:**
1. **Fresh install test:**
   ```bash
   rm -rf /tmp/test-codex-install
   python -m venv /tmp/test-codex-install
   source /tmp/test-codex-install/bin/activate
   pip install -e .
   python -m pytest tests/smoke/ -v
   ```

2. **Profile test:**
   ```bash
   pip install -e ".[core]"
   codex-ml --help
   ```

3. **Verify no regressions:**
   ```bash
   python -m pytest tests/ -x -q
   ```

### Phase 1 Sign-Off

**Completion Checklist:**
- [ ] All 6 gaps resolved
- [ ] 27 entry points verified (kept or removed with justification)
- [ ] Smoke tests pass (100%)
- [ ] Installation guide complete
- [ ] Zero warnings on install
- [ ] Fresh install works end-to-end

**Success Criteria:**
```bash
$ pip install codex-ml[core]==0.1.0
# ... no warnings ...
Successfully installed 46 packages

$ codex-ml --help
Usage: codex-ml [OPTIONS] COMMAND [ARGS]...
  ✅ WORKS
```

---

## Phase 2: Runtime Profile Preparation

**Duration:** ~2 hours  
**Status:** PENDING Phase 1 completion  
**Objective:** Validate [runtime] profile dependencies

**Scope:**
- [ ] Verify torch/transformers installation on GPU
- [ ] Test inference pipelines
- [ ] Verify FastAPI server startup
- [ ] Test RAG pipeline components

**Entry Points for Runtime:**
- ML inference: `codex-infer`
- Model evaluation: `codex-eval`
- FastAPI server: `codex-serve`

---

## Phase 3: Full Profile Preparation

**Duration:** ~2 hours  
**Status:** PENDING Phase 2 completion  
**Objective:** Validate [full] profile dependencies

**Scope:**
- [ ] Verify dev tools (pytest, mypy, ruff)
- [ ] Verify MLflow/wandb integration
- [ ] Test end-to-end training pipeline
- [ ] Verify documentation generation

---

## Execution Authority & Delegation Model

**D-Tier Autonomy Enabled:** ✅ YES

Per user memory: "@mbaetiong grants blanket approval for all agent autonomous plans, decisions, and actions"

**Parallel Execution Model:**
- Lane 1.1, 1.2, 1.3 can execute simultaneously
- Lane 2.1, 2.2 can start after Lane 1.1 completes
- Lane 3.1, 3.2 can start after Lane 1.2 completes

**Agent Delegation:**
- **Lane 1.1:** `code-review` agent (simple file edit)
- **Lane 1.2:** `general-purpose` agent (complex refactoring)
- **Lane 1.3:** `code-analysis-agent` (entry point audit)
- **Lane 2.1:** `code-review` agent (simple file edit)
- **Lane 2.2:** `general-purpose` agent (setuptools configuration)
- **Lane 3.1:** `test-pattern-guardian` agent (test creation)
- **Lane 3.2:** `documentation-quality-agent` (guide creation)

---

## Resource Requirements

| Resource | Type | Status |
|----------|------|--------|
| Python 3.12+ | Runtime | ✅ Available |
| setuptools 83.0+ | Build tool | ✅ Available |
| pytest | Testing | ✅ Available |
| GitHub MCP | API access | ✅ Available |
| Custom agents | Execution | ✅ Available |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Breaking API changes | Low | High | Version bump to v0.1.1 |
| Failed entry points | Medium | Medium | Smoke tests catch early |
| Package discovery issues | Low | High | setuptools audit + test |
| Incomplete codex.logging | Low | Critical | Audit completeness first |
| Import regressions | Low | Medium | Full test suite validation |

---

## Success Metrics

| Metric | Target | Current | Post-Phase 1 |
|--------|--------|---------|-------------|
| Installation warnings | 0 | 1 | 0 |
| Functional entry points | 27/27 | 0/27 | 20+/27 |
| Smoke test pass rate | 100% | N/A | 100% |
| Base install size | <100 MB | 65-75 MB | 65-75 MB |
| CLI tool availability | 100% | 0% | 100% |

---

## Timeline & Milestones

**Campaign Start:** 2026-07-10T18:06:00Z  
**Phase 1 Target:** 2026-07-10T22:06:00Z (4 hours)  
**Phase 2 Start:** 2026-07-11T00:00:00Z (after Phase 1)  
**Phase 3 Start:** 2026-07-11T03:00:00Z (after Phase 2)

**Milestone Checkpoints:**
- ✅ Wave 1 complete: All critical issues resolved (1.5 hours)
- ✅ Wave 2 complete: Medium issues resolved (30 min)
- ✅ Wave 3 complete: Low-priority items complete (1 hour)
- ✅ Integration: Fresh install + full test suite (30 min)
- ✅ Sign-off: All gates passed (ready for PyPI)

---

## Rollback Plan

If any wave fails:

1. **Lane failure:** Revert that lane's commits, continue others
2. **Integration failure:** Revert all Phase 1 commits, diagnose root cause
3. **Regression detected:** Revert to known-good state, incrementally fix

**Rollback command:**
```bash
git revert <commit_sha> --no-edit
```

---

## Documentation Artifacts

To be created:
- **.codex/archive/misc/INSTALL.md** - Comprehensive installation guide
- **tests/smoke/test_install.py** - Smoke test suite
- **CAMPAIGN_INSTALL_FIX_v0.1.0_PROGRESS.md** - Real-time progress tracker
- **CAMPAIGN_INSTALL_FIX_v0.1.0_RESULTS.md** - Final results & metrics

---

## Approval & Sign-Off

**Campaign Authorization:** ✅ D-Tier Autonomous  
**User Authority:** @mbaetiong  
**Execution Start:** Immediately upon approval  

**To Proceed:** Execute Lane 1.1, 1.2, 1.3 in parallel

---

**Campaign Plan Created:** 2026-07-10T18:06:30Z  
**Plan Version:** 1.0  
**Status:** 📋 READY FOR EXECUTION
