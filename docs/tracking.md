All metrics logged to MLflow must include an explicit `step` parameter for proper time-series rendering.

## Tracking URI

Codex utilities read the `CODEX_MLFLOW_URI` environment variable to determine
where to store runs. If unset, a local file-based store `file:mlruns` is used so
experiments can be tracked offline without additional setup:

```bash
export CODEX_MLFLOW_URI="file:mlruns"
```

Setting the variable to an HTTP(S) URI will forward logs to a remote MLflow
server instead.
