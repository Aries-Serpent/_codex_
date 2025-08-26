## 2025-05-19 – Validation metrics & splits
- Added: `--val-split`/`--test-split` flags and per-epoch validation logging to `metrics.json`.
- Deferred: stratified splits, GPU-heavy metrics, and online trackers.
- Risks: small datasets may skip evaluation when insufficient tokens.

## 2025-11-09 – Offline experiment tracking
- Added unified `codex_ml.monitoring.codex_logging` with optional TensorBoard, W&B, and MLflow sinks.
- Patched `engine_hf_trainer.py` and `functional_training.py` to sample CPU/GPU metrics and log per-step scalars.
- Added offline test coverage for logging bootstrap and docs for monitoring and experiment tracking.
- Deferred: full Trainer callbacks and extended NVML telemetry.
