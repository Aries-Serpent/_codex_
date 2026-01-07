# Configuration Structure

**Status:** Canonical configuration root established  
**Date:** 2024-12-07  
**Work Package:** WP-F (Config Consolidation)

## Overview

This directory (`configs/`) is the **canonical configuration root** for all Hydra-based configuration in the _codex_ repository. 

## Directory Structure

```
configs/
├── README.md                    # Original README
├── CONFIGURATION_STRUCTURE.md   # This file
├── defaults.yaml                # Default configuration
├── base/                        # Base configurations
│   ├── data/                    # Data loading configs
│   ├── model/                   # Model architecture configs
│   ├── training/                # Training hyperparameters
│   └── evaluation/              # Evaluation configs
├── deployment/                  # Deployment configurations
├── evaluation/                  # Evaluation-specific configs
├── experiments/                 # Experiment tracking configs
├── safety/                      # Safety and security configs
├── schemas/                     # Configuration schemas
└── sweeps/                      # Hyperparameter sweep configs
```

## Legacy Configuration Directories

For backward compatibility, the following directories are maintained as legacy aliases:

- `conf/` - Legacy Hydra config root (deprecated, use `configs/` instead)
- `config/` - Miscellaneous configuration files (non-Hydra)
- `config_legacy/` - Archived legacy configurations

### Migration Path

**Current (Legacy):**
```python
from hydra import initialize_config_dir
initialize_config_dir(config_dir="conf")
```

**Recommended (Canonical):**
```python
from hydra import initialize_config_dir
initialize_config_dir(config_dir="configs")
```

**With Backward Compatibility:**
```python
from hydra import initialize, compose
from hydra.core.global_hydra import GlobalHydra

# Initialize with canonical root
with initialize(config_path="../configs", version_base=None):
    cfg = compose(config_name="defaults")
    
# Or for legacy compatibility:
GlobalHydra.instance().clear()
with initialize(config_path="../conf", version_base=None):
    cfg = compose(config_name="config")
```

## Configuration Best Practices

### 1. Use Structured Configs

Prefer Python dataclasses for type safety:

```python
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

@dataclass
class TrainingConfig:
    batch_size: int = 32
    learning_rate: float = 1e-4
    
cs = ConfigStore.instance()
cs.store(name="training_base", node=TrainingConfig)
```

### 2. Compose Configurations

Use Hydra's composition:

```yaml
# defaults.yaml
defaults:
  - base/data: default
  - base/model: transformer
  - base/training: adamw
  - _self_
```

### 3. Environment-Specific Overrides

```bash
# Development
python train.py +experiment=dev

# Production
python train.py +experiment=prod
```

## Hydra Search Path Configuration

The repository supports multiple configuration roots via Hydra search path:

```python
from hydra import initialize_config_module
from hydra.core.plugins import Plugins
from hydra.plugins.search_path_plugin import SearchPathPlugin

class CodexSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path):
        search_path.append(provider="codex", path="pkg://configs")
        search_path.append(provider="codex-legacy", path="pkg://conf")
```

## Configuration Validation

All configurations should be validated against schemas:

```bash
# Validate configuration
python scripts/validate_config.py --config configs/defaults.yaml

# Generate JSON schema
python scripts/generate_config_schema.py --output configs/schemas/
```

## Testing Configuration

```bash
# List available config groups
nox -s config_index

# Test configuration composition
python -c "
from hydra import initialize, compose
with initialize(config_path='../configs', version_base=None):
    cfg = compose(config_name='defaults')
    print(cfg)
"
```

## Migration Guide

### For Users (Gradual Migration)

**Phase 1:** Continue using existing configs (no change required)
```python
# Works unchanged
from hydra import initialize_config_dir
initialize_config_dir(config_dir="conf")
```

**Phase 2:** Update imports to use canonical path (recommended)
```python
# Updated
from hydra import initialize_config_dir
initialize_config_dir(config_dir="configs")
```

**Phase 3:** Leverage new structure (optional)
```python
# New organized structure
with initialize(config_path="../configs/base", version_base=None):
    cfg = compose(config_name="training/adamw")
```

### For Developers (Adding New Configs)

1. **Create configs in `configs/` directory**
2. **Follow existing structure** (base/, deployment/, etc.)
3. **Add schema validation** in `configs/schemas/`
4. **Update tests** in `tests/config/`
5. **Document in README** or this file

## Troubleshooting

### "Config not found" Error

```bash
# Check available configs
python tools/configs/list_groups.py

# Or use nox
nox -s config_index
```

### Multiple Config Roots Conflict

If experiencing conflicts:
```python
# Clear Hydra singleton
from hydra.core.global_hydra import GlobalHydra
GlobalHydra.instance().clear()

# Re-initialize with correct path
with initialize(config_path="../configs", version_base=None):
    cfg = compose(config_name="defaults")
```

## Related Documentation

- [Hydra Documentation](https://hydra.cc/)
- [Configuration Best Practices](../docs/capabilities/configuration.md)
- [Training Configuration Guide](../docs/capabilities/configuration.md)
- [Deployment Configuration](../docs/capabilities/configuration.md)

## Changelog

### 2024-12-07 (WP-F: Config Consolidation)
- Established `configs/` as canonical root
- Documented legacy paths (`conf/`, `config/`)
- Added migration guide for gradual transition
- Backward compatibility maintained

---

**Note:** This consolidation is part of WP-F (Config Consolidation) from the MLOps Gap Analysis roadmap, addressing configuration sprawl across multiple directories.
