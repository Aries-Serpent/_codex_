# Monitoring & Experiment Tracking

This project provides optional integration for:
- **TensorBoard** (scalars, histograms): logs under `runs/<run-name>/tensorboard/`
- **Weights & Biases (W&B)**: enable with `--enable-wandb` and run with `WANDB_MODE=offline` (or `disabled`) plus `WANDB_PROJECT=<your_project>`
- **MLflow** (local file store): enable with `--mlflow-enable`, optionally set `--mlflow-tracking-uri` and `--mlflow-experiment`; logs to `runs/<run-name>/mlruns/`

Both `scripts/deploy_codex_pipeline.py` and the Hydra CLI (`python -m codex_ml.cli.main`) honor these flags to stream metrics, GPU utilization, and persist run artifacts.

## Quickstart

```bash
python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-mlflow
# With Weights & Biases
WANDB_MODE=offline WANDB_PROJECT=myproj python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-wandb
# Pipeline example
python scripts/deploy_codex_pipeline.py --corpus data.jsonl --demos demos.jsonl --prefs prefs.jsonl --output-dir out --enable-wandb --mlflow-enable
# Hydra CLI example
python -m codex_ml.cli.main --enable-wandb --mlflow-enable
```

### Viewing
- TensorBoard: `tensorboard --logdir runs/demo/tensorboard`
- MLflow UI: `mlflow ui --backend-store-uri file:runs/demo/mlruns`

All executions run locally via CLI. Do NOT activate any GitHub Actions online files.

## Prometheus (optional)

<!-- SENTINEL -->
<!-- BEGIN: CODEX_MONITORING_DOC -->
# Monitoring & Experiment Tracking

Flags:
- `--enable-wandb`
- `--mlflow-enable` / `--mlflow-tracking-uri` / `--mlflow-experiment`

Behavior:
- TensorBoard: logs to `<output>/tb`
- Weights & Biases: enabled when flag set (honours `WANDB_MODE` for offline/disabled)
- MLflow: wraps `mlflow.*` via `codex_ml.tracking.mlflow_utils.*`; artifacts/runs tracked where configured

## Hardware metrics

`codex_ml.monitoring.codex_logging` samples CPU/RAM via `psutil` and GPU stats via NVML
(`pynvml`), falling back to `torch.cuda.mem_get_info`. These values are logged alongside
training metrics when the above flags are used.
