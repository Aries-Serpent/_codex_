# Completed resolution plans (2025-10-06 → 2025-10-07)

## Offline tracking guard + deterministic logging
- Added `codex_ml.tracking.guards` as the canonical offline enforcement layer with structured `TrackingDecision` output and rich environment inspection, including legacy allow-list envs and local URI normalization.
  - Source: `src/codex_ml/tracking/guards.py`
- Exercised guard behaviour across MLflow/W&B permutations and legacy overrides.
  - Tests: `tests/tracking/test_tracking_guards.py`
- Documented the offline workflow, canonical NDJSON logger, and guard telemetry expectations in the observability module notes.
  - Docs: `docs/modules/observability.md`

## Unified training façade + compatibility shims
- Centralised training entry point via `codex_ml.training.unified_training` with deterministic seeding, checkpoint emission, and legacy wrapper warnings.
  - Source: `src/codex_ml/training/unified_training.py`
  - Package exports: `src/codex_ml/training/__init__.py`
- Added checkpoint core load support so resume flows have parity with save operations.
  - Source: `src/codex_ml/checkpointing/checkpoint_core.py`
- Expanded documentation for unified training goals, determinism guidance, and checkpoint integrity notes.
  - Docs: `docs/unified_training.md`
- Added regression coverage for legacy warning emissions and dataset determinism utilities used by resume flows.
  - Tests: `tests/training/test_unified_training_warnings.py`, `tests/data/test_dataset_determinism.py`

## Tokenization + metrics surface consolidation
- Introduced canonical tokenization API with minimal fallback tokenizer and compat shim emitting deprecations.
  - Sources: `src/codex_ml/tokenization/api.py`, `src/codex_ml/tokenization/compat.py`
- Stable metrics re-export layer for accuracy/F1/BLEU/ROUGE/perplexity/token accuracy with fallback resolution.
  - Source: `src/codex_ml/metrics/api.py`
- Added tokenization alias documentation and expanded CLI usage notes emphasising package-style invocation.
  - Docs: `docs/tokenization_api.md`, `docs/cli.md`

## Detector + aggregation utilities
- Seeded detectors package exports and unified-training detector with scoring heuristics plus JSON-friendly aggregator utilities.
  - Sources: `src/codex_ml/detectors/__init__.py`, `src/codex_ml/detectors/unified_training.py`, `src/codex_ml/detectors/aggregate.py`
- Detector coverage asserts the detector reports failures when the module is missing and passes when expected symbols exist.
  - Tests: `tests/detectors/test_unified_training.py`

## Documentation landing pages and structured logging references
- Added/linked landing docs for manifest integrity, safety API, data determinism, quality gates, performance, releasing, ops index, tests overview, detectors, checkpoint schema v2, and NDJSON summary CLI usage.
  - Docs: `docs/manifest_integrity.md`, `docs/safety_api.md`, `docs/data_determinism.md`, `docs/quality_gates.md`, `docs/performance.md`, `docs/releasing.md`, `docs/index.md`, `docs/ops.md`, `docs/tests_overview.md`, `docs/detectors.md`, `docs/checkpoint_schema_v2.md`, `docs/ndjson_summary.md`
- Logged comparative research references for future offline review.
  - Docs: `docs/SEARCH_NOTES.md`

## CLI coverage + checkpointing/training regression suite
- Validated and expanded CLI surfaces for manifest hashing, tracking guard introspection, and checkpoint verification.
  - Sources: `src/codex_ml/cli/manifest.py`, `src/codex_ml/cli/tracking_decide.py`, `src/codex_ml/cli/checkpoint_validate.py`
  - Tests: `tests/cli/test_cli_manifest.py`, `tests/cli/test_cli_tracking_decide.py`, `tests/cli/test_cli_checkpoint_validate.py`
- Added checkpoint regression coverage for RNG capture, optimizer parity, retention policies, metadata schema compliance, compat shims, and IO round-trips.
  - Tests: `tests/checkpointing/test_rng_state_roundtrip.py`, `tests/checkpointing/test_resume_optimizer_rng_equivalence.py`, `tests/checkpointing/test_retention_and_digest.py`, `tests/checkpointing/test_meta_schema.py`, `tests/checkpointing/test_checkpoint_schema_and_compat.py`, `tests/checkpointing/test_checkpoint_core_io.py`
- Exercised unified training orchestration hooks for resume parity, error propagation, deterministic seeding, and epoch naming helpers.
  - Tests: `tests/training/test_unified_training_parity_and_resume.py`, `tests/training/test_mid_epoch_naming.py`, `tests/training/test_mid_epoch_resume_equivalence.py`, `tests/training/test_scheduler_amp_resume_parity.py`, `tests/training/test_cuda_determinism_guard.py`
- Strengthened tokenization + tracking wrappers with deprecation warnings and NDJSON summary verification.
  - Tests: `tests/tokenization/test_tokenization_api_and_deprecation.py`, `tests/tracking/test_tracking_ndjson_summary.py`
