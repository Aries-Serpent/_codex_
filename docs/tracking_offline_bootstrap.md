# Offline Tracking Bootstrap

Prepare local MLflow and W&B offline/disabled tracking:
```bash
python -m codex_ml offline-bootstrap --mlflow-dir mlruns_local --wandb-disable
```
Output (JSON) includes the final MLflow `file:///` URI and W&B mode/disabled state.

- **MLflow**: Uses a local file store unless you explicitly point to a remote URI.
- **W&B**: Set `WANDB_MODE=offline` to log runs locally and `wandb sync` later, or set `WANDB_DISABLED=true` to disable entirely.
