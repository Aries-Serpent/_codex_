# Changelog

## Unreleased - 2025-09-22
- Hardened the offline SentencePiece adapter by avoiding redundant allocations
  and adding stub tests for pad-id fallback and iterable decode coverage.
- Added registry-aware causal LM loader with AMP dtype flags, defensive LoRA
  wiring and accompanying docs/tests.
- Replaced the audit prompt with an offline-first template that mandates deterministic inventory outputs and expanded guardrails.
- Added an offline audit validation guide plus local `codex_local_audit.sh` / `codex-audit` shims to capture deterministic artefacts.
- Seeded audit-first reports (`reports/`) and refreshed AUDIT_PROMPT for offline workflow.
- Introduced markdown fence validator with pytest coverage and pre-commit integration.
- Documented local tooling commands, deferred items, and next-menu focus for future runs.
- Added reusable audit templates for security sweeps, observability runbooks, and report updates.
- Hardened monitoring: added a TensorBoard wrapper, W&B offline shim, periodic system
  metrics sampler with NDJSON output, and regression tests/documentation for the
  new logging hooks.

## Unreleased - 2025-09-21
- Added Typer-based CLI tests that cover plugin registry introspection and monitoring NDJSON export flows offline.
- Added offline stub modules for yaml/omegaconf/hydra/torch to keep quick CLI tests running without external deps.
- Verified pending September patches already integrated for eval loop, Hydra entrypoint, deterministic loader, and telemetry defaults.
- Disabled GitHub Actions workflows locally to enforce offline execution policy.
- Ran targeted pytest suite (`tests/codex_ml`) to confirm evaluation logic and data loader wiring.
- Clarified `codex` CLI group behaviour: invoking groups with no subcommand now prints contextual help and `codex run` with no task emits the whitelist banner.
- Populated offline model/data/metric registries with guarded GPT-2, TinyLLaMA, and tiny corpus fixtures plus Hydra config snippets and regression tests.
- Seeded the plugin catalogues with offline-ready defaults (GPT-2, TinyLLaMA, tiny corpus, weighted accuracy) and extended docs/quickstart guidance on optional usage versus minimal setups.
- Added offline functional trainer and heuristic reward-model shims, CLI discovery tests, and a composite `offline/catalogue` config for one-command baseline activation.
- Introduced ultra-light offline fixtures (tiny vocabulary/model, scripted agent, length reward) with registry entries, Hydra preset (`offline/tiny_fixtures`), and integration tests for graceful error messages.

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
