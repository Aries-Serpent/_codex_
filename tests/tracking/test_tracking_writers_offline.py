import builtins
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from codex_ml.logging.run_logger import RunLogger
from codex_ml.tracking.writers import MLflowWriter, NdjsonWriter, TensorBoardWriter, WandbWriter


@pytest.fixture
def summary_path(tmp_path: Path) -> Path:
    return tmp_path / "tracking_summary.ndjson"


def _load_summary(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_ndjson_writer_is_deterministic(tmp_path: Path) -> None:
    writer = NdjsonWriter(tmp_path / "metrics.ndjson")
    row = {
        "timestamp": "2024-01-01T00:00:00Z",
        "run_id": "run-1",
        "step": 2,
        "split": "eval",
        "metric": "loss",
        "value": 0.5,
        "dataset": Path("data/train"),
        "tags": {"b": 2, "a": 1},
    }
    writer.log(row)
    payload = (tmp_path / "metrics.ndjson").read_text(encoding="utf-8").strip()
    expected = (
        '{"$schema":"https://codexml.ai/schemas/run_metrics.schema.json","schema_version":"v1",'
        '"timestamp":"2024-01-01T00:00:00Z","run_id":"run-1","step":2,"split":"eval","metric":"loss",'
        '"value":0.5,"dataset":"data/train","tags":{"a":1,"b":2}}'
    )
    assert payload == expected


def test_ndjson_writer_injects_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    writer = NdjsonWriter(tmp_path / "metrics.ndjson")
    fake_now = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    class _FakeDateTime:
        @staticmethod
        def now(tz: timezone) -> datetime:  # type: ignore[override]
            assert tz is timezone.utc
            return fake_now

    monkeypatch.setattr("codex_ml.tracking.writers.datetime", _FakeDateTime)
    writer._logger.run_id = "auto-run"
    writer.log(
        {
            "step": 1,
            "split": "train",
            "metric": "loss",
            "value": 1.0,
            "dataset": None,
            "tags": {},
        }
    )
    payload = json.loads((tmp_path / "metrics.ndjson").read_text(encoding="utf-8").strip())
    assert payload["run_id"] == "auto-run"
    assert payload["timestamp"] == "2024-01-02T03:04:05Z"


def test_tensorboard_writer_emits_offline_summary(
    tmp_path: Path, summary_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delitem(sys.modules, "torch", raising=False)
    monkeypatch.delitem(sys.modules, "torch.utils", raising=False)
    monkeypatch.delitem(sys.modules, "torch.utils.tensorboard", raising=False)
    monkeypatch.setitem(sys.modules, "torch", ModuleType("torch"))

    writer = TensorBoardWriter(tmp_path / "tb", summary_path=summary_path)
    writer.log({})
    writer.close()
    summary = _load_summary(summary_path)
    assert summary and summary[-1]["component"] == "tensorboard"
    assert summary[-1]["status"] in {"disabled", "enabled"}


def test_mlflow_writer_enforces_local_uri(
    summary_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "mlflow":
            raise ImportError("mlflow missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("CODEX_MLFLOW_URI", raising=False)
    monkeypatch.delitem(sys.modules, "mlflow", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    writer = MLflowWriter(None, "exp", "run", {}, summary_path=summary_path)
    writer.log({})
    writer.close()

    summary = _load_summary(summary_path)
    assert summary and summary[-1]["component"] == "mlflow"
    assert summary[-1]["status"] == "disabled"
    uri = summary[-1]["extra"].get("tracking_uri")
    assert uri and uri.startswith("file:")
    assert summary[-1]["extra"].get("requested_uri", "") == ""
    assert summary[-1]["extra"].get("fallback_reason", "") == ""


def test_mlflow_writer_rejects_remote_uri(
    tmp_path: Path, summary_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))
    dummy = ModuleType("mlflow")
    recorded: dict[str, Any] = {}

    def _set_tracking_uri(uri: str) -> None:
        recorded["uri"] = uri

    def _set_experiment(name: str) -> None:
        recorded["experiment"] = name

    def _start_run(run_name: str | None = None):  # pragma: no cover - simple stub
        recorded["run_name"] = run_name
        return object()

    def _set_tags(tags: dict | None) -> None:
        recorded["tags"] = tags

    def _log_metric(name: str, value: float, step: int) -> None:
        recorded.setdefault("metrics", []).append((name, value, step))

    dummy.set_tracking_uri = _set_tracking_uri  # type: ignore[attr-defined]
    dummy.set_experiment = _set_experiment  # type: ignore[attr-defined]
    dummy.start_run = _start_run  # type: ignore[attr-defined]
    dummy.set_tags = _set_tags  # type: ignore[attr-defined]
    dummy.log_metric = _log_metric  # type: ignore[attr-defined]
    dummy.end_run = lambda: None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlflow", dummy)

    writer = MLflowWriter(
        "http://example.com",
        "exp",
        "run",
        {"stage": "test"},
        summary_path=summary_path,
    )
    writer.log({"metric": "loss", "value": 0.1, "step": 1})
    writer.close()

    assert recorded["uri"].startswith("file:")
    summary = _load_summary(summary_path)
    extra = summary[-1]["extra"]
    assert extra["tracking_uri"].startswith("file:")
    assert extra["requested_uri"] == "http://example.com"
    assert extra["fallback_reason"] == "non_local_uri"


def test_wandb_writer_emits_summary(summary_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "wandb":
            raise ImportError("wandb missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "wandb", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    writer = WandbWriter("proj", "run", {}, summary_path=summary_path)
    writer.log({})
    writer.close()

    summary = _load_summary(summary_path)
    assert summary and summary[-1]["component"] == "wandb"
    assert summary[-1]["status"] == "disabled"


def test_run_logger_honours_legacy_toggle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_TRACKING_LEGACY_NDJSON", "1")
    logger = RunLogger(tmp_path / "run", "legacy-run")
    logger.log_metric(step=0, split="train", metric="loss", value=1.23, tags={})
    logger.close()

    metrics_path = tmp_path / "run" / "metrics.ndjson"
    payload = json.loads(metrics_path.read_text(encoding="utf-8").strip())
    assert "run_id" not in payload
    assert "timestamp" not in payload
    assert payload["metric"] == "loss"
