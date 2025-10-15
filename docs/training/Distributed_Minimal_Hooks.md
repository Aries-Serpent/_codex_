# Minimal Distributed Hooks

The `codex_ml.distributed.minimal` module offers safe helper functions that do nothing
when `torch.distributed` is unavailable. This keeps local development and CI workflows fast
while enabling opt-in DDP runs.

## Quick start

```python
from codex_ml.distributed import (
    barrier,
    cleanup,
    get_rank,
    get_world_size,
    init_distributed_if_needed,
)

init_distributed_if_needed()  # gated by CODEX_DDP=1
rank = get_rank()
world = get_world_size()
# ... training loop ...
barrier()
cleanup()
```

## Enabling distributed mode

```bash
export CODEX_DDP=1
python -m codex_ml.cli.hydra_main --config-path configs --config-name default
```

The helper defaults to the NCCL backend but automatically falls back to `gloo` when CUDA is
unavailable. All functions return sensible defaults (`rank=0`, `world_size=1`) if the process
group was never initialised.

## Failure handling

`init_distributed_if_needed` catches and suppresses errors thrown during initialisation so
single-process workflows stay usable even in partially configured environments (e.g., missing
hostfile or incorrect backend).
