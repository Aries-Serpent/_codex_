# ADR-005: Configuration Management via Hydra
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Accepted
**Date:** 2026-07-10
**Author:** @mbaetiong
**Session:** S250-doc-arch

---

## Context

The platform needs to support:
- Multiple experiments with different configurations
- Easy parameter sweeping for hyperparameter tuning
- Reproducible runs with captured configuration
- Different configs for dev/test/prod environments
- Override configs from CLI without code changes
- Type-safe configuration (schema validation)

Manual configuration management (dict files, environment variables) became unmaintainable as complexity grew.

---

## Decision

Use **Hydra** as the configuration management framework:

**Why Hydra:**
1. **Composition** — Layer configs (base experiment run-specific)
2. **Type Safety** — OmegaConf schema validation
3. **CLI Overrides** — `--opt key=value` from command line
4. **Automatic Reproducibility** — Configs captured in runs
5. **Structured Configs** — Dataclass-based config schema
6. **Multirun Support** — Hyperparameter sweeps
7. **Large community** — Well-maintained, widely used

**Configuration hierarchy:**

```
config/
├── defaults.yaml           # Base defaults for all runs
├── training/
│   ├── baseline.yaml       # Training config baseline
│   ├── distributed.yaml    # Distributed training specific
│   └── experimental/
│       ├── exp_001.yaml    # Experiment 1 override
│       └── exp_002.yaml    # Experiment 2 override
├── data/
│   ├── default.yaml        # Default data config
│   └── large_dataset.yaml  # Large dataset specific
├── model/
│   ├── transformer.yaml    # Transformer model
│   └── rnn.yaml            # RNN model
└── environment/
    ├── dev.yaml            # Development settings
    ├── test.yaml           # Test settings
    └── prod.yaml           # Production settings
```

**Usage patterns:**

```bash
# Base run with defaults
python main.py train

# Run with experiment override
python main.py train +experiment=exp_001

# CLI parameter sweep
python main.py -m train \
  model=transformer,rnn \
  training.learning_rate=1e-3,1e-4,1e-5

# Specific config selection
python main.py train \
  environment=prod \
  data=large_dataset \
  model.hidden_size=1024
```

---

## Configuration Schema (Example)

```python
from dataclasses import dataclass, field
from hydra.core.config_store import ConfigStore

@dataclass
class TrainingConfig:
    max_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-4
    warmup_steps: int = 1000
    eval_interval: int = 1000

@dataclass
class ModelConfig:
    class_path: str = "codex.models.TransformerModel"
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    dropout: float = 0.1

@dataclass
class AppConfig:
    training: TrainingConfig = field(default_factory=TrainingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    data_path: str = "data/train.csv"

cs = ConfigStore.instance()
cs.store(name="config", node=AppConfig)
```

---

## Consequences

### Positive
 Configuration fully reproducible and versionable
 Experiments easy to run and compare
 No hardcoded parameters scattered throughout codebase
 Team can run experiments without code changes
 Type safety catches config errors early
 CLI-based workflows feel natural to users

### Negative
 Learning curve for Hydra concepts (Compose API, overrides)
 Large config files can become hard to navigate
 Debugging config composition issues can be tricky

### Mitigations
- Comprehensive Hydra training for team
- Config files well-organized and commented
- `hydra-help` available to debug composition issues
- Config validation layer before training starts

---

## Implementation Details

**Validation layer (applied before training):**

```python
def validate_config(cfg: AppConfig) -> bool:
    """Validate configuration for consistency."""
    assert cfg.training.batch_size > 0, "batch_size must be positive"
    assert cfg.training.learning_rate > 0, "learning_rate must be positive"
    assert cfg.model.hidden_size % cfg.model.num_heads == 0, \
        "hidden_size must be divisible by num_heads"
    
    # Type checking
    assert isinstance(cfg.training.max_epochs, int)
    assert isinstance(cfg.model.hidden_size, int)
    return True
```

**Configuration capture in runs:**

```python
@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: AppConfig):
    # Hydra automatically saves cfg as .hydra/config.yaml
    # in the output directory for reproducibility
    print(OmegaConf.to_yaml(cfg))  # Pretty-print config
    
    # Train with cfg
    trainer = Trainer(cfg)
    trainer.train()
```

---

## Related ADRs
- ADR-004: 5-Layer Architecture
- ADR-007: Environment-Based Secrets Management
