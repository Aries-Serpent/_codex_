# Deferred Items

**Last Updated:** 2026-06-22

The following enhancements were intentionally deferred during various Codex hardening passes. Items from earlier planning notes
have been merged with the more detailed backlog to give a single queue of follow-ups.

## Advanced RL support
- **Status**: Deferred.
- **Rationale**: Implementing RL agents and reward models adds significant scope beyond the current supervised focus. The minimal
  plan is to finish scaffolding and add a trivial reward model for testing before expanding further.

## Full multi-node distributed training
- **Status**: Deferred.
- **Rationale**: Single-node multi-GPU coverage is sufficient. Multi-node support (DeepSpeed/FSDP) requires additional test
  infrastructure and remains out of scope for now.

## Comprehensive secret scanning integration
- **Status**: Deferred.
- **Rationale**: Third-party scanners such as TruffleHog or Gitleaks can generate false positives in offline environments. A future
  security audit will select and tune an appropriate toolchain.

## Notebook auto-generation
- **Status**: Deferred.
- **Rationale**: Interactive notebooks are nice-to-have; curated manual examples provide more predictable onboarding today.

## Plugin registry unification
- **Status**: Deferred.
- **Rationale**: The metrics registry now supports dynamic registration, but extending the same pattern to models and datasets
  requires refactoring multiple call sites and adding new Hydra schemas. The refactor risks breaking current training pipelines
  without a comprehensive integration suite.
- **Next steps**:
  1. Catalogue existing entry points under `codex_ml.registry` and identify overlap with Hydra configs.
  2. Design a shared registry facade covering models, datasets, and tokenizers with consistent provenance metadata.
  3. Backfill tests that exercise the registry override path before rollout.

## MLflow UI bootstrap
- **Status**: Deferred.
- **Rationale**: Bundling an MLflow tracking UI introduces extra binaries and background processes, conflicting with the offline
  policy of the base image.
- **Next steps**:
  1. Provide a documented `make mlflow-ui` target that launches the UI on demand.
  2. Ship a smoke test that verifies metrics visibility through the REST API without a persistent server.
  3. Evaluate lightweight alternatives (for example, a Rich TUI) for local metric inspection when network access is disabled.

## System metrics expansion
- **Status**: Deferred.
- **Rationale**: Extending GPU/CPU sampling to include per-process breakdowns and NVML event streaming adds optional dependencies
  and increases the test matrix.
- **Next steps**:
  1. Prototype an opt-in sampler behind `monitoring.system_metrics.extended=true`.
  2. Document output schemas and update monitoring tests accordingly.
  3. Add alerting hooks only after the sampling layer stabilises.
