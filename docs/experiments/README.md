# Experiment Logging

Codex writes all run artefacts to the `runs/` directory.  Each invocation of
`run_functional_training` or the `codex codex train` CLI creates a new
timestamped folder:

``` text
runs/
  20240101-120000-toy-train/
    metrics.ndjson
    params.ndjson
    config.ndjson
    config.json
    provenance.ndjson
    checkpoints/
```
## File formats

* **metrics.ndjson** – schema `v1` rows with timestamp, run id, metric name,
  value, split and dataset.
* **params.ndjson** – parameter key/value pairs recorded at run start.
* **config.ndjson** / **config.json** – resolved, serialisable configuration
  snapshot for reproducibility.
* **provenance.ndjson** – git commit, hostname, working directory and other
  provenance hints.

All files are valid line-delimited JSON and can be consumed with tools such as
`jq`, `sqlite-utils`, or the helper script
[`examples/mlflow_offline.py`](../../examples/mlflow_offline.py).

## Enabling optional trackers

Tracking backends are disabled by default.  Opt-in per run using environment
variables or the CLI flags added in this update:

```bash
# Enable MLflow offline logging to ./runs/mlflow
codex codex train --config configs/training/base.yaml \
    --mlflow-uri file:./runs/mlflow

# Enable W&B offline logging to the "toy" project
codex codex train --config configs/training/base.yaml \
    --wandb-project toy
```
Internally these map to the following environment variables:

| Variable | Purpose | Default |
| -------- | ------- | ------- |
| `CODEX_MLFLOW_ENABLE` | Toggle MLflow logging | `0` |
| `CODEX_MLFLOW_URI` | MLflow tracking URI | `file:./mlruns` |
| `CODEX_WANDB_ENABLE` | Toggle W&B logging | `0` |
| `CODEX_WANDB_PROJECT` | W&B project name | Experiment name |

TensorBoard logging can be enabled by setting `tracking.tensorboard: true` in the
configuration; logs are emitted under `<run_dir>/tb`.
