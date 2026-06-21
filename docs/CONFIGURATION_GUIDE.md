# Configuration Guide

## Overview

Codex ML uses Hydra for configuration management, enabling flexible, reproducible experiments through YAML files and command-line overrides.

**Configuration Root**: `configs/`
**Framework**: Hydra / OmegaConf

## Configuration Structure

```
configs/
├── training/
│   ├── default.yaml
│   ├── bert.yaml
│   ├── gpt.yaml
│   └── tokenizer/  # pragma: allowlist secret
│       └── offline/
│           └── tiny_vocab.yaml
├── data/
│   ├── default.yaml
│   └── preprocessing.yaml
├── hardware/
│   ├── default.yaml
│   ├── cuda.yaml
│   └── cpu.yaml
└── experiment/
    ├── base_experiment.yaml
    └── hyperparameter_sweep.yaml
```

## Core Configuration Files

### 1. Training Configuration (`configs/training/default.yaml`)

```yaml
# Model configuration
model:
  name: bert-base-uncased
  pretrained: true
  num_labels: 2
  max_length: 512
  dropout: 0.1

# Training hyperparameters
training:
  batch_size: 32
  num_epochs: 3
  learning_rate: 2e-5
  warmup_steps: 500
  warmup_ratio: 0.1
  weight_decay: 0.01
  gradient_accumulation_steps: 1
  
  # Advanced options
  gradient_checkpointing: false
  mixed_precision: false  # or 'fp16', 'bf16'
  max_grad_norm: 1.0
  
# Optimization
optimizer:
  type: adamw  # adamw, adam, sgd
  betas: [0.9, 0.999]
  eps: 1e-8

# Learning rate scheduler
scheduler:
  type: linear  # linear, cosine, constant
  num_cycles: 0.5
  pct_start: 0.1

# Logging
logging:
  level: INFO
  log_dir: ./logs
  log_interval: 100
  
# Checkpointing
checkpoint:
  save_dir: ./checkpoints
  save_interval: 500
  keep_last_n: 3
  save_best: true
  metric: eval_loss
  metric_mode: min  # min or max
```

### 2. Data Configuration (`configs/data/default.yaml`)

```yaml
# Dataset paths
data:
  train_path: data/train.jsonl
  eval_path: data/eval.jsonl
  test_path: data/test.jsonl
  
  # Data loading
  num_workers: 4
  prefetch_factor: 2
  pin_memory: true
  
# Preprocessing
preprocessing:
  # Text processing
  lowercase: false
  remove_special_chars: false
  remove_punctuation: false
  
  # Normalization
  normalize_whitespace: true
  remove_extra_spaces: true
  
  # Length filtering
  min_length: 1
  max_length: 512
  
  # Sampling
  max_samples: null  # null = all samples
  sample_ratio: 1.0  # Use fraction of data
  
# Data splits
splits:
  train_ratio: 0.8
  eval_ratio: 0.1
  test_ratio: 0.1
  random_seed: 42
```

### 3. Hardware Configuration (`configs/hardware/cuda.yaml`)

```yaml
# Device configuration
device:
  type: cuda  # cuda, cpu, tpu
  device_ids: [0, 1, 2, 3]  # For multi-GPU
  
# Distributed training
distributed:
  enabled: true
  backend: nccl  # nccl, gloo
  num_processes: 4
  
# GPU optimization
gpu:
  enable_tf32: true  # for A100
  cudnn_benchmark: true
  memory_fraction: 0.9
  
# Ray configuration (for distributed training)
ray:
  num_workers: 4
  use_gpu: true
  resources_per_worker:
    GPU: 1
    CPU: 4
```

## Using Configurations

### Basic Usage

```bash
# Use default configuration
python train.py

# Use specific configuration
python train.py --config-name bert

# Use configuration from subdirectory
python train.py --config-path configs/training/tokenizer/offline \
                 --config-name tiny_vocab
```

### Command-Line Overrides

```bash
# Override single parameter
python train.py training.batch_size=64

# Override nested parameters
python train.py training.batch_size=64 \
               training.learning_rate=1e-5 \
               data.num_workers=8

# Override with dot notation
python train.py model.name=roberta-base \
               model.max_length=1024
```

### Multi-Run Sweeps

```bash
# Sweep over multiple values
python train.py -m training.batch_size=32,64,128 \
                  training.learning_rate=1e-5,2e-5

# Cartesian product of parameters
python train.py -m training.batch_size=32,64 \
                  training.learning_rate=1e-5,2e-5
# Runs: 4 experiments (2x2)
```

## Composition & Defaults

### Multi-Config Composition

```bash
# Compose from multiple files
python train.py --config-path configs \
               -c training=bert,data=default,hardware=cuda

# Override specific sections
python train.py +model.cache_dir=/tmp/cache
```

### Config Groups

Create hierarchical configs with defaults:

```
configs/
├── training/
│   ├── default.yaml
│   ├── bert.yaml
│   └── gpt.yaml
├── data/
│   ├── default.yaml
│   └── large.yaml
└── config.yaml
```

In `config.yaml`:
```yaml
defaults:
  - training: default
  - data: default

# Other config...
experiment_name: exp_001
```

## Advanced Configuration

### Interpolation

Reference other values in config:

```yaml
model:
  name: bert-base-uncased
  cache_dir: ./cache/${model.name}

training:
  output_dir: ./output/${model.name}/${now:%Y-%m-%d_%H-%M-%S}

data:
  train_path: data/${data_type}/train.jsonl
```

### Variable Resolution

```bash
python train.py data_type=bert_pretokenized
# Resolves: data/bert_pretokenized/train.jsonl
```

### Structured Configs with Dataclasses

```python
from dataclasses import dataclass
from omegaconf import OmegaConf, MISSING

@dataclass
class TrainingConfig:
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 3

# Create config from dataclass
config = OmegaConf.structured(TrainingConfig)
```

## Accessing Configurations in Code

### Basic Access

```python
from omegaconf import DictConfig

def train(cfg: DictConfig):
    print(f"Batch size: {cfg.training.batch_size}")
    print(f"Learning rate: {cfg.training.learning_rate}")
```

### Type-Safe Access

```python
from omegaconf import DictConfig, OmegaConf

def train(cfg: DictConfig):
    # Type-safe conversion
    train_cfg = OmegaConf.to_container(cfg.training)
    
    batch_size = train_cfg['batch_size']
    lr = train_cfg['learning_rate']
```

### Config Validation

```python
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, validator

class TrainingParams(BaseModel):
    batch_size: int
    learning_rate: float
    
    @validator('batch_size')
    def batch_size_positive(cls, v):
        if v <= 0:
            raise ValueError('batch_size must be positive')
        return v

# Validate
cfg_dict = OmegaConf.to_container(cfg)
valid_cfg = TrainingParams(**cfg_dict.training)
```

## Environment-Specific Configurations

### Production Configuration

Create `configs/hardware/production.yaml`:
```yaml
device:
  type: cuda
  device_ids: [0, 1, 2, 3]
  
distributed:
  enabled: true
  num_processes: 4
  backend: nccl
  
training:
  batch_size: 256
  mixed_precision: bf16
  gradient_accumulation_steps: 2
```

Run production:
```bash
python train.py --config-path configs/hardware \
               --config-name production
```

### Development Configuration

Create `configs/hardware/dev.yaml`:
```yaml
device:
  type: cpu
  
distributed:
  enabled: false
  
training:
  batch_size: 8
  num_epochs: 1
  log_interval: 10
```

Run development:
```bash
python train.py --config-path configs/hardware \
               --config-name dev
```

## Best Practices

1. **Use Defaults**
   ```yaml
   # Bad: Hardcoded values everywhere
   batch_size: 32
   learning_rate: 2e-5
   
   # Good: Use clear defaults with documentation
   defaults:
     - _self_
     - training: default
   ```

2. **Version Configurations**
   ```bash
   git commit -m "Update training config: reduce LR to 1e-5"
   ```

3. **Document All Parameters**
   ```yaml
   # Document purpose and recommended values
   training:
     batch_size: 32  # Tune based on GPU memory (32-256)
     learning_rate: 2e-5  # Lower for fine-tuning (1e-6 to 5e-5)
   ```

4. **Use Environment Variables**
   ```bash
   export DATA_PATH=/path/to/data
   python train.py data.train_path=${DATA_PATH}/train.jsonl
   ```

5. **Create Experiment Presets**
   ```yaml
   # configs/experiment/quick_test.yaml
   defaults:
     - /training: bert
     - /data: default
     - /hardware: cpu
   
   training:
     num_epochs: 1
     log_interval: 10
   ```

## See Also

- [Hydra Documentation](https://hydra.cc/)
- [OmegaConf Documentation](https://omegaconf.readthedocs.io/)
- [Quickstart Guide](./QUICKSTART.md)
- [Training Guide](./distributed_training_guide.md)


---
## 📎 Consolidated from: docs/configuration/CONFIG_USAGE.md

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

- **Migration Guide:** [HYDRA_MIGRATION_GUIDE.md](configuration/HYDRA_MIGRATION_GUIDE.md)
- **Migration Mapping:** [MIGRATION_MAPPING.md](configuration/MIGRATION_MAPPING.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **PS-01 Planset:** `.github/plans/PLANSET_01_CONFIGURATION_CONSOLIDATION.md`

---

**Maintained By:** PS-01 Configuration Consolidation  
**Questions:** File an issue with "configuration" label

