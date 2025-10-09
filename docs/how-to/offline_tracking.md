# Offline tracking (MLflow & W&B)

This guide shows how to initialize local, offline-friendly tracking.

## Quick start
```bash
python -m codex_ml.cli tracking bootstrap --mlflow --mlflow-uri file:./mlruns
python -m codex_ml.cli tracking bootstrap --wandb --project codex-demo --mode offline
```

To inspect the MLflow UI locally:
```bash
mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1 --port 8080
```

When using W&B offline, sync later:
```bash
wandb sync wandb/dryrun-*
```
