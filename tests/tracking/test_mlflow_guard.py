from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.parse import urlparse


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

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.ensure_file_backend()
    assert uri.startswith("file:")
    path = Path(urlparse(uri).path)
    assert path.exists()
    assert os.environ.get("MLFLOW_TRACKING_URI") == uri
    assert os.environ.get("CODEX_MLFLOW_URI") == uri


def test_plain_paths_are_normalised_to_file_uri(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", str(tmp_path / "plain_runs"))
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.ensure_file_backend()
    assert uri.startswith("file:")
    assert os.environ["MLFLOW_TRACKING_URI"] == uri
    assert os.environ["CODEX_MLFLOW_URI"] == uri
    path = Path(urlparse(uri).path)
    assert path.exists()


def test_bootstrap_blocks_remote_by_default(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://example.com/mlflow")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.bootstrap_offline_tracking()
    assert uri.startswith("file:")
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
    assert os.environ["CODEX_MLFLOW_URI"].startswith("file:")


def test_bootstrap_respects_allow_remote(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://remote.example/mlflow")
    monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", "1")
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    guard = importlib.import_module("codex_ml.tracking.mlflow_guard")
    importlib.reload(guard)

    uri = guard.bootstrap_offline_tracking()
    assert uri == "https://remote.example/mlflow"
    assert os.environ["MLFLOW_TRACKING_URI"] == uri


def test_summary_records_fallback_reason_when_downgraded(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_ALLOW_REMOTE", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)

    dummy = ModuleType("mlflow")
    recorded: dict[str, Any] = {}

    def _set_tracking_uri(uri: str) -> None:
        recorded["uri"] = uri

    dummy.set_tracking_uri = _set_tracking_uri  # type: ignore[attr-defined]
    dummy.set_experiment = lambda name: None  # type: ignore[attr-defined]
    dummy.start_run = lambda run_name=None: object()  # type: ignore[attr-defined]
    dummy.set_tags = lambda tags=None: None  # type: ignore[attr-defined]
    dummy.log_metric = lambda name, value, step: None  # type: ignore[attr-defined]
    dummy.end_run = lambda: None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlflow", dummy)

    summary_path = tmp_path / "tracking_summary.ndjson"
    from codex_ml.tracking.writers import MLflowWriter

    writer = MLflowWriter(
        "https://example.invalid/mlflow",
        "exp",
        "run",
        {},
        summary_path=summary_path,
    )
    writer.log({"metric": "loss", "value": 0.1, "step": 1})
    writer.close()

    summary = _load_summary(summary_path)
    assert summary, "expected summary record"
    extra = summary[-1]["extra"]
    assert extra["requested_uri"] == "https://example.invalid/mlflow"
    assert extra["effective_uri"].startswith("file:")
    assert extra["tracking_uri"].startswith("file:")
    assert extra["fallback_reason"] == "remote_disallowed"
    assert extra["allow_remote"] is False
    assert extra["allow_remote_flag"] == ""
    assert extra["system_metrics_enabled"] is False
    assert recorded["uri"].startswith("file:")


def test_summary_records_allow_remote_and_uri_passthrough(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", "1")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "https://remote.mlflow")
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))

    dummy = ModuleType("mlflow")

    def _noop(*args, **kwargs):
        return None

    dummy.set_tracking_uri = lambda uri: None  # type: ignore[attr-defined]
    dummy.set_experiment = _noop  # type: ignore[attr-defined]
    dummy.start_run = lambda run_name=None: object()  # type: ignore[attr-defined]
    dummy.set_tags = _noop  # type: ignore[attr-defined]
    dummy.log_metric = _noop  # type: ignore[attr-defined]
    dummy.end_run = _noop  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlflow", dummy)

    summary_path = tmp_path / "tracking_summary.ndjson"
    from codex_ml.tracking.writers import MLflowWriter

    writer = MLflowWriter(
        "https://remote.mlflow",
        "exp",
        "run",
        {},
        summary_path=summary_path,
    )
    writer.close()

    summary = _load_summary(summary_path)
    assert summary, "expected summary record"
    extra = summary[-1]["extra"]
    assert extra["requested_uri"] == "https://remote.mlflow"
    assert extra["effective_uri"] == "https://remote.mlflow"
    assert extra["fallback_reason"] == ""
    assert extra["allow_remote"] is True
    assert extra["allow_remote_flag"] in {"1", "true", "yes", "on"}
    assert extra["allow_remote_env"] == "MLFLOW_ALLOW_REMOTE"
