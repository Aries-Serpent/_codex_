All metrics logged to MLflow must include an explicit `step` parameter for proper time-series rendering.

## Tracking URI

Codex utilities read the `CODEX_MLFLOW_URI` environment variable to determine
where to store runs. If unset, a local file-based store `file:mlruns` is used so
experiments can be tracked offline without additional setup:

```bash
export CODEX_MLFLOW_URI="file:mlruns"
```text
Setting the variable to an HTTP(S) URI will forward logs to a remote MLflow
server instead.

## CLI toggles

Training and resume commands expose explicit MLflow controls to avoid implicit
logging:

```bash
# Enable MLflow with a local file store
codex train --config configs/training/base.yaml --mlflow --mlflow-tracking-uri file:mlruns

# Disable MLflow even if the config enables it
codex train --config configs/training/base.yaml --no-mlflow

# Override experiment and run names when resuming from a manifest
codex resume manifest.json --mlflow --mlflow-experiment demo --mlflow-run-name resumed-run
```

Flags forward directly into the training config (`training.logging.mlflow_*`) so
that offline runs remain deterministic. Use `--no-mlflow` for air-gapped
environments.

## Custom metric hooks and summaries

The HuggingFace trainer wrapper exposes a custom metrics callback registry via
`training/engine_hf_trainer.py`. Add callables to `training.metrics.custom` in
the config to emit additional scalars; each hook receives the trainer, model,
and step to compute values. Metrics are written to NDJSON or CSV depending on
`--metrics-writer` and are summarised at the end of the run.

To export MLflow summaries alongside local writers, enable MLflow (CLI flag or
config) and set `logging.mlflow_enable=true`. Summary statistics are logged with
the same keys as the NDJSON/CSV writers, ensuring parity across sinks. When
`CODEX_JSON_LOGGING=1`, logs remain structured for downstream parsing.
