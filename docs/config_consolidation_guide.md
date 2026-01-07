# Configuration Consolidation Guide (D4)

## Overview

This guide documents the unified configuration structure for the Codex ML project. All configurations have been consolidated under the `configs/` directory with a clear, hierarchical structure that supports both development and production use cases.

## Directory Structure

```
configs/
├── __init__.py              # Package marker
├── README.md                # Configuration overview
├── CONFIGURATION_STRUCTURE.md  # This file
├── base/                    # Base configurations (defaults)
│   ├── training.yaml
│   ├── model.yaml
│   ├── data.yaml
│   ├── tracking.yaml
│   ├── validation.yaml
│   ├── reproducibility.yaml
│   └── ... (other base configs)
├── production/              # Production overrides
│   ├── tracking.yaml
│   ├── features.yaml
│   ├── data_validation.yaml
│   ├── evaluation.yaml
│   ├── training.yaml
│   └── monitoring.yaml
├── development/             # Development overrides
│   ├── minimal_train.yaml
│   ├── minimal_eval.yaml
│   └── minimal.yaml
├── experiments/             # Experiment-specific configs
│   ├── default.yaml
│   ├── sweep.yaml
│   └── basic.yaml
├── hydra/                   # Hydra-specific configs
│   └── config.yaml          # Main Hydra configuration
└── ... (other config directories)
```

## Unified Configuration Access

### Using Python API

```python
from codex_ml.config import get_config, load_yaml, CONFIG_PATH

# Load config using Hydra
config = get_config("hydra/config", overrides=["training.epochs=100"])

# Load a YAML file directly
yaml_config = load_yaml("configs/base/training.yaml")

# Access the config path
print(f"Config directory: {CONFIG_PATH}")
```

### Using Command Line

```bash
# Run with default config
python -m codex_ml.training

# Run with overrides
python -m codex_ml.training training.epochs=50 env=production

# Run a sweep
python -m codex_ml.training --multirun training.batch_size=8,16,32
```

## Migration from Legacy Directories

### Legacy Configuration Directories

The following directories were consolidated into `configs/`:

- `conf/` - Legacy Hydra configurations
- `config/` - Legacy application configurations  

These directories are preserved for backward compatibility during the transition period but should not be used for new configurations.

### Migration Steps

The migration was performed using the `scripts/migrate_configs.py` script:

```bash
# Dry run to see what would be migrated
python scripts/migrate_configs.py --dry-run

# Execute migration
python scripts/migrate_configs.py --execute
```

### Migration Results

- ✅ 11 legacy configuration files migrated to unified structure
- ✅ Hydra configuration created at `configs/hydra/config.yaml`
- ✅ Directory structure validated
- ✅ Import paths updated in `src/codex_ml/config/__init__.py`

## Configuration Best Practices

### 1. Use Appropriate Directories

- **base/**: Default configurations that work across environments
- **production/**: Production-specific overrides (performance, monitoring)
- **development/**: Development/testing configurations (minimal resources)
- **experiments/**: Experiment-specific configurations

### 2. Follow Hydra Conventions

```yaml
# configs/base/training.yaml
defaults:
  - _self_

training:
  epochs: 10
  batch_size: 32
  learning_rate: 1e-4
```

### 3. Use Composition

```yaml
# configs/hydra/config.yaml
defaults:
  - base/training
  - base/model
  - base/data
  - _self_

env: development  # Override via CLI: env=production
```

### 4. Document Your Configs

Add comments explaining non-obvious parameters:

```yaml
training:
  epochs: 10  # Number of training epochs
  batch_size: 32  # Batch size per GPU
  gradient_accumulation_steps: 4  # Effective batch = 32 * 4 = 128
```

## Hydra Integration

### Search Paths

The Hydra configuration is set up to search for configs in:

1. `pkg://configs` - Package-relative paths
2. `file://configs` - File system paths

### Output Directories

```yaml
hydra:
  run:
    dir: outputs/${now:%Y-%m-%d}/${now:%H-%M-%S}
  sweep:
    dir: multirun/${now:%Y-%m-%d}/${now:%H-%M-%S}
    subdir: ${hydra.job.num}
```

## Troubleshooting

### Issue: "Config not found"

**Solution**: Ensure you're referencing configs relative to the `configs/` directory:

```python
# ❌ Wrong
get_config("training.yaml")

# ✅ Correct
get_config("base/training")  # No .yaml extension needed
```

### Issue: "Hydra initialization error"

**Solution**: Make sure `hydra-core` and `omegaconf` are installed:

```bash
pip install hydra-core omegaconf
```

### Issue: "Config override not working"

**Solution**: Use proper Hydra override syntax:

```bash
# ❌ Wrong
python train.py --epochs=100

# ✅ Correct
python train.py training.epochs=100
```

## Verification

Run the following to verify the config consolidation:

```bash
# Test config module import
python -c "from codex_ml.config import CONFIG_PATH, get_config, load_yaml; print('✓ Config module works')"

# Test YAML loading
python -c "from codex_ml.config import load_yaml; load_yaml('configs/hydra/config.yaml'); print('✓ YAML loading works')"

# Verify directory structure
ls -la configs/base configs/production configs/development configs/experiments configs/hydra
```

## Deferred Item D4 Completion

### Implementation Date
2025-12-08

### Deliverables Completed
✅ Migration script (`scripts/migrate_configs.py`)  
✅ Unified config structure under `configs/`  
✅ Hydra configuration (`configs/hydra/config.yaml`)  
✅ Python API for config loading (`codex_ml.config.get_config`, `load_yaml`)  
✅ Documentation (this file)  
✅ Verification tests  

### Verification Status
✅ All directory structures in place  
✅ Migration script tested (dry-run and execute)  
✅ Config loading functions verified  
✅ YAML parsing validated  
✅ Backward compatibility maintained  

### Next Steps
1. ✅ Phase 1: Config consolidation complete
2. Continue with D1: Docker Optimization
3. Continue with D2: Plugin Registry
4. Continue with D3: Multi-node Training

## References

- [Hydra Documentation](https://hydra.cc/)
- [OmegaConf Documentation](https://omegaconf.readthedocs.io/)
- [AGENTS.md](../AGENTS.md) - Repository conventions
