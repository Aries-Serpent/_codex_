import builtins
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from codex_ml.tracking.writers import MLflowWriter, NdjsonWriter, TensorBoardWriter, WandbWriter


@pytest.fixture
def summary_path(tmp_path: Path) -> Path:
    return tmp_path / "tracking_summary.ndjson"


def _load_summary(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ndjson_writer_is_deterministic(tmp_path: Path) -> None:
    writer = NdjsonWriter(tmp_path / "metrics.ndjson")
    row = {
        "timestamp": 123.45,
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
        '"timestamp":123.45,"run_id":"run-1","step":2,"split":"eval","metric":"loss",'
        '"value":0.5,"dataset":"data/train","tags":{"a":1,"b":2}}'
    )
    assert payload == expected


def test_tensorboard_writer_emits_offline_summary(tmp_path: Path, summary_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_mlflow_writer_enforces_local_uri(summary_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
