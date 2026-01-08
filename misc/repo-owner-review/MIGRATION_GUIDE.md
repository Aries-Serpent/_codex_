# Configuration Migration Guide

**Last Updated**: 2025-12-12  
**Purpose**: Step-by-step migration from `conf/` to `configs/` directory structure

---

## Overview

The repository is consolidating configuration files from the legacy `conf/` directory to the standard `configs/` directory structure. This guide provides detailed instructions for updating all 196+ code references.

---

## Migration Timeline

| Phase | Date | Action |
|-------|------|--------|
| **Deprecation Notice** | Dec 2025 | All `conf/` files marked deprecated |
| **Grace Period** | Jan 2026 - Jun 2026 | Both directories functional |
| **Migration Deadline** | Jun 30, 2026 | All references should be updated |
| **Removal** | v2.0.0 (Q2 2026) | `conf/` directory removed |

---

## Configuration File Mapping

### Complete Path Mapping

| Legacy Path (`conf/`) | New Path (`configs/`) | Status |
|-----------------------|----------------------|--------|
| `conf/config.yaml` | `configs/base/config.yaml` | ⚠️ Deprecated |
| `conf/data/local.yaml` | `configs/base/local.yaml` | ⚠️ Deprecated |
| `conf/evaluation/minimal.yaml` | `configs/evaluation/base.yaml` | ⚠️ Deprecated |
| `conf/experiment/basic.yaml` | `configs/experiments/basic.yaml` | ⚠️ Deprecated |
| `conf/experiment/default.yaml` | `configs/experiments/default.yaml` | ⚠️ Deprecated |
| `conf/experiment/sweep.yaml` | `configs/experiments/sweep.yaml` | ⚠️ Deprecated |
| `conf/minimal_eval.yaml` | `configs/development/minimal_eval.yaml` | ⚠️ Deprecated |
| `conf/minimal_train.yaml` | `configs/development/minimal_train.yaml` | ⚠️ Deprecated |
| `conf/model/base.yaml` | `configs/training/model/base.yaml` | ⚠️ Deprecated |
| `conf/training/minimal.yaml` | `configs/development/minimal.yaml` | ⚠️ Deprecated |

---

## Step-by-Step Migration

### Step 1: Find All References

Use these commands to locate all references to the `conf/` directory:

```bash
# Find all Python files referencing conf/ (matches quoted path references)
grep -rn '"conf/' --include="*.py" . | grep -v "configs/"
grep -rn "'conf/" --include="*.py" . | grep -v "configs/"

# Find all YAML files referencing conf/
grep -rn "conf/" --include="*.yaml" --include="*.yml" . | grep -v "configs/"

# Count total references (quoted paths only to avoid false positives)
grep -rE '["'"'"']conf/' --include="*.py" . | grep -v "configs/" | wc -l
```

### Step 2: Update Python Imports

#### Before (Legacy)

```python
from omegaconf import OmegaConf

# Loading legacy config
config = OmegaConf.load("conf/config.yaml")

# Hydra configuration
@hydra.main(config_path="../conf", config_name="config")
def train(cfg):
    pass
```

#### After (New)

```python
from omegaconf import OmegaConf

# Loading new config
config = OmegaConf.load("configs/base/config.yaml")

# Hydra configuration
@hydra.main(config_path="../configs/base", config_name="config")
def train(cfg):
    pass
```

### Step 3: Update Path References

#### OmegaConf Load Patterns

```python
# Old pattern
OmegaConf.load("conf/minimal_train.yaml")

# New pattern
OmegaConf.load("configs/development/minimal_train.yaml")
```

#### Hydra Decorators

```python
# Old pattern
@hydra.main(config_path="conf", config_name="config")

# New pattern
@hydra.main(config_path="configs/base", config_name="config")
```

#### Path Construction

```python
# Old pattern
config_dir = Path(__file__).parent / "conf"

# New pattern
config_dir = Path(__file__).parent / "configs"
```

### Step 4: Update Test Fixtures

Tests that use configuration files need to be updated:

```python
# Old pattern (conftest.py)
@pytest.fixture
def minimal_config():
    return OmegaConf.load("conf/minimal_train.yaml")

# New pattern
@pytest.fixture
def minimal_config():
    return OmegaConf.load("configs/development/minimal_train.yaml")
```

### Step 5: Verify Changes

After making updates, run these verification steps:

```bash
# Run tests
pytest tests/ -v

# Check for remaining references
grep -rn "\"conf/" --include="*.py" .

# Verify configs load correctly
python -c "from omegaconf import OmegaConf; OmegaConf.load('configs/base/config.yaml')"
```

---

## Automated Migration Tool

Use the consolidation script for automated migration:

```bash
# Preview changes (dry run)
python scripts/remediation/consolidate_configs.py --dry-run

# View migration guide
python scripts/remediation/consolidate_configs.py --generate-guide

# Generate SHIM entries for tracking
python scripts/remediation/consolidate_configs.py --generate-shim

# Execute migration (use with caution)
python scripts/remediation/consolidate_configs.py --execute
```

---

## Search and Replace Commands

For bulk updates, use these sed commands:

```bash
# Update Python files
find . -name "*.py" -exec sed -i 's|"conf/config.yaml"|"configs/base/config.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/minimal_train.yaml"|"configs/development/minimal_train.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/minimal_eval.yaml"|"configs/development/minimal_eval.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/data/local.yaml"|"configs/base/local.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/model/base.yaml"|"configs/training/model/base.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/training/minimal.yaml"|"configs/development/minimal.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/experiment/basic.yaml"|"configs/experiments/basic.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/experiment/default.yaml"|"configs/experiments/default.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/experiment/sweep.yaml"|"configs/experiments/sweep.yaml"|g' {} \;
find . -name "*.py" -exec sed -i 's|"conf/evaluation/minimal.yaml"|"configs/evaluation/base.yaml"|g' {} \;

# Update Hydra config_path arguments
find . -name "*.py" -exec sed -i 's|config_path="conf"|config_path="configs/base"|g' {} \;
find . -name "*.py" -exec sed -i "s|config_path='conf'|config_path='configs/base'|g" {} \;
find . -name "*.py" -exec sed -i 's|config_path="../conf"|config_path="../configs/base"|g' {} \;
```

---

## Common Issues and Solutions

### Issue 1: Hydra Cannot Find Config

**Symptom**: `ConfigCompositionException: Cannot find primary config`

**Solution**: Ensure both `config_path` and `config_name` are updated:

```python
# Make sure the config file exists at the new path
@hydra.main(config_path="../configs/base", config_name="config", version_base=None)
```

### Issue 2: Missing Defaults

**Symptom**: `MissingMandatoryValue` for defaults

**Solution**: Update defaults references in the config files:

```yaml
# Old defaults
defaults:
  - experiment: basic

# may need to update to:
defaults:
  - /experiments: basic
```

### Issue 3: Relative Import Issues

**Symptom**: `FileNotFoundError` when loading configs

**Solution**: Use absolute paths or `pkg_resources`:

```python
from pathlib import Path
import pkg_resources

# Option 1: Absolute path from module
config_path = Path(__file__).parent.parent / "configs" / "base" / "config.yaml"

# Option 2: Using pkg_resources
config_path = pkg_resources.resource_filename("codex", "configs/base/config.yaml")
```

---

## Verification Checklist

Before marking migration complete:

- [ ] All Python files updated (grep shows no `"conf/` references)
- [ ] All YAML files updated (no internal references to `conf/`)
- [ ] All tests pass (`pytest tests/`)
- [ ] Hydra applications start correctly
- [ ] No `DeprecationWarning` messages in logs
- [ ] Documentation updated
- [ ] CI/CD pipelines working

---

## Migration Assistance

### Need Help?

1. **Documentation**: See `configs/README.md` for new structure details
2. **Automated Tool**: Use `scripts/remediation/consolidate_configs.py`
3. **Repository Owner**: Create an issue with `[Config Migration]` prefix

### Reporting Issues

If you encounter migration issues:

1. Document the specific file and line number
2. Include the error message
3. Create an issue with:
   - Title: `[Config Migration] <brief description>`
   - Label: `config-migration`
   - Include before/after code snippets

---

## Reference

### Directory Structure Comparison

```
# Legacy Structure (conf/)
conf/
├── config.yaml
├── minimal_eval.yaml
├── minimal_train.yaml
├── data/
│   └── local.yaml
├── evaluation/
│   └── minimal.yaml
├── experiment/
│   ├── basic.yaml
│   ├── default.yaml
│   └── sweep.yaml
├── model/
│   └── base.yaml
└── training/
    └── minimal.yaml

# New Structure (configs/)
configs/
├── base/
│   ├── config.yaml
│   └── local.yaml
├── development/
│   ├── minimal.yaml
│   ├── minimal_eval.yaml
│   └── minimal_train.yaml
├── evaluation/
│   └── base.yaml
├── experiments/
│   ├── basic.yaml
│   ├── default.yaml
│   └── sweep.yaml
└── training/
    └── model/
        └── base.yaml
```

---

**Migration Guide Version**: 1.0  
**Author**: Copilot AI Assistant  
**Related Files**: `conf/DEPRECATED.md`, `scripts/remediation/consolidate_configs.py`
