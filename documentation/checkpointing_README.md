# Checkpointing Integration Hints

To use the `CheckpointManager` within a training script:

```python
from pathlib import Path
from codex_ml.utils.checkpointing import CheckpointManager

mgr = CheckpointManager(Path("output/checkpoints"), keep_last=5, keep_best=1)
# To resume
# info = mgr.resume_from(Path("output/checkpoints/epoch-10"), model, optimizer, scheduler)
# During training after each epoch
# mgr.save(epoch, model, optimizer, scheduler, tokenizer, config, metrics)
```

Add CLI flags such as `--checkpoint-dir`, `--resume-from`, `--keep-last`, and `--keep-best`
to your training entrypoint and wire them to the `CheckpointManager`.
