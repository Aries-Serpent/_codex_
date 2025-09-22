# Changelog

## Unreleased - 2025-09-21
- Added offline stub modules for yaml/omegaconf/hydra/torch to keep quick CLI tests running without external deps.
- Verified pending September patches already integrated for eval loop, Hydra entrypoint, deterministic loader, and telemetry defaults.
- Disabled GitHub Actions workflows locally to enforce offline execution policy.
- Ran targeted pytest suite (`tests/codex_ml`) to confirm evaluation logic and data loader wiring.
- Populated offline model/data/metric registries with guarded GPT-2, TinyLLaMA, and tiny corpus fixtures plus Hydra config snippets and regression tests.
- Seeded the plugin catalogues with offline-ready defaults (GPT-2, TinyLLaMA, tiny corpus, weighted accuracy) and extended docs/quickstart guidance on optional usage versus minimal setups.
- Added offline functional trainer and heuristic reward-model shims, CLI discovery tests, and a composite `offline/catalogue` config for one-command baseline activation.

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

### Unreleased - 2025-09-21
- Documented repo map, capability audit, and high-signal findings in `.codex/status/_codex_status_update-2025-09-21.md`.
- Added docs/pruning_log.md to capture deferred components with rationale.
- Hardened automation by disabling remote GitHub workflows for offline use only.
- Refreshed docs/gaps_report.md header for readability and downstream tooling.
- Introduced regression tests for tokenizer fallbacks, model registry errors, functional training evaluation, telemetry defaults, and checkpoint round-trips.
- Authored codex_patch_runner utility script to automate patch application, gating, and manifest generation.
- Emitted offline manifest and status artefacts under `.codex/status/` for traceability.
