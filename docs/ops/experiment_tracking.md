<!-- BEGIN: CODEX_MLFLOW_DOCS -->
# Experiment Tracking (MLflow)

This project provides optional MLflow integration that can be enabled via CLI flags.
If MLflow is not installed, tracking gracefully degrades to local JSON artifact logging.

## CLI Flags
- `--mlflow-enable` — turn on MLflow logging.
- `--mlflow-tracking-uri` — defaults to `./mlruns` (local file store).
- `--mlflow-experiment` — experiment name (default `codex-experiments`).

### Example

```bash
python scripts/deploy_codex_pipeline.py \
  --corpus data/corpus.jsonl --demos data/demos.jsonl --prefs data/prefs.jsonl \
  --output-dir out --mlflow-enable --mlflow-tracking-uri ./mlruns \
  --mlflow-experiment demo
```

## Programmatic Usage
```python
from codex_ml.tracking import (
    MlflowConfig,
    start_run,
    log_params,
    log_metrics,
    log_artifacts,
    ensure_local_artifacts,
)
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
* Local artifacts live under `output/experiments/<timestamp>` with checkpoints in `output/checkpoints/`.
* Re-running with the same seed **should** yield identical metrics (subject to nondeterministic ops).

`seed_snapshot` can be used directly when only seed logging is required; `ensure_local_artifacts` calls it internally.

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. Run validations locally in the Codex environment.
