# [How-to]: Checkpoint Metadata, Integrity & Retention  
> Generated: 2025-10-09 20:04:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Overview
- Atomic writes (tmpfile→fsync→os.replace)
- Metadata fields: schema_version, created_at, git_sha, config_hash, rng, env, metric_key, metric_value, sha256
- Best‑k retention via index.json (mode=min|max)

Python API
```python
from src.codex_ml.utils.checkpoint_core import save_checkpoint, load_checkpoint, load_best, verify_checkpoint
ckpt_path, meta = save_checkpoint("artifacts/ckpts", {"state": 1}, metric_value=0.123, metric_key="val_loss", mode="min", top_k=3)
state, meta2 = load_checkpoint(ckpt_path, restore_rng=True)
best_state, best_meta, best_path = load_best("artifacts/ckpts")
verify = verify_checkpoint(best_path)
```

Index Schema (index.json)
| Field | Type | Notes |
|-------|------|-------|
| schema_version | str | "1.0" |
| metric_key | str | e.g., "val_loss" |
| mode | str | "min" or "max" |
| top_k | int | Kept checkpoints |
| entries[].path | str | Relative filename |
| entries[].metric | number? | Comparison value |
| entries[].created_at | int | Epoch seconds |
| entries[].sha256 | str | Checksum |

Notes
- load_best() chooses entry according to mode and metric.
- verify_checkpoint() recalculates checksum for tamper detection.

*End*