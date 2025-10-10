# Offline Tracking Bootstrap

Use `python -m codex_ml.cli track bootstrap` to enforce **local** tracking stores and offline modes for MLflow and Weights & Biases.

```bash
python -m codex_ml.cli track bootstrap --root ./mlruns_local --backend both --mode offline --write-env .codex/exports.env --print-exports
source <(python -m codex_ml.cli track bootstrap --root ./mlruns_local --backend mlflow --print-exports)
```

- **MLflow**: produces a `file:` tracking URI (`MLFLOW_TRACKING_URI`) and defaults the experiment name to `codex-local`.
- **Weights & Biases**: sets `WANDB_MODE=offline` by default (use `--mode disabled` to emit `WANDB_DISABLED=true`).

See also:

- MLflow Tracking docs (local file URIs and `MLFLOW_TRACKING_URI`).
- W&B environment variables (`WANDB_MODE=offline`, `WANDB_DISABLED=true`).
