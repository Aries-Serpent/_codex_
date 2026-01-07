# Guide: Training Reproducibility
> Generated: 2025-10-20 06:15:16 UTC | Author: mbaetiong

## Checklist
- Seeds: set Python, NumPy, and framework RNG seeds.
- Deterministic Ops: enable deterministic kernels where available; avoid nondeterministic ops.
- Data: use checksum-validated datasets; record split seeds and sharding parameters.
- Checkpointing: store schema-versioned checkpoints with canonical JSON metadata and `sha256` digests.
- Config: record full Hydra overrides and resolved config snapshots.

## Metrics
- Log metrics with stable names and types; avoid dynamic metric name generation.
- For flaky tests, prefer fixed-size samples and fixed evaluation seeds.
