# Checkpoint retention + RNG snapshots

## Filename schema

Checkpoints follow `epoch{E}-metric{VAL}.pt`.

## Best-K retention

* `mode` can be `min` or `max`.
* Metrics that parse as `NaN` (or missing) are treated as **worst**.
* Ties break toward the **newer epoch** so the latest checkpoint is retained.

## RNG capture & restore

`save_checkpoint` stores CPU and (if available) CUDA RNG states. `load_checkpoint(..., restore_rng=True)` restores them for deterministic resume.
