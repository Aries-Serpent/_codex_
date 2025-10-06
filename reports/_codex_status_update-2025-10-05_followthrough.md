# Follow-Through Audit — Status Update 2025-10-05

This note cross-references the remediation guidance from the 2025-10-05 status update and documents the current implementation or remaining work. Each subsection quotes the relevant gap/plan from the report and cites the code paths that now satisfy (or still miss) the recommendation.

## Capability Follow-Through

### Tokenization
- **Original gap/plan:** Add a SentencePiece adapter, surface `vocab_size`/`pad_token_id`/`eos_token_id`, and expose padding & truncation via the CLI.【F:reports/_codex_status_update-2025-10-05.md†L50-L53】
- **Implementation:** `SentencePieceTokenizer` wires special-token handling and pad/eos IDs, while the CLI `encode` helper supports optional padding/truncation parameters for offline smoke usage.【F:src/codex_ml/tokenization/adapter.py†L137-L207】【F:src/codex_ml/tokenization/cli.py†L51-L99】
- **Further work:** The command-line `encode` subparser still prints raw IDs; consider adding flags that write padded/truncated sequences directly so CLI usage mirrors the helper signature.

### ChatGPT Codex Modeling
- **Original gap/plan:** Load Hugging Face causal/MLM models offline and automatically apply LoRA when `lora_enable` is set.【F:reports/_codex_status_update-2025-10-05.md†L50-L54】
- **Implementation:** The model registry resolves offline checkpoints for GPT-2 and TinyLlama, falling back to cached weights, and the training harness now applies LoRA adapters whenever the config toggles are true.【F:src/codex_ml/models/registry.py†L21-L198】【F:src/codex_ml/training/__init__.py†L1284-L1309】
- **Further work:** Integration tests that exercise the offline `TinyLlama` path remain desirable to confirm error messages when weights are missing.

### Training Engine
- **Original gap/plan:** Add gradient accumulation, gradient clipping, and richer scheduling hooks to the functional trainer.【F:reports/_codex_status_update-2025-10-05.md†L50-L55】
- **Implementation:** `TrainingRunConfig` exposes accumulation and clipping knobs, and the functional trainer divides loss per accumulation step and clips gradients before optimizer updates to keep large runs stable.【F:src/codex_ml/training/__init__.py†L90-L139】【F:src/codex_ml/training/functional_training.py†L295-L335】
- **Further work:** Distributed (DDP/FSDP) execution is still intentionally deferred per the report’s deferred items; revisit when hardware resources are available.【F:reports/_codex_status_update-2025-10-05.md†L351-L357】

### Configuration Management
- **Original gap/plan:** Ship discoverable YAML defaults and merge them with dataclass settings via Hydra.【F:reports/_codex_status_update-2025-10-05.md†L50-L55】
- **Implementation:** The repo now carries `configs/default.yaml`, and the Hydra entrypoint merges those defaults with runtime overrides so contributors can inspect and tweak structured configs offline.【F:configs/default.yaml†L1-L20】【F:src/codex_ml/cli/hydra_main.py†L1-L73】
- **Further work:** Document how per-task YAMLs (e.g., evaluation vs. fine-tuning) should override the shared defaults to avoid duplication.

### Evaluation & Metrics
- **Original gap/plan:** Extend evaluation to emit aggregate metrics (including NDJSON/CSV variants) so downstream analysis does not require manual parsing.【F:reports/_codex_status_update-2025-10-05.md†L50-L56】
- **Implementation:** The evaluation utility averages losses and metric hooks while preserving device transfers, giving a deterministic summary for NDJSON sinks.【F:src/codex_ml/training/eval.py†L1-L91】
- **Further work:** CSV/Parquet emission is still on the backlog; consider parameterizing `training.metrics_out` to support multiple formats without breaking NDJSON consumers.

### Logging & Monitoring
- **Original gap/plan:** Provide an opt-in system metrics collector and CLI toggle for CPU/GPU telemetry.【F:reports/_codex_status_update-2025-10-05.md†L50-L58】
- **Implementation:** `TrainingRunConfig` exposes `log_system_metrics` plus interval/path settings, and the monitoring module spins a background sampler that tolerates missing `psutil`/`pynvml` while streaming metrics to NDJSON.【F:src/codex_ml/training/__init__.py†L116-L156】【F:src/codex_ml/monitoring/system_metrics.py†L441-L519】
- **Further work:** Add regression tests asserting that enabling metrics writes records when optional deps are present (and emits warnings otherwise).

### Checkpointing & Resume
- **Original gap/plan:** Prune older checkpoints and compress new ones to avoid unbounded disk growth.【F:reports/_codex_status_update-2025-10-05.md†L50-L58】
- **Implementation:** Retention is configurable through `keep_last_n`, `_prune_checkpoint_files` trims stale artifacts alongside their sidecars, and epoch checkpoints adopt a zipped `.ptz` layout during functional training.【F:src/codex_ml/training/__init__.py†L116-L133】【F:src/codex_ml/training/__init__.py†L396-L407】【F:src/codex_ml/training/__init__.py†L1047-L1057】
- **Further work:** Confirm that resumption logic recognises `.ptz` extensions across both functional and huggingface-trainer flows.

### Data Handling
- **Original gap/plan:** Guard against silent data drift by hashing shards and providing deterministic streaming loaders.【F:reports/_codex_status_update-2025-10-05.md†L50-L59】
- **Implementation:** JSONL loaders normalise inputs and shuffle with fixed seeds, while the dataset loader writes manifest checksums and streams text deterministically across sharded sources.【F:src/codex_ml/data/jsonl_loader.py†L13-L72】【F:src/codex_ml/data/loader.py†L1-L194】
- **Further work:** Dataset streaming via Hugging Face `datasets` remains optional; consider documenting best-effort fallbacks when that extra isn’t installed.

### Security & Safety
- **Original gap/plan:** Harden offline security scans so vulnerabilities surface without network access.【F:reports/_codex_status_update-2025-10-05.md†L50-L59】
- **Implementation:** The pip-audit wrapper automatically falls back to cached/offline mode, ensuring security checks run during air-gapped reviews without failing the workflow.【F:tools/pip_audit_wrapper.py†L1-L79】
- **Further work:** High-bandit findings noted in the report should still be triaged; add tracking issues or mark waivers when acceptable risk is documented.【F:reports/_codex_status_update-2025-10-05.md†L319-L334】

### Experiment Tracking
- **Original gap/plan:** Keep MLflow local unless developers explicitly opt in to remote URIs and ensure flattened parameter logging.【F:reports/_codex_status_update-2025-10-05.md†L50-L59】
- **Implementation:** `ensure_local_tracking` forces file-backed URIs, logging explicit warnings when remote hosts are blocked, and `_as_flat_params` flattens nested config structures for reproducible logging.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L1-L137】
- **Further work:** Persist the effective tracking URI in run artifacts so provenance reports reflect the guard’s final decision.

### Extensibility
- **Original gap/plan:** Strengthen plugin registries to surface load failures early and avoid circular imports.【F:reports/_codex_status_update-2025-10-05.md†L50-L59】
- **Implementation:** The registry core performs entry-point discovery lazily, tracks failed plugins, and exposes helpers for temporary registrations, providing clear errors when extensions cannot be loaded.【F:src/codex_ml/registry/base.py†L1-L186】
- **Further work:** Automate periodic scans of `_failed_entry_points` so CI/local gates highlight third-party extension regressions promptly.

## High-Signal & Deferred Items

The Oct-05 update also called out structural risks—distributed training, RLHF reward agents, dataset streaming, external moderation APIs, and automated release tooling—that remain deferred by design.【F:reports/_codex_status_update-2025-10-05.md†L351-L357】 Capture any decision to tackle these in dedicated roadmap entries so their status is visible in future audits.

## Recommended Next Steps

1. Backfill regression tests for system-metrics logging and offline model loading to guard recent changes.
2. Extend metrics sinks to emit CSV/Parquet alongside NDJSON so the evaluation gap is fully closed.
3. Document outstanding bandit findings and deferred capabilities in `DEFERRED.md` to keep remediation ownership explicit.
