# Next Iteration Prompt (v1.3.0) — File Consolidation & Shim Removal

@copilot complete the final convergence phase by consolidating legacy modules into src/ canonical locations and removing temporary shims. This iteration achieves 99% production readiness.

## Context (v1.2.9 Complete)

**Completed**:
- ✅ v1.2.8: 57.6% legacy import reduction (99 → 42 occurrences)
- ✅ v1.2.9: Canonical src.* shims added to resolve split-brain
- ✅ Production readiness: 85%
- ✅ All refactored imports now work via shims

**Current State**:
- Root `training/` contains: engine_hf_trainer, functional_training, data_utils, checkpoint_manager, config
- `src/training/` contains: trainer, simple_trainer, checkpointing + **5 shim files**
- Shims bridge gap between refactored imports and legacy locations

---

## Objectives (v1.3.0 - Optional)

1. **File Consolidation** (Primary Goal)
   - Move legacy `training/*.py` modules to `src/training/`
   - Verify no import breakage
   - Update root `training/__init__.py` to re-export from src if needed

2. **Shim Removal**
   - Delete shim files (now redundant)
   - Verify imports still work
   - Update tests if needed

3. **Final Validation**
   - Run full audit pipeline (S1-S7)
   - Prove determinism (2 runs)
   - Verify no regressions
   - Execute test suite

4. **Documentation Finalization**
   - Update architecture documentation
   - Document import path conventions
   - Create v1.3.0 completion report

---

## Execution Plan

### Step 1: Backup and Plan

```bash
# Create backup branch
git checkout -b feature/file-consolidation-v1.3.0

# List files to move
ls -1 training/*.py | grep -v __init__
# Expected: engine_hf_trainer.py, functional_training.py, data_utils.py, etc.
```

### Step 2: Move Modules (Careful!)

```bash
# Move core training modules
mv training/engine_hf_trainer.py src/training/
mv training/functional_training.py src/training/
mv training/data_utils.py src/training/
mv training/checkpoint_manager.py src/training/
mv training/config.py src/training/

# Also move supporting modules
mv training/cache.py src/training/
mv training/datasets.py src/training/
mv training/streaming.py src/training/
mv training/evaluate.py src/training/
# ... (all other .py files except __init__.py)
```

### Step 3: Update Root Compatibility Shim

Edit `training/__init__.py` to re-export from `src.training`:

```python
"""Compatibility shim for legacy training imports."""
import sys as _sys

# Import all modules from src.training
from src.training import *  # noqa: F401, F403

# Ensure legacy imports still work via sys.modules
from src.training import engine_hf_trainer, functional_training, data_utils, checkpoint_manager, config
_sys.modules["training.engine_hf_trainer"] = engine_hf_trainer
_sys.modules["training.functional_training"] = functional_training
_sys.modules["training.data_utils"] = data_utils
_sys.modules["training.checkpoint_manager"] = checkpoint_manager
_sys.modules["training.config"] = config
```

### Step 4: Remove Shim Files

```bash
# Delete shim files (now redundant)
rm src/training/engine_hf_trainer.py  # Remove old shim
rm src/training/functional_training.py  # Remove old shim
rm src/training/data_utils.py  # Remove old shim
rm src/training/checkpoint_manager.py  # Remove old shim
rm src/training/config.py  # Remove old shim

# Note: Actual implementation files were moved in Step 2
# The shims had same names, so this removes the shims
# CAREFUL: Ensure moved files exist before deleting shims!
```

### Step 5: Verify Imports

```bash
# Test both import paths still work
python -c "from training.engine_hf_trainer import run_hf_trainer; print('✓ Legacy import works')"
python -c "from src.training.engine_hf_trainer import run_hf_trainer; print('✓ Canonical import works')"

# Test other modules
python -c "from src.training.checkpoint_manager import CheckpointManager; print('✓ CheckpointManager works')"
```

### Step 6: Update Tests

Remove or update shim equivalence tests:
```bash
# Option A: Remove test (no longer needed)
rm tests/validation/test_import_shims.py

# Option B: Update test to verify both paths work post-consolidation
# (both should now point to same actual module in src/training/)
```

### Step 7: Full Validation Suite

```bash
# Legacy import analysis (should remain at 42)
python scripts/remediation/analyze_legacy_usage.py

# Shadowing checks (split-brain should be resolved!)
python scripts/remediation/verify_conflicts.py --expect-site-packages

# Full audit pipeline
python scripts/space_traversal/audit_runner.py run

# Determinism
python scripts/space_traversal/verify_determinism.py --runs 2

# Regression diff
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json

# Test suite
pytest -q tests/validation/
```

### Step 8: Documentation Updates

Create/update:
1. `docs/validation/v1.3.0_Consolidation_Report.md`
   - Files moved
   - Validation results
   - Architecture simplified

2. `docs/Architecture.md` (if exists)
   - Update import path conventions
   - Document src/ as canonical

3. Update `verify_conflicts.py`
   - Remove "warning" mode for split-brain
   - Make it fail hard if both root and src/ have same modules

---

## Acceptance Criteria (v1.3.0 Complete)

- [ ] All legacy `training/*.py` modules moved to `src/training/`
- [ ] Shim files removed
- [ ] Both import paths work (legacy via compatibility, canonical direct)
- [ ] All tests pass
- [ ] Determinism PASS (2 runs identical)
- [ ] No split-brain warnings (verify_conflicts clean)
- [ ] Legacy import count: 42 (maintained)
- [ ] Documentation updated
- [ ] Production readiness: **99%** ✅

---

## Risk Mitigation

1. **Import breakage**: Test both paths after each move
2. **Test failures**: Run tests incrementally
3. **Rollback**: Keep backup branch
4. **Circular imports**: Move files in dependency order

---

## Alternative: Keep Shims (Acceptable)

If file consolidation is too risky or unnecessary:
- **Keep shims permanently**
- **Document as architectural pattern**
- **Update verify_conflicts.py to allow split-brain with shims**
- **Production readiness: 85%** (acceptable)

---

## Success Metrics

**Minimum (v1.3.0 PASS)**:
- Files consolidated
- No import breakage
- Tests pass
- Documentation complete

**Optimal (Exceeds Expectations)**:
- Split-brain fully resolved
- Architecture clean and documented
- 99% production readiness achieved

---

## Begin v1.3.0 Execution

**Decision Required**: Choose consolidation (99%) or keep shims (85%)

**If consolidating**: Follow steps 1-8 above

**If keeping shims**: Update documentation and mark as architectural pattern

---

**Status**: v1.2.9 complete, shims operational, ready for final consolidation  
**Production Readiness**: 85% (99% achievable via consolidation)  
**Authorization**: @mbaetiong approved autonomous work
