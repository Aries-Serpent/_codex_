# Monitoring & Experiment Tracking

This project provides optional integration for:

- **TensorBoard** (scalars, histograms): logs under `runs/<run-name>/tensorboard/`
- **Weights & Biases (W&B)**: enable with `--enable-wandb` and run with `WANDB_MODE=offline` (or `disabled`) plus `WANDB_PROJECT=<your_project>`
- **MLflow** (local file store): enable with `--mlflow-enable`, optionally set `--mlflow-tracking-uri` and `--mlflow-experiment`; logs to `runs/<run-name>/mlruns/`

Both `deploy/deploy_codex_pipeline.py` and the Hydra CLI (`python -m codex_ml.cli.main`) honor these flags to stream metrics and persist run artifacts.

## Quickstart

```bash
python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-mlflow
# With Weights & Biases
WANDB_MODE=offline WANDB_PROJECT=myproj python tools/monitoring_integrate.py --run-name demo --enable-tensorboard --enable-wandb
# Pipeline example
python deploy/deploy_codex_pipeline.py --corpus data.jsonl --demos demos.jsonl --prefs prefs.jsonl --output-dir out --enable-wandb --mlflow-enable
# Hydra CLI example
python -m codex_ml.cli.main --enable-wandb --mlflow-enable
# Functional trainer example with system metrics logging (writes to <checkpoint_dir>/system_metrics.jsonl)
python -m codex_ml.cli train-model --config configs/training/base.yaml --system-metrics AUTO --system-metrics-interval 15
```

### Viewing

- TensorBoard: `tensorboard --logdir runs/demo/tensorboard`
- MLflow UI: `mlflow ui --backend-store-uri file:runs/demo/mlruns`

All executions run locally via CLI. Do NOT activate any GitHub Actions online files.

## System metrics logging

- `codex_ml.monitoring.system_metrics.SystemMetricsLogger` uses `psutil` to capture CPU utilisation, memory statistics, load averages, and per-process usage. When `psutil` is missing or disabled the module emits a structured `system_metrics.psutil_missing` warning (and `system_metrics.dependency_missing` during import failures) and falls back to a minimal CPU-only sampler (load averages, heuristic CPU %, and process RSS where available).
- Enable the logger via training CLI flag `--system-metrics`. Passing `AUTO` (or omitting a value) writes to `<checkpoint_dir>/system_metrics.jsonl`; provide a relative or absolute path to redirect output.
- Control sampling cadence with `--system-metrics-interval <seconds>` (minimum 0.1 s). Records are newline-delimited JSON objects.
- Feature flags: set `CODEX_MONITORING_ENABLE_PSUTIL=0` to skip psutil entirely. GPU telemetry is opt-in via `CODEX_MONITORING_ENABLE_GPU=1` (optionally `CODEX_MONITORING_ENABLE_NVML=1` for NVML-backed metrics); force-disable it with `CODEX_MONITORING_DISABLE_GPU=1` or `configure_system_metrics(poll_gpu=False)`.

## Prometheus (optional)

<!-- SENTINEL -->

<!-- BEGIN: CODEX_MONITORING_DOC -->

# Monitoring & Experiment Tracking

Flags:

- `--enable-wandb`
- `--mlflow-enable` / `--mlflow-tracking-uri` / `--mlflow-experiment`
- `--system-metrics` / `--system-metrics-interval`

Behavior:

- TensorBoard: logs to `<output>/tb`
- Weights & Biases: enabled when flag set (honours `WANDB_MODE` for offline/disabled)
- MLflow: wraps `mlflow.*` via `codex_ml.tracking.mlflow_utils.*`; artifacts/runs tracked where configured
- System metrics: writes newline-delimited JSON samples (CPU %, memory, load averages, process stats) under `<checkpoint_dir>/system_metrics.jsonl` or the path supplied to the flag.

## Hardware metrics

`codex_ml.monitoring.system_metrics` provides the CPU/memory sampler. When the `--system-metrics`
flag is active the functional trainer launches `SystemMetricsLogger` in the background to
append samples during training. GPU telemetry is opt-in: set
`CODEX_MONITORING_ENABLE_GPU=1` (and, if necessary, `CODEX_MONITORING_ENABLE_NVML=1`) to
initialise NVML, or `CODEX_MONITORING_DISABLE_GPU=1`/`configure_system_metrics(poll_gpu=False)`
to keep sampling CPU-only environments quiet. When dependencies are missing the sampler
degrades gracefully with structured warnings (`system_metrics.psutil_missing`) and minimal telemetry.
