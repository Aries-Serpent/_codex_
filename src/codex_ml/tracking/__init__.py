"""Public helpers for configuring experiment tracking.

Importing :mod:`codex_ml.tracking` keeps the public surface intentionally
compact: scripts can bootstrap MLflow with :func:`start_run`, stream structured
metrics with :func:`log_metrics`, and snapshot metadata with
:func:`ensure_local_artifacts` without importing the heavier internal modules.

Features:
    - **Offline-First Logging**: Works without network connection
    - **MLflow Integration**: Experiment tracking and model registry
    - **NDJSON Streaming**: Efficient structured logging
    - **Graceful Fallback**: Continues to work if MLflow unavailable
    - **Memory Consolidation**: Automatic pattern learning

Example:
    >>> from codex_ml.tracking import init_experiment, log_metrics, start_run
    >>> 
    >>> ctx = init_experiment(cfg)
    >>> with start_run(cfg.experiment.name):
    ...     log_metrics({"loss": 0.12}, step=1, enabled=cfg.tracking.mlflow.enable)
    >>> ctx.finalize()

Installation:
    Tracking is included in all profiles. For MLflow server:
    pip install mlflow

Configuration:
    Set environment variables:
    
    MLFLOW_TRACKING_URI: MLflow server URI (default: file:./artifacts/mlruns)
    CODEX_OFFLINE_MODE: Force offline mode (default: auto-detect)
    CODEX_CHECKPOINT_DIR: Checkpoint directory (default: .codex/checkpoints)

Offline-First Behavior:
    When MLflow is unavailable:
    - Events logged to NDJSON files in .codex/experiments/
    - Logs automatically sync when MLflow becomes available
    - All data preserved, no loss of telemetry

Integration with Memory Systems:
    Logging integrates with memory systems to:
    - Store events in STM (short-term memory)
    - Consolidate patterns to LTM (long-term memory)
    - Enable cross-session pattern queries
    - Support autonomous learning and decision-making

Memory Consolidation:
    >>> from codex_ml.tracking import log_metrics
    >>> from codex_ml.monitoring.codex_logging import CodexLogger
    >>> 
    >>> logger = CodexLogger(experiment_name="training")
    >>> for epoch in range(100):
    ...     log_metrics({"epoch": epoch, "loss": compute_loss()})
    ...     # Events automatically consolidated to LTM every 10 events
    >>> 
    >>> patterns = logger.query_patterns("*")  # Access learned patterns

See Also:
    - docs/optional_features_guide.md for Memory Systems details
    - docs/INTEGRATION_GUIDE_COMPREHENSIVE.md for full examples
    - docs/PERFORMANCE_TUNING.md for optimization

Classes:
    ExperimentContext: Manages experiment lifecycle
    MlflowConfig: MLflow configuration
    RunInfo: Run information and metadata

Functions:
    init_experiment: Initialize an experiment
    start_run: Start MLflow run context
    log_metrics: Log metrics to MLflow
    log_params: Log hyperparameters
    log_artifacts: Log artifacts (files, models)
    ensure_local_artifacts: Ensure artifacts saved locally
    seed_snapshot: Save random seed snapshot

Each helper is documented for direct use in notebooks and automation scripts,
and remains stable across releases so that lightweight tooling can rely on it.

Author: Codex Team
Version: 0.3.0
"""

# BEGIN: CODEX_MLFLOW_INIT
from .experiments import (
    RunInfo,
    finish_run,
    load_events,
    log_metric,
    new_run_info,
)
from .experiments import start_run as start_local_run
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
    "ExperimentContext",
    "MlflowConfig",
    "RunInfo",
    "ensure_local_artifacts",
    "finish_run",
    "init_experiment",
    "load_events",
    "log_artifacts",
    "log_metric",
    "log_metrics",
    "log_params",
    "new_run_info",
    "seed_snapshot",
    "start_local_run",
    "start_run",
]
# END: CODEX_MLFLOW_INIT
