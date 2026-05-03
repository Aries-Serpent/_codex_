"""Tests for the monitoring CLI utilities."""

from __future__ import annotations

import ast
import csv
import json
from pathlib import Path

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

from codex_ml.monitoring import cli as monitoring_cli


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_inspect_reports_line_counts(tmp_path: Path, runner: CliRunner) -> None:
    records = [
        {"ts": 1.0, "run_id": "r1", "phase": "train", "step": 1, "metric": "loss", "value": 0.1},
        {"ts": 2.0, "run_id": "r1", "phase": "train", "step": 2, "metric": "loss", "value": 0.2},
        {"ts": 3.0, "run_id": "r1", "phase": "eval", "step": 3, "metric": "acc", "value": 0.9},
    ]
    log_path = tmp_path / "logs.ndjson"
    log_path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    result = runner.invoke(monitoring_cli.app, ["inspect", str(log_path)])

    assert result.exit_code == 0
    summary = ast.literal_eval(result.stdout.strip())
    assert summary["path"] == str(log_path)
    assert summary["lines"] == len(records)


def test_export_generates_csv_from_ndjson(tmp_path: Path, runner: CliRunner) -> None:
    src = tmp_path / "records.ndjson"
    rows = [
        {
            "ts": 10.0,
            "run_id": "run-42",
            "phase": "train",
            "step": 7,
            "split": "train",
            "dataset": "dataset-A",
            "metric": "loss",
            "value": 0.123,
            "meta": {"info": 1},
        },
        {"ts": 11.0},
    ]
    src.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    dst = tmp_path / "out.csv"

    result = runner.invoke(monitoring_cli.app, ["export", str(src), str(dst)])

    assert result.exit_code == 0
    with dst.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        exported = list(reader)

    assert reader.fieldnames == [
        "version",
        "ts",
        "run_id",
        "phase",
        "step",
        "split",
        "dataset",
        "metric",
        "value",
        "meta",
    ]
    assert exported[0]["version"] == "1"
    assert exported[0]["metric"] == "loss"
    assert exported[0]["meta"] == "{'info': 1}"
    assert exported[1]["ts"] == "11.0"
    assert exported[1]["run_id"] == ""
