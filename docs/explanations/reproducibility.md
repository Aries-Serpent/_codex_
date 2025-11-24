# Reproducibility notes

- Seeds propagate through `DataConfig.seed` and the training CLI fallback; they
  also influence the cache key so split reuse remains deterministic.
- Cache keys include dataset mtime, ratios, and record count to avoid stale
  reuse when source data changes.
- Experiment events are timestamped but otherwise derived from deterministic
  configs. The aggregated summary records only local paths and metrics.
- LoRA usage is opt-in and requires the `peft` dependency; when disabled, the
  model builder uses a plain torch module and avoids remote downloads.

Following these practices keeps runs reproducible even when Hydra is not
available.
