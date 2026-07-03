"""
Test Mlflow Guard

Test module for mlflow guard.
"""

from __future__ import annotations

import tempfile
import types
from unittest import mock

import pytest

from codex_ml.logging import mlflow_guard


def test_offline_mode_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_OFFLINE_MODE", "1")
    assert not mlflow_guard.init_mlflow_safe(), "Condition must be true"


def test_init_mlflow_success(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_mlflow = types.SimpleNamespace(
        active_run=lambda: None,
        set_tracking_uri=lambda uri: uri,
        start_run=lambda: None,
        log_metric=lambda *args, **kwargs: None,
        log_params=lambda *args, **kwargs: None,
        log_artifact=lambda *args, **kwargs: None,
    )
    with mock.patch.dict("sys.modules", {"mlflow": stub_mlflow}):
        monkeypatch.setattr(mlflow_guard, "mlflow", stub_mlflow, raising=False)
        assert mlflow_guard.init_mlflow_safe(offline_mode=False), "Condition must be true"
        mlflow_guard.log_metric_safe("loss", 0.1, step=1)
        mlflow_guard.log_params_safe({"lr": 1e-3})
        mlflow_guard.log_artifact_safe(os.path.join(tempfile.gettempdir(), "path"))


def test_init_mlflow_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    failing_mlflow = types.SimpleNamespace(
        active_run=lambda: None,
        set_tracking_uri=lambda uri: (_ for _ in ()).throw(RuntimeError("boom")),
        start_run=lambda: None,
    )
    with mock.patch.dict("sys.modules", {"mlflow": failing_mlflow}):
        monkeypatch.setattr(mlflow_guard, "mlflow", failing_mlflow, raising=False)
        assert not mlflow_guard.init_mlflow_safe(offline_mode=False), "Condition must be true"
