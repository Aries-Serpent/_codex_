# Unified Training Capability

## Overview

The unified training capability provides a standardized, deterministic training infrastructure for ML models. It ensures reproducible results through careful management of random seeds, checksum verification, and manifest tracking.

## Key Features

### Deterministic Training
- Consistent random number generation (rng) with explicit seed management
- Reproducible results across different runs
- Baseline comparison for regression detection

### Safety and Validation
- Bounded memory operations to prevent exhaustion
- Input sanitize operations for path validation
- Checksum verification for data integrity (sha256)
- Manifest tracking for experiment reproducibility

### Offline Operation
- No network dependencies during training
- Local caching of all required resources
- WANDB_MODE=offline support for isolated execution

## Configuration

```python
from codex_ml.training import UnifiedTrainingConfig

config = UnifiedTrainingConfig(
    seed=42,  # Explicit seed for reproducibility
    deterministic=True,
    offline_mode=True,
    checksum_validation=True,
)
```

## Safeguards

The unified training system implements several safeguards:

1. **Seed Management**: Explicit seed configuration for rng reproducibility
2. **Checksum Validation**: sha256 checksums for data integrity
3. **Manifest Tracking**: Complete manifest of training artifacts
4. **Baseline Comparison**: Regression detection against baselines
5. **Offline Mode**: No external dependencies, WANDB_MODE=offline
6. **Sanitize Inputs**: Path validation and sanitization
7. **Bounded Operations**: Memory and resource limits

## Usage

### Basic Training

```python
from codex_ml.training import run_unified_training

result = run_unified_training(
    config=config,
    data_path="data/training",
)
```

### With Reproducibility

```python
# Set explicit seed for reproducibility
config.seed = 42
config.deterministic = True

# Enable offline mode
config.offline_mode = True

# Verify data integrity
config.checksum_validation = True
```

## Best Practices

1. Always set explicit seeds for reproduce-ability
2. Enable deterministic mode for consistent results
3. Use offline mode in production environments
4. Validate checksums before training
5. Track experiments with manifests
6. Compare against baselines for regression detection
7. Sanitize all input paths

## Related Capabilities

- train_loop: Core training loop implementation
- checkpointing: Model checkpoint management
- experiment-management: Experiment tracking
- reproducibility: Reproducibility guarantees
