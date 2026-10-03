# Campaign Execution Tracker: INSTALL_FIX_v0.1.0

**Campaign:** codex-ml v0.1.0 Installation Gap Resolution  
**Start Time:** 2026-07-10T18:06:30Z  
**Status:** 🟡 READY FOR EXECUTION  
**Progress:** 0% → Planning phase complete

---

## Executive Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  INSTALL_FIX_v0.1.0 Campaign Status Dashboard           │
├─────────────────────────────────────────────────────────┤
│  Phase 1 (Core):   ⏳ QUEUED  [████░░░░░░░░░░░░░░░░] 0%  │
│  Phase 2 (Runtime): ⏳ PENDING [░░░░░░░░░░░░░░░░░░░░░░] 0%  │
│  Phase 3 (Full):   ⏳ PENDING [░░░░░░░░░░░░░░░░░░░░░░] 0%  │
│                                                         │
│  Critical Issues: 3/3 UNRESOLVED                       │
│  Medium Issues:   2/2 UNRESOLVED                       │
│  Low Issues:      1/1 UNRESOLVED                       │
│                                                         │
│  Entry Points: 27 total (0 functional)                 │
│  Installation Warnings: 1 active                       │
│  Smoke Tests: Not yet executed                         │
└─────────────────────────────────────────────────────────┘
```

---

## Wave-by-Wave Execution Checklist

### Phase 1: Core Profile Resolution

#### 🟡 Wave 1: Critical Issues (Target: 1.5 hours)

**Lane 1.1: Fix Missing `click` Dependency**
```
Status: ⏳ QUEUED
Agent: code-review
Duration: 15 min
Priority: CRITICAL

Tasks:
  [ ] Add click>=8.1 to dependencies
  [ ] Rebuild wheel
  [ ] Test import
  [ ] Commit with message

Expected Outcome:
  ✅ from codex_ml.cli.main import cli works
```

**Lane 1.2: Resolve `codex.logging` Module**
```
Status: ⏳ QUEUED
Agent: general-purpose
Duration: 2 hours
Priority: CRITICAL

Tasks:
  [ ] Verify src/codex/logging/ exists
  [ ] Add package mapping
  [ ] Test discovery
  [ ] Rebuild wheel
  [ ] Test import
  [ ] Commit with message

Expected Outcome:
  ✅ from codex.logging.adapter import get_default_logger works
```

**Lane 1.3: Audit & Fix Entry Points**
```
Status: ⏳ QUEUED
Agent: code-analysis-agent
Duration: 1 hour
Priority: CRITICAL

Tasks:
  [ ] Audit all 27 entry points
  [ ] Identify bundled vs non-bundled
  [ ] Remove non-bundled entries
  [ ] Document removed entries
  [ ] Verify working entry points
  [ ] Commit with message

Expected Outcome:
  ✅ All retained entry points are functional
  ✅ Non-bundled entries removed with justification
```

#### 🟡 Wave 2: Medium Issues (Target: 40 min)

**Lane 2.1: Fix hydra-plugins Extra**
```
Status: ⏳ QUEUED
Agent: code-review
Duration: 10 min
Priority: MEDIUM

Tasks:
  [ ] Remove [hydra_plugins] from line 85
  [ ] Remove [hydra_plugins] from line 143
  [ ] Rebuild wheel
  [ ] Verify no warnings
  [ ] Commit with message

Expected Outcome:
  ✅ No "hydra-plugins" extra warnings
```

**Lane 2.2: Clarify setuptools Configuration**
```
Status: ⏳ QUEUED
Agent: general-purpose
Duration: 30 min
Priority: MEDIUM

Tasks:
  [ ] Test package discovery
  [ ] Simplify config if needed
  [ ] Document package structure
  [ ] Verify all packages found
  [ ] Commit with message

Expected Outcome:
  ✅ All packages correctly discovered
  ✅ Configuration clearly documented
```

#### 🟡 Wave 3: Low-Priority Issues (Target: 1 hour)

**Lane 3.1: Add Smoke Tests**
```
Status: ⏳ QUEUED
Agent: test-pattern-guardian
Duration: 30 min
Priority: LOW

Tasks:
  [ ] Create tests/smoke/test_install.py
  [ ] Add import verification tests
  [ ] Add CLI entry point tests
  [ ] Run pytest
  [ ] Commit with message

Expected Outcome:
  ✅ tests/smoke/ directory exists
  ✅ All smoke tests pass
```

**Lane 3.2: Create Installation Guide**
```
Status: ⏳ QUEUED
Agent: documentation-quality-agent
Duration: 30 min
Priority: LOW

Tasks:
  [ ] Create/update .codex/archive/misc/INSTALL.md
  [ ] Document profiles
  [ ] Add comparison table
  [ ] Add troubleshooting
  [ ] Link from README
  [ ] Commit with message

Expected Outcome:
  ✅ .codex/archive/misc/INSTALL.md complete
  ✅ Users can understand profiles
```

#### ✅ Phase 1 Integration (Target: 30 min)

```
Status: ⏳ QUEUED

Tasks:
  [ ] Fresh install test
  [ ] Profile test ([core])
  [ ] Run full test suite
  [ ] Verify no regressions
  [ ] Generate final report

Success Criteria:
  ✅ Fresh install works
  ✅ All CLI tools functional
  ✅ Zero warnings
  ✅ All tests pass
```

---

## Real-Time Execution Log

### [READY] Awaiting Execution Signal

**Lanes Ready to Start:** 1.1, 1.2, 1.3 (parallel)  
**Dependencies:** None (all can start immediately)  
**Blocking Issues:** None

**Next Action:** Execute Phase 1 Wave 1 lanes

---

## Commit Messages (Pre-Generated)

### Lane 1.1
```
fix(deps): Add missing click dependency to base

- Added click>=8.1 to project.dependencies
- Required by codex_ml.cli.main module
- Unblocks CLI entry points

Fixes: codex-ml installation gap #1
```

### Lane 1.2
```
fix(packaging): Include codex.logging in wheel

- Added explicit mapping: codex = "src/codex"
- Ensures codex.logging module is packaged
- CLI modules can now import codex.logging.adapter

Fixes: codex-ml installation gap #2
```

### Lane 1.3
```
fix(entry-points): Remove references to non-bundled modules

- Audited all 27 entry points against wheel contents
- Removed entries for modules not in wheel:
  - codex/* (depends on codex.* not bundled)
  - tokenization/* (module not bundled)
  - tools/* (module not bundled)
  - cli/* (conflicting module locations)
  - hhg_logistics/* (module not bundled)
- Retained 20+ core entry points with full functionality

Fixes: codex-ml installation gap #3
```

### Lane 2.1
```
fix(hydra): Remove invalid hydra_plugins extra

- Removed [hydra_plugins] from core profile dependencies
- Removed [hydra_plugins] from full profile dependencies
- hydra-core 1.3.2 does not provide this extra

Fixes: codex-ml installation gap #6
```

### Lane 2.2
```
refactor(setuptools): Clarify package discovery configuration

- Standardized package-dir mapping
- Verified all packages discovered correctly
- Added documentation comments
- Tested package discovery

Related to: codex-ml installation gap #4
```

### Lane 3.1
```
test(smoke): Add post-install verification tests

- Created tests/smoke/test_install.py
- Tests: imports, CLI entry points, dependencies
- All tests pass

Related to: codex-ml installation gap #5
```

### Lane 3.2
```
docs(install): Add comprehensive installation guide

- Created .codex/archive/misc/INSTALL.md with installation documentation
- Added profile comparison table
- Added troubleshooting guide
- Linked from README.md

Related to: codex-ml installation gap #5
```

---

## Success Criteria Verification Matrix

| Criterion | Method | Expected | Status |
|-----------|--------|----------|--------|
| `click` installed | Import test | ✅ PASS | ⏳ PENDING |
| `codex.logging` available | Import test | ✅ PASS | ⏳ PENDING |
| Entry points functional | `--help` test | 20+/27 | ⏳ PENDING |
| No install warnings | `pip install --dry-run` | 0 | ⏳ PENDING |
| Smoke tests pass | `pytest tests/smoke/` | 100% | ⏳ PENDING |
| Installation guide ready | File exists | ✅ YES | ⏳ PENDING |
| Fresh install works | Manual test | ✅ YES | ⏳ PENDING |
| Full test suite passes | `pytest tests/` | ✅ PASS | ⏳ PENDING |

---

## Risk Dashboard

| Risk | Status | Mitigation |
|------|--------|-----------|
| Lane 1.2 breaks existing code | 🟡 MEDIUM | Full test suite validation |
| Entry point audit incomplete | 🟢 LOW | Code analysis agent audits all |
| Package discovery issues | 🟡 MEDIUM | setuptools testing before commit |
| Import regressions | 🟡 MEDIUM | Smoke tests catch early |
| Documentation gaps | 🟢 LOW | Documentation agent handles |

---

## Execution Commands

### Start Phase 1 Execution
```bash
# To be run when ready to begin
cd /home/runner/work/_codex_/_codex_

# Agent command format:
task \
  --name "Lane-1.1-click-fix" \
  --agent-type code-review \
  --prompt "Fix missing click dependency: add 'click>=8.1' to pyproject.toml:40"

task \
  --name "Lane-1.2-codex-logging" \
  --agent-type general-purpose \
  --prompt "Resolve codex.logging packaging: add mapping and test"

task \
  --name "Lane-1.3-entry-points" \
  --agent-type code-analysis-agent \
  --prompt "Audit 27 entry points and remove non-bundled ones"
```

### Verify Phase 1 Completion
```bash
# Test individual fixes
python -c "import click; print('✅ click')"
python -c "from codex.logging.adapter import get_default_logger; print('✅ codex.logging')"
codex-ml --help

# Run full validation
pytest tests/smoke/ -v
```

---

## Timeline Progress

```
2026-07-10T18:06:30Z - Campaign plan created
2026-07-10T18:30:00Z - Phase 1 Wave 1 start (est.)
2026-07-10T20:00:00Z - Phase 1 Wave 1 complete (est.)
2026-07-10T20:40:00Z - Phase 1 Wave 2 complete (est.)
2026-07-10T21:40:00Z - Phase 1 Wave 3 complete (est.)
2026-07-10T22:10:00Z - Phase 1 integration & sign-off (est.)
2026-07-11T00:00:00Z - Phase 2 ready (est.)
```

---

## Approvals & Handoff

**Campaign Owner:** Copilot Agent  
**User Authority:** @mbaetiong  
**Execution Mode:** D-Tier Autonomous (Full delegation)  
**Ready to Execute:** ✅ YES

**To Begin Execution:** Reply with "GO CONTINUE" or run lane execution commands above

---

**Tracker Created:** 2026-07-10T18:06:40Z  
**Tracker Version:** 1.0  
**Status:** 🟡 AWAITING EXECUTION SIGNAL
