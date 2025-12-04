# Registries and plugin hooks

The Codex stack exposes lightweight registries for datasets, metrics, models, and tokenizers. Extensions stay offline-first and can be shipped as local modules.

## Adding a dataset
- Register via the dataset registry helper (see `src/codex_ml/data/registry.py` if present) or extend the factory in your module.
- Provide a small smoke test and document the expected schema.

## Adding a metric
- Implement the metric under `src/codex_ml/metrics/` or as a plugin module.
- Register the callable in the metrics registry so it can be resolved by name.

## Adding a model or tokenizer
- Extend `src/codex_ml/models/registry.py` with a new entry or provide a plugin module that imports and registers at import time.
- Follow the LoRA validation rules (dtype/device) when attaching adapters.

## Plugin packaging tips
- Prefer pure-Python plugins; avoid network calls in module import paths.
- Ship an extras entry in `pyproject.toml` if dependencies are optional.
- Document any new CLI flags or config knobs in the relevant guide under `docs/`.
