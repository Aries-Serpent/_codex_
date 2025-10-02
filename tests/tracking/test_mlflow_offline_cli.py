from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from examples import mlflow_offline


def _stub_mlflow(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    dummy = ModuleType("mlflow")
    recorded: dict[str, Any] = {"set_tracking_uri": [], "set_experiment": []}

    def _set_tracking_uri(uri: str) -> None:
        recorded["set_tracking_uri"].append(uri)

    def _set_experiment(name: str) -> None:
        recorded["set_experiment"].append(name)

    dummy.set_tracking_uri = _set_tracking_uri  # type: ignore[attr-defined]
    dummy.set_experiment = _set_experiment  # type: ignore[attr-defined]
    dummy.start_run = lambda run_name=None: object()  # type: ignore[attr-defined]
    dummy.set_tags = lambda tags=None: None  # type: ignore[attr-defined]
    dummy.log_metric = lambda name, value, step: None  # type: ignore[attr-defined]
    dummy.end_run = lambda: None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlflow", dummy)
    return recorded


def test_smoke_cli_writes_metrics_and_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded = _stub_mlflow(monkeypatch)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)
    uri = mlflow_offline.run_smoke(tmp_path)
    assert uri.startswith("file:")
    assert recorded["set_tracking_uri"] and recorded["set_tracking_uri"][-1].startswith("file:")

    runs_dir = tmp_path / "runs"
    run_dirs = list(runs_dir.iterdir())
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    metrics_path = run_dir / "metrics.ndjson"
    summary_path = run_dir / "tracking_summary.ndjson"
    assert metrics_path.exists()
    assert summary_path.exists()

    metrics_payload = metrics_path.read_text(encoding="utf-8").strip().splitlines()
    assert metrics_payload, "expected metrics to be logged"

    summary = [json.loads(line) for line in summary_path.read_text(encoding="utf-8").splitlines()]
    assert summary and summary[-1]["component"] == "mlflow"
    extra = summary[-1]["extra"]
    assert extra["effective_uri"].startswith("file:")
    assert extra["allow_remote"] is False
    assert extra["system_metrics_enabled"] is False


def test_smoke_cli_blocks_remote_without_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_mlflow(monkeypatch)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)
    with pytest.raises(SystemExit):
        mlflow_offline.run_smoke(tmp_path, tracking_uri="https://remote.example")
