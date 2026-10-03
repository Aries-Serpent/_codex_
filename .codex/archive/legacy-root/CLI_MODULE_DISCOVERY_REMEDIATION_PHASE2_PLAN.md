# CLI Module Discovery Remediation Strategy
**Phase 10 Post-Release | Phase 2 (Remediation & Execution)**  
**Start Date**: 2026-07-17 | **Est. Duration**: 2-3 hours  
**Authority**: D-tier autonomous approval

---

## Status Report: Phase 1 Complete ✅

**Phase 1 Reconnaissance Completed**:
- ✅ CLI module structure mapped (20+ modules, 330+ tests)
- ✅ 7 root causes identified and prioritized
- ✅ ~80 failing tests categorized and analyzed
- ✅ Quick fixes applied (2 × <5min fixes = 5 tests fixed)

**Current Status**:
- Tests Passing: 291/330 CLI tests (88%)
- Tests Fixed by Quick Fixes: 5
- Tests Remaining: ~40 direct failures + ~40 indirect (missing deps)

---

## Phase 2: Targeted Remediation Strategy

### Priority 1: IMMEDIATE (< 30 min) — P0 & Quick Wins

#### 1.1 RC-4: Torch Stub Interference (P0 - CI Blocker)

**Status**: 1 test failure, cascading impact  
**Issue**: Torch stubs prevent subprocess CLI commands from working  
**Affected Test**: `tests/test_evaluate_cli.py::test_evaluate_cli_runs`

**Option A: Environment Setup (Recommended)**
- Disable torch stubs in dev environment for CLI work
- Update `.github/workflows/ci.yml` to use real torch when running CLI tests
- Create `conftest.py` fixture to replace torch stubs with real torch

**Option B: Code-Level Workaround**
- Modify `codex_ml/cli/evaluate.py` to handle torch stub case
- Add torch replacement in subprocess before importing models
- Document in CLI module

**Recommended Action**: 
```bash
# In dev environment conftest.py
@pytest.fixture(scope="session", autouse=True)
def fix_torch_stubs():
    """Replace torch stubs with real torch for CLI tests."""
    import sys
    import importlib
    if "torch" in sys.modules:
        torch_mod = sys.modules["torch"]
        if getattr(torch_mod, "__version__", "").endswith("stub"):
            del sys.modules["torch"]
            # Load real torch from site-packages
            ...
```

**Effort**: 15 min | **Files**: conftest.py, 1 test file | **Impact**: Fix 1 test + unblock cascading failures

---

#### 1.2 RC-7: Optional Dependency Availability (P2)

**Status**: ~40 tests skip/fail due to missing optional deps  
**Issue**: Optional dependencies not installed in dev environment  
**Missing Deps**:
- `faiss-cpu` — Vector search for RAG
- `sentence-transformers` — Text embeddings
- `tenacity` — Retry logic

**Recommended Action**:
```bash
# Install optional deps for CLI work
pip install faiss-cpu sentence-transformers tenacity

# Or update requirements-dev.txt to include optional CLI dependencies
```

**Effort**: 5 min | **Impact**: Fix ~40 tests by making deps available

---

### Priority 2: SHORT-TERM (1-2 hours) — P1 & Architecture Issues

#### 2.1 RC-2: RAG Module Attribute Mismatches (P1)

**Status**: 14 test failures  
**Issue**: Tests expect functions that don't exist in `codex.rag` module  
**Missing Functions**:
1. `build_index_from_files()` — Build RAG index from files
2. `manage_tenant_indices()` — Multi-tenant index management
3. `get_metrics()` — Collect RAG metrics

**Investigation Needed**:
1. Check if these functions exist elsewhere in codebase
2. Determine if tests are outdated stubs or if implementations are missing
3. Find if there's a RAG module implementation that should be used instead

**Options**:
- **Option A**: Implement missing RAG functions in `aries_serpent_core/rag/__init__.py`
- **Option B**: Update tests to use correct module paths and function names
- **Option C**: Remove/skip these CLI commands if RAG is not yet implemented

**Investigation Commands**:
```bash
# Search for these functions
grep -r "build_index_from_files\|manage_tenant_indices\|get_metrics" src/ --include="*.py"

# Check RAG module structure
ls -la src/aries_serpent_core/rag/

# Check what RAG module exports
python -c "from aries_serpent_core.rag import *; import aries_serpent_core.rag as rag; print(dir(rag))"
```

**Effort**: 1-2 hours | **Files**: tests/test_cli_rag.py + aries_serpent_core/rag/__init__.py | **Impact**: Fix 14 tests

---

#### 2.2 RC-5: CLI Path Discovery (Already Fixed ✅)

**Status**: COMPLETE — Fixed in Phase 1  
**What Was Done**:
- Updated `tests/e2e/test_cli_workflows.py` to look in correct CLI paths
- Changed from `codex/cli.py` to `aries_serpent_core/cli.py`

**Result**: 1 test now passes ✅

---

### Priority 3: MEDIUM-TERM (2-3 hours) — P2 & API Drift

#### 3.1 RC-3: CLI API Interface Drift (P2)

**Status**: 20 test failures in `tests/test_reporting_cli.py`  
**Issue**: ReportingCLI API changed but tests not updated

**Error Patterns**:
```python
# 1. __init__ signature mismatch
TypeError: ReportingCLI.__init__() got an unexpected keyword argument 'config'

# 2. generate_report() signature issues
TypeError: ReportingCLI.generate_report() got multiple values for argument 'format'

# 3. Missing methods
AttributeError: 'ReportingCLI' object has no attribute 'format_metrics'
AttributeError: 'ReportingCLI' object has no attribute 'parse_args'
AttributeError: 'ReportingCLI' object has no attribute 'write_report'
```

**Investigation Strategy**:
1. Read actual `ReportingCLI` implementation in `aries_serpent_core/reporting/cli.py`
2. Compare with test expectations
3. Determine which is correct:
   - Is implementation incomplete? (need to add methods)
   - Are tests outdated? (need to update tests)

**Two Sub-Options**:
- **Option A**: Update test fixture to match actual ReportingCLI API
- **Option B**: Refactor ReportingCLI to match test expectations

**Effort**: 2-3 hours | **Files**: tests/test_reporting_cli.py + aries_serpent_core/reporting/cli.py | **Impact**: Fix 20 tests

---

#### 3.2 RC-6: Missing RAG Module Implementations (Secondary)

**Status**: Depends on RC-2 investigation  
**Issue**: Same as RC-2 — need to determine if functions should exist  
**Action**: Coordinate with RC-2 remediation

---

### Priority 4: INVESTIGATION (Post-Remediation)

#### 4.1 RC-1: Missing `os` Import (Already Fixed ✅)

**Status**: COMPLETE — Fixed in Phase 1  
**Result**: 4 tests now pass ✅

---

## Remediation Execution Plan

### Phase 2A: Quick Wins (30 min)
```
TASK: Install optional dependencies & fix torch stubs
1. pip install faiss-cpu sentence-transformers tenacity  [5 min]
2. Add torch stub replacement fixture to conftest.py     [15 min]
3. Run tests to verify fixes                              [10 min]
EXPECTED RESULT: +40 tests passing (optional deps installed)
                 +1 test passing (torch fix)
```

### Phase 2B: Investigation & RAG Module (1 hour)
```
TASK: Investigate RAG module state & requirements
1. Read aries_serpent_core/rag/__init__.py                 [15 min]
2. Check test expectations vs implementation               [15 min]
3. Search codebase for missing functions                   [15 min]
4. Determine remediation path (implement vs update tests)  [15 min]
OUTCOME: Decision on RC-2 & RC-6 approach
```

### Phase 2C: ReportingCLI Interface Fix (1.5-2 hours)
```
TASK: Fix ReportingCLI API mismatch (RC-3)
1. Read actual ReportingCLI implementation                 [20 min]
2. Compare with test expectations                         [15 min]
3. Decide: implement missing methods OR update tests      [10 min]
4. Apply fixes                                            [45-60 min]
5. Run tests to verify                                    [15 min]
EXPECTED RESULT: +20 tests passing
```

---

## Success Criteria

### Phase 2 Completion Targets

| Root Cause | Target | Effort | Expected Result |
|-----------|--------|--------|-----------------|
| RC-1 | ✅ Complete | <5 min | +4 tests (DONE) |
| RC-4 | 🎯 Target | 15 min | +1 test |
| RC-5 | ✅ Complete | <5 min | +1 test (DONE) |
| RC-7 | 🎯 Target | 5 min | +40 tests |
| RC-2 | 🔍 Investigate | 1 hour | +14 tests (if implemented) |
| RC-3 | 🎯 Target | 2 hours | +20 tests |
| RC-6 | 🔍 With RC-2 | 1 hour | +12 tests (if implemented) |
| **Total** | — | **5-10 hrs** | **+92 tests** |

### Overall Phase 2 Goal

**Primary Goal**: Get to 90%+ passing rate on CLI tests
- Current: 291/330 passing (88%)
- Target: 310-320/330 passing (93-97%)
- Minimum acceptable: 300/330 passing (90%)

**Secondary Goal**: Document CLI module discovery for future work
- Update `.codex/CLI_MODULE_DISCOVERY_GUIDE.md`
- Create remediation runbook for similar issues
- Update dev environment setup guide

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review Phase 1 reconnaissance report
- [ ] Confirm D-tier autonomous approval active
- [ ] Verify batch scan passes (baseline)

### Phase 2A: Dependencies & Torch Fix (30 min)
- [ ] Install optional CLI dependencies
- [ ] Create conftest.py torch stub fix
- [ ] Run test suite to verify improvements
- [ ] Document fixes in .codex/

### Phase 2B: RAG Module Investigation (1 hour)
- [ ] Read RAG module implementation
- [ ] Compare with test expectations
- [ ] Document findings
- [ ] Decide implementation vs test update approach
- [ ] (Conditional) Implement missing functions or update tests

### Phase 2C: ReportingCLI Fix (1.5-2 hours)
- [ ] Read ReportingCLI implementation
- [ ] Compare with test expectations
- [ ] Decide approach (implement vs update tests)
- [ ] Apply fixes
- [ ] Run tests to verify

### Post-Implementation
- [ ] Run full test suite (batch scan)
- [ ] Generate final status report
- [ ] Commit changes with detailed message
- [ ] Update Phase 2 completion report

---

## Risk Mitigation

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| RAG functions not needed | Medium | Medium | Phase 2B investigation determines scope |
| ReportingCLI too complex | Low | Medium | May need code-analysis-agent for deeper refactor |
| Optional deps cause new issues | Low | Low | Test thoroughly before commit |
| Torch fix breaks other tests | Low | Low | Run full batch scan after fix |
| Time overrun | Medium | Low | Prioritize (complete P1 + optional P2) |

### Escalation Path

If any of these occur, escalate to code-analysis-agent:
1. RAG module significantly incomplete
2. ReportingCLI requires major architectural refactor
3. New blockers discovered during remediation
4. Phase 2 time exceeds 3 hours

---

## Deliverables

### Phase 2 Completion Report

Create `.codex/CLI_MODULE_DISCOVERY_REMEDIATION_RESULTS_2026_07_20.md`:

```markdown
# Phase 2 Remediation Results
**Date**: 2026-07-17 | **Duration**: X hours

## Summary
- ✅ Quick fixes applied: 2/2
- 🎯 Root causes addressed: 5/7
- 📊 Test improvement: XXX → XXX passing (+XX%)
- 🔍 Investigations completed: 2/2

## Results by Root Cause
...
```

### Updated Development Guide

Create `docs/dev-setup/CLI_DEVELOPMENT_GUIDE.md`:
- How to set up CLI in dev environment
- Optional dependencies required
- Known issues and workarounds
- Commands to test CLI functionality

---

## Timeline & Milestones

| Milestone | Time | Status |
|-----------|------|--------|
| Phase 1: Reconnaissance | -30 min | ✅ Complete |
| Phase 2A: Quick fixes | 30 min | 🎯 Next |
| Phase 2B: Investigation | 1 hour | 🎯 Next |
| Phase 2C: ReportingCLI fix | 2 hours | 🎯 Next |
| Phase 2: Testing & verification | 30 min | 🎯 Next |
| Phase 2: Documentation | 30 min | 🎯 Next |
| **Total Phase 2** | **4-5 hours** | **In Progress** |

---

## Next Steps

**Immediate Action**:
1. Review this Phase 2 remediation plan ✓
2. Execute Phase 2A (install deps, fix torch)
3. Execute Phase 2B (RAG investigation)
4. Execute Phase 2C (ReportingCLI fix)
5. Generate final Phase 2 completion report
6. Commit all changes

**Authority**: All decisions autonomous per D-tier approval  
**Reporting**: Update main session with Phase 2 results when complete

---

**Generated**: 2026-07-17 19:52 UTC  
**Status**: Ready for Phase 2 Execution  
**Approval**: D-tier autonomous active
