# Codex system overview

This document sketches the offline-first flow across training, inference, and tracking surfaces.

## Data and training flow
1. **Configs**: Hydra-friendly YAML under `configs/` defines model/data/train/logging defaults.
2. **Training**: `codex-train` launches CPU-friendly loops, optionally enabling `--system-metrics` for telemetry.
3. **Checkpoints**: Training writes checkpoints and metrics under `runs/` with NDJSON logs.

## Inference flow
- `src/codex_ml/serving/inference_server.py` mounts a FastAPI app with `/predict` and `/embed` routes.
- The default `SimpleInferenceModel` runs deterministically and is safe for local smoke tests.
- Error handling returns HTTP 500 with clear messages; health/metrics endpoints remain lightweight.

## Experiment tracking and quality gates
- Runs and provenance live under `runs/` and `reports/` for local auditability.
- Duplication analysis (`tools/duplication_analyzer.py`) enforces code health and writes `reports/duplication_report.json`.
- Gap/task alignment is captured in `codex_gap_registry.yaml` with tasks defined in `codex_task_sequence.yaml`.

## Extensibility
- Registries for datasets, metrics, models, and tokenizers can be extended via local plugins; see `docs/extensibility/registries_and_plugins.md`.
- LoRA configurations are validated for dtype and device before adapters are applied.
