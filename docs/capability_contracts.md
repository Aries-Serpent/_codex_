# Capability Contracts and Extension Guide

This document summarizes the formal contracts introduced for Track B (Capability Specialization) and how to extend them offline.

## Tokenization Contract

- Interface: `codex_ml.interfaces.contracts.TokenizerContract`
- Required methods: `encode(text: str) -> list[int]`, `decode(ids: Sequence[int]) -> str`, `add_special_tokens`, `save(path: Path)`
- Required properties: `vocab_size`, `name_or_path`
- Error modes: non-string input to `encode` raises `TypeError`; non-integer ids to `decode` raise `ValueError`.
- Validation helper: `validate_tokenizer_contract(adapter)` performs smoke tests and type checks.

### Extending

Implement the methods and raise the documented errors for invalid inputs. Call `validate_tokenizer_contract` in tests to confirm compliance.

## Training Contract

- Interface helpers: `validate_training_model(model)` and `validate_training_config(config)`
- Training step must be callable, return a mapping of string metric keys to numeric values, and run without network access.
- Config fields: `batch_size`, `learning_rate`, `num_epochs` (optional `seed`). Missing or non-positive values raise `TrainingContractError`.

### Extending

Attach a `.step(batch, state)` method to new trainers and reuse `validate_training_config` when loading user-provided dictionaries.

## Evaluation and Metrics

- API: `codex_ml.evaluation.loop.run_metrics_evaluation` accepts metric names or callables (resolved via `codex_ml.metrics.api.get_metric`).
- Logging: pass NDJSON/CSV writers to record `run_id`, `metric`, `step`, and structured tags. System metrics (CPU/memory) are collected when available.
- Offline tracking: MLflow is configured in offline mode when enabled; a local `mlruns` store is used automatically.

### Extending

Register new metrics via `codex_ml.metrics.api.register_metric` or supply callables directly. Writers accept `run_id` and `default_tags` for additional labeling.

## Deployment and Plugins

- Packaging helper: `codex_ml.deployment.package.build_service_package` creates a tarball with a manifest and model pointer. It applies prompt scanning and loads secrets from the offline store.
- Plugin registry: `deployment_registry` (backed by `codex_ml.plugins.registry.Registry`) lets you register hooks that receive the packaged artefact path.
- CLI: `codex-ml package-service <model_dir>` builds packages offline via `codex_ml.cli.main`.

### Extending

Register new deployment hooks with `@deployment_registry.register("name")` and ensure they operate on local files only.

## Security Utilities

- Prompt scanning: `scan_prompt_for_unsafe_content(prompt)` rejects dangerous patterns (e.g., SQL drops, destructive shell commands).
- Secret loading: `load_secret(name, store_path=".codex/secrets.json")` reads from environment or the offline store without network calls.

### Extending

Add organization-specific patterns or rotate stores by passing custom paths to the helpers while keeping the offline constraints intact.
