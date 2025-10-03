"""User-facing helpers for configuring experiment tracking.

This package exposes a compact surface around MLflow integration that can be
used without importing the heavier implementation modules. Typical usage:

```python
from codex_ml.tracking import init_experiment, log_metrics, start_run

ctx = init_experiment(cfg)
with start_run(cfg.experiment.name):
    log_metrics({"loss": 0.12}, step=1, enabled=cfg.tracking.mlflow.enable)
ctx.finalize()
```

The functions imported below remain stable entry points for notebooks and
scripts that only need to start runs or push metrics and artifacts.
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
