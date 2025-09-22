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

### Test coverage

- `tests/cli/test_monitoring_cli.py` exercises the Typer commands (`inspect` and `export`) against temporary NDJSON data to keep
  the CLI working offline. Companion coverage in `tests/cli/test_plugins_cli.py` verifies plugin registry inspection commands.

### Viewing

- TensorBoard: `tensorboard --logdir runs/demo/tensorboard`
- MLflow UI: `mlflow ui --backend-store-uri file:runs/demo/mlruns`

All executions run locally via CLI. Do NOT activate any GitHub Actions online files.

## System metrics logging

- `codex_ml.monitoring.system_metrics.SystemMetricsLogger` uses `psutil` to capture CPU utilisation, memory statistics, load averages, and per-process usage.
- Enable the logger via training CLI flag `--system-metrics`. Passing `AUTO` (or omitting a value) writes to `<checkpoint_dir>/system_metrics.jsonl`; provide a relative or absolute path to redirect output.
- Control sampling cadence with `--system-metrics-interval <seconds>` (minimum 0.1 s). Records are newline-delimited JSON objects.
- When `psutil` is unavailable the CLI prints `[monitoring-error]` and continues training without metrics, keeping runs resilient in constrained environments.

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
append samples during training. GPU telemetry is not yet implemented; future iterations may
extend the logger with NVML integration once available.
