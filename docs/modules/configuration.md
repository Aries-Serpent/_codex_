# Configuration System

Codex ML relies on structured [Hydra](https://hydra.cc) configuration backed by
Python dataclasses defined in `codex_ml.config`. Four primary configuration
trees live under `configs/`:

```
configs/
├── tokenization/base.yaml   # Tokenizer training defaults
├── training/base.yaml       # Functional trainer defaults
├── eval/base.yaml           # Evaluation runner defaults
└── data/base.yaml           # Data preparation defaults
```

Each YAML file maps directly onto a dataclass (`TokenizationConfig`,
`TrainingConfig`, `EvaluationConfig`, and `DataConfig`). When a file omits a
section the dataclass provides sane defaults so lightweight configs are easy to
compose.

## Loading Configuration Programmatically

Use `load_app_config` to parse YAML and obtain both the dataclass instance and
resolved OmegaConf object:

```python
from codex_ml.config import load_app_config

cfg, raw = load_app_config("configs/training/base.yaml")
print(cfg.training.batch_size)  # 32 (default)
```

Validation runs automatically during loading. Violations raise `ConfigError`
with a fully-qualified path to the offending key (for example,
`training.batch_size: must be positive`). Missing files also surface as a
`ConfigError` to provide actionable CLI feedback.

Hydra-style overrides can be supplied via the `overrides` parameter. Dotlist
entries take precedence over file values:

```python
cfg, _ = load_app_config(
    "configs/training/base.yaml", overrides=("training.learning_rate=0.0005",)
)
assert cfg.training.learning_rate == 5e-4
```

## CLI Usage

Every CLI command that consumes configuration accepts a `--config` argument and
supports inline overrides. Examples:

```bash
# Train with a larger batch size and different output directory
codex train --config configs/training/base.yaml training.batch_size=64 \
  training.output_dir=runs/large

# Run evaluation and restrict to five examples
codex evaluate --config configs/eval/base.yaml evaluation.max_samples=5

# Prepare cached splits with a custom seed
codex prepare-data --config configs/data/base.yaml data.shuffle_seed=123
```

Overrides apply after the YAML file is parsed, so command line values always win
over on-disk defaults. All commands forward the resolved `DictConfig` to legacy
code paths while also using the strongly-typed dataclasses for validation.

## Default Resolution & Manifests

The loader is permissive about extra keys: structured defaults are merged with
file content, and any unknown settings are preserved in the resulting
`DictConfig`. `DataConfig` includes support for deterministic sharding,
normalised newlines, UTF-8 validation with fallbacks, and split ratio
verification. `prepare_data_from_config` writes cached splits alongside a JSON
manifest describing counts and checksums to aid reproducibility.

`EvaluationConfig` mirrors this pattern for the evaluation runner, ensuring
metric requests (perplexity, accuracy, F1, BLEU, ROUGE-L) have the requisite
inputs before execution.

## Troubleshooting

- **`ConfigError` mentioning a nested path** – inspect the YAML field referenced
  in the message. Dataclasses provide descriptive errors such as
  `data.split_ratios: values must sum to 1.0`.
- **Override not applied** – ensure the override matches the dataclass path
  (`training.learning_rate=...`). Invalid keys surface as `ConfigError`
  exceptions before any work is performed.
- **Optional dependencies** – evaluation metrics such as BLEU and ROUGE-L
  require `sacrebleu` or `nltk` / `rouge_score`. Install them locally if those
  metrics are requested.
