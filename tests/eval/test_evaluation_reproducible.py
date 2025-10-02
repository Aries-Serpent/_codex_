from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

pytest.importorskip("omegaconf")

try:  # optional dependency for RNG disturbance
    import numpy as np
except Exception:  # pragma: no cover - numpy unavailable
    np = None

from codex_ml.config import EvaluationConfig  # noqa: E402
from codex_ml.eval.runner import run_evaluation  # noqa: E402
from codex_ml.utils.provenance import load_environment_summary  # noqa: E402


def test_run_evaluation_repeatable(tmp_path) -> None:
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        '{"text": "hello", "prediction": "hello", "target": "hello"}\n',
        encoding="utf-8",
    )

    cfg1 = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["accuracy"],
        output_dir=str(tmp_path / "eval1"),
        seed=21,
    )

    summary1 = run_evaluation(cfg1)
    summary_payload1 = json.loads(Path(summary1["summary_path"]).read_text())

    random.random()
    if np is not None:
        np.random.rand()

    cfg2 = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["accuracy"],
        output_dir=str(tmp_path / "eval2"),
        seed=21,
    )

    summary2 = run_evaluation(cfg2)
    summary_payload2 = json.loads(Path(summary2["summary_path"]).read_text())

    assert summary1["metrics"] == summary2["metrics"]
    assert summary1["num_records"] == summary2["num_records"]
    assert summary1["run_id"] == summary2["run_id"]
    assert summary_payload1["run_id"] == summary1["run_id"]
    assert summary_payload2["run_id"] == summary2["run_id"]

    prov1 = load_environment_summary(tmp_path / "eval1" / "provenance")
    prov2 = load_environment_summary(tmp_path / "eval2" / "provenance")
    assert prov1["seed"] == prov2["seed"] == 21
    assert prov1["command"] == prov2["command"] == "evaluate"

    records1 = [
        json.loads(line)
        for line in (tmp_path / "eval1" / "records.ndjson").read_text().splitlines()
    ]
    records2 = [
        json.loads(line)
        for line in (tmp_path / "eval2" / "records.ndjson").read_text().splitlines()
    ]
    assert records1 == records2

    metrics1 = [
        json.loads(line)
        for line in (tmp_path / "eval1" / "metrics.ndjson").read_text().splitlines()
    ]
    metrics2 = [
        json.loads(line)
        for line in (tmp_path / "eval2" / "metrics.ndjson").read_text().splitlines()
    ]
    assert metrics1 == metrics2
    assert metrics1, "Expected at least one metrics row"
    required_keys = {"run_id", "timestamp", "split", "step", "metric", "value", "tags"}
    for row in metrics1:
        assert row["run_id"] == summary1["run_id"]
        assert required_keys.issubset(row)
        assert row["tags"]["phase"] == "evaluation"
