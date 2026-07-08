"""
MLflow Model Registry Integration

Provides centralized model versioning, lineage tracking, and deployment
stage management using MLflow Model Registry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

# Optional MLflow dependency
try:
    import mlflow

    MlflowClient = mlflow.tracking.MlflowClient

    _HAS_MLFLOW = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    _HAS_MLFLOW = False
    mlflow = None
    MlflowClient = None


class DeploymentStage(Enum):
    """Model deployment stages"""

    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


@dataclass
class ModelVersion:
    """Model version information"""

    name: str
    version: str
    stage: DeploymentStage
    description: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    run_id: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "stage": self.stage.value,
            "description": self.description,
            "tags": self.tags,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "run_id": self.run_id,
            "source": self.source,
        }


class ModelRegistry:
    """
    MLflow Model Registry integration for centralized model management.

    Provides model versioning, lineage tracking, and deployment stage management.
    """

    def __init__(self, tracking_uri: Optional[str] = None):
        """Initialize model registry

        Args:
            tracking_uri: MLflow tracking URI (defaults to MLFLOW_TRACKING_URI env var)
        """
        if not _HAS_MLFLOW:
            raise RuntimeError("MLflow not installed. Install with: pip install mlflow")

        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

        self.client = MlflowClient()
        logger.info(f"Initialized ModelRegistry with URI: {mlflow.get_tracking_uri()}")

    def register_model(
        self,
        model_uri: str,
        name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None,
    ) -> ModelVersion:
        """Register a new model or create a new version

        Args:
            model_uri: URI to model artifact (e.g., runs:/<run_id>/model)
            name: Model name
            description: Model description
            tags: Optional tags

        Returns:
            ModelVersion with registration details
        """
        try:
            # Register model (creates new version if model exists)
            result = mlflow.register_model(model_uri, name)

            # Add description
            if description:
                self.client.update_model_version(
                    name=name, version=result.version, description=description
                )

            # Add tags
            if tags:
                for key, value in tags.items():
                    self.client.set_model_version_tag(
                        name=name, version=result.version, key=key, value=value
                    )

            logger.info(f"Registered model {name} version {result.version}")

            return self.get_model_version(name, result.version)

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to register model {name}: <ERROR_TYPE>")
            raise

    def get_model_version(self, name: str, version: str) -> ModelVersion:
        """Get specific model version

        Args:
            name: Model name
            version: Version number

        Returns:
            ModelVersion details
        """
        try:
            mv = self.client.get_model_version(name=name, version=version)

            return ModelVersion(
                name=mv.name,
                version=mv.version,
                stage=DeploymentStage(mv.current_stage),
                description=mv.description or "",
                tags=mv.tags or {},
                metrics={},  # Metrics from run would need separate lookup
                created_at=datetime.fromtimestamp(mv.creation_timestamp / 1000),
                updated_at=datetime.fromtimestamp(mv.last_updated_timestamp / 1000),
                run_id=mv.run_id,
                source=mv.source,
            )
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to get model version {name}/{version}: <ERROR_TYPE>")
            raise

    def list_model_versions(
        self, name: str, stage: Optional[DeploymentStage] = None
    ) -> list[ModelVersion]:
        """list all versions of a model

        Args:
            name: Model name
            stage: Optional stage filter

        Returns:
            list of ModelVersions
        """
        try:
            filter_string = f"name='{name}'"
            if stage:
                filter_string += f" AND current_stage='{stage.value}'"

            versions = self.client.search_model_versions(filter_string)

            return [
                ModelVersion(
                    name=mv.name,
                    version=mv.version,
                    stage=DeploymentStage(mv.current_stage),
                    description=mv.description or "",
                    tags=mv.tags or {},
                    metrics={},
                    created_at=datetime.fromtimestamp(mv.creation_timestamp / 1000),
                    updated_at=datetime.fromtimestamp(mv.last_updated_timestamp / 1000),
                    run_id=mv.run_id,
                    source=mv.source,
                )
                for mv in versions
            ]
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to list model versions for {name}: <ERROR_TYPE>")
            raise

    def promote_model(
        self,
        name: str,
        version: str,
        stage: DeploymentStage,
        archive_existing: bool = True,
    ) -> ModelVersion:
        """Promote model to a deployment stage

        Args:
            name: Model name
            version: Version to promote
            stage: Target deployment stage
            archive_existing: Archive existing models in target stage

        Returns:
            Updated ModelVersion
        """
        try:
            self.client.transition_model_version_stage(
                name=name,
                version=version,
                stage=stage.value,
                archive_existing_versions=archive_existing,
            )

            logger.info(f"Promoted model {name} version {version} to {stage.value}")

            return self.get_model_version(name, version)
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to promote model {name}/{version} to {stage.value}: <ERROR_TYPE>")
            raise

    def archive_model(self, name: str, version: str) -> ModelVersion:
        """Archive a model version

        Args:
            name: Model name
            version: Version to archive

        Returns:
            Updated ModelVersion
        """
        return self.promote_model(name, version, DeploymentStage.ARCHIVED, archive_existing=False)

    def delete_model_version(self, name: str, version: str) -> None:
        """Delete a model version

        Args:
            name: Model name
            version: Version to delete
        """
        try:
            self.client.delete_model_version(name=name, version=version)
            logger.info(f"Deleted model {name} version {version}")
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to delete model {name}/{version}: <ERROR_TYPE>")
            raise

    def get_latest_version(
        self, name: str, stage: Optional[DeploymentStage] = None
    ) -> Optional[ModelVersion]:
        """Get latest model version

        Args:
            name: Model name
            stage: Optional stage filter

        Returns:
            Latest ModelVersion or None
        """
        versions = self.list_model_versions(name, stage)
        if not versions:
            return None

        # Sort by version number (descending)
        versions.sort(key=lambda v: int(v.version), reverse=True)
        return versions[0]

    def compare_models(self, name: str, version1: str, version2: str) -> dict[str, Any]:
        """Compare two model versions

        Args:
            name: Model name
            version1: First version
            version2: Second version

        Returns:
            Comparison dictionary
        """
        try:
            mv1 = self.get_model_version(name, version1)
            mv2 = self.get_model_version(name, version2)

            return {
                "model_name": name,
                "version_1": mv1.to_dict(),
                "version_2": mv2.to_dict(),
                "stage_diff": mv1.stage.value != mv2.stage.value,
                "created_diff_days": (
                    (mv2.created_at - mv1.created_at).days
                    if mv1.created_at and mv2.created_at
                    else None
                ),
            }
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to compare models {name}/{version1} vs {version2}: <ERROR_TYPE>")
            raise

    def get_model_lineage(self, name: str, version: str) -> dict[str, Any]:
        """Get model lineage information

        Args:
            name: Model name
            version: Model version

        Returns:
            Lineage information including run details
        """
        try:
            mv = self.get_model_version(name, version)

            if not mv.run_id:
                return {"model": mv.to_dict(), "lineage": None}

            # Get run information
            run = self.client.get_run(mv.run_id)

            lineage = {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "start_time": datetime.fromtimestamp(run.info.start_time / 1000),
                "end_time": (
                    datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None
                ),
                "status": run.info.status,
                "parameters": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags,
            }

            return {"model": mv.to_dict(), "lineage": lineage}
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to get model lineage for {name}/{version}: <ERROR_TYPE>")
            raise

    def list_models(self) -> list[str]:
        """list all registered model names

        Returns:
            list of model names
        """
        try:
            models = self.client.search_registered_models()
            return [model.name for model in models]
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to list models: <ERROR_TYPE>")
            raise

    def export_model(self, name: str, version: str, output_dir: str) -> Path:
        """Export model version to local directory

        Args:
            name: Model name
            version: Model version
            output_dir: Output directory path

        Returns:
            Path to exported model
        """
        try:
            mv = self.get_model_version(name, version)

            if not mv.source:
                raise ValueError(f"Model {name}/{version} has no source URI")

            output_path = Path(output_dir) / f"{name}-v{version}"
            output_path.mkdir(parents=True, exist_ok=True)

            # Download model artifacts
            model_uri = f"models:/{name}/{version}"
            mlflow.pyfunc.load_model(model_uri)

            logger.info(f"Exported model {name}/{version} to {output_path}")
            return output_path
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to export model {name}/{version}: <ERROR_TYPE>")
            raise


def get_default_registry(tracking_uri: Optional[str] = None) -> ModelRegistry:
    """Get default model registry instance

    Args:
        tracking_uri: Optional MLflow tracking URI

    Returns:
        ModelRegistry instance
    """
    return ModelRegistry(tracking_uri=tracking_uri)


if __name__ == "__main__":
    # Example usage
    if _HAS_MLFLOW:
        registry = ModelRegistry()

        # list models
        models = registry.list_models()
        logger.info(f"Registered models: {models}")

        # Example: Register a model (requires existing run)
        # model_version = registry.register_model(
        #     model_uri="runs:/<run_id>/model",
        #     name="my_model",
        #     description="Example model",
        #     tags={"env": "dev"}
        # )
    else:
        logger.info("MLflow not installed. Install with: pip install mlflow")
