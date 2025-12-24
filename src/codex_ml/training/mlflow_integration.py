"""MLflow tracking integration with offline fallback.

This module provides MLflow experiment tracking with graceful degradation
when MLflow is unavailable. Designed for offline-first operation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["MLflowTracker", "is_mlflow_available"]

try:
    import mlflow

    MLFLOW_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    MLFLOW_AVAILABLE = False
    logger.info("MLflow not installed. Install with: pip install mlflow")


def is_mlflow_available() -> bool:
    """Check if MLflow is available."""
    return MLFLOW_AVAILABLE


class MLflowTracker:
    """MLflow experiment tracker with graceful degradation.

    Features:
    - Offline-first design (local tracking by default)
    - Graceful degradation if MLflow unavailable
    - Automatic experiment creation
    - Context manager support
    - Fallback to no-op if MLflow fails

    Example:
        >>> tracker = MLflowTracker("my_experiment")
        >>> tracker.log_params({"lr": 0.001, "batch_size": 32})
        >>> tracker.log_metrics({"loss": 0.5, "accuracy": 0.9}, step=10)
        >>> tracker.log_artifact("model.pt")
    """

    def __init__(
        self,
        experiment_name: str,
        tracking_uri: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ):
        """Initialize MLflow tracker.

        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking URI (default: ./mlruns for offline)
            run_name: Optional run name
            tags: Optional tags dict
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri or "./mlruns"
        self.run_name = run_name
        self.tags = tags or {}
        self.active = False
        self.run_id: Optional[str] = None

        if MLFLOW_AVAILABLE:
            self._initialize()

    def _initialize(self):
        """Initialize MLflow with error handling."""
        try:
            # set tracking URI (local by default for offline)
            mlflow.set_tracking_uri(self.tracking_uri)

            # set or create experiment
            mlflow.set_experiment(self.experiment_name)

            self.active = True
            logger.info(
                f"MLflow tracking enabled: {self.tracking_uri}, "
                f"experiment: {self.experiment_name}"
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(
                f"MLflow initialization failed: {e}. " f"Continuing without MLflow tracking."
            )
            self.active = False

    def start_run(self, run_name: Optional[str] = None, tags: Optional[dict[str, str]] = None):
        """Start an MLflow run.

        Args:
            run_name: Optional run name
            tags: Optional tags dict
        """
        if not self.active:
            return

        try:
            run_name = run_name or self.run_name
            run_tags = {**self.tags, **(tags or {})}

            mlflow.start_run(run_name=run_name, tags=run_tags)
            self.run_id = mlflow.active_run().info.run_id
            logger.info(f"Started MLflow run: {self.run_id}")
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to start MLflow run: {e}")
            self.active = False

    def end_run(self):
        """End the current MLflow run."""
        if not self.active:
            return

        try:
            mlflow.end_run()
            logger.info(f"Ended MLflow run: {self.run_id}")
            self.run_id = None
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to end MLflow run: {e}")

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow.

        Args:
            metrics: dict of metric name -> value
            step: Optional step number
        """
        if not self.active:
            return

        try:
            mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to log metrics to MLflow: {e}")

    def log_params(self, params: dict[str, Any]):
        """Log parameters to MLflow.

        Args:
            params: dict of parameter name -> value
        """
        if not self.active:
            return

        try:
            # Convert all values to strings (MLflow requirement)
            str_params = {k: str(v) for k, v in params.items()}
            mlflow.log_params(str_params)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to log params to MLflow: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Log an artifact (file) to MLflow.

        Args:
            local_path: Path to local file
            artifact_path: Optional destination path in artifact store
        """
        if not self.active:
            return

        try:
            if not Path(local_path).exists():
                logger.warning(f"Artifact not found: {local_path}")
                return

            mlflow.log_artifact(local_path, artifact_path)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to log artifact to MLflow: {e}")

    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        """Log multiple artifacts (directory) to MLflow.

        Args:
            local_dir: Path to local directory
            artifact_path: Optional destination path in artifact store
        """
        if not self.active:
            return

        try:
            if not Path(local_dir).exists():
                logger.warning(f"Artifact directory not found: {local_dir}")
                return

            mlflow.log_artifacts(local_dir, artifact_path)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to log artifacts to MLflow: {e}")

    def set_tags(self, tags: dict[str, str]):
        """set tags for the current run.

        Args:
            tags: dict of tag name -> value
        """
        if not self.active:
            return

        try:
            mlflow.set_tags(tags)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Failed to set MLflow tags: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start_run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.end_run()
        return False


def init_mlflow(
    experiment_name: str,
    tracking_uri: Optional[str] = None,
    run_name: Optional[str] = None,
    tags: Optional[dict[str, str]] = None,
    auto_start: bool = True,
) -> MLflowTracker:
    """Initialize MLflow tracking (convenience function).

    Args:
        experiment_name: Name of the experiment
        tracking_uri: Tracking URI (default: ./mlruns)
        run_name: Optional run name
        tags: Optional tags
        auto_start: Whether to start run immediately

    Returns:
        MLflowTracker instance

    Example:
        >>> tracker = init_mlflow("my_exp", run_name="run_1")
        >>> tracker.log_params({"lr": 0.001})
        >>> # Training loop
        >>> tracker.log_metrics({"loss": 0.5}, step=0)
        >>> tracker.end_run()
    """
    tracker = MLflowTracker(experiment_name, tracking_uri, run_name, tags)

    if auto_start:
        tracker.start_run()

    return tracker
