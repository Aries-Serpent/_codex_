"""Example production training script with MLflow tracking integration.

This script demonstrates Phase 6.1: MLflow Tracking Integration
- Uses MLflowTracker for experiment tracking
- Maintains offline-first design
- Graceful degradation if MLflow unavailable
- Logs params, metrics, and artifacts
- Compatible with existing training workflows
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# Import existing training infrastructure
from codex_ml.training.mlflow_integration import MLflowTracker, is_mlflow_available
from codex_ml.training.loop import run_minimal_training
from codex_ml.logging.metrics import MetricLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Load training configuration.

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary
    """
    # Default configuration
    config = {
        "training": {
            "base_loss": 10.0,
            "decay": 0.9,
            "learning_rate": 0.001,
            "batch_size": 32,
            "max_steps": 100,
        },
        "tracking": {
            "mlflow_enabled": False,  # Opt-in
            "experiment_name": "production_training",
            "tracking_uri": "./mlruns",
        },
    }

    # Load from file if provided
    if config_path:
        import yaml

        with open(config_path) as f:
            loaded_config = yaml.safe_load(f)
            config.update(loaded_config)

    return config


def train_with_tracking(
    config: Dict[str, Any], run_dir: str = "artifacts/runs"
) -> Dict[str, float]:
    """Run training with optional MLflow tracking.

    Args:
        config: Training configuration
        run_dir: Directory for run artifacts

    Returns:
        Training results
    """
    tracking_config = config.get("tracking", {})
    mlflow_enabled = tracking_config.get("mlflow_enabled", False)

    # Initialize MLflow tracker (no-op if disabled or unavailable)
    tracker = None
    if mlflow_enabled and is_mlflow_available():
        logger.info("MLflow tracking enabled")
        tracker = MLflowTracker(
            experiment_name=tracking_config.get("experiment_name", "production_training"),
            tracking_uri=tracking_config.get("tracking_uri", "./mlruns"),
            run_name=tracking_config.get("run_name"),
            tags=tracking_config.get("tags", {}),
        )
    else:
        if mlflow_enabled and not is_mlflow_available():
            logger.warning(
                "MLflow tracking requested but MLflow not available. Continuing without tracking."
            )
        else:
            logger.info("MLflow tracking disabled")

    # Start tracking run
    if tracker:
        tracker.start_run()

        # Log training parameters
        training_params = config.get("training", {})
        tracker.log_params(
            {
                "learning_rate": training_params.get("learning_rate"),
                "batch_size": training_params.get("batch_size"),
                "max_steps": training_params.get("max_steps"),
                "base_loss": training_params.get("base_loss"),
                "decay": training_params.get("decay"),
            }
        )

        # Log configuration as artifact
        config_path = Path(run_dir) / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        import yaml

        with open(config_path, "w") as f:
            yaml.dump(config, f)
        tracker.log_artifact(str(config_path))

    # Run training (existing training loop)
    max_steps = config.get("training", {}).get("max_steps", 100)
    results = run_minimal_training(config, max_steps, run_dir)

    # Log final metrics to MLflow
    if tracker:
        tracker.log_metrics(
            {
                "loss_final": results["loss_final"],
            }
        )

        # Log metrics file as artifact
        metrics_path = Path(run_dir) / "metrics.ndjson"
        if metrics_path.exists():
            tracker.log_artifact(str(metrics_path))

        # End tracking run
        tracker.end_run()

    logger.info(f"Training completed. Final loss: {results['loss_final']:.4f}")

    return results


def main():
    """Main training entry point."""
    parser = argparse.ArgumentParser(description="Production training with MLflow tracking")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config file (YAML)",
        default=None,
    )
    parser.add_argument(
        "--mlflow-enabled",
        action="store_true",
        help="Enable MLflow tracking (opt-in)",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="production_training",
        help="MLflow experiment name",
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        default="artifacts/runs/production",
        help="Directory for run artifacts",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override with CLI args
    if args.mlflow_enabled:
        config.setdefault("tracking", {})["mlflow_enabled"] = True

    if args.experiment_name:
        config.setdefault("tracking", {})["experiment_name"] = args.experiment_name

    # Run training
    results = train_with_tracking(config, args.run_dir)

    logger.info("Training completed successfully!")
    logger.info(f"Results: {results}")

    return 0


if __name__ == "__main__":
    exit(main())
