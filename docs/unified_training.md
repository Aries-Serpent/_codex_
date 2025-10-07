# Unified Training Façade

This module introduces a single entry point:

```python
from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
```

## Goals
- One façade: `run_unified_training(cfg)` to reduce drift between legacy loops.
- Determinism first: optional seeding + CuDNN settings.
- Grad clipping, resume hooks, and checkpoint save at epoch boundaries.
- Thin legacy adapters (`train_loop`, `functional_training`) that emit `DeprecationWarning`.

## Determinism
We follow PyTorch guidance for seeding and DataLoader determinism (workers reseeding, generator usage):
- Reproducibility notes: https://docs.pytorch.org/docs/stable/notes/randomness.html
- DataLoader API: https://docs.pytorch.org/docs/stable/data.html

## Checkpointing
The core schema stores a `weights.pt` payload with model/optimizer state and a sidecar `metadata.json`
with `schema_version`.
- Saving/loading multiple components pattern: https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html

## Tracking & Offline Modes
Enforcement logic prefers local `file://` URIs when offline, and normalizes path-like values:
- MLflow Tracking: https://mlflow.org/docs/latest/ml/tracking/
- W&B offline behavior via environment: https://docs.wandb.ai/guides/track/environment-variables/
- W&B offline guide: https://docs.wandb.ai/support/run_wandb_offline/

## Tests
New tests cover:
- Warning emission for legacy adapters (`pytest.warns`).
- Offline/remote matrix for tracking guards.
- Deterministic data ordering, shard coverage, and UTF-8 digest stability.

## Deprecation Plan
- `train_loop` and `functional_training` are retained as thin shims for one release.
- Downstream callers should move to `run_unified_training(cfg=..., ...)`.
