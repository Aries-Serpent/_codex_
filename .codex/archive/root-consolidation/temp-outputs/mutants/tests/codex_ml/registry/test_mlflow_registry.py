"""
Test Mlflow Registry

Test module for mlflow registry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from codex_ml.registry import mlflow_registry


def _setup_dummy_mlflow(monkeypatch):
    events: list[str] = []

    class DummyModelVersion:
        def __init__(self, name: str, version: str, stage: str = "None") -> None:
            self.name = name
            self.version = version
            self.current_stage = stage
            self.description = "desc"
            self.tags = {"tag": "value"}
            now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            self.creation_timestamp = now_ms
            self.last_updated_timestamp = now_ms
            self.run_id = "run-1"
            self.source = "runs:/run-1/model"

    class DummyClient:
        def __init__(self) -> None:
            self.updated = []
            self.tags = []

        def update_model_version(self, name: str, version: str, description: str):
            self.updated.append((name, version, description))

        def set_model_version_tag(self, name: str, version: str, key: str, value: str):
            self.tags.append((name, version, key, value))

        def get_model_version(self, name: str, version: str):
            return DummyModelVersion(name, version)

        def search_model_versions(self, _filter: str):
            return [DummyModelVersion("demo", "1", stage="Staging")]

    class DummyMlflow:
        def __init__(self) -> None:
            self.tracking_uri = None

        def set_tracking_uri(self, uri: str):
            self.tracking_uri = uri
            events.append(f"set_uri:{uri}")

        def get_tracking_uri(self):
            return self.tracking_uri or "file:///tmp"

        def register_model(self, model_uri: str, name: str):
            events.append(f"register:{model_uri}:{name}")
            return SimpleNamespace(version="1")

    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(mlflow_registry, "mlflow", dummy_mlflow)
    monkeypatch.setattr(mlflow_registry, "MlflowClient", DummyClient)
    monkeypatch.setattr(mlflow_registry, "_HAS_MLFLOW", True)
    return dummy_mlflow, events


def test_model_registry_registers_and_lists_models(monkeypatch):
    _dummy_mlflow, events = _setup_dummy_mlflow(monkeypatch)
    registry = mlflow_registry.ModelRegistry(tracking_uri="file:///tmp/mlruns")

    model_version = registry.register_model(
        model_uri="runs:/run-123/model", name="demo", description="test", tags={"stage": "dev"}
    )

    assert model_version.name == "demo", "name is not valid"
    assert model_version.version == "1", "version is not valid"
    assert model_version.stage.value in {"None", "Staging", "Production", "Archived"}
    assert ("register:runs:/run-123/model:demo") in events, "Condition must be true"

    retrieved = registry.get_model_version("demo", "1")
    assert retrieved.name == "demo", "name is not valid"

    versions = registry.list_model_versions("demo")
    assert versions and versions[0].name == "demo", "name is not valid"


def test_model_registry_requires_mlflow(monkeypatch):
    monkeypatch.setattr(mlflow_registry, "_HAS_MLFLOW", False)
    with pytest.raises(RuntimeError):
        mlflow_registry.ModelRegistry()
