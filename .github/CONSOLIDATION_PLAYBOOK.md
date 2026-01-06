# Consolidation Playbook: Move & Shim Removal (v1.2.9-pre)

> Generated: Previous Cycle-12-05 | Author: mbaetiong  
> Status: Draft | Target: v1.3.0

🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Scope

This playbook defines the procedure for consolidating split-brain architecture by moving authoritative runtime modules from legacy root directories (`training/`, `tokenization/`) to canonical `src/` locations, updating compatibility shims, and removing redundant forwarding shims.

## Prerequisites

Before starting consolidation:

- [ ] All decision gates PASS (see `docs/Architecture.md`)
- [ ] Shim inventory complete (`.github/SHIM_INVENTORY.yaml`)
- [ ] Equivalence tests passing (`test_shim_equivalence.py`)
- [ ] Determinism validated (2+ identical runs)
- [ ] Strict conflict detection configured
- [ ] Rollback procedures tested
- [ ] Owner approvals documented

## Consolidation Phases

### Phase 0: Preparation & Dry-Run

**Objective**: Validate consolidation plan without making changes

```bash
# 1. Create backup branch
git checkout -b backup/pre-consolidation-v1.2.9
git push origin backup/pre-consolidation-v1.2.9

# 2. Create consolidation branch
git checkout main
git pull --rebase origin main
git checkout -b feature/consolidate-to-src

# 3. Generate consolidation plan (dry-run)
python scripts/remediation/migrate_to_src.py \
  --dry-run \
  --modules training.engine_hf_trainer training.functional_training \
  --output audit_artifacts/dry_runs/consolidation_plan.json

# 4. Review plan artifacts
cat audit_artifacts/dry_runs/consolidation_plan.json
```

**Validation**:
- [ ] Dry-run plan generated successfully
- [ ] File moves list correct (legacy → src/)
- [ ] Import updates list complete
- [ ] Shim removal list accurate
- [ ] Test impact assessment < threshold (e.g., 10 tests)

### Phase 1: Move Modules to src/

**Objective**: Relocate authoritative implementations to canonical locations

```bash
# Move modules in small batches (5-6 files per batch)
python scripts/remediation/migrate_to_src.py \
  --apply \
  --batch-size 6 \
  --modules training.engine_hf_trainer training.functional_training training.data_utils \
  --backup-suffix .consolidation_backup

# Validate syntax after each batch
python -m py_compile src/training/*.py

# Commit per batch
git add -A
git commit -m "feat(consolidation): move training.engine_hf_trainer et al to src/training/ (batch 1/2)"
```

**Post-Move Checklist** (per batch):
- [ ] Files moved successfully
- [ ] Backups created (`.consolidation_backup`)
- [ ] Syntax validation passes
- [ ] Git commit created
- [ ] No file deletions (only moves)

### Phase 2: Update Root Shims

**Objective**: Convert root `__init__.py` to compatibility shims

**Before** (`training/__init__.py`):
```python
# Current: imports from src.training
from src.training.trainer import Trainer
```

**After** (`training/__init__.py`):
```python
"""
Legacy compatibility shim for training module.
All implementations now live under src/training/.
This module provides backward compatibility during transition.
"""
import warnings

warnings.warn(
    "Importing from 'training' is deprecated. Use 'src.training' instead. "
    "This compatibility layer will be removed in v2.0.0.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export canonical implementations
from src.training.engine_hf_trainer import *  # noqa: F401, F403
from src.training.functional_training import *  # noqa: F401, F403
from src.training.trainer import *  # noqa: F401, F403
# ... (all modules)
```

**Update Script**:
```bash
# Apply shim template to root __init__.py
python scripts/remediation/update_root_shims.py \
  --modules training tokenization \
  --template templates/consolidation/root_shim_template.py

# Validate
python -m py_compile training/__init__.py tokenization/__init__.py

# Commit
git add training/__init__.py tokenization/__init__.py
git commit -m "feat(consolidation): update root shims to re-export from src/"
```

**Validation**:
- [ ] Deprecation warnings added
- [ ] All modules re-exported
- [ ] Syntax valid
- [ ] Legacy imports still work (backward compatibility)

### Phase 3: Remove Redundant Canonical Shims

**Objective**: Clean up forwarding shims in `src/` (no longer needed after move)

```bash
# Identify redundant shims (dry-run first)
python scripts/consolidation/remove_shims.sh --dry-run

# Review list
cat audit_artifacts/shims_to_remove.txt

# Apply removal
python scripts/consolidation/remove_shims.sh --apply

# Commit
git add -A
git commit -m "chore(consolidation): remove redundant canonical shims post-move"
```

**Shims to Remove**:
- `src/training/engine_hf_trainer.py` (forwarding shim)
- `src/training/functional_training.py` (forwarding shim)
- `src/training/data_utils.py` (forwarding shim)
- `src/training/checkpoint_manager.py` (forwarding shim)
- `src/training/config.py` (forwarding shim)
- `src/tokenization/train_tokenizer.py` (forwarding shim)

**Keep** (actual implementations):
- `src/training/trainer.py`
- `src/training/simple_trainer.py`
- `src/training/checkpointing.py`

**Validation**:
- [ ] Only forwarding shims removed
- [ ] Actual implementations retained
- [ ] `src.*` imports still work
- [ ] Legacy imports still work (via root compat shim)

### Phase 4: Update Remaining Legacy Imports

**Objective**: Migrate remaining direct legacy imports to canonical `src.*`

```bash
# Analyze remaining legacy imports
python scripts/remediation/analyze_legacy_usage.py

# Target: 11 training + 29 hydra (from v1.2.9)
# Focus on the 11 training imports first

# Manual updates (small batches)
# Update each file's imports: training.X → src.training.X

# Validate per file
python -m py_compile path/to/updated/file.py

# Commit per batch (5 files)
git add <files>
git commit -m "refactor(consolidation): migrate remaining training imports to src.* (batch X/Y)"
```

**Validation**:
- [ ] Legacy count decreasing
- [ ] No syntax errors
- [ ] Tests pass (if runnable)

### Phase 5: Final Validation

**Objective**: Comprehensive validation of consolidated state

```bash
# 1. Syntax validation (all Python files)
find src/ training/ tokenization/ -name "*.py" -exec python -m py_compile {} +

# 2. Import resolution test
python -c "from src.training.engine_hf_trainer import *; print('✓ Import works')"
python -c "from training.engine_hf_trainer import *; print('✓ Legacy compat works')"

# 3. Equivalence tests
pytest -q tests/validation/test_shim_equivalence.py

# 4. Strict conflict detection
python scripts/remediation/verify_conflicts.py --mode strict --output audit_artifacts/conflicts.json

# 5. Determinism validation (2 runs)
python scripts/space_traversal/verify_determinism.py --runs 2

# 6. Full audit pipeline
python scripts/space_traversal/audit_runner.py run

# 7. Baseline diff
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json
```

**Validation Checklist**:
- [ ] All syntax validation passes
- [ ] Canonical imports work (`src.*`)
- [ ] Legacy imports work (via compat shim)
- [ ] Equivalence tests PASS
- [ ] Strict conflicts PASS (or whitelisted)
- [ ] Determinism PASS (identical runs)
- [ ] Audit pipeline completes
- [ ] No regression in baseline diff

### Phase 6: Baseline Update

**Objective**: Update baseline artifacts and metadata

```bash
# Update baseline
bash scripts/ci/establish_baseline.sh --force

# Commit baseline
git add audit_artifacts/baselines/capabilities_scored.json
git add audit_artifacts/baselines/metadata.json
git commit -m "chore(consolidation): update baseline post-consolidation"
```

**Validation**:
- [ ] Baseline updated successfully
- [ ] Metadata includes consolidation note
- [ ] SHA256 recorded
- [ ] Capability count stable or improved

### Phase 7: Rollback Validation

**Objective**: Verify rollback procedure works (before merging)

```bash
# 1. Create rollback test branch
git checkout -b test/consolidation-rollback
git reset --hard backup/pre-consolidation-v1.2.9

# 2. Validate pre-consolidation state
pytest -q tests/validation/
python scripts/space_traversal/verify_determinism.py --runs 2

# 3. Return to consolidation branch
git checkout feature/consolidate-to-src

# 4. Document rollback procedure
cat > ROLLBACK_PROCEDURE.md <<EOF
# Rollback Procedure for Consolidation PR

If issues arise post-merge:

1. Revert merge commit:
   git revert <merge_commit_sha> -m 1

2. Restore from backup branch:
   git checkout backup/pre-consolidation-v1.2.9
   git checkout -b hotfix/rollback-consolidation
   git cherry-pick <needed_fixes>

3. Validate:
   pytest -q tests/validation/
   python scripts/space_traversal/verify_determinism.py --runs 2

4. Emergency restore from backups:
   python scripts/remediation/migrate_to_src.py --restore backups/*.consolidation_backup
EOF
```

**Validation**:
- [ ] Rollback procedure documented
- [ ] Backup branch accessible
- [ ] Backup files exist (`.consolidation_backup`)
- [ ] Rollback tested on separate branch
- [ ] Rollback validation passes

## PR Checklist

Before opening consolidation PR:

### Code Changes
- [ ] All modules moved to `src/`
- [ ] Root shims updated (deprecation warnings)
- [ ] Redundant canonical shims removed
- [ ] Remaining legacy imports updated
- [ ] Syntax validation passes

### Testing & Validation
- [ ] Equivalence tests PASS
- [ ] Strict conflicts PASS
- [ ] Determinism PASS (2 runs)
- [ ] Full audit completes
- [ ] Baseline updated
- [ ] No regressions

### Documentation
- [ ] Consolidation plan attached (dry-run)
- [ ] Rollback procedure documented
- [ ] SHIM_INVENTORY.yaml updated (shims marked deprecated/removed)
- [ ] Architecture.md updated
- [ ] CHANGELOG entry created

### Safety Nets
- [ ] Backup branch created and pushed
- [ ] Rollback tested on separate branch
- [ ] Backup files present (`.consolidation_backup`)
- [ ] Owner approvals documented

### Artifacts
- [ ] Dry-run plan (audit_artifacts/dry_runs/)
- [ ] Validation logs (determinism, conflicts, tests)
- [ ] Before/after legacy import counts
- [ ] Baseline diff report

## Post-Merge Actions

After PR merges:

1. **Tag Release**: `git tag v1.3.0-consolidated && git push origin v1.3.0-consolidated`
2. **Update Docs**: Mark v1.3.0 as stable in README
3. **Monitor**: Watch CI for 48 hours post-merge
4. **Cleanup**: Remove backup branch after 30 days (if stable)
5. **Announce**: Notify team of deprecation timeline for legacy imports

## Troubleshooting

### Issue: Import errors after consolidation
**Solution**: Check root shim re-exports are complete
```bash
# Verify all modules exported
python -c "import training; print(dir(training))"
```

### Issue: Tests fail with ModuleNotFoundError
**Solution**: Update test imports or extend root shim
```bash
# Add missing module to root shim
echo "from src.training.missing_module import *  # noqa" >> training/__init__.py
```

### Issue: Determinism fails post-consolidation
**Solution**: Check for path-dependent behavior in moved modules
```bash
# Re-run with verbose output
python scripts/space_traversal/verify_determinism.py --runs 2 --verbose
```

### Issue: Need to rollback
**Solution**: Use documented rollback procedure
```bash
# Revert merge commit
git revert <merge_commit_sha> -m 1

# Or restore from backup
git checkout backup/pre-consolidation-v1.2.9
```

## Success Criteria

Consolidation is successful when:

- ✅ All modules in canonical locations (`src/`)
- ✅ Backward compatibility maintained (legacy imports work via compat shim)
- ✅ All validation gates PASS
- ✅ Production readiness ≥99%
- ✅ Rollback procedure tested and documented
- ✅ Team notified of changes

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 0. Preparation | 0.5 day | Decision gates met |
| 1. Move modules | 1 day | Dry-run approved |
| 2. Update root shims | 0.5 day | Phase 1 complete |
| 3. Remove redundant shims | 0.5 day | Phase 2 complete |
| 4. Update legacy imports | 1 day | Phase 3 complete |
| 5. Final validation | 1 day | All changes complete |
| 6. Baseline update | 0.25 day | Validation passes |
| 7. Rollback validation | 0.25 day | Parallel with others |
| **Total** | **4-5 days** | Sequential execution |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.2.9-pre | Previous Cycle-12-05 | mbaetiong | Initial playbook draft |

---

**Status**: Draft | **Next Review**: Upon decision to proceed with consolidation
