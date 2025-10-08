# Offline Tracking Bootstrap

Prepare local MLflow and W&B offline/disabled tracking:
```bash
python -m codex_ml offline-bootstrap --mlflow-dir mlruns_local --wandb-disable
```
Output (JSON) includes the final MLflow `file:///` URI and W&B mode/disabled state.

- **MLflow**: Uses a local **file** store (`file:///...`) for offline runs; point `MLFLOW_TRACKING_URI` to a server when ready.
- **W&B**: Set `WANDB_MODE=offline` to log runs locally and `wandb sync` later; use `WANDB_DISABLED=true` for a full opt-out.
