# Audit Requirement Mapping

This document summarises how the inspected modules relate to the upcoming audit requirements (CLI surface, metric registry, manifest generation, offline tests, lock file management, and documentation). It also captures immediate observations about cross-module dependencies that may influence remediation work.

## Requirement Coverage Snapshot

| File | Key functionality | Audit requirements touched | Edits needed? |
| --- | --- | --- | --- |
| `src/tokenizer/fast_tokenizer.py` | Wrapper and loader logic for fast tokenizers with graceful fallbacks. | Supports CLI needs by providing a resilient loader for command-line tooling. | Likely minor adjustments (expose via CLI module, add audit logging). |
| `src/tokenization/train_tokenizer.py` | Hydra-driven training pipeline that writes tokenizer artifacts and manifest metadata. | CLI entry (`hydra.main`) and manifest generation already in place. | Ensure manifest schema matches audit format; add CLI docs/tests as needed. |
| `src/codex_ml/metrics_base.py` | Core binary classification metrics shared by evaluation code. | Feeds into the metric registry layer. | Confirm functions are registered; expand docs/tests for audit traceability. |
| `src/codex_ml/eval/metrics.py` | Comprehensive evaluation metric implementations plus legacy offline test helper. | Metric registry (direct usage) and offline test scaffolding. | Align error handling with registry expectations; document offline test workflow. |
| `src/codex_ml/eval/runner.py` | Evaluation orchestration, metrics aggregation, and manifest/NDJSON outputs. | Manifest coverage (dataset + evaluation manifests) and registry integration. | Validate manifest schema & add CLI flags; verify registry fallbacks. |
| `src/codex_ml/tracking/writers.py` | Tracking writers that emit NDJSON metrics and manifest descriptors. | Manifest coverage (metrics manifest) and metric logging infrastructure. | Audit schema conformance; surface CLI controls for enabling writers. |
| `src/codex_ml/monitoring/system_metrics.py` | System metrics sampling/logging for offline runs. | Supports offline monitoring/tests requirements. | Harden dependency fallbacks; document CLI hooks for enabling sampling. |
| `src/training/trainer.py` | Extended trainer with checkpoint management and structured logging hooks. | Indirectly supports metric registry/logging expectations. | Map emitted metrics to registry schema; document CLI invocation path. |
| `training/engine_hf_trainer.py` | HF Trainer wrapper with CLI parser, offline logging, NDJSON export. | CLI surface plus manifest-style logging of metrics. | Align CLI help/docs with audit, ensure metrics manifest references registry. |
| `configs/` | Hydra configuration tree for tokenization, training, and evaluation workflows. | Documentation/CLI readiness via reproducible config defaults. | Cross-link configs in docs; ensure defaults align with manifest + registry fields. |

## Cross-Module Observations

- `src/codex_ml/eval/runner.py` consumes `codex_ml.metrics.registry.get_metric` and the `NdjsonWriter`, so registry changes or writer schema updates require coordinated edits across evaluation and tracking layers.
- `src/codex_ml/tracking/writers.py` optionally inspects `codex_ml.monitoring.system_metrics` to record dependency availability, tying monitoring enablement to tracking summaries.
- `training/engine_hf_trainer.py` depends on tracking utilities (e.g., `NDJSONMetricsWriter`, logging bootstrap) and checkpoint helpers; manifest or registry changes must be reflected in its logging payloads.
- Hydra-based CLIs (`src/tokenization/train_tokenizer.py`, configs under `configs/`) expect directory layouts and config defaults that downstream runners (`src/codex_ml/eval/runner.py`, `training/engine_hf_trainer.py`) also consume.
