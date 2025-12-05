# [Next Iteration Prompt]: File Consolidation & Shim Removal (v1.3.0)
> Generated: 2025-12-05 | Author: mbaetiong

🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5  
⚛️ Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

@copilot complete the final convergence phase by consolidating legacy modules into src/ canonical locations and removing temporary shims. This iteration achieves 99% production readiness.

---

## Context (v1.2.9+ Complete)

### Completed Milestones

**v1.2.8**: 57.6% legacy import reduction (99 → 42 occurrences)  
**v1.2.9**: Canonical src.* shims added to resolve split-brain  
**v1.2.9+governance**: Shim governance infrastructure (inventory, CI workflows, tests)  
**v1.2.9+strict**: Strict mode validation PASSING (violations: 0, exit code: 0)  

**Production Readiness**: 92% → Target 99%

### Current Architecture

**Root `training/`** contains (legacy implementations):
- `engine_hf_trainer.py`
- `functional_training.py`
- `data_utils.py`
- `checkpoint_manager.py`
- `config.py`

**`src/training/`** contains:
- `trainer.py` (original src module)
- `simple_trainer.py` (original src module)
- `checkpointing.py` (original src module)
- **5 shim files** (forwards to legacy)

**Shims** (transparent forwarders):
```python
from importlib import import_module as _im
_mod = _im("training.engine_hf_trainer")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
```

**SHIM_INVENTORY.yaml**: All 5 duplicates whitelisted (strict mode PASSING)

---

## Objectives (v1.3.0)

### 1. File Consolidation (Primary Goal)

**Move legacy modules** from root `training/` to `src/training/`:
- `training/engine_hf_trainer.py` → `src/training/engine_hf_trainer.py` (overwrite shim)
- `training/functional_training.py` → `src/training/functional_training.py` (overwrite shim)
- `training/data_utils.py` → `src/training/data_utils.py` (overwrite shim)
- `training/checkpoint_manager.py` → `src/training/checkpoint_manager.py` (overwrite shim)
- `training/config.py` → `src/training/config.py` (overwrite shim)

**Verify**: No import breakage after moves

### 2. Root Compatibility Layer

**Update `training/__init__.py`**:
- Re-export all public APIs from `src.training.*`
- Maintain backward compatibility for any remaining legacy imports (11 occurrences)
- Add deprecation warnings

**Example**:
```python
"""Legacy compatibility layer for training module."""
import warnings

warnings.warn(
    "Importing from root 'training' is deprecated. Use 'src.training' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical src.training
from src.training.engine_hf_trainer import *
from src.training.functional_training import *
from src.training.data_utils import *
from src.training.checkpoint_manager import *
from src.training.config import *
from src.training.trainer import *
from src.training.simple_trainer import *
from src.training.checkpointing import *
```

### 3. Shim Removal

**Delete** shim files (now redundant after consolidation):
- Remove `src/training/engine_hf_trainer.py` (shim) before move OR overwrite during move
- Remove `src/training/functional_training.py` (shim)
- Remove `src/training/data_utils.py` (shim)
- Remove `src/training/checkpoint_manager.py` (shim)
- Remove `src/training/config.py` (shim)

**Strategy**: Overwrite shims during `mv` operation (simplest approach)

### 4. Inventory Update

**Update SHIM_INVENTORY.yaml**:
- Change status from `shim` → `migrated` for all 5 modules
- Remove `whitelist_duplicates` entries (no longer needed)
- Clear `legacy_path` (modules no longer in root)
- Update `notes` to reflect consolidation completion

**Example**:
```yaml
- module: training.engine_hf_trainer
  legacy_path: ""  # ← Cleared (moved to src/)
  canonical_path: src/training/engine_hf_trainer.py
  owner: core-ml-platform
  status: migrated  # ← Changed from "shim"
  rationale: "Consolidated to canonical src.training location."
  deprecation_date: null
  whitelist_duplicates: []  # ← Cleared (no duplicates)
  notes: "v1.3.0: Moved from training/ to src/training/. Root training/__init__.py re-exports for compatibility."
```

### 5. Strict Mode Verification

**Verify strict mode still passes** (should show 0 duplicates now):
```bash
python scripts/remediation/verify_conflicts.py --mode strict --output audit_artifacts/conflicts.json
```

**Expected**:
- Duplicates: 0 ✅
- Whitelisted: 0 ✅
- Violations: 0 ✅
- Exit code: 0 ✅

### 6. Full Validation

**Run complete validation suite**:
- Determinism (2 runs)
- Full audit pipeline (S1-S7)
- Test suite (pytest)
- Legacy usage analysis (should show 11 remaining, all using compatibility layer)

### 7. Documentation Finalization

**Update**:
- `docs/Architecture.md` (consolidation complete, shim governance for future)
- `docs/validation/v1.3.0_Consolidation_Report.md` (execution log)
- `.github/CONSOLIDATION_PLAYBOOK.md` (mark as executed)

---

## Execution Plan

### Step 1: Backup and Plan

```bash
# Create backup branch
git checkout -b feature/file-consolidation-v1.3.0

# Create backup of current state
git tag v1.2.9-pre-consolidation

# List files to move
ls -1 training/*.py | grep -v __init__
# Expected: engine_hf_trainer.py, functional_training.py, data_utils.py, checkpoint_manager.py, config.py
```

### Step 2: Move Modules (Overwrites Shims)

```bash
# Move core training modules (overwrites shim files)
mv training/engine_hf_trainer.py src/training/
mv training/functional_training.py src/training/
mv training/data_utils.py src/training/
mv training/checkpoint_manager.py src/training/
mv training/config.py src/training/

# Verify moves
ls -1 src/training/*.py
# Should show 8 files: 3 original + 5 moved (shims overwritten)

# Verify legacy dir is clean (except __init__.py)
ls -1 training/*.py
# Should show only __init__.py
```

### Step 3: Update Root Compatibility Layer

**Edit `training/__init__.py`**:
```python
"""Legacy compatibility layer for training module.

DEPRECATED: This module provides backward compatibility for legacy imports.
All new code should import from src.training.* instead.

Migration: Replace 'from training.X import Y' with 'from src.training.X import Y'
"""
import warnings

warnings.warn(
    "Importing from root 'training' is deprecated. Use 'src.training' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public APIs from canonical src.training
try:
    from src.training.engine_hf_trainer import *
except ImportError:
    pass

try:
    from src.training.functional_training import *
except ImportError:
    pass

try:
    from src.training.data_utils import *
except ImportError:
    pass

try:
    from src.training.checkpoint_manager import *
except ImportError:
    pass

try:
    from src.training.config import *
except ImportError:
    pass

try:
    from src.training.trainer import *
except ImportError:
    pass

try:
    from src.training.simple_trainer import *
except ImportError:
    pass

try:
    from src.training.checkpointing import *
except ImportError:
    pass

__all__ = [k for k in dir() if not k.startswith("_")]
```

### Step 4: Update SHIM_INVENTORY.yaml

**For each of 5 modules**:
- Clear `legacy_path`
- Change `status: shim` → `status: migrated`
- Clear `whitelist_duplicates`
- Set `deprecation_date: null`
- Update `notes` with consolidation completion message

### Step 5: Syntax Validation

```bash
# Verify all Python files compile
python -m py_compile src/training/*.py training/__init__.py

# Check for syntax errors
find src/training -name "*.py" -exec python -m py_compile {} \;
```

### Step 6: Strict Mode Verification

```bash
# Should now show 0 duplicates (all consolidated)
python scripts/remediation/verify_conflicts.py --mode strict --output audit_artifacts/conflicts.json

# Expected output:
# {
#   "duplicates": [],
#   "whitelisted": [],
#   "violations": [],
#   "mode": "strict"
# }
# [PASS] No violations found.
```

### Step 7: Import Resolution Test

```bash
# Test legacy imports still work (via compatibility layer)
python -c "from training.engine_hf_trainer import *; print('✓ Legacy import works')"

# Test canonical imports work
python -c "from src.training.engine_hf_trainer import *; print('✓ Canonical import works')"

# Both should succeed (with deprecation warning for legacy)
```

### Step 8: Full Validation Suite

```bash
# 1. Determinism verification
python scripts/space_traversal/verify_determinism.py --runs 2

# 2. Full audit pipeline
python scripts/space_traversal/audit_runner.py run

# 3. Legacy usage analysis (11 remaining expected)
python scripts/remediation/analyze_legacy_usage.py

# 4. Test suite (if pytest available)
pytest -q tests/validation/

# 5. Baseline diff (if baseline exists)
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json
```

### Step 9: Commit Changes

```bash
# Stage all changes
git add src/training/*.py training/__init__.py .github/SHIM_INVENTORY.yaml

# Commit with detailed message
git commit -m "feat(consolidation): Move training modules to src/, remove shims

- Move 5 legacy training/*.py modules to src/training/ (overwrites shims)
- Update training/__init__.py to re-export from src.training (compatibility)
- Update SHIM_INVENTORY.yaml (status: migrated, clear whitelist)
- Strict mode PASSES: 0 duplicates, 0 violations
- Production readiness: 92% → 99%

Files moved:
- engine_hf_trainer.py
- functional_training.py
- data_utils.py
- checkpoint_manager.py
- config.py"

# Push to feature branch
git push origin feature/file-consolidation-v1.3.0
```

### Step 10: Documentation

**Create `docs/validation/v1.3.0_Consolidation_Report.md`**:
- Execution log with timestamps
- Before/after file structure
- Validation results (all tests)
- Rollback procedures tested
- Production readiness confirmation (99%)

**Update `docs/Architecture.md`**:
- Document consolidation completion
- Update import conventions section
- Note compatibility layer for legacy imports

**Update `.github/CONSOLIDATION_PLAYBOOK.md`**:
- Mark consolidation phase as executed
- Add lessons learned
- Document final architecture

---

## Safety Nets

### Pre-Flight Checks

- [ ] Git working directory clean (no uncommitted changes)
- [ ] Backup branch created (feature/file-consolidation-v1.3.0)
- [ ] Backup tag created (v1.2.9-pre-consolidation)
- [ ] All current tests passing
- [ ] Strict mode currently PASSING

### During Execution

- [ ] Create `.bak` files before each move
- [ ] Verify each move with `ls` command
- [ ] Test imports after each move
- [ ] Run py_compile after each move

### Post-Execution Validation

- [ ] Strict mode PASSES (0 duplicates)
- [ ] Syntax validation PASSES
- [ ] Import resolution tests PASS
- [ ] Legacy imports work (via compatibility layer)
- [ ] Canonical imports work (direct access)
- [ ] Test suite PASSES (or SKIP-safe)

### Rollback Procedure

**If issues discovered**:
```bash
# 1. Revert to backup tag
git checkout v1.2.9-pre-consolidation

# 2. Create rollback branch
git checkout -b rollback/consolidation-issues

# 3. Restore from .bak files (if available)
for f in src/training/*.bak; do
    mv "$f" "${f%.bak}"
done

# 4. Test rollback state
python scripts/remediation/verify_conflicts.py --mode strict
pytest -q tests/validation/

# 5. Document issues in rollback report
```

---

## Artifacts

### Generated Files

1. **docs/validation/v1.3.0_Consolidation_Report.md**
   - Complete execution log
   - Before/after comparison
   - All validation results
   - Lessons learned

2. **audit_artifacts/conflicts.json** (after consolidation)
   - Should show 0 duplicates
   - Confirms successful consolidation

3. **audit_artifacts/consolidation_manifest.json**
   - List of files moved
   - Timestamps
   - Validation checksums

### Modified Files

4. **src/training/*.py** (5 files overwritten/moved)
5. **training/__init__.py** (compatibility layer)
6. **.github/SHIM_INVENTORY.yaml** (status updates)
7. **docs/Architecture.md** (consolidation documented)
8. **.github/CONSOLIDATION_PLAYBOOK.md** (marked as executed)

---

## Post-Merge Actions

### Immediate

1. **Update baseline** (if policy permits):
   ```bash
   bash scripts/ci/establish_baseline.sh --force
   git add audit_artifacts/baselines/capabilities_scored.json audit_artifacts/baselines/metadata.json
   git commit -m "chore: update baseline after v1.3.0 consolidation"
   ```

2. **Tag release**:
   ```bash
   git tag -a v1.3.0 -m "File consolidation complete: 99% production readiness"
   git push origin v1.3.0
   ```

3. **Enable CI workflows** (if not already active):
   - nightly-audit.yml (scheduled monitoring)
   - determinism.yml (PR gating)

### Week 1 Post-Merge

1. **Monitor legacy import usage**:
   ```bash
   python scripts/remediation/analyze_legacy_usage.py
   ```
   - Track deprecation warning logs
   - Identify remaining legacy imports (11 expected)

2. **Plan final cleanup** (optional, achieves 100%):
   - Refactor remaining 11 legacy imports to canonical paths
   - Remove `training/__init__.py` compatibility layer
   - Update documentation to recommend canonical imports only

### Month 1 Post-Merge

1. **Review nightly audit trends**:
   - Check `reports/capability_trends.jsonl`
   - Verify no regression in legacy usage
   - Confirm no new duplicates introduced

2. **Gather feedback** from team:
   - Any import issues encountered?
   - Deprecation warnings causing problems?
   - Documentation sufficient?

---

## Troubleshooting

### Issue: Import Errors After Move

**Symptom**: `ModuleNotFoundError: No module named 'training.engine_hf_trainer'`

**Diagnosis**:
```bash
# Check if file exists at new location
ls -l src/training/engine_hf_trainer.py

# Check if compatibility layer working
python -c "import training; print(dir(training))"
```

**Solution**:
- Verify file move completed
- Check `training/__init__.py` has correct re-exports
- Verify `sys.path` includes repo root

### Issue: Strict Mode Fails After Consolidation

**Symptom**: Strict mode shows violations after consolidation

**Diagnosis**:
```bash
# Check for leftover files
ls -l training/*.py | grep -v __init__

# Run strict mode with verbose output
python scripts/remediation/verify_conflicts.py --mode strict
```

**Solution**:
- Verify all legacy files moved (none remain except `__init__.py`)
- Check SHIM_INVENTORY.yaml updated correctly
- Regenerate inventory: `python scripts/remediation/list_shims.py ...`

### Issue: Tests Fail After Move

**Symptom**: Test suite fails with import errors

**Diagnosis**:
```bash
# Run single failing test with verbose
pytest -vv tests/path/to/test_file.py::test_function

# Check which import failing
python -c "from src.training.module import function"
```

**Solution**:
- Update test imports if they used legacy paths
- Verify compatibility layer working
- Check for circular import issues

---

## Success Criteria

### Minimum (v1.3.0 PASS)

- [ ] All 5 legacy modules moved to `src/training/`
- [ ] Root `training/__init__.py` compatibility layer working
- [ ] Strict mode PASSES (0 duplicates, 0 violations)
- [ ] Syntax validation PASSES (all files compile)
- [ ] Import resolution tests PASS (legacy + canonical)
- [ ] SHIM_INVENTORY.yaml updated (status: migrated)
- [ ] Documentation updated (Architecture.md, Consolidation Report)

### Stretch (Exceeds Expectations)

- [ ] Full test suite PASSES (no regressions)
- [ ] Determinism proven (2 runs identical)
- [ ] Full audit pipeline PASSES
- [ ] Baseline updated
- [ ] CI workflows active and passing
- [ ] v1.3.0 release tagged

---

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Backup & Plan | 10 min | Tag, branch, checklist |
| Move Files | 15 min | 5 files, verify each |
| Update __init__ | 15 min | Compatibility layer |
| Update Inventory | 10 min | 5 module entries |
| Syntax Validation | 5 min | py_compile |
| Strict Mode Test | 5 min | verify_conflicts |
| Import Tests | 10 min | Legacy + canonical |
| Full Validation | 30 min | If dependencies available |
| Documentation | 30 min | Reports and updates |
| **Total** | **2-3 hours** | Including validation |

---

## After v1.3.0 Success (99% Readiness)

### Optional Path to 100%

**Refactor remaining 11 legacy imports**:
1. Identify exact locations (analyze_legacy_usage.py)
2. Update to canonical `src.training.*` imports
3. Remove `training/__init__.py` compatibility layer
4. Update documentation

**Timeline**: 1-2 weeks (can be done incrementally)

**Benefit**: Fully canonical import structure, no legacy layer

### Alternative: Maintain 99%

**Keep compatibility layer permanently**:
- Document as architectural decision (ADR)
- Maintain `training/__init__.py` with deprecation warnings
- Monitor legacy usage trends
- Acceptable if team prefers gradual migration

**Benefit**: Zero breaking changes, smooth transition

---

## Next Prompt (Auto-Generate After v1.3.0 PASS)

**v1.3.1 — Final Cleanup & 100% Readiness**:
- Refactor remaining 11 legacy imports
- Remove compatibility layer
- Update documentation
- Final production deployment guide
- Celebration & lessons learned

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| v1.3.0-draft | 2025-12-05 | Initial consolidation plan |
| v1.3.0-ready | TBD | After v1.2.9+strict PASS |

---

**Status**: Ready for execution after v1.2.9+strict PASS  
**Authorization**: @mbaetiong approved autonomous execution  
**Goal**: Move from 92% → 99% production readiness via file consolidation
