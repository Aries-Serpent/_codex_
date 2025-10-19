# Deferred Enhancements

The following items were intentionally deferred during the Codex-ready hardening. Each entry lists the rationale and a lightweight follow-up plan so future contributors can pick up the work.

## Plugin registry unification
- **Status**: Deferred.
- **Rationale**: The metrics registry now supports dynamic registration, but extending the same pattern to models and datasets requires refactoring multiple call sites and introducing new Hydra schemas. This would risk breaking existing training pipelines without a full integration test suite.
- **Next steps**:
  1. Catalogue the current entry points under `codex_ml.registry` and identify overlap with Hydra configs.
  2. Design a shared registry facade that can register models, datasets, and tokenizers with consistent provenance metadata.
  3. Backfill tests that exercise the registry override path before rolling out to production configs.

## MLflow UI bootstrap
- **Status**: Deferred.
- **Rationale**: Launching a bundled MLflow tracking UI requires packaging additional binaries and managing a background process, which conflicts with the offline-only policy for the base image.
- **Next steps**:
  1. Provide a documented `make mlflow-ui` target that launches the UI only when explicitly requested.
  2. Ship a smoke test that verifies metrics are visible via the REST API without requiring a persistent server.
  3. Evaluate lightweight alternatives (e.g., Rich TUI) for local metric inspection when network access is disabled.

## System metrics expansion
- **Status**: Deferred.
- **Rationale**: Extending GPU/CPU sampling to include per-process breakdowns and NVML event streaming would add new optional dependencies and increase test matrix complexity.
- **Next steps**:
  1. Prototype an opt-in sampler behind `monitoring.system_metrics.extended=true`.
  2. Document expected output schemas and update existing monitoring tests to validate them.
  3. Add alerting hooks only after the sampling layer stabilises.
