# Changelog

## Unreleased - 2025-09-21
- Added offline stub modules for yaml/omegaconf/hydra/torch to keep quick CLI tests running without external deps.
- Verified pending September patches already integrated for eval loop, Hydra entrypoint, deterministic loader, and telemetry defaults.
- Disabled GitHub Actions workflows locally to enforce offline execution policy.
- Ran targeted pytest suite (`tests/codex_ml`) to confirm evaluation logic and data loader wiring.

## Mapping
- Identified tokenization adapters in `src/codex_ml/tokenization/hf_tokenizer.py`.
- Located MiniLM model in `src/codex_ml/models/minilm.py`.
- Training utilities reside under `src/codex_ml/training/` and `training/`.
- Existing telemetry utilities in `src/codex_ml/telemetry/`.
- No dataset registry found; will be added under `src/codex_ml/data/`.

## Changes
- Added round-trip tokenizer and MiniLM forward tests.
- Integrated optional MLflow logging and Prometheus telemetry into demo training loop.
- Introduced `codex_ml.cli` with `train-model` and `evaluate` commands.
- Implemented dataset registry with HuggingFace streaming fallback.
- Updated `noxfile.py` coverage gates and `pytest.ini` default markers.
- Expanded README with training, evaluation, logging, and dataset examples.
- Moved new CLI into `codex_ml/cli/` package and lazy-loaded heavy dependencies.
