"""Typer-based tests for the codex_ml.monitoring CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

from codex_ml.monitoring import cli as monitoring_cli

pytestmark = pytest.mark.not_slow


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


def _write_ndjson(path: Path, records: Iterable[dict[str, object]]) -> Path:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    return path


@pytest.fixture()
def telemetry_events(tmp_path: Path) -> Path:
    return _write_ndjson(
        tmp_path / "telemetry.ndjson",
        [
            {
                "ts": 123.0,
                "run_id": "run-1",
                "phase": "train",
                "step": 1,
                "metric": "loss",
                "value": 0.5,
            },
            {
                "ts": 124.0,
                "run_id": "run-1",
                "phase": "eval",
                "step": 2,
                "metric": "accuracy",
                "value": 0.8,
            },
        ],
    )


def test_inspect_reports_line_count(cli_runner: CliRunner, telemetry_events: Path) -> None:
    result = cli_runner.invoke(monitoring_cli.app, ["inspect", str(telemetry_events)])

    assert result.exit_code == 0
    assert "'lines': 2" in result.stdout
    assert str(telemetry_events) in result.stdout


def test_export_generates_csv(cli_runner: CliRunner, tmp_path: Path) -> None:
    src = _write_ndjson(
        tmp_path / "source.ndjson",
        [
            {
                "ts": 1.0,
                "run_id": "run-A",
                "phase": "train",
                "step": 1,
                "split": "train",
                "metric": "loss",
                "value": 0.4,
                "dataset": "dummy",
                "meta": {"source": "unit-test"},
            },
            {
                "ts": 2.0,
                "run_id": "run-A",
                "phase": "eval",
                "step": 2,
                "metric": "accuracy",
                "value": 0.9,
                "meta": {},
            },
        ],
    )
    dst = tmp_path / "telemetry.csv"

    result = cli_runner.invoke(monitoring_cli.app, ["export", str(src), str(dst)])

    assert result.exit_code == 0
    output_lines = dst.read_text().splitlines()
    assert output_lines[0].startswith(
        "version,ts,run_id,phase,step,split,dataset,metric,value,meta"
    )
    assert "unit-test" in output_lines[1]
    assert "accuracy" in "".join(output_lines[1:])


def test_export_rejects_unknown_format(cli_runner: CliRunner, telemetry_events: Path) -> None:
    destination = telemetry_events.with_suffix(".json")

    result = cli_runner.invoke(
        monitoring_cli.app,
        ["export", str(telemetry_events), str(destination), "--fmt", "json"],
    )

    assert result.exit_code != 0
    assert "unsupported format" in result.stdout or "unsupported format" in result.stderr
