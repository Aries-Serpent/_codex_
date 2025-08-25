# Monitoring & Experiment Tracking

This project provides optional integration for:
- **TensorBoard** (scalars, histograms): logs under `runs/<run-name>/tensorboard/`
- **Weights & Biases (W&B)**: enable with `--enable-wandb` and environment `WANDB_PROJECT=<your_project>`
- **MLflow** (local file store): logs to `runs/<run-name>/mlruns/`

## Quickstart

```bash
python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-mlflow
# With Weights & Biases
WANDB_PROJECT=myproj python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-wandb
```

### Viewing
- TensorBoard: `tensorboard --logdir runs/demo/tensorboard`
- MLflow UI: `mlflow ui --backend-store-uri file:runs/demo/mlruns`

All executions run locally via CLI. Do NOT activate any GitHub Actions online files.
