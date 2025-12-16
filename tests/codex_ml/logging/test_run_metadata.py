from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from codex_ml.logging.run_metadata import build_run_metadata, log_run_metadata


class DummyLogger:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def log(self, payload):
        self.calls.append(payload)


def test_build_run_metadata_includes_commit_and_paths(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text("{}", encoding="utf-8")

    payload = build_run_metadata(
        seed=42,
        deterministic=True,
        resume=False,
        dataset_format="jsonl",
        dataset_source=dataset_path,
        train_examples="10",
        eval_examples=5,
        missing_optional=["mlflow", "mlflow"],
        extras={"note": "demo", "skip": None},
        commit_lookup=lambda: "abc123",
    )

    assert payload["git_commit"] == "abc123"
    assert payload["dataset_source"] == str(dataset_path)
    assert payload["train_examples"] == 10
    assert payload["eval_examples"] == 5
    assert payload["missing_optional"] == ["mlflow"]
    assert payload["note"] == "demo"


def test_log_run_metadata_invokes_logger(monkeypatch):
    logger = DummyLogger()

    payload = log_run_metadata(
        logger,
        seed=None,
        deterministic=False,
        resume=True,
        dataset_format="parquet",
        dataset_source="s3://bucket/data",
        missing_optional=["wandb"],
        extras={"run_id": "run-1"},
        commit_lookup=lambda: "commit-xyz",
    )

    assert logger.calls and logger.calls[0] == payload
    assert payload["resume"] is True
    assert payload["deterministic"] is False
    assert payload["dataset_source"] == "s3://bucket/data"


def test_build_run_metadata_handles_non_path_inputs(monkeypatch):
    payload = build_run_metadata(
        dataset_source=SimpleNamespace(path="/tmp/path"),
        train_examples=None,
        eval_examples="invalid",
        extras={"value": 0},
    )

    assert payload.get("dataset_source") == "namespace(path='/tmp/path')"
    assert "train_examples" not in payload
    assert "eval_examples" not in payload
    assert payload["value"] == 0
