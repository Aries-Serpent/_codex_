"""Typer CLI coverage for monitoring NDJSON utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

from codex_ml.monitoring import cli as monitoring_cli


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


def _write_ndjson(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")


def test_inspect_reports_line_count(cli_runner: CliRunner, tmp_path: Path) -> None:
    log_path = tmp_path / "events.ndjson"
    _write_ndjson(
        log_path,
        [
            {
                "ts": 1.0,
                "run_id": "run-a",
                "phase": "train",
                "step": 1,
                "metric": "loss",
                "value": 0.5,
            },
            {
                "ts": 2.0,
                "run_id": "run-a",
                "phase": "eval",
                "step": 2,
                "metric": "accuracy",
                "value": 0.8,
            },
        ],
    )

    result = cli_runner.invoke(monitoring_cli.app, ["inspect", str(log_path)])

    assert result.exit_code == 0
    assert "'lines': 2" in result.stdout
    assert str(log_path) in result.stdout


def test_export_generates_csv(cli_runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "telemetry.ndjson"
    _write_ndjson(
        src,
        [
            {
                "ts": 3.0,
                "run_id": "demo",
                "phase": "train",
                "step": 3,
                "split": "train",
                "dataset": "demo-set",
                "metric": "loss",
                "value": 0.4,
                "meta": {"source": "unit-test"},
            },
            {
                "ts": 4.0,
                "run_id": "demo",
                "phase": "eval",
                "step": 4,
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
    assert any("accuracy" in line for line in output_lines[1:])


def test_export_rejects_unknown_format(cli_runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "telemetry.ndjson"
    _write_ndjson(
        src,
        [
            {
                "ts": 1.0,
                "run_id": "demo",
                "phase": "train",
                "step": 1,
                "metric": "loss",
                "value": 0.1,
            }
        ],
    )
    dst = tmp_path / "telemetry.json"

    result = cli_runner.invoke(monitoring_cli.app, ["export", str(src), str(dst), "--fmt", "json"])

    assert result.exit_code != 0
    assert "unsupported format" in result.stdout or "unsupported format" in result.stderr
