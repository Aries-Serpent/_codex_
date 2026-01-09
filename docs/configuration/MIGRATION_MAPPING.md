# Configuration Migration Mapping - PS-01 Cycle 2

**Status:** Planning  
**Created:** 2026-01-08  
**Target:** Pre-commit Cycle 2

## Executive Summary

This document maps the migration of configuration files from the current fragmented structure to a consolidated Hydra-managed system. The repository currently has:

- **136 YAML files** in `configs/` directory
- **12 files** in `conf/` directory (marked as deprecated)
- **Multiple overlapping structures** causing "configuration drift"

## Current State Analysis

### Directory Structure Paradox

The repository has conflicting deprecation notices:
1. `conf/DEPRECATED.md` says use `configs/` instead (Dec 2025)
2. PS-01 Planset says consolidate into `conf/` (Hydra convention)

**Resolution:** Hydra convention (`conf/`) takes precedence per PS-01 objectives. The previous deprecation will be reversed as part of this planset.

### Config File Inventory

| Category | Location | Count | Hydra-Ready? |
|----------|----------|-------|--------------|
| Training configs | `configs/training/` | ~40 | Partial |
| Model configs | `configs/training/model/` | ~10 | Yes |
| Data configs | `configs/training/data/` | ~8 | Yes |
| Evaluation configs | `configs/evaluation/` | ~6 | Yes |
| Deployment configs | `configs/deployment/` | ~25 | No |
| MSP configs | `configs/msp/` | 3 | Partial |
| Event configs | `configs/events/` | 1 | Yes |
| Safety configs | `configs/safety/` | ~5 | Partial |
| Experiment configs | `configs/experiments/` | ~8 | Yes |
| Base configs | `configs/base/` | ~15 | Partial |
| **Total** | | **136** | **~60% ready** |

## Migration Strategy

### Phase 1: High-Priority Configs (Cycle 2)

Migrate configs that:
- Are actively used in training/evaluation workflows
- Have clear Hydra composition benefits
- Have minimal external dependencies

**Target configs:**
1. `configs/training/` → `conf/training/`
2. `configs/evaluation/` → `conf/evaluation/`
3. `configs/experiments/` → `conf/experiment/`
4. Error configs (✅ already migrated in Cycle 1)

### Phase 2: Medium-Priority Configs (Cycle 3)

Migrate configs that:
- Support infrastructure and tools
- Have moderate coupling to external systems

**Target configs:**
1. `configs/base/` → `conf/base/`
2. `configs/msp/` → `conf/msp/`
3. `configs/safety/` → `conf/safety/`

### Phase 3: Low-Priority Configs (Post-PS-01)

Keep in `configs/` for now:
- Deployment-specific configs (tight coupling to CI/CD)
- Third-party tool configs (alertmanager, grafana)
- Legacy configs awaiting deprecation

## Detailed Migration Mapping

### Training Configurations

| Source (configs/) | Destination (conf/) | Priority | Notes |
|-------------------|---------------------|----------|-------|
| `training/model/base.yaml` | `model/base.yaml` | P0 | Core model config |
| `training/model/toy.yaml` | `model/toy.yaml` | P1 | Testing |
| `training/model/offline/*.yaml` | `model/offline/*.yaml` | P1 | Offline models |
| `training/data/tiny.yaml` | `data/tiny.yaml` | P0 | Core data config |
| `training/data/offline/*.yaml` | `data/offline/*.yaml` | P1 | Offline data |
| `training/continual/*.yaml` | `training/continual/*.yaml` | P1 | Continual learning |
| `training/tokenizer/*.yaml` | `training/tokenizer/*.yaml` | P1 | Tokenizer configs |
| `training/sweeps/*.yaml` | `training/sweeps/*.yaml` | P2 | Hyperparameter sweeps |

### Evaluation Configurations

| Source (configs/) | Destination (conf/) | Priority | Notes |
|-------------------|---------------------|----------|-------|
| `evaluation/metrics/*.yaml` | `evaluation/metrics/*.yaml` | P0 | Core metrics |
| `evaluation/reasoning/*.yaml` | `evaluation/reasoning/*.yaml` | P1 | Reasoning eval |

### Experiment Configurations

| Source (configs/) | Destination (conf/) | Priority | Notes |
|-------------------|---------------------|----------|-------|
| `experiments/*.yaml` | `experiment/*.yaml` | P1 | All experiments |

### Infrastructure Configurations

| Source (configs/) | Destination (conf/) | Priority | Notes |
|-------------------|---------------------|----------|-------|
| `base/config.yaml` | `config.yaml` | P0 | Root config |
| `base/environment/*.yaml` | `environment/*.yaml` | P1 | Env configs |
| `base/logging/*.yaml` | `logging/*.yaml` | P0 | Logging setup |
| `base/safety/*.yaml` | `safety/*.yaml` | P1 | Safety configs |
| `msp/*.yaml` | `msp/*.yaml` | P1 | MSP service configs |

## Migration Checklist per Config

For each config file being migrated:

- [ ] **Analyze** config structure and dependencies
- [ ] **Create** new file in `conf/` with Hydra defaults if applicable
- [ ] **Test** config loads via new ConfigLoader
- [ ] **Add** backward compatibility alias in `configs/` (symlink or stub)
- [ ] **Update** code references to use new path
- [ ] **Document** in migration notes
- [ ] **Verify** tests pass

## Hydra Composition Patterns

### Config Groups

Organize configs into logical groups:

```
conf/
├── config.yaml              # Root config with defaults
├── errors/
│   └── defaults.yaml        # ✅ Cycle 1
├── model/
│   ├── base.yaml
│   ├── toy.yaml
│   └── offline/
│       ├── gpt2.yaml
│       └── tinyllama.yaml
├── data/
│   ├── tiny.yaml
│   └── offline/
│       └── tiny_corpus.yaml
├── training/
│   ├── base.yaml
│   ├── continual/
│   │   ├── base.yaml
│   │   └── rehearsal.yaml
│   └── tokenizer/
│       └── train_tokenizer.yaml
└── evaluation/
    ├── base.yaml
    └── metrics/
        └── default.yaml
```

### Defaults List Pattern

Root config with composition:

```yaml
# conf/config.yaml
defaults:
  - _self_
  - model: base
  - data: tiny
  - training: base
  - evaluation: base
  - errors: defaults
  - override hydra/hydra_logging: colorlog
  - override hydra/job_logging: colorlog

# Application config
app:
  name: codex
  version: 1.0.0
```

## Backward Compatibility Strategy

### Dual-Path Support (2 Cycles)

During migration:
1. New code uses `conf/` via ConfigLoader
2. Old code continues using `configs/` (no changes)
3. ConfigLoader supports both paths with precedence

### Implementation

```python
# In ConfigLoader
def _find_config_dir(self, config_dir: str | None) -> Path:
    """Find config directory with fallback to legacy paths."""
    if config_dir is None:
        # Try new convention first
        new_path = self.repo_root / "conf"
        if new_path.exists():
            return new_path
        # Fallback to legacy
        return self.repo_root / "configs"
    return Path(config_dir)
```

## Update Patterns

### Code Import Updates

```python
# OLD (direct YAML loading)
import yaml
with open("configs/training/model/base.yaml") as f:
    config = yaml.safe_load(f)

# NEW (Hydra composition)
from codex.utils.config_loader import load_config
config = load_config("base", config_dir="conf/model")
```

### CLI Updates

```python
# OLD (hardcoded paths)
@click.option("--config", type=click.Path(), default="configs/training/base.yaml")

# NEW (Hydra composition)
@click.option("--config-name", default="base")
@click.option("--config-dir", default="conf/training")
```

## Testing Strategy

### Unit Tests

```python
def test_config_migration():
    """Test config loads from both old and new locations."""
    # Load from new location
    new_cfg = load_config("base", config_dir="conf/model")
    
    # Load from old location
    old_cfg = load_config("base", config_dir="configs/training/model")
    
    # Verify equivalence
    assert new_cfg == old_cfg
```

### Integration Tests

- [ ] Training pipeline with new configs
- [ ] Evaluation pipeline with new configs
- [ ] Experiment launcher with new configs
- [ ] All CLI commands with new configs

## Risk Assessment

### High Risk Areas

1. **Training Pipelines**: Heavy config dependency
   - **Mitigation**: Extensive testing, gradual rollout
   
2. **CI/CD Workflows**: Hardcoded paths
   - **Mitigation**: Update workflows, test in dev environment

3. **External Tools**: May reference old paths
   - **Mitigation**: Symlinks for compatibility

### Rollback Plan

If critical issues arise:
1. Revert code changes to use `configs/`
2. Keep new `conf/` structure for gradual migration
3. Extend grace period by 1 cycle

## Success Metrics

### Cycle 2 Targets

- [ ] 20+ configs migrated to `conf/`
- [ ] All training configs Hydra-composable
- [ ] Zero regression in existing functionality
- [ ] Migration documentation complete

### Overall PS-01 Targets

- [ ] 80+ configs migrated (60% of total)
- [ ] Config loading time <100ms
- [ ] -500 lines of duplicate config code
- [ ] Single source of truth established

## Timeline

| Milestone | Target | Status |
|-----------|--------|--------|
| Cycle 1: Error configs | ✅ Complete | Done |
| Cycle 2: Training configs | Week 2 | Planning |
| Cycle 2: Evaluation configs | Week 2 | Planning |
| Cycle 3: Infrastructure configs | Week 3 | Planned |
| Cycle 3: Full testing | Week 3 | Planned |

## References

- PS-01 Planset: `.github/plans/PLANSET_01_CONFIGURATION_CONSOLIDATION.md`
- Migration Guide: `docs/configuration/HYDRA_MIGRATION_GUIDE.md`
- Existing Deprecated Notice: `conf/DEPRECATED.md` (to be updated)
- Config Inventory: `configs/CONFIGURATION_STRUCTURE.md`

## Next Actions

1. Update `conf/DEPRECATED.md` to reflect new strategy
2. Begin migrating training configs (highest priority)
3. Update ConfigLoader to support dual-path fallback
4. Create automated migration script for bulk updates
5. Update codebase to use new ConfigLoader

---

**Document Owner:** GitHub Copilot (PS-01)  
**Review Date:** After Cycle 2 completion  
**Last Updated:** 2026-01-08
