# [Docs]: Reproducibility & Determinism
> Generated: 2025-09-26 02:35:00 | Author: mbaetiong  
Roles: [Primary], [Secondary] ⚡ Energy: [5]

## Overview
This document outlines how training runs in the `_codex_` project preserve reproducibility and how to restore or continue experiments deterministically. It has been updated to include: CUDNN determinism helper, checkpoint SHA256 hashing, config snapshot persistence, and checkpoint retention utilities.

## Pillars
| Pillar | Mechanism | Location / Artifact |
|--------|-----------|---------------------|
| Seeding | Unified `_set_seed` applying Python, NumPy, Torch | `codex_ml/train_loop.py` |
| Deterministic Default | `seed=None or 0` → fixed `1234` | `train_loop._DEFAULT_SEED` |
| CUDNN Determinism (opt-in) | `set_cudnn_deterministic(True)` | `utils/determinism.py` |
| Checkpointing | Model, optimizer, scheduler, metadata | `checkpoint.pt`, `metadata.json` |
| Latest Pointer | Fast resume discovery | `latest.json` |
| Checkpoint Integrity | SHA256 of checkpoint stored | `latest.json.checkpoint_sha256` |
| Config Snapshot | Persisted run config | `config.snapshot.json` |
| Scheduler State | Included in `checkpoint.pt` | Via `save_checkpoint` |
| Optimizer State | Included in `checkpoint.pt` | Adam / others |
| Resume Logic | Loads last epoch + states | `_attempt_resume` |
| LR Tracking | Per-epoch learning rate history | `learning_rate_history` metric |
| Retention Policy | Prune old epoch dirs | `utils/retention.py` |

## Seeds
| Source | Action |
|--------|--------|
| Python `random` | `random.seed(seed)` |
| NumPy (if installed) | `np.random.seed(seed)` |
| Torch CPU | `torch.manual_seed(seed)` |
| Torch CUDA | `torch.cuda.manual_seed_all(seed)` |

Optional GPU determinism (not auto-enabled):
```python
from codex_ml.utils.determinism import set_cudnn_deterministic
set_cudnn_deterministic(True)  # benchmark=False enforced internally
```

## Checkpoint Structure
```
<checkpoint_dir>/
  latest.json
  config.snapshot.json
  epoch-0001/
    checkpoint.pt
    metadata.json
  epoch-0002/
    checkpoint.pt
    metadata.json
  ...
```

### `latest.json` (extended)
```json
{
  "epoch": 4,
  "path": "epoch-0004",
  "created_at": "2025-09-26T02:30:12Z",
  "model_params": 1234567,
  "optimizer_steps_total": 42,
  "scheduler_type": "linear",
  "checkpoint_sha256": "5ad3d1f9b1a4c8c0..."
}
```

### `metadata.json` (extended)
```json
{
  "epoch": 4,
  "created_at": "...",
  "optimizer_steps_total": 42,
  "optimizer_steps_epoch": 3,
  "steps_per_epoch": 5,
  "grad_accum": 2,
  "avg_loss": 0.0123,
  "scheduler_type": "linear",
  "current_lrs": [0.00072],
  "learning_rate_history_len": 4,
  "checkpoint_sha256": "5ad3d1f9b1a4c8c0..."
}
```

## Learning Rate History
```
"learning_rate_history": [
  [0.001],
  [0.0008333],
  [0.0006666]
]
```
- `linear`: epoch-wise interpolation to `final_lr_scale * base_lr`
- `step`: decays per `step_size`, `gamma`

## Resume Flow
1. Supply `checkpoint.dir` and `checkpoint.resume=true` (Hydra) or `resume=True`.
2. `latest.json` is parsed for last epoch + sha256.
3. `checkpoint.pt` (model, optimizer, scheduler) loaded.
4. Training continues at `last_epoch + 1`, or short-circuits if complete.

## Retention Policy
Implemented via `prune_checkpoints()`:
| Policy Key | Meaning |
|------------|---------|
| `keep_last` | Keep newest N epochs |
| `keep_every` | Retain epochs divisible by this number |
| `max_epochs` | Optional hard cap after selection |
| Always Protected | Epoch referenced by `latest.json` |

Example retention execution after each save:
```python
run_training(
  epochs=10,
  checkpoint_dir="ckpts",
  retention_policy={"keep_last": 3, "keep_every": 5}
)
```

## Config Snapshot
If `run_config` dict passed to `run_training`, it is written to:
```
<checkpoint_dir>/config.snapshot.json
```
Overwritten each run (future enhancement: versioning / hashing).

## Failure Handling
| Scenario | Behavior |
|----------|----------|
| Corrupt `latest.json` | Warn → start epoch 1 |
| Missing checkpoint file | Ignore resume; continue fresh |
| Model mismatch | Warning; continue without state restore |
| Partial epoch crash | Previous epoch safe |
| Failed retention deletion | Warning only |

## Integrity
| Aspect | Mechanism |
|--------|-----------|
| Checkpoint Hash | SHA256 of `checkpoint.pt` |
| Propagation | Stored in `latest.json` + `metadata.json` |
| Resume Info | `resume_meta.previous_checkpoint_sha256` |

## Minimal Example
```bash
python -m codex_ml.cli.train epochs=5 checkpoint.dir=artifacts/ck \
  checkpoint.resume=true scheduler.type=linear scheduler.final_lr_scale=0.3 \
  reproducibility.cudnn_deterministic=true \
  checkpoint.retention.keep_last=2
```

## Programmatic Usage
```python
from codex_ml.train_loop import run_training

result = run_training(
    epochs=4,
    checkpoint_dir="ck",
    run_config={"epochs": 4, "model_name": "Tiny"},
    retention_policy={"keep_last": 2},
    deterministic_cudnn=True,
)
print(result["checkpoint_sha256_last"])
```

## Reproducibility Checklist
| Item | Status | Action |
|------|--------|--------|
| Fixed seed default | ✅ | Use / override `seed` |
| CUDNN deterministic toggle | ✅ | Pass `deterministic_cudnn=True` |
| Full LR trace | ✅ | Inspect `learning_rate_history` |
| State continuity after resume | ✅ | See `resumed_from_epoch` |
| Checkpoint integrity hash | ✅ | Verify `checkpoint_sha256_last` |
| Config capture | ✅ | `config.snapshot.json` |
| Atomic latest pointer | ❌ | Future: temp + rename |
| Retention pruning | ✅ | Provide `retention_policy` |
| Integrity hash in pointer | ✅ | In `latest.json` |

## Roadmap Enhancements
1. Atomic write + backup for `latest.json`.
2. Hash + size recorded in retention reports.
3. Keep hashed snapshot of run config (compare drift).
4. Optional digital signature for checkpoints.

---