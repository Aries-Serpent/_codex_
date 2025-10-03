"""Public helpers for configuring experiment tracking.

Importing :mod:`codex_ml.tracking` keeps the public surface intentionally
compact: scripts can bootstrap MLflow with :func:`start_run`, stream structured
metrics with :func:`log_metrics`, and snapshot metadata with
:func:`ensure_local_artifacts` without importing the heavier internal modules.

Example
-------
```python
from codex_ml.tracking import init_experiment, log_metrics, start_run

ctx = init_experiment(cfg)
with start_run(cfg.experiment.name):
    log_metrics({"loss": 0.12}, step=1, enabled=cfg.tracking.mlflow.enable)
ctx.finalize()
```

Each helper is documented for direct use in notebooks and automation scripts,
and remains stable across releases so that lightweight tooling can rely on it.
"""

# BEGIN: CODEX_MLFLOW_INIT
from .init_experiment import ExperimentContext, init_experiment
from .mlflow_utils import (
    MlflowConfig,
    ensure_local_artifacts,
    log_artifacts,
    log_metrics,
    log_params,
    seed_snapshot,
    start_run,
)

__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "ensure_local_artifacts",
    "seed_snapshot",
    "ExperimentContext",
    "init_experiment",
]
# END: CODEX_MLFLOW_INIT
