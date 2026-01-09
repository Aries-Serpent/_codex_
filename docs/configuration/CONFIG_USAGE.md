# Configuration Usage Guide

**Last Updated:** 2026-01-09  
**PS-01 Status:** Cycle 3 (Validation & Testing)

---

## Overview

This guide provides practical examples and patterns for using the centralized configuration system introduced in PS-01 Configuration Consolidation.

## Quick Start

### Loading a Configuration

```python
from codex.utils.config_loader import load_config

# Load model configuration
cfg = load_config("base", config_dir="conf/model")

# Access config values
print(cfg.model.name)  # or cfg["model"]["name"]
```

### With Overrides

```python
# Override specific values
cfg = load_config(
    "base",
    config_dir="conf/training",
    overrides=[
        "training.epochs=10",
        "training.device=cuda",
        "training.batch_size=16"
    ]
)
```

---

## Configuration Structure

### Directory Organization

```
conf/
├── errors/           # Error definitions
│   └── defaults.yaml
├── model/            # Model configurations
│   ├── base.yaml
│   ├── toy.yaml
│   └── offline/
├── training/         # Training configurations
│   ├── base.yaml
│   ├── continual/
│   └── offline/
├── evaluation/       # Evaluation configurations
│   ├── base.yaml
│   └── reasoning/
└── data/             # Data configurations
    ├── base.yaml
    ├── tiny.yaml
    └── offline/
```

---

## Common Patterns

### Pattern 1: Loading with Fallback

```python
from codex.utils.config_loader import load_config

# Will try conf/ first, fall back to configs/ if not found
cfg = load_config("legacy_config", config_dir="conf/model", allow_fallback=True)
```

**Use Case:** During migration period when configs exist in both locations

### Pattern 2: Hydra Interpolation

```yaml
# conf/training/base.yaml
training:
  epochs: 10
  max_epochs: ${training.epochs}  # Reference same value

# Backward compatibility
epochs: ${training.epochs}
```

**Use Case:** Maintain backward compatibility without duplication

### Pattern 3: Nested Config Composition

```yaml
# conf/experiment/my_experiment.yaml
defaults:
  - /model: base
  - /training: base
  - /data: tiny

# Override specific values
training:
  epochs: 20
```

**Use Case:** Compose experiments from reusable components

### Pattern 4: Error Handling

```python
from codex.utils.config_loader import get_loader, MissingConfigException

loader = get_loader()

try:
    cfg = loader.load_config("nonexistent", allow_fallback=False)
except MissingConfigException as e:
    # Get structured error
    error = loader.get_error("config_errors", "missing_config")
    print(error.format(file=e.missing_cfg_file))
```

**Use Case:** Graceful error handling with structured messages

---

## Examples by Use Case

### Training Pipeline

```python
from codex.utils.config_loader import load_config

# Load training configuration
train_cfg = load_config("base", config_dir="conf/training")

# Load model configuration
model_cfg = load_config("base", config_dir="conf/model")

# Load data configuration
data_cfg = load_config("tiny", config_dir="conf/data")

# Override for specific run
train_cfg = load_config(
    "base",
    config_dir="conf/training",
    overrides=[
        f"training.output_dir=runs/experiment_{run_id}",
        "training.epochs=50",
        "training.device=cuda"
    ]
)
```

### Evaluation Pipeline

```python
from codex.utils.config_loader import load_config

# Load evaluation configuration
eval_cfg = load_config("base", config_dir="conf/evaluation")

# Load specific reasoning configuration
reasoning_cfg = load_config("base", config_dir="conf/evaluation/reasoning")

# Override metrics
eval_cfg = load_config(
    "base",
    config_dir="conf/evaluation",
    overrides=["metrics.use_weighted_accuracy=true"]
)
```

### Experimentation

```python
from codex.utils.config_loader import load_config

# Load experiment configuration (with defaults list)
exp_cfg = load_config("my_experiment", config_dir="conf/experiment")

# All composed configs are accessible
print(exp_cfg.model.name)
print(exp_cfg.training.epochs)
print(exp_cfg.data.train_path)
```

---

## Override Syntax

### Simple Values

```python
overrides = [
    "key=value",
    "nested.key=value",
    "training.epochs=10"
]
```

### Complex Values

```python
overrides = [
    "list_key=[1,2,3]",
    "dict_key={a: 1, b: 2}",
    "bool_key=true",
    "float_key=0.001"
]
```

### Interpolation in Overrides

```python
overrides = [
    "training.output_dir=runs/${model.name}",
    "training.checkpoint_dir=${training.output_dir}/checkpoints"
]
```

---

## Best Practices

### DO ✅

1. **Use ConfigLoader for all config loading**
   ```python
   from codex.utils.config_loader import load_config
   cfg = load_config("base", config_dir="conf/model")
   ```

2. **Leverage Hydra interpolation for DRY**
   ```yaml
   training:
     epochs: 10
     max_epochs: ${training.epochs}
   ```

3. **Organize configs by logical groups**
   ```
   conf/model/     # Model-specific
   conf/training/  # Training-specific
   conf/data/      # Data-specific
   ```

4. **Use overrides for run-specific changes**
   ```python
   cfg = load_config("base", overrides=["training.seed=42"])
   ```

5. **Handle errors gracefully**
   ```python
   try:
       cfg = load_config("config", allow_fallback=False)
   except MissingConfigException:
       # Handle missing config
   ```

### DON'T ❌

1. **Don't hardcode config paths**
   ```python
   # Bad
   with open("configs/training/base.yaml") as f:
       cfg = yaml.safe_load(f)
   
   # Good
   cfg = load_config("base", config_dir="conf/training")
   ```

2. **Don't duplicate config values**
   ```yaml
   # Bad
   training:
     epochs: 10
   max_epochs: 10  # Duplication!
   
   # Good
   training:
     epochs: 10
   max_epochs: ${training.epochs}
   ```

3. **Don't skip error handling**
   ```python
   # Bad
   cfg = load_config("config")  # May fail silently
   
   # Good
   try:
       cfg = load_config("config", allow_fallback=False)
   except MissingConfigException as e:
       logger.error(f"Config not found: {e.missing_cfg_file}")
   ```

---

## Migration from Legacy Code

### Before (Legacy)

```python
import yaml

with open("configs/training/base.yaml") as f:
    config = yaml.safe_load(f)

epochs = config["training"]["epochs"]
```

### After (New System)

```python
from codex.utils.config_loader import load_config

config = load_config("base", config_dir="conf/training")

# Access via attribute (if OmegaConf available)
epochs = config.training.epochs

# Or via dict (always works)
epochs = config["training"]["epochs"]
```

---

## Advanced Usage

### Custom Config Directory

```python
from pathlib import Path
from codex.utils.config_loader import ConfigLoader

# Create loader with custom root
loader = ConfigLoader(repo_root=Path("/custom/path"))
cfg = loader.load_config("base", config_dir="conf/model")
```

### Programmatic Override Application

```python
from codex.utils.config_loader import ConfigLoader

loader = ConfigLoader()

# Build overrides dynamically
overrides = []
if use_gpu:
    overrides.append("training.device=cuda")
if debug_mode:
    overrides.append("training.epochs=1")

cfg = loader.load_config("base", config_dir="conf/training", overrides=overrides)
```

### Accessing Structured Errors

```python
from codex.utils.config_loader import get_loader

loader = get_loader()

# Get specific error definition
error = loader.get_error("config_errors", "missing_config")
if error:
    print(f"Code: {error.code}")
    print(f"Message: {error.message}")
    print(f"Resolution: {error.resolution}")
```

---

## Testing Configurations

### In Unit Tests

```python
import pytest
from codex.utils.config_loader import load_config

def test_training_config():
    cfg = load_config("base", config_dir="conf/training")
    
    assert cfg is not None
    assert "training" in cfg
    assert cfg.training.epochs > 0

def test_config_overrides():
    cfg = load_config(
        "base",
        config_dir="conf/training",
        overrides=["training.epochs=5"]
    )
    
    assert cfg.training.epochs == 5
```

### In Integration Tests

```python
def test_training_pipeline_with_config():
    cfg = load_config("base", config_dir="conf/training")
    
    # Use config in training
    trainer = Trainer(config=cfg)
    results = trainer.train()
    
    assert results.epochs_completed == cfg.training.epochs
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Related Documentation

- **Migration Guide:** [HYDRA_MIGRATION_GUIDE.md](HYDRA_MIGRATION_GUIDE.md)
- **Migration Mapping:** [MIGRATION_MAPPING.md](MIGRATION_MAPPING.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **PS-01 Planset:** `.github/plans/PLANSET_01_CONFIGURATION_CONSOLIDATION.md`

---

**Maintained By:** PS-01 Configuration Consolidation  
**Questions:** File an issue with "configuration" label
