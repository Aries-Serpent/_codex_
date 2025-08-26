## 2025-05-19 – Validation metrics & splits
- Added: `--val-split`/`--test-split` flags and per-epoch validation logging to `metrics.json`.
- Deferred: stratified splits, GPU-heavy metrics, and online trackers.
- Risks: small datasets may skip evaluation when insufficient tokens.

## 2025-11-09 – Offline experiment tracking
- Added unified `codex_ml.monitoring.codex_logging` with optional TensorBoard, W&B, and MLflow sinks.
- Patched `engine_hf_trainer.py` and `functional_training.py` to sample CPU/GPU metrics and log per-step scalars.
- Added offline test coverage for logging bootstrap and docs for monitoring and experiment tracking.
- Deferred: online W&B/remote MLflow servers, full Trainer callbacks, and extended NVML telemetry.
## 2025-08-26 – LoRA and deterministic splits
- Implemented optional LoRA adapter with graceful fallback when `peft` is missing.
- Added grad accumulation and mixed precision helpers to `functional_training.py`.
- Introduced deterministic data splitting utility.
- Generated `requirements.lock` and local test gate script.
- Sanitized external links in README for offline use.
## CI policy docs — 2025-08-26T20:17:49Z
- Created /workspace/_codex_/docs/ci.md (web search allowed; remote CI disallowed)

## Disable remote CI — 2025-08-26T20:17:49Z
- Patched 5 workflow file(s) to `workflow_dispatch` and guarded jobs.
- Total jobs guarded: 7

