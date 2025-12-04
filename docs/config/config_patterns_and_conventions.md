# Configuration Patterns & Conventions in `_codex_` (Scaffolding)

This document describes the current, **minimal** configuration patterns
for `_codex_`. The goal is to provide a typed "spine" that can support:

- Local validation
- Simple tooling
- Future integration with Hydra or other config systems

## 1. Top-Level Structure

The canonical shape of a run config is:

```yaml
model:
  model_name: "codex-minimal"
  hidden_size: 256
  num_layers: 4
  dropout: 0.1
  dtype: "float32"

training:
  learning_rate: 1.0e-3
  batch_size: 8
  max_steps: 100
  gradient_accumulation_steps: 1
  log_every_n_steps: 10
  seed: 123

data:
  dataset_name: "dummy"
  train_split: "train"
  eval_split: "validation"
  shuffle: true
  num_workers: 0

eval:
  batch_size: 8
  split: "validation"
  max_batches: null
```

All of these sections are optional. Missing sections are filled in with
reasonable defaults during validation.

## 2. Schema Module

The schema is implemented in:

* `codex_ml.config.schema`

Key types:

* `ModelConfig`
* `TrainingConfig`
* `DataConfig`
* `EvalConfig`
* `CodexConfig`
* `ConfigValidationError`

The main entrypoint is:

```python
from codex_ml.config import schema

cfg = schema.from_dict(raw_dict)
```

where `raw_dict` is typically produced by:

```python
import yaml, pathlib as p
raw_dict = yaml.safe_load(p.Path("conf/my_run.yaml").read_text()) or {}
cfg = schema.from_dict(raw_dict)
```

## 3. Validation Tool

The validation tool:

* `tools/codex_config_validate.py`

Usage:

```bash
python tools/codex_config_validate.py \
  --conf-dir conf \
  --json-out codex_config_validation_report.json \
  --md-out codex_config_validation_report.md
```

Behavior:

* Scans `conf/` recursively for `*.yaml`.
* For each file:
  * Parses YAML.
  * Calls `schema.from_dict(...)`.
* Produces:
  * A JSON report with per-file status.
  * A Markdown summary table.
  * Returns non-zero exit code if any file fails validation.

This tool is wired into `codex_task_sequence.yaml` so that configuration
issues are detected early.

## 4. Hydra Compatibility (Future Work)

The current schema is **Hydra-friendly** but does not require Hydra:

* The shape of `CodexConfig` aligns with common Hydra section patterns.
* Nothing prevents using these dataclasses as the "target" of a Hydra
  instantiation step in the future.

Future work may:

* Introduce a dedicated `conf/` tree with Hydra-friendly defaults.
* Provide example `hydra.main()` entrypoints that adapt to the schema.
* Add explicit support for structured configs.

## 5. Best Practices

* Keep configs small and explicit.
* Prefer descriptive, stable field names.
* Use the validation tool as a *local gate* before running longer jobs.
* When adding new fields, consider:
  * Updating the schema dataclasses (with defaults).
  * Extending validation tests.
  * Updating docs and example configs.
