# Offline Tracking Bootstrap

The `codex-offline-bootstrap` CLI helps enforce **local** tracking stores and offline modes for MLflow and Weights & Biases.

```bash
codex-offline-bootstrap env --mlruns-dir ./mlruns --write .codex/exports.sh
source .codex/exports.sh
```

- **MLflow**: uses a local `file://` tracking URI by default, mirroring the MLflow Tracking documentation for file-based stores.
- **Weights & Biases**: sets `WANDB_MODE=offline` unless you already configured an explicit offline/disabled mode.

See also:

- MLflow Tracking docs (local file URIs and `MLFLOW_TRACKING_URI`).
- W&B environment variables (`WANDB_MODE=offline`, `WANDB_DISABLED=true`).
