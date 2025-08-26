<!-- BEGIN: CODEX_MLFLOW_DOCS -->
# Experiment Tracking (MLflow)

This project provides optional MLflow integration that can be enabled via CLI flags.
If MLflow is not installed, tracking gracefully degrades to local JSON artifact logging.

## CLI Flags
- `--mlflow-enable` — turn on MLflow logging.
- `--mlflow-tracking-uri` — defaults to `./mlruns` (local file store).
- `--mlflow-experiment` — experiment name (default `codex-experiments`).

You can attach these to an existing `argparse.ArgumentParser` via:

```python
from codex_ml.tracking import add_mlflow_flags, mlflow_from_args
parser = argparse.ArgumentParser()
add_mlflow_flags(parser)
cfg = mlflow_from_args(parser.parse_args())
```

## Programmatic Usage
```python
from codex_ml.tracking import (
    MlflowConfig,
    ensure_local_artifacts,
    log_artifacts,
    log_metrics,
    log_params,
    seed_snapshot,
    start_run,
)
from pathlib import Path
cfg = MlflowConfig(enable=True, tracking_uri="./mlruns", experiment="demo")
run_dir = Path("output/experiments/12345")
with start_run(cfg) as run:
    enabled = bool(run)
    log_params({"model": "demo"}, enabled=enabled)
    log_metrics({"accuracy": 0.9}, step=1, enabled=enabled)
    ensure_local_artifacts(run_dir, {"status": "ok"}, {"seed": 42}, enabled=enabled)
    seed_snapshot({"python": 42}, run_dir, enabled=enabled)
    log_artifacts(run_dir, enabled=enabled)
```

## Reproducibility

* Fix random seeds across libraries.
* Local policy: always write `output/experiments/<timestamp>/summary.json` and `seeds.json`.
* Keep checkpoints under `output/checkpoints/…`.
* When MLflow is enabled, log those directories as run artifacts.
* Re-running with the same seed **should** yield identical metrics (subject to nondeterministic ops).

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. Run validations locally in the Codex environment.
