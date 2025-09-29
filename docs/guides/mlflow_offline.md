# MLflow: Offline-by-default Guard

This project prefers **local file-backed** MLflow tracking by default to avoid accidental remote logging.

## TL;DR
```python
from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking
ensure_local_tracking()  # defaults to file:./artifacts/mlruns
```

- Honors `MLFLOW_TRACKING_URI` if it points to a local path or `file:` URI.
- You can override the default local path in code:
  ```python
  ensure_local_tracking("file:/tmp/my_mlruns")
  ```

### Opt-in remote usage
Remote URIs (`http(s)`) are blocked unless you **explicitly opt in**:
```bash
export CODEX_MLFLOW_ALLOW_REMOTE=1
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
```
When using the helper context manager:
```python
from codex_ml.utils.experiment_tracking_mlflow import maybe_mlflow
with maybe_mlflow(enable=True, run_name="demo", tracking_uri="http://127.0.0.1:5000") as m:
    # If not opted in, guard forces a local file: backend.
    print("effective:", m.get_tracking_uri())
```

## Notes
- MLflow supports configuring the tracking target via `MLFLOW_TRACKING_URI` or `mlflow.set_tracking_uri(...)`. A `file:` URI keeps runs local.
- This guard is **offline-first** and does **not** start a server.

## Validation (local)
To validate documentation code-fence integrity using the project hook:

```bash
pre-commit run validate-fences --files docs/guides/mlflow_offline.md
```

Alternatively, use the helper script added under `tools/validate_fences.py`.
