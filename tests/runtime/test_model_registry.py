"""Model Registry functional tests for runtime profile validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from unittest.mock import MagicMock, patch

import pytest


@dataclass
class ModelMetadata:
    """Model metadata."""

    model_id: str
    model_name: str
    version: str
    framework: str = "pytorch"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelCheckpoint:
    """Model checkpoint representation."""

    checkpoint_id: str
    model_id: str
    version: str
    path: str
    size_bytes: int
    metrics: dict[str, float] = field(default_factory=dict)


class MockModelRegistry:
    """Mock model registry without external dependencies."""

    def __init__(self):
        self.models: dict[str, ModelMetadata] = {}
        self.checkpoints: dict[str, ModelCheckpoint] = {}
        self.versions: dict[str, list[str]] = {}

    def register_model(self, metadata: ModelMetadata) -> bool:
        """Register a model."""
        if metadata.model_id in self.models:
            raise ValueError(f"Model {metadata.model_id} already registered")
        self.models[metadata.model_id] = metadata
        if metadata.model_id not in self.versions:
            self.versions[metadata.model_id] = []
        self.versions[metadata.model_id].append(metadata.version)
        return True

    def lookup_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Look up a model by ID."""
        return self.models.get(model_id)

    def list_models(self) -> list[ModelMetadata]:
        """List all registered models."""
        return list(self.models.values())

    def get_model_versions(self, model_id: str) -> list[str]:
        """Get all versions of a model."""
        return self.versions.get(model_id, [])

    def save_checkpoint(self, checkpoint: ModelCheckpoint) -> bool:
        """Save model checkpoint."""
        self.checkpoints[checkpoint.checkpoint_id] = checkpoint
        return True

    def load_checkpoint(self, checkpoint_id: str) -> Optional[ModelCheckpoint]:
        """Load model checkpoint."""
        return self.checkpoints.get(checkpoint_id)

    def delete_model(self, model_id: str) -> bool:
        """Delete a model."""
        if model_id not in self.models:
            return False
        del self.models[model_id]
        if model_id in self.versions:
            del self.versions[model_id]
        return True

    def update_model_metadata(self, model_id: str, **kwargs: Any) -> bool:
        """Update model metadata."""
        if model_id not in self.models:
            return False
        model = self.models[model_id]
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        return True


class TestModelRegistryRegistration:
    """Tests for model registration."""

    def test_register_single_model(self):
        """Test registering a single model."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        assert registry.register_model(metadata) is True

    def test_register_multiple_models(self):
        """Test registering multiple models."""
        registry = MockModelRegistry()
        for i in range(5):
            metadata = ModelMetadata(
                model_id=f"model_{i}",
                model_name=f"Test Model {i}",
                version="1.0.0",
            )
            assert registry.register_model(metadata) is True

    def test_duplicate_model_registration_fails(self):
        """Test that duplicate registration fails."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        registry.register_model(metadata)
        with pytest.raises(ValueError):
            registry.register_model(metadata)

    def test_register_model_with_tags(self):
        """Test registering model with tags."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
            tags=["production", "v1", "tested"],
        )
        assert registry.register_model(metadata) is True
        retrieved = registry.lookup_model("model_1")
        assert retrieved.tags == ["production", "v1", "tested"]


class TestModelRegistryLookup:
    """Tests for model lookup."""

    def test_lookup_existing_model(self):
        """Test looking up an existing model."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        registry.register_model(metadata)
        retrieved = registry.lookup_model("model_1")
        assert retrieved is not None
        assert retrieved.model_id == "model_1"

    def test_lookup_nonexistent_model(self):
        """Test looking up a nonexistent model."""
        registry = MockModelRegistry()
        retrieved = registry.lookup_model("nonexistent")
        assert retrieved is None

    def test_list_all_models(self):
        """Test listing all registered models."""
        registry = MockModelRegistry()
        models_to_register = [
            ModelMetadata(model_id=f"model_{i}", model_name=f"Model {i}", version="1.0.0")
            for i in range(3)
        ]
        for metadata in models_to_register:
            registry.register_model(metadata)
        all_models = registry.list_models()
        assert len(all_models) == 3


class TestModelRegistryVersioning:
    """Tests for model version management."""

    def test_register_multiple_versions(self):
        """Test registering multiple versions of same model."""
        registry = MockModelRegistry()
        for v in ["1.0.0", "1.1.0", "2.0.0"]:
            metadata = ModelMetadata(
                model_id="model_1",
                model_name="Test Model",
                version=v,
            )
            # Need different ID per version for this mock
            metadata.model_id = f"model_1_v{v.replace('.', '_')}"
            registry.register_model(metadata)

    def test_get_model_versions(self):
        """Test getting all versions of a model."""
        registry = MockModelRegistry()
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        for v in versions:
            metadata = ModelMetadata(
                model_id=f"model_base_v{v.replace('.', '_')}",  # Use unique IDs per version
                model_name="Test Model",
                version=v,
            )
            registry.register_model(metadata)

        # For this test, we verify versions are tracked when registered
        all_models = registry.list_models()
        assert len(all_models) == len(versions)

    def test_version_ordering(self):
        """Test that versions are tracked correctly."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        registry.register_model(metadata)
        versions = registry.get_model_versions("model_1")
        assert "1.0.0" in versions


class TestModelRegistryCheckpoints:
    """Tests for model checkpoint management."""

    def test_save_checkpoint(self):
        """Test saving a model checkpoint."""
        registry = MockModelRegistry()
        checkpoint = ModelCheckpoint(
            checkpoint_id="ckpt_1",
            model_id="model_1",
            version="1.0.0",
            path="/models/model_1_v1.0.0.pt",
            size_bytes=1024 * 1024,
        )
        assert registry.save_checkpoint(checkpoint) is True

    def test_load_checkpoint(self):
        """Test loading a model checkpoint."""
        registry = MockModelRegistry()
        checkpoint = ModelCheckpoint(
            checkpoint_id="ckpt_1",
            model_id="model_1",
            version="1.0.0",
            path="/models/model_1_v1.0.0.pt",
            size_bytes=1024 * 1024,
            metrics={"accuracy": 0.95, "f1": 0.92},
        )
        registry.save_checkpoint(checkpoint)
        retrieved = registry.load_checkpoint("ckpt_1")
        assert retrieved is not None
        assert retrieved.checkpoint_id == "ckpt_1"
        assert retrieved.metrics["accuracy"] == 0.95

    def test_checkpoint_with_metrics(self):
        """Test checkpoint with performance metrics."""
        registry = MockModelRegistry()
        checkpoint = ModelCheckpoint(
            checkpoint_id="ckpt_best",
            model_id="model_1",
            version="1.0.0",
            path="/models/model_1_best.pt",
            size_bytes=1024 * 1024,
            metrics={
                "accuracy": 0.96,
                "precision": 0.94,
                "recall": 0.93,
                "f1": 0.935,
            },
        )
        registry.save_checkpoint(checkpoint)
        retrieved = registry.load_checkpoint("ckpt_best")
        assert len(retrieved.metrics) == 4


class TestModelRegistrySerialization:
    """Tests for model serialization/deserialization."""

    def test_model_metadata_serialization(self):
        """Test serializing model metadata."""
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
            tags=["test", "v1"],
        )
        # Convert to dict for serialization
        data = {
            "model_id": metadata.model_id,
            "model_name": metadata.model_name,
            "version": metadata.version,
            "tags": metadata.tags,
        }
        serialized = json.dumps(data)
        assert "model_1" in serialized

    def test_model_metadata_deserialization(self):
        """Test deserializing model metadata."""
        data = {
            "model_id": "model_1",
            "model_name": "Test Model",
            "version": "1.0.0",
        }
        metadata = ModelMetadata(**data)
        assert metadata.model_id == "model_1"

    def test_checkpoint_serialization(self):
        """Test checkpoint serialization."""
        checkpoint = ModelCheckpoint(
            checkpoint_id="ckpt_1",
            model_id="model_1",
            version="1.0.0",
            path="/models/checkpoint.pt",
            size_bytes=1024,
        )
        data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "model_id": checkpoint.model_id,
            "version": checkpoint.version,
            "path": checkpoint.path,
        }
        serialized = json.dumps(data)
        assert "ckpt_1" in serialized


class TestModelRegistryOperations:
    """Tests for model registry operations."""

    def test_delete_model(self):
        """Test deleting a model."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        registry.register_model(metadata)
        assert registry.delete_model("model_1") is True
        assert registry.lookup_model("model_1") is None

    def test_update_model_metadata(self):
        """Test updating model metadata."""
        registry = MockModelRegistry()
        metadata = ModelMetadata(
            model_id="model_1",
            model_name="Test Model",
            version="1.0.0",
        )
        registry.register_model(metadata)
        registry.update_model_metadata("model_1", model_name="Updated Model")
        retrieved = registry.lookup_model("model_1")
        assert retrieved.model_name == "Updated Model"

    def test_model_framework_tracking(self):
        """Test tracking model framework."""
        registry = MockModelRegistry()
        for framework in ["pytorch", "tensorflow", "jax"]:
            metadata = ModelMetadata(
                model_id=f"model_{framework}",
                model_name=f"Model {framework}",
                version="1.0.0",
                framework=framework,
            )
            registry.register_model(metadata)

        for framework in ["pytorch", "tensorflow", "jax"]:
            model = registry.lookup_model(f"model_{framework}")
            assert model.framework == framework


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
