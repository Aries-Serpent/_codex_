# Phase 1: Core Profile Resolution - Execution Brief
**Campaign:** codex-ml v0.1.0 Installation Gap Resolution  
**Execution Date:** 2026-07-10T20:04:56Z  
**Authority:** @mbaetiong D-Tier Autonomous (GO CONTINUE)  
**Status:** 🟢 **EXECUTION AUTHORIZED**

---

## Critical Status

**Phase 1 Prerequisite for Phase 3:** ✅ REQUIRED  
Phase 1 resolves the 6 installation gaps that block Phase 3 (Full Profile Validation).

**Current Blockers:**
- ❌ Issue 2: `codex.logging` module not in wheel (CRITICAL)
- ❌ Issue 3: Entry points reference non-existent modules (CRITICAL)

---

## Phase 1 Wave 1: Critical Issues (3 Parallel Lanes)

### Lane 1.1: Fix Missing `click` Dependency
**Status:** ✅ ALREADY DONE (click>=8.1 in dependencies)
**Verification:** Confirmed in pyproject.toml

### Lane 1.2: BLOCKING - Resolve `codex.logging` Module
**Priority:** CRITICAL  
**Duration:** 2 hours  
**Agent:** `general-purpose`

**Tasks:**
1. ✅ Verify src/codex/logging/ exists and is complete
2. Add explicit mapping: `codex = "src/codex"` to package-dir (pyproject.toml line ~340)
3. Verify setuptools finds module: `python -m setuptools find_packages`
4. Rebuild wheel: `pip install -e .`
5. Test import: `python -c "from codex.logging.adapter import get_default_logger"`
6. Commit with message

**Current Failure:**
```
ModuleNotFoundError: No module named 'codex.logging'
```

**Resolution Path:**
1. Edit `pyproject.toml` [tool.setuptools.package-dir]
2. Add line: `codex = "src/codex"`
3. Rebuild and test

### Lane 1.3: Audit & Fix Entry Points
**Priority:** CRITICAL  
**Duration:** 1 hour  
**Agent:** `code-analysis-agent`

**Tasks:**
1. Audit all 27 entry points in pyproject.toml:289
2. Identify which modules are bundled vs non-bundled
3. Keep only bundled entry points
4. Remove non-bundled with justification
5. Verify remaining entry points work
6. Commit with message

---

## Execution Model

### Dispatch Agents Immediately
```
GO CONTINUE → Dispatch 2 agents NOW:
  Lane 1.2 (general-purpose): Fix codex.logging module
  Lane 1.3 (code-analysis-agent): Audit entry points

Timeline:
  00:00-60:00  Lane 1.2 runs (codex.logging fix)
  00:00-60:00  Lane 1.3 runs in parallel (entry points audit)
  60:00-120:00 Wave 2 (medium issues)
  120:00-180:00 Wave 3 (low issues)
```

---

## Success Verification

**Lane 1.2 Success:**
```bash
$ python -c "from codex.logging.adapter import get_default_logger"
$ python -c "from codex_ml.cli.main import cli; cli(['--help'])"
✅ Both import successfully
```

**Lane 1.3 Success:**
```bash
$ codex-ml --help  # Works
$ codex-train --help  # Works
$ codex-eval --help  # Works
✅ All kept entry points functional
```

---

## Next Phase Trigger

**Phase 3 Unblocked When:**
✅ Phase 1 complete
✅ Phase 2 complete

**Phase 3 Will:**
1. Run 4-lane parallel validation (dev tools, MLflow, wandb, training)
2. Verify all `[full]` profile dependencies
3. Test end-to-end training pipeline
4. Generate final report + sign-off

---

**AUTHORIZATION:** @mbaetiong D-Tier Autonomous (GO CONTINUE)  
**ACTION:** Dispatch agents for Phase 1 Wave 1 execution NOW
