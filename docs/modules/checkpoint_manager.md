# Checkpoint Manager

**Last Updated:** 2026-06-22

`CheckpointManager` keeps recent and best checkpoints.

- `keep_last`: number of recent checkpoints to retain.
- `keep_best`: retain checkpoints with best metric.
- `save(step, model, optimizer, scheduler, metrics=...)` persists state.
- `resume_from(path, ...)` restores model and optimizer.

Checkpoints include RNG state for deterministic resume.
