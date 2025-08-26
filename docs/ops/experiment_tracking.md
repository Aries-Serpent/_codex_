<!-- BEGIN: CODEX_MLFLOW_DOCS -->
# Experiment Tracking (MLflow)

This project provides optional MLflow integration that can be enabled via CLI flags.
If MLflow is not installed, tracking gracefully degrades to local JSON artifact logging.

## CLI Flags
- `--mlflow-enable` — turn on MLflow logging.
- `--mlflow-tracking-uri` — defaults to `./mlruns` (local file store).
- `--mlflow-experiment` — experiment name (default `codex-experiments`).

## Programmatic Usage
```python
from codex_ml.tracking import MlflowConfig, start_run, log_params, log_metrics, log_artifacts, ensure_local_artifacts
from pathlib import Path
cfg = MlflowConfig(enable=True, tracking_uri="./mlruns", experiment="demo")
run_dir = Path("output/experiments/12345")
with start_run(cfg) as run:
    enabled = bool(run)
    log_params({"model": "demo"}, enabled=enabled)
    log_metrics({"accuracy": 0.9}, step=1, enabled=enabled)
    ensure_local_artifacts(run_dir, {"status": "ok"}, {"seed": 42})
    log_artifacts(run_dir, enabled=enabled)
```

## Reproducibility

* Fix random seeds across libraries.
* Log `seeds.json` and config snapshot along with checkpoints.
* Re-running with the same seed **should** yield identical metrics (subject to nondeterministic ops).

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. Run validations locally in the Codex environment.
