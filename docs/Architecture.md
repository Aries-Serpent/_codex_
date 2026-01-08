# Architecture: Shim Governance & Canonical Import Policy (v1.2.9)

> Generated: 2025-12-05 | Author: mbaetiong  
> Status: Active | Readiness: 85% → 99% path

🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Overview

This document defines the governance policy for import shims and canonical module paths during the convergence from split-brain architecture to a unified `src.*` canonical structure.

## Policy Summary

- **Canonical Location**: All runtime modules should ultimately live under `src/`
- **Legacy Shims**: Temporary shims may exist in root paths (e.g., `training/`) during convergence
- **Shim Implementation**: Shims MUST re-export from `src.*` and maintain API equivalence
- **Identity Requirements**: `training.X` must resolve to equivalent functionality as `src.training.X`
- **CI Enforcement**: Strict conflict detection enabled; duplicates allowed only if whitelisted

## Current State (v1.2.9)

### Import Reduction Progress
- **Baseline**: 99 legacy import occurrences
- **Current**: 42 occurrences (57.6% reduction ✅)
- **Tokenization**: 100% migrated to `src.*` (13 → 0)
- **Training**: 79% migrated to `src.*` (53 → 11)
- **Models**: 50% migrated to `src.*` (4 → 2)
- **Hydra**: config_legacy fallbacks (29 preserved for compatibility)

### Shim Architecture

**Active Shims** (as of v1.2.9):
- `src/training/engine_hf_trainer.py` → forwards to `training.engine_hf_trainer`
- `src/training/functional_training.py` → forwards to `training.functional_training`
- `src/training/data_utils.py` → forwards to `training.data_utils`
- `src/training/checkpoint_manager.py` → forwards to `training.checkpoint_manager`
- `src/training/config.py` → forwards to `training.config`
- `src/tokenization/train_tokenizer.py` → forwards to `tokenization.train_tokenizer`

**Shim Pattern**:
```python
"""Canonical import shim for src.training.module_name"""
from importlib import import_module as _im

_mod = _im("training.module_name")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
```

## Governance Rules

### Rule 1: Canonicalization Priority
| Priority | Action | Timeline |
|----------|--------|----------|
| P0 | Migrate high-usage runtime modules to `src/` | Phase 1 (Current Cycle) |
| P1 | Keep minimal, documented shims during transition | Until migration complete |
| P2 | Deprecate and remove shims after migration | Phase 2 (Current Cycle) |

### Rule 2: Shim Requirements
All shims MUST:
- Re-export ALL public APIs from the legacy module
- Maintain API equivalence (validated by `test_shim_equivalence.py`)
- Include deprecation date in `.github/SHIM_INVENTORY.yaml`
- Document rationale and ownership

### Rule 3: CI Gating
- **Strict Mode**: Enabled in CI via `verify_conflicts.py --mode strict`
- **Whitelist**: Duplicates allowed only if listed in `.github/SHIM_INVENTORY.yaml`
- **PR Blocking**: Non-whitelisted duplicates block merge
- **Shim-Aware Mode**: Available for local debugging only

### Rule 4: Decision Gates for Consolidation
Before moving a module from legacy to `src/`:

| Gate | Requirement | Validation |
|------|-------------|------------|
| **Ownership** | Owner approved in SHIM_INVENTORY.yaml | Manual review |
| **Usage Trend** | Legacy imports for module < 10% for 90 days | Nightly audit metrics |
| **Test Equivalence** | test_shim_equivalence + full suite PASS | CI validation |
| **No Split-Brain** | verify_conflicts strict shows no violations | CI check |
| **Low Risk** | Affects < 10 tests | Impact analysis |
| **Rollback Ready** | Backup branch + tested rollback script | Pre-consolidation prep |

### Rule 5: Rollback Procedures
Every consolidation PR MUST include:
- Backup branch before changes
- Tested rollback script
- Rollback validation (tests + determinism)
- Documented rollback steps in PR description

## Tooling & Automation

### Inventory Management
```bash
# Generate shim inventory
python scripts/remediation/list_shims.py \
  --roots training src/training tokenization src/tokenization \
  --output .github/SHIM_INVENTORY.yaml
```

### Conflict Detection
```bash
# Strict mode (CI gating)
python scripts/remediation/verify_conflicts.py \
  --mode strict \
  --output audit_artifacts/conflicts.json

# Shim-aware mode (local debugging)
python scripts/remediation/verify_conflicts.py \
  --mode shim-aware \
  --output audit_artifacts/conflicts.json
```

### Equivalence Testing
```bash
# Run shim equivalence tests
pytest -q tests/validation/test_shim_equivalence.py

# Strict identity mode (CI only)
SHIM_IDENTITY_STRICT=1 pytest -q tests/validation/test_shim_equivalence.py
```

### Nightly Audit
- **Workflow**: `.github/workflows/nightly-audit.yml`
- **Schedule**: Daily at 02:00 UTC
- **Outputs**: Inventory, conflicts, legacy usage report
- **Alerting**: Auto-creates issue on violations

### Determinism Validation
- **Workflow**: `.github/workflows/determinism.yml`
- **Trigger**: Pull requests touching `src/`, `scripts/`, `tests/`, `training/`, `tokenization/`
- **Checks**: Full audit, 2-run determinism, strict conflicts
- **Artifacts**: Uploaded for review

## Path to 99% Readiness

### Current: 85% Ready (v1.2.9)
✅ Split-brain resolved via shims  
✅ All imports work correctly  
✅ CI gating in place  
✅ Inventory and governance established

### Target: 99% Ready (v1.3.0)
Two paths available:

**Option A: Full Consolidation** (99% readiness)
1. Move legacy modules from `training/` → `src/training/`
2. Move legacy modules from `tokenization/` → `src/tokenization/`
3. Update root `__init__.py` files as compatibility shims
4. Remove canonical shim files (no longer needed)
5. Update remaining legacy imports (11 training + 29 hydra)
6. Final validation and baseline update

**Option B: Shim Governance** (85-90% readiness, permanent)
1. Keep shims as architectural pattern
2. Formalize in ADR (Architecture Decision Record)
3. Maintain via inventory and nightly audits
4. System remains operational and maintainable

## References

- **Shim Inventory**: `.github/SHIM_INVENTORY.yaml`
- **Consolidation Playbook**: `.github/CONSOLIDATION_PLAYBOOK.md`
- **Wave 3 Convergence Plan**: `docs/validation/Wave3_SplitBrain_Convergence.md`
- **v1.2.9 Validation Log**: `docs/validation/v1.2.9_Validation_Log.md`
- **v1.3.0 Next Steps**: `.github/copilot_agent_task_prompt_v1.3.0.md`

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.2.9 | 2025-12-05 | mbaetiong | Initial policy definition |

---

**Status**: Active | **Next Review**: Phase 1 (Current Cycle) or upon consolidation decision
