"""Continuous learning pipeline for auto-retraining on drift detection.

This module provides infrastructure for continuous model improvement through
automated retraining when drift is detected.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["ContinuousLearningPipeline", "ModelRegistry", "ModelVersion"]


@dataclass
class ModelVersion:
    """Model version information.

    Attributes:
        version: Version identifier
        model_path: Path to model checkpoint
        metrics: Performance metrics
        trained_at: Training timestamp
        dataset_hash: Hash of training dataset
        drift_score: Drift score that triggered retraining
    """

    version: str
    model_path: Path
    metrics: dict[str, float]
    trained_at: str
    dataset_hash: Optional[str] = None
    drift_score: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "model_path": str(self.model_path),
            "metrics": self.metrics,
            "trained_at": self.trained_at,
            "dataset_hash": self.dataset_hash,
            "drift_score": self.drift_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelVersion:
        """Create from dictionary."""
        return cls(
            version=data["version"],
            model_path=Path(data["model_path"]),
            metrics=data["metrics"],
            trained_at=data["trained_at"],
            dataset_hash=data.get("dataset_hash"),
            drift_score=data.get("drift_score"),
        )


class ModelRegistry:
    """Registry for tracking model versions."""

    def __init__(self, registry_path: Path | str):
        """Initialize model registry.

        Args:
            registry_path: Path to registry JSON file
        """
        self.registry_path = Path(registry_path)
        self.versions: list[ModelVersion] = []
        self.load()

    def load(self) -> None:
        """Load registry from disk."""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                self.versions = [ModelVersion.from_dict(v) for v in data.get("versions", [])]
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Failed to load registry: <ERROR_TYPE>")

    def save(self) -> None:
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"versions": [v.to_dict() for v in self.versions]}
        self.registry_path.write_text(json.dumps(data, indent=2))

    def register(self, version: ModelVersion):
        """Register a new model version.

        Args:
            version: Model version to register
        """
        self.versions.append(version)
        self.save()
        logger.info(f"Registered model version: {version.version}")

    def get_latest(self) -> Optional[ModelVersion]:
        """Get latest model version."""
        return self.versions[-1] if self.versions else None

    def get_by_version(self, version: str) -> Optional[ModelVersion]:
        """Get model by version string.

        Args:
            version: Version identifier

        Returns:
            ModelVersion or None if not found
        """
        for v in self.versions:
            if v.version == version:
                return v
        return None


class ContinuousLearningPipeline:
    """Continuous learning pipeline with auto-retraining."""

    def __init__(
        self,
        model_name: str,
        registry_path: Path | str = "models/registry.json",
        drift_threshold: float = 0.15,
        min_samples_retrain: int = 1000,
        performance_degradation_threshold: float = 0.05,
    ):
        """Initialize continuous learning pipeline.

        Args:
            model_name: Name of the model
            registry_path: Path to model registry
            drift_threshold: Drift score threshold for retraining
            min_samples_retrain: Minimum samples required to retrain
            performance_degradation_threshold: Max acceptable performance drop
        """
        self.model_name = model_name
        self.registry = ModelRegistry(registry_path)
        self.drift_threshold = drift_threshold
        self.min_samples_retrain = min_samples_retrain
        self.performance_degradation_threshold = performance_degradation_threshold

    def should_retrain(
        self,
        drift_score: float,
        samples_count: int,
        current_performance: Optional[dict[str, float]] = None,
    ) -> bool:
        """Determine if retraining should be triggered.

        Args:
            drift_score: Current drift score
            samples_count: Number of new samples available
            current_performance: Current model performance metrics

        Returns:
            True if retraining should be triggered
        """
        # Check drift threshold
        if drift_score < self.drift_threshold:
            logger.info(f"Drift score {drift_score:.3f} below threshold {self.drift_threshold}")
            return False

        # Check minimum samples
        if samples_count < self.min_samples_retrain:
            logger.info(f"Sample count {samples_count} below minimum {self.min_samples_retrain}")
            return False

        # Check performance degradation
        if current_performance:
            latest = self.registry.get_latest()
            if latest:
                for metric, value in current_performance.items():
                    if metric in latest.metrics:
                        baseline = latest.metrics[metric]
                        if value < baseline - self.performance_degradation_threshold:
                            logger.warning(
                                f"Performance degradation detected: "
                                f"{metric} {value:.3f} < {baseline:.3f}"
                            )
                            return True

        logger.info(f"Retraining triggered: drift_score={drift_score:.3f}, samples={samples_count}")
        return True

    def retrain(
        self,
        train_fn: Callable,
        train_data: Any,
        dataset_hash: Optional[str] = None,
        drift_score: Optional[float] = None,
    ) -> ModelVersion:
        """Execute retraining.

        Args:
            train_fn: Training function that returns (model, metrics)
            train_data: Training dataset
            dataset_hash: Hash of training dataset
            drift_score: Drift score that triggered retraining

        Returns:
            New model version
        """
        logger.info(f"Starting retraining for {self.model_name}")

        # Train model
        _model, metrics = train_fn(train_data)

        # Generate version
        version_num = len(self.registry.versions) + 1
        version_str = f"v{version_num}.0"

        # Save model
        model_path = Path(f"models/{self.model_name}/{version_str}/model.pt")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        # Note: Actual model saving would happen here
        # torch.save(model.state_dict(), model_path)

        # Create version
        new_version = ModelVersion(
            version=version_str,
            model_path=model_path,
            metrics=metrics,
            trained_at=datetime.now(UTC).isoformat(),
            dataset_hash=dataset_hash,
            drift_score=drift_score,
        )

        # Register
        self.registry.register(new_version)

        logger.info(f"Retraining complete: {version_str}, metrics={metrics}")
        return new_version

    def compare_models(
        self,
        new_version: ModelVersion,
        baseline_version: Optional[ModelVersion] = None,
        primary_metric: str = "accuracy",
    ) -> dict[str, Any]:
        """Compare two model versions.

        Args:
            new_version: New model version
            baseline_version: Baseline version (latest if None)
            primary_metric: Primary metric for comparison

        Returns:
            Comparison results
        """
        if baseline_version is None:
            # Get second-to-last version as baseline
            if len(self.registry.versions) >= 2:
                baseline_version = self.registry.versions[-2]
            else:
                logger.warning("No baseline version available for comparison")
                return {"is_better": True, "improvement": None}

        new_metric = new_version.metrics.get(primary_metric, 0.0)
        baseline_metric = baseline_version.metrics.get(primary_metric, 0.0)

        improvement = new_metric - baseline_metric
        is_better = improvement > -self.performance_degradation_threshold

        result = {
            "is_better": is_better,
            "improvement": improvement,
            "new_metric": new_metric,
            "baseline_metric": baseline_metric,
            "primary_metric": primary_metric,
        }

        logger.info(f"Model comparison: {result}")
        return result

    def deploy_model(self, version: ModelVersion):
        """Deploy a model version to production.

        Args:
            version: Model version to deploy
        """
        # In production, this would:
        # 1. Copy model to production location
        # 2. Update serving configuration
        # 3. Trigger model reload in serving infrastructure
        # 4. Update monitoring dashboards

        logger.info(f"Deploying model {version.version} to production")
        # Placeholder for actual deployment logic

    def rollback(self, to_version: Optional[str] = None):
        """Rollback to a previous model version.

        Args:
            to_version: Version to rollback to (previous if None)
        """
        if to_version:
            version = self.registry.get_by_version(to_version)
        else:
            # Rollback to previous version
            if len(self.registry.versions) >= 2:
                version = self.registry.versions[-2]
            else:
                logger.error("No previous version available for rollback")
                return

        if version:
            logger.warning(f"Rolling back to version {version.version}")
            self.deploy_model(version)
        else:
            logger.error(f"Version {to_version} not found in registry")
