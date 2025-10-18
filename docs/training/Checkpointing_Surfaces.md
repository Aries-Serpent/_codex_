# Checkpointing Surfaces — Canonical vs Legacy

This guide clarifies the checkpointing modules and their intended usage. Canonical paths remain stable; legacy shims continue to work with deprecation guidance.

## Overview
| Surface | Status | Purpose |
|--------|--------|---------|
| codex_ml/utils/checkpoint_core.py | Canonical | Low-level IO, integrity helpers (hash, atomics) |
| codex_ml/utils/checkpointing.py | Canonical | High-level API, schema_version, markers (last/best) |
| src/training/checkpointing.py | Canonical | Trainer-facing utilities, retention, weights_only |
| training/checkpoint_manager.py | Canonical | Retention policy & metadata continuity |
| src/utils/checkpoint*.py | Legacy-compatible | Deprecation shim to canonical APIs |

## Behavior Contracts
- Schema version is consistent across canonical writers/readers.
- Markers:
  - last: pointer to last completed step checkpoint
  - best.json: metadata including target metric, value, path
- Integrity:
  - checksums manifest alongside weights if configured
  - atomic writes on metadata files to avoid partial states

## Usage Snippets
Python:
```python
from codex_ml.utils.checkpointing import save_checkpoint, load_checkpoint

meta = save_checkpoint(
    out_dir="runs/exp1/checkpoints",
    step=1200,
    state={"model": model_state, "optimizer": opt_state},
    metrics={"val_loss": 1.23},
    best_key="val_loss",
    keep_last_k=3,
)
state = load_checkpoint(meta["path"], weights_only=True)
```

CLI (if exposed via runners):
```bash
python -m codex_ml.cli.checkpoint --info latest
```

## Deprecation Mapping
| Legacy Import | Use Instead |
|---------------|-------------|
| src/utils/checkpoint.py | codex_ml/utils/checkpointing.py |
| src/utils/checkpointing.py | codex_ml/utils/checkpointing.py |
| training/checkpoint.py | training/checkpoint_manager.py |

Notes:
- Legacy shims emit DeprecationWarning but preserve behavior.
- Prefer canonical imports in new code and documentation.

## Testing Guidance
- Ensure best.json updates only on strict improvement.
- Verify last marker always points to the most recent completed checkpoint.
- Run tests/checkpointing and tests/utils/test_checkpointing_core.py to validate invariants.

*End of guide*
