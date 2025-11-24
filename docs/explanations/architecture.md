# Architecture overview

Track G adds small, composable building blocks rather than a monolithic
training stack:

- `codex_ml.codex_model` builds torch models from local checkpoints and applies
  optional PEFT adapters when available.
- `codex_ml.codex_data` handles deterministic shuffling and caching of dataset
  splits, keyed by dataset content and seed.
- `conf/` holds Hydra defaults grouped by domain (`model/`, `data/`,
  `training/`, `experiment/`). The training CLI prefers these configs when
  Hydra is installed.
- `codex_ml.tracking.experiments` records run metadata and metrics to NDJSON for
  offline aggregation. `scripts/analyze_experiments.py` converts those events
  into markdown/JSON summaries consumed by the audit scorecard.

The flow remains offline-first: no remote fetches, deterministic seeds, and
artifacts stored under `artifacts/`.
