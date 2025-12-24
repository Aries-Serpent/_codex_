"""Complete MLflow integration for experiment tracking.

Provides full MLflow integration with offline-first design and graceful degradation.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

__all__ = ["MLflowTracker", "log_metric", "log_param", "log_artifact"]


class MLflowTracker:
    """Complete MLflow experiment tracker with offline-first design."""

    def __init__(
        self,
        enabled: bool = False,
        tracking_uri: str = "file:./mlruns",
        experiment_name: str = "codex_experiments",
        run_name: Optional[str] = None,
    ):
        """Initialize MLflow tracker.

        Args:
            enabled: Enable MLflow tracking
            tracking_uri: MLflow tracking URI (defaults to local file storage)
            experiment_name: Experiment name
            run_name: Run name (auto-generated if None)
        """
        self.enabled = enabled
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.run_name = run_name
        self._mlflow = None
        self._run = None
        self._active = False

        if self.enabled:
            self._init_mlflow()

    def _init_mlflow(self):
        """Initialize MLflow if available."""
        try:
            import mlflow

            self._mlflow = mlflow
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow initialized: {self.tracking_uri}")
        except ImportError as e:
            logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            logger.warning("MLflow not available, tracking disabled")
            self.enabled = False
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"MLflow initialization failed: {e}")
            self.enabled = False

    @contextmanager
    def start_run(self, run_name: Optional[str] = None, nested: bool = False):
        """Context manager for MLflow run.

        Args:
            run_name: Run name (uses instance default if None)
            nested: Whether this is a nested run

        Yields:
            MLflow run object or None
        """
        if not self.enabled or self._mlflow is None:
            yield None
            return

        run_name = run_name or self.run_name
        try:
            self._run = self._mlflow.start_run(run_name=run_name, nested=nested)
            self._active = True
            logger.info(f"Started MLflow run: {run_name or 'auto'}")
            yield self._run
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"MLflow run failed: {e}")
            yield None
        finally:
            if self._active:
                try:
                    self._mlflow.end_run()
                    self._active = False
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Failed to end MLflow run: {e}")

    def log_params(self, params: Dict[str, Any]):
        """Log parameters to current run.

        Args:
            params: Dictionary of parameters to log
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.log_params(params)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log params: {e}")

    def log_param(self, key: str, value: Any):
        """Log single parameter.

        Args:
            key: Parameter name
            value: Parameter value
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.log_param(key, value)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log param {key}: {e}")

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to current run.

        Args:
            metrics: Dictionary of metrics to log
            step: Step number (optional)
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log metrics: {e}")

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        """Log single metric.

        Args:
            key: Metric name
            value: Metric value
            step: Step number (optional)
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.log_metric(key, value, step=step)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log metric {key}: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Log artifact file to current run.

        Args:
            local_path: Path to local file
            artifact_path: Path within artifact store (optional)
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        if not Path(local_path).exists():
            logger.warning(f"Artifact file not found: {local_path}")
            return

        try:
            self._mlflow.log_artifact(local_path, artifact_path=artifact_path)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log artifact: {e}")

    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        """Log directory of artifacts.

        Args:
            local_dir: Path to local directory
            artifact_path: Path within artifact store (optional)
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        if not Path(local_dir).is_dir():
            logger.warning(f"Artifact directory not found: {local_dir}")
            return

        try:
            self._mlflow.log_artifacts(local_dir, artifact_path=artifact_path)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to log artifacts: {e}")

    def set_tag(self, key: str, value: Any):
        """Set tag on current run.

        Args:
            key: Tag name
            value: Tag value
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.set_tag(key, value)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to set tag {key}: {e}")

    def set_tags(self, tags: Dict[str, Any]):
        """Set multiple tags on current run.

        Args:
            tags: Dictionary of tags
        """
        if not self.enabled or not self._active or self._mlflow is None:
            return

        try:
            self._mlflow.set_tags(tags)
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug(f"Failed to set tags: {e}")

    def end_run(self):
        """End current run manually."""
        if self._active and self._mlflow is not None:
            try:
                self._mlflow.end_run()
                self._active = False
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.debug(f"Failed to end run: {e}")


# Global tracker instance (can be configured via init)
_global_tracker: Optional[MLflowTracker] = None


def get_tracker() -> MLflowTracker:
    """Get global tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MLflowTracker(enabled=False)
    return _global_tracker


def init_tracking(
    enabled: bool = True,
    tracking_uri: str = "file:./mlruns",
    experiment_name: str = "codex_experiments",
) -> MLflowTracker:
    """Initialize global MLflow tracker.

    Args:
        enabled: Enable tracking
        tracking_uri: Tracking URI
        experiment_name: Experiment name

    Returns:
        MLflowTracker instance
    """
    global _global_tracker
    _global_tracker = MLflowTracker(
        enabled=enabled, tracking_uri=tracking_uri, experiment_name=experiment_name
    )
    return _global_tracker


# Convenience functions using global tracker
def log_metric(name: str, value: float, step: Optional[int] = None) -> None:
    """Log metric using global tracker.

    Args:
        name: Metric name
        value: Metric value
        step: Step number (optional)
    """
    get_tracker().log_metric(name, value, step=step)


def log_param(name: str, value: Any) -> None:
    """Log parameter using global tracker.

    Args:
        name: Parameter name
        value: Parameter value
    """
    get_tracker().log_param(name, value)


def log_artifact(local_path: str, artifact_path: Optional[str] = None) -> None:
    """Log artifact using global tracker.

    Args:
        local_path: Path to local file
        artifact_path: Path within artifact store (optional)
    """
    get_tracker().log_artifact(local_path, artifact_path=artifact_path)
