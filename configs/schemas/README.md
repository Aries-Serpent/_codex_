# Configuration Schemas

Structured schema helpers for Codex configurations live here. The package exposes the `register_schema` utility (see `__init__.py`) for Hydra structured configs and contains JSON/YAML schema blueprints used in validation tooling.

## Files

- `__init__.py` – Hydra structured config dataclasses (`AppCfg`, `TrainCfg`, `DataCfg`) and a `register_schema` helper.
- `training.schema.yaml` – YAML schema covering core training settings.
- `data.schema.yaml` – Dataset manifest schema for ingestion utilities.
- `model.schema.yaml` – Model configuration schema capturing LoRA/precision toggles.
- `training_profile.schema.json` – JSON schema for the Hydra profile used by `codex_ml.cli.train`.
- `evaluation.schema.json` – JSON schema for the evaluation CLI defaults.

## Validating Configurations

Run schema checks via the CLI:

```bash
python -m codex_ml.validation.schema_check --config-dir configs/
```text

You can also import the structured config module directly:

```python
from configs.schemas import register_schema

register_schema()  # registers "app" schema with Hydra
```text

## Updating Schemas

1. Keep field descriptions in sync with the corresponding YAML defaults (`configs/base/app.yaml`, `configs/training/base.yaml`, etc.).
2. Use JSON Schema 2020-12 or minimal YAML schema definitions for offline validation.
3. Update tests under `tests/configuration/` if new required fields are introduced.
4. Document schema changes in `docs/` when CLI behaviour changes.
