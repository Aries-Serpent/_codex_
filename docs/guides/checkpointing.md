# Checkpointing Integration Guide

**Last Updated:** 2026-06-22

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
