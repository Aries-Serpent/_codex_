from __future__ import annotations

import importlib
import json
import os
import sys
import types
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest


def _install_stub_mlflow(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("mlflow")

    class _DummyRun:
        def __enter__(self):  # pragma: no cover - trivial
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
            return False

    def set_tracking_uri(uri: str) -> None:
        module.tracking_uri = uri

    def set_experiment(name: str) -> None:
        module.experiment = name

    def start_run(run_name: str | None = None):
        module.run_name = run_name
        return _DummyRun()

    def set_tags(tags):
        module.tags = dict(tags)

    def log_metric(name: str, value: float, step: int) -> None:
        metrics = getattr(module, "metrics", [])
        metrics.append((name, value, step))
        module.metrics = metrics

    def log_params(params):
        module.params = dict(params)

    def log_artifact(path: str) -> None:
        module.artifact = path

    def log_artifacts(path: str) -> None:  # pragma: no cover - compatibility
        module.artifacts_path = path

    def end_run() -> None:  # pragma: no cover - trivial
        module.ended = True

    module.set_tracking_uri = set_tracking_uri
    module.set_experiment = set_experiment
    module.start_run = start_run
    module.set_tags = set_tags
    module.log_metric = log_metric
    module.log_params = log_params
    module.log_artifact = log_artifact
    module.log_artifacts = log_artifacts
    module.end_run = end_run

    monkeypatch.setitem(sys.modules, "mlflow", module)
    return module


def _reload_guard() -> types.ModuleType:
    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    return importlib.reload(guard)


def _reload_writers() -> types.ModuleType:
    writers = importlib.import_module("codex_ml.tracking.writers")
    return importlib.reload(writers)


def _load_summary(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_ensure_file_backend_sets_local_uri(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = _reload_guard()

    decision = guard.ensure_file_backend_decision()
    uri = decision.effective_uri
    parsed = urlparse(uri)
    assert parsed.scheme == "file"
    path = Path(parsed.path)
    assert path.name == "mlruns"
    assert path.exists()
    assert os.environ.get("MLFLOW_TRACKING_URI") == uri
    assert os.environ.get("CODEX_MLFLOW_URI") == uri
    assert decision.system_metrics_enabled is False


def test_plain_paths_are_normalised_to_file_uri(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", str(tmp_path / "plain_runs"))
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = _reload_guard()

    decision = guard.ensure_file_backend_decision()
    uri = decision.effective_uri
    parsed = urlparse(uri)
    assert parsed.scheme == "file"
    assert os.environ["MLFLOW_TRACKING_URI"] == uri
    assert os.environ["CODEX_MLFLOW_URI"] == uri
    path = Path(parsed.path)
    assert path.name == "plain_runs"
    assert path.exists()


def test_bootstrap_blocks_remote_by_default(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://example.com/mlflow")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    guard = _reload_guard()

    decision = guard.bootstrap_offline_tracking_decision()
    parsed = urlparse(decision.effective_uri)
    assert parsed.scheme == "file"
    assert urlparse(os.environ["MLFLOW_TRACKING_URI"]).scheme == "file"
    assert urlparse(os.environ["CODEX_MLFLOW_URI"]).scheme == "file"
    assert decision.fallback_reason in {"non_file_scheme", "non_local_host"}


def test_bootstrap_respects_allow_remote(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://remote.example/mlflow")
    monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", "1")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = _reload_guard()

    decision = guard.bootstrap_offline_tracking_decision()
    assert decision.effective_uri == "https://remote.example/mlflow"
    assert os.environ["MLFLOW_TRACKING_URI"] == decision.effective_uri
    assert decision.allow_remote is True


def test_summary_records_fallback_reason_when_downgraded(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "local"))
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    _install_stub_mlflow(monkeypatch)
    _reload_guard()
    writers = _reload_writers()
    writers._reset_summary_rotation_state_for_tests()

    summary_path = tmp_path / "tracking_summary.ndjson"
    writer = writers.MLflowWriter(
        "https://example.com/mlflow",
        "offline-smoke",
        "run-id",
        {},
        summary_path=summary_path,
    )
    writer.close()

    lines = [json.loads(line) for line in summary_path.read_text().splitlines() if line]
    assert lines, "summary should contain at least one record"
    extra = lines[-1]["extra"]
    assert extra["requested_uri"] == "https://example.com/mlflow"
    assert extra["effective_uri"].startswith("file:///")
    assert extra["fallback_reason"] == "non_local_uri"
    assert extra["allow_remote_flag"] == ""
    assert extra["allow_remote"] is False
    assert extra["system_metrics_enabled"] is False


def test_summary_records_allow_remote_and_uri_passthrough(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "local"))
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://remote.example/mlflow")
    monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", "1")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    _install_stub_mlflow(monkeypatch)
    _reload_guard()
    writers = _reload_writers()
    writers._reset_summary_rotation_state_for_tests()

    summary_path = tmp_path / "tracking_summary.ndjson"
    writer = writers.MLflowWriter(
        "https://remote.example/mlflow",
        "offline-smoke",
        "run-id",
        {},
        summary_path=summary_path,
    )
    writer.close()

    lines = [json.loads(line) for line in summary_path.read_text().splitlines() if line]
    assert lines, "summary should contain at least one record"
    extra = lines[-1]["extra"]
    assert extra["requested_uri"] == "https://remote.example/mlflow"
    assert extra["effective_uri"] == "https://remote.example/mlflow"
    assert extra["fallback_reason"] == ""
    assert extra["allow_remote_flag"] == "1"
    assert extra["allow_remote"] is True
    assert extra["system_metrics_enabled"] is False
