# Checkpointing Integration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

`CheckpointManager` provides save/restore of model state, optimizer state, LR scheduler, tokenizer, and training configuration. It supports keep-last and keep-best rotation policies to bound disk usage.

## Basic Usage

```python
from pathlib import Path
from codex_ml.utils.checkpointing import CheckpointManager

mgr = CheckpointManager(Path("output/checkpoints"), keep_last=5, keep_best=1)
```

**Save a checkpoint after each epoch:**

```python
mgr.save(
    epoch=epoch,
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    tokenizer=tokenizer,
    config=config,
    metrics={"val_loss": val_loss},
)
```

**Resume from the latest checkpoint:**

```python
info = mgr.resume_from(
    Path("output/checkpoints/epoch-10"), model, optimizer, scheduler
)
print(f"Resumed from epoch {info['epoch']}")
```

## CLI Flags

Add these flags to your training entry-point and wire them to `CheckpointManager`:

| Flag | Default | Description |
|------|---------|-------------|
| `--checkpoint-dir` | `output/checkpoints` | Where checkpoints are saved |
| `--resume-from` | `None` | Path to resume checkpoint |
| `--keep-last` | `5` | Keep N most-recent checkpoints |
| `--keep-best` | `1` | Keep N best checkpoints by metric |

## Rotation Policy

When `keep_last=5`, checkpoints older than the 5 most recent are deleted automatically. `keep_best=1` retains the single lowest-loss checkpoint regardless of age.

## Multi-lane operating rules

The repository's Chronicle cost model treats `P1`, `P2`, `S1`, and `Seq` as lane labels, not as a permission override. The actual gate is the warning budget and checkpoint state. By default, `chronicle cost-tips` warns at `16,000` credits and recommends stopping at `20,000` credits.

- `P1`: continue only while the lane stays below the warning threshold and the latest verified state has been checkpointed.
- `P2`: queue behind `P1` or resume from a checkpoint once the lane is back under budget.
- `S1`: keep support work narrow and resumable; do not expand it beyond the current checkpoint boundary.
- `Seq`: run this as the sequential validation/review gate before opening a new exploration lane.

Operationally, a warning budget means "stop broadening this lane"; a hard budget means "save the checkpoint, stop the lane, and resume from the last verified checkpoint in a narrower task". Heavy sessions without checkpoint signals are treated as a cost-risk signal and should be split before more exploration.

```python
# save after each independently verifiable lane
info = mgr.save(
    epoch=epoch,
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    tokenizer=tokenizer,
    config=config,
    metrics={"val_loss": val_loss},
)

# resume from the last checkpoint when a lane hits warning or hard budget
resume = mgr.resume_from(Path("output/checkpoints/epoch-10"), model, optimizer, scheduler)
```
