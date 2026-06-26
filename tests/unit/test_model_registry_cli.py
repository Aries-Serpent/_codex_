from __future__ import annotations

import importlib.util
import sys
import types
from argparse import Namespace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import pytest


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Repository root not found from test path"
    raise RuntimeError(msg)


def _load_registry_module():
    fake_mlflow_registry = types.ModuleType("codex_ml.registry.mlflow_registry")

    class _DeploymentStage(Enum):
        NONE = "None"
        STAGING = "Staging"
        PRODUCTION = "Production"
        ARCHIVED = "Archived"

    class _ModelRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

    fake_mlflow_registry._HAS_MLFLOW = True
    fake_mlflow_registry.DeploymentStage = _DeploymentStage
    fake_mlflow_registry.ModelRegistry = _ModelRegistry

    fake_registry_pkg = types.ModuleType("codex_ml.registry")
    fake_registry_pkg.__path__ = []  # Mark as package
    fake_registry_pkg.mlflow_registry = fake_mlflow_registry

    # Save previous sys.modules entries
    saved_registry = sys.modules.get("codex_ml.registry")
    saved_mlflow_registry = sys.modules.get("codex_ml.registry.mlflow_registry")

    try:
        sys.modules["codex_ml.registry"] = fake_registry_pkg
        sys.modules["codex_ml.registry.mlflow_registry"] = fake_mlflow_registry

        module_path = _repo_root() / "src" / "codex_ml" / "cli" / "registry.py"
        spec = importlib.util.spec_from_file_location(
            "codex_ml_cli_registry_under_test", module_path
        )
        assert spec is not None and spec.loader is not None, "spec must be initialized"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        # Restore previous sys.modules entries
        if saved_registry is not None:
            sys.modules["codex_ml.registry"] = saved_registry
        else:
            sys.modules.pop("codex_ml.registry", None)

        if saved_mlflow_registry is not None:
            sys.modules["codex_ml.registry.mlflow_registry"] = saved_mlflow_registry
        else:
            sys.modules.pop("codex_ml.registry.mlflow_registry", None)


class _FakeVersion:
    def __init__(
        self,
        version: str = "1",
        stage: object | None = None,
        created_at: datetime | None = None,
        description: str = "desc",
    ) -> None:
        if stage is None:
            stage = types.SimpleNamespace(value="Staging")
        self.version = version
        self.stage = stage
        self.created_at = created_at or datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.description = description

    def to_dict(self) -> dict[str, str]:
        return {
            "version": self.version,
            "stage": self.stage.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


def test_list_models_command_text(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def list_models(self) -> list[str]:
            return ["alpha", "beta"]

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.list_models_command(Namespace(tracking_uri="sqlite:///mlruns.db", json=False))
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert "Registered Models (2):" in out, "Condition must be true"
    assert "alpha" in out and "beta" in out, "Condition must be true"


def test_list_versions_command_json_uses_stage_filter(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()
    calls: list[object | None] = []

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def list_model_versions(self, name: str, stage: object | None = None) -> list[_FakeVersion]:
            assert name == "demo", "name is not valid"
            calls.append(stage)
            return [_FakeVersion(version="3", stage=registry.DeploymentStage.PRODUCTION)]

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.list_versions_command(
        Namespace(tracking_uri=None, stage="production", name="demo", json=True)
    )
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert '"versions"' in out and '"3"' in out, "Condition must be true"
    assert calls == [registry.DeploymentStage.PRODUCTION], "calls is not valid"


def test_promote_model_command_keep_existing_sets_archive_false(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()
    captured: dict[str, object] = {}

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def promote_model(
            self,
            name: str,
            version: str,
            stage: object,
            archive_existing: bool = True,
        ) -> _FakeVersion:
            captured.update(
                {
                    "name": name,
                    "version": version,
                    "stage": stage,
                    "archive_existing": archive_existing,
                }
            )
            return _FakeVersion(version=version, stage=stage)

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.promote_model_command(
        Namespace(
            tracking_uri=None,
            name="demo",
            version="9",
            stage="staging",
            keep_existing=True,
            json=False,
        )
    )
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert "Promoted demo version 9 to Staging" in out, "Condition must be true"
    assert captured["archive_existing"] is False, "Condition must be true"


def test_compare_models_command_text(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()
    comparison = {
        "version_1": {"stage": "Staging", "created_at": "2026-01-01T00:00:00+00:00"},
        "version_2": {"stage": "Production", "created_at": "2026-01-03T00:00:00+00:00"},
        "created_diff_days": 2,
    }

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def compare_models(self, name: str, version1: str, version2: str) -> dict[str, object]:
            assert (name, version1, version2) == ("demo", "1", "2")
            return comparison

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.compare_models_command(
        Namespace(tracking_uri=None, name="demo", version1="1", version2="2", json=False)
    )
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert "Version 1" in out and "Version 2" in out, "Condition must be true"
    assert "Time difference: 2 days" in out, "Condition must be true"


def test_get_lineage_command_no_lineage(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def get_model_lineage(self, name: str, version: str) -> dict[str, object]:
            assert (name, version) == ("demo", "4")
            return {"lineage": None}

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.get_lineage_command(
        Namespace(tracking_uri=None, name="demo", version="4", json=False)
    )
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert "No lineage information available" in out, "Condition must be true"


def test_export_model_command_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def export_model(self, name: str, version: str, output_dir: str) -> str:
            assert (name, version, output_dir) == ("demo", "4", "build/out")
            return "build/out/demo-v4"

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.export_model_command(
        Namespace(tracking_uri=None, name="demo", version="4", output_dir="build/out")
    )
    out = capsys.readouterr().out
    assert code == 0, "code is not valid"
    assert "Exported demo version 4 to build/out/demo-v4" in out, "Condition must be true"


def test_list_models_command_error_path(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    code = registry.list_models_command(Namespace(tracking_uri=None, json=False))
    err = capsys.readouterr().err
    assert code == 1, "code is not valid"
    assert "Error: boom" in err, "Error should be raised or set"


def test_main_returns_error_when_mlflow_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    registry = _load_registry_module()
    monkeypatch.setattr(registry, "_HAS_MLFLOW", False)
    code = registry.main(["list-models"])
    err = capsys.readouterr().err
    assert code == 1, "code is not valid"
    assert "MLflow not installed" in err, "Condition must be true"


def test_main_dispatch_list_models(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _load_registry_module()

    class _FakeRegistry:
        def __init__(self, tracking_uri: str | None = None) -> None:
            self.tracking_uri = tracking_uri

        def list_models(self) -> list[str]:
            return []

    monkeypatch.setattr(registry, "_HAS_MLFLOW", True)
    monkeypatch.setattr(registry, "ModelRegistry", _FakeRegistry)
    assert registry.main(["--json", "list-models"]) == 0
