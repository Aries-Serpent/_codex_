# Offline Tracking Bootstrap CLI

Bootstrap a local-first tracking workspace:

```bash
python -m codex_ml.cli track bootstrap --root ./mlruns_local --backend both --mode offline --write-env .codex/exports.env
```

- Generates a `.env` file with `MLFLOW_TRACKING_URI` and W&B offline/disabled variables.
- Creates `./mlruns_local/mlruns` for MLflow and `./mlruns_local/wandb` for W&B runs.
- Use `--mode disabled` to emit `WANDB_DISABLED=true` instead of offline mode.

To export variables in the current shell without writing a file:

```bash
python -m codex_ml.cli track bootstrap --root ./mlruns_local --backend mlflow --print-exports
```
