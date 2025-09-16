# MLflow Offline Workflows

Codex keeps MLflow disabled by default to avoid accidental network calls.  When
ready, opt in locally:

```bash
codex codex train --config configs/training/base.yaml \
    --mlflow-uri file:./runs/mlflow
```

This sets `CODEX_MLFLOW_ENABLE=1` for the duration of the run and points MLflow
at a filesystem-backed store (`./runs/mlflow`).  Inspect results without leaving
the machine:

```bash
mlflow ui --backend-store-uri file:./runs/mlflow
```

For a higher-level summary, run
[`examples/mlflow_offline.py`](../../examples/mlflow_offline.py) against a run
directory.  The helper prints the MLflow command above and highlights the most
recent metrics.

TensorBoard remains a network-free alternative.  Enable it by setting
`tracking.tensorboard: true` in your config and launch via
`tensorboard --logdir runs/<run>/tb`.
