"""Smoke tests for the codex_ml.monitoring CLI utilities."""

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


def test_inspect_reports_line_count(cli_runner: CliRunner, tmp_path: Path) -> None:
    log_path = tmp_path / "events.ndjson"
    log_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 123.0,
                        "run_id": "run-1",
                        "phase": "train",
                        "step": 1,
                        "metric": "loss",
                        "value": 0.5,
                    }
                ),
                json.dumps(
                    {
                        "ts": 124.0,
                        "run_id": "run-1",
                        "phase": "eval",
                        "step": 2,
                        "metric": "accuracy",
                        "value": 0.8,
                    }
                ),
            ]
        )
        + "\n"
    )

    result = cli_runner.invoke(monitoring_cli.app, ["inspect", str(log_path)])

    assert result.exit_code == 0
    assert "'lines': 2" in result.stdout
    assert str(log_path) in result.stdout


def test_export_generates_csv(cli_runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "telemetry.ndjson"
    src.write_text(
        "\n".join(
            [
                json.dumps(
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
                    }
                ),
                json.dumps(
                    {
                        "ts": 2.0,
                        "run_id": "run-A",
                        "phase": "eval",
                        "step": 2,
                        "metric": "accuracy",
                        "value": 0.9,
                        "meta": {},
                    }
                ),
            ]
        )
        + "\n"
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


def test_export_rejects_unknown_format(cli_runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "telemetry.ndjson"
    src.write_text("{}\n")
    dst = tmp_path / "telemetry.json"

    result = cli_runner.invoke(monitoring_cli.app, ["export", str(src), str(dst), "--fmt", "json"])

    assert result.exit_code != 0
    assert "unsupported format" in result.stdout or "unsupported format" in result.stderr
