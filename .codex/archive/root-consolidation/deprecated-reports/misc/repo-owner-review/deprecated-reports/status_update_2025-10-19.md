# Status Update — 2025-10-19

## Completed
- Added a Typer-powered tokenizer CLI with `vocab`, `encode`, and `decode` helpers plus graceful fallbacks.
- Extended the fast tokenizer wrapper with vocabulary utilities and a `build_tokenizer` helper that prefers `transformers` but falls back to local JSON artefacts.
- Integrated the metrics registry into the evaluation runner and added temporary registration tests.
- Persisted a `dataset_manifest.json` during evaluation and surfaced the path in the return payload.
- Introduced offline-aware `tests_offline` nox session semantics and documented usage in the README alongside the new dependency lock flow and CLI quickstart.
- Logged deferred features and next steps in `docs/deferred.md`.

## Outstanding
- Broader registry unification (models/datasets) still needs design work before implementation.
- MLflow UI bootstrap remains deferred pending an offline-friendly activation flow.
- Extended system metrics sampling (per-process/NVML streaming) is postponed until we can expand the monitoring test matrix.
