## 2025-05-19 – Validation metrics & splits
- Added: `--val-split`/`--test-split` flags and per-epoch validation logging to `metrics.json`.
- Deferred: stratified splits, GPU-heavy metrics, and online trackers.
- Risks: small datasets may skip evaluation when insufficient tokens.
