"""Tests for the metric registry utilities."""

from __future__ import annotations

import sys
import types
import uuid
from importlib import import_module
from importlib.machinery import ModuleSpec
from pathlib import Path

import pytest


def _install_pydantic_stubs() -> None:
    try:
        import_module("pydantic")
    except ModuleNotFoundError:
        pydantic_module = types.ModuleType("pydantic")

        class _BaseModel:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

            @classmethod
            def model_json_schema(cls) -> dict:
                return {}

        def _field(**kwargs):  # type: ignore[no-untyped-def]
            return kwargs.get("default")

        pydantic_module.BaseModel = _BaseModel
        pydantic_module.Field = _field
        pydantic_module.__spec__ = ModuleSpec("pydantic", loader=None)
        sys.modules.setdefault("pydantic", pydantic_module)

    try:
        import_module("pydantic_settings")
    except ModuleNotFoundError:
        pydantic_settings_module = types.ModuleType("pydantic_settings")

        base_model = getattr(sys.modules.get("pydantic"), "BaseModel", object)

        class _BaseSettings(base_model):
            model_config = {}

        def _settings_config_dict(**kwargs):  # type: ignore[no-untyped-def]
            return dict(**kwargs)

        pydantic_settings_module.BaseSettings = _BaseSettings
        pydantic_settings_module.SettingsConfigDict = _settings_config_dict
        pydantic_settings_module.__spec__ = ModuleSpec("pydantic_settings", loader=None)
        sys.modules.setdefault("pydantic_settings", pydantic_settings_module)


_install_pydantic_stubs()

from codex_ml.eval.runner import _compute_metrics
from codex_ml.metrics import registry
from codex_ml.registry.base import RegistryConflictError


def _read_error_log(base_dir: Path) -> str:
    files = sorted(base_dir.glob("errors_*.md"))
    assert files, "expected an error log to be created"
    return files[-1].read_text(encoding="utf-8")


def test_register_and_get_metric_roundtrip(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_ERROR_REPORTS_DIR", str(tmp_path))
    metric_name = f"test-metric-{uuid.uuid4().hex}"

    def metric(predictions, targets):
        return float(len(predictions))

    registry.register(metric_name, metric)
    retrieved = registry.get(metric_name)
    assert retrieved is metric, "retrieved is not valid"
    assert metric_name in registry.list_metrics(), "Condition must be true"


def test_register_duplicate_logs_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_ERROR_REPORTS_DIR", str(tmp_path))
    metric_name = f"duplicate-metric-{uuid.uuid4().hex}"

    registry.register(metric_name, lambda preds, targs: 1.0)
    with pytest.raises(RegistryConflictError):
        registry.register(metric_name, lambda preds, targs: 0.0)

    log_contents = _read_error_log(tmp_path)
    assert metric_name in log_contents, "Content must not be empty"
    assert "metric.register" in log_contents, "Content must not be empty"


def test_compute_metrics_uses_registry_metric(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_ERROR_REPORTS_DIR", str(tmp_path))
    metric_name = f"integration-metric-{uuid.uuid4().hex}"

    def integration_metric(predictions, targets):
        return {
            "total": float(len(predictions)),
            "matches": float(sum(int(p == t) for p, t in zip(predictions, targets))),
        }

    with registry.metric_registry.temporarily_registered({metric_name: integration_metric}):
        records = [
            {"prediction": 1, "target": 1},
            {"prediction": 0, "target": 1},
            {"prediction": 2, "target": 2},
        ]
        results = _compute_metrics(records, [metric_name])

    assert metric_name in results, "Result must not be empty"
    assert results[metric_name]["total"] == 3.0, "Result must not be empty"
    assert results[metric_name]["matches"] == 2.0, "Result must not be empty"
