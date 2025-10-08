# Resume Cookbook

Practical recipes for resuming Codex ML training jobs.

## Unified training façade

```python
from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training

cfg = UnifiedTrainingConfig(
    model_name="demo",
    epochs=3,
    resume_from="artifacts/checkpoints/epoch-0001",
    deterministic=True,
)
run_unified_training(
    cfg,
    callbacks=[],
)
```

Tips:
- Always persist the `cfg` used for the original run alongside the checkpoint
  directory so that resume invocations reproduce the same parameters.
- When `resume_from` points at an epoch directory written by
  `checkpoint_core.save_checkpoint`, the optimizer state is restored and the
  next epoch index is computed automatically.

## Functional training legacy entry point

Legacy callers can continue to use `codex_ml.training.run_functional_training`
while migrating to the unified façade. The compat shim emits a
`DeprecationWarning` so CI can alert on stale import paths.

```python
from codex_ml.training import run_functional_training

state = run_functional_training(
    {...},  # existing functional config
)
```

## Tracking integration

Resumed runs reuse the tracking guards in
`codex_ml.tracking.guards`. Ensure `CODEX_ALLOW_REMOTE_TRACKING=1` is set if you
intentionally resume against a remote MLflow server.

## Verification checklist

- ✅ Restore model/optimizer weights by loading a checkpoint and running a
  short evaluation loop.  If metrics diverge, confirm that the `device` and
  AMP settings match the original run.
- ✅ Inspect `metadata.json` in the checkpoint directory to verify the `epoch`
  field and any custom notes written by callbacks.
- ✅ Re-run quick smoke tests (`nox -s tests -- training::resume`) before
  resuming large hyperparameter sweeps.
