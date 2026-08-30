"""Training integration with MLflow tracking.

Provides utilities to integrate MLflow tracking into training loops.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from codex_ml.tracking.mlflow_wrapper import MLflowTracker, get_tracker

logger = logging.getLogger(__name__)

__all__ = ["TrainingTracker", "init_training_tracking", "log_training_step"]


class TrainingTracker:
    """Training-specific MLflow tracker integration."""

    def __init__(
        self,
        config: dict[str, Any],
        run_name: Optional[str] = None,
        auto_log: bool = True,
    ):
        """Initialize training tracker.

        Args:
            config: Training configuration dictionary
            run_name: Run name (auto-generated if None)
            auto_log: Automatically log hyperparameters
        """
        self.config = config
        self.run_name = run_name
        self.auto_log = auto_log

        # Extract tracking config
        tracking_config = config.get("tracking", {})
        mlflow_config = tracking_config.get("mlflow", {})

        self.enabled = mlflow_config.get("enabled", False)
        self.tracker = MLflowTracker(
            enabled=self.enabled,
            tracking_uri=mlflow_config.get("tracking_uri", "file:./mlruns"),
            experiment_name=mlflow_config.get("experiment_name", "codex_training"),
            run_name=run_name,
        )

        self._run_active = False

    def start(self):
        """Start tracking run and log hyperparameters."""
        if not self.enabled:
            logger.info("MLflow tracking disabled")
            return

        self._run_context = self.tracker.start_run(self.run_name)
        self._run_context.__enter__()
        self._run_active = True

        if self.auto_log:
            self._log_hyperparameters()

    def _log_hyperparameters(self):
        """Log hyperparameters from config."""
        training_config = self.config.get("training", {})

        # Extract common hyperparameters
        params = {}
        for key in [
            "learning_rate",
            "lr",
            "batch_size",
            "epochs",
            "num_epochs",
            "weight_decay",
            "dropout",
            "hidden_size",
            "num_layers",
        ]:
            if key in training_config:
                params[key] = training_config[key]

        # Log model config if present
        if "model" in self.config:
            model_config = self.config["model"]
            for key in ["model_type", "architecture", "pretrained"]:
                if key in model_config:
                    params[f"model_{key}"] = model_config[key]

        if params:
            self.tracker.log_params(params)
            logger.info(f"Logged {len(params)} hyperparameters")

    def log_step(
        self,
        step: int,
        metrics: dict[str, float],
        prefix: str = "",
    ):
        """Log metrics for a training step.

        Args:
            step: Step number
            metrics: Dictionary of metrics
            prefix: Prefix for metric names (e.g., "train/", "val/")
        """
        if not self._run_active:
            return

        prefixed_metrics = {
            f"{prefix}{key}" if prefix else key: value for key, value in metrics.items()
        }

        self.tracker.log_metrics(prefixed_metrics, step=step)

    def log_epoch(
        self,
        epoch: int,
        train_metrics: dict[str, float],
        val_metrics: Optional[dict[str, float]] = None,
    ):
        """Log metrics for an epoch.

        Args:
            epoch: Epoch number
            train_metrics: Training metrics
            val_metrics: Validation metrics (optional)
        """
        self.log_step(epoch, train_metrics, prefix="train/")

        if val_metrics:
            self.log_step(epoch, val_metrics, prefix="val/")

    def log_artifact(self, path: str, artifact_path: Optional[str] = None):
        """Log artifact file.

        Args:
            path: Local file path
            artifact_path: Path within artifact store
        """
        if not self._run_active:
            return

        self.tracker.log_artifact(path, artifact_path=artifact_path)

    def log_checkpoint(self, checkpoint_path: str, epoch: int):
        """Log model checkpoint.

        Args:
            checkpoint_path: Path to checkpoint file
            epoch: Epoch number
        """
        if not self._run_active:
            return

        self.tracker.log_artifact(checkpoint_path, artifact_path=f"checkpoints/epoch_{epoch}")
        self.tracker.set_tag("best_epoch", epoch)

    def log_final_metrics(self, metrics: dict[str, float]):
        """Log final metrics at end of training.

        Args:
            metrics: Final metrics dictionary
        """
        if not self._run_active:
            return

        for key, value in metrics.items():
            self.tracker.set_tag(f"final_{key}", value)

        logger.info(f"Logged {len(metrics)} final metrics")

    def end(self):
        """End tracking run."""
        if self._run_active:
            self._run_context.__exit__(None, None, None)
            self._run_active = False
            logger.info("Ended MLflow tracking run")


def init_training_tracking(
    config: dict[str, Any],
    run_name: Optional[str] = None,
) -> TrainingTracker:
    """Initialize training tracker from config.

    Args:
        config: Configuration dictionary
        run_name: Run name

    Returns:
        TrainingTracker instance
    """
    return TrainingTracker(config, run_name=run_name)


def log_training_step(
    step: int,
    loss: float,
    metrics: Optional[dict[str, float]] = None,
    prefix: str = "train/",
):
    """Convenience function to log training step using global tracker.

    Args:
        step: Step number
        loss: Loss value
        metrics: Additional metrics
        prefix: Metric prefix
    """
    tracker = get_tracker()

    all_metrics = {"loss": loss}
    if metrics:
        all_metrics.update(metrics)

    prefixed = {f"{prefix}{k}": v for k, v in all_metrics.items()}
    tracker.log_metrics(prefixed, step=step)
