# Local Experiment Tracking (Offline)

Use the CLI to initialise a local tracking root:

```bash
python -m codex_ml.cli track bootstrap --root ./.local/track --backend both --mode offline --write-env .codex/track.env --print-exports
```

- **MLflow**: sets `MLFLOW_TRACKING_URI` to a `file:` store under `.local/track/mlruns` with a default experiment name of `codex-local`.
- **Weights & Biases**: configures either `WANDB_MODE=offline` (default) or `WANDB_DISABLED=true` and stores runs under `.local/track/wandb`.

Then export the variables or source the `.env`:

```bash
set -a && . .codex/track.env && set +a
```

To visualise MLflow locally:

```bash
mlflow ui --backend-store-uri "$MLFLOW_TRACKING_URI"
```

To later sync W&B offline runs:

```bash
wandb init  # set project
wandb sync .local/track/wandb
```
