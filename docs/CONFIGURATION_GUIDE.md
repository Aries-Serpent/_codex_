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
