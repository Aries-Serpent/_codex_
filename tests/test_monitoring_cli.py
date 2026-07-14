from collections.abc import Iterable
from pathlib import Path

import pytest
from typer.testing import CliRunner

from codex_ml.monitoring import cli as monitoring_cli

pytest.importorskip("mlflow")


def _write_ndjson(path: Path, records: Iterable) -> Path:
    """Write NDJSON file."""
    import json
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    return path


@pytest.fixture()
def cli_runner() -> CliRunner:
    """Create a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture()
def telemetry_events(tmp_path: Path) -> Path:
    """Create sample telemetry events NDJSON file."""
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


def test_export_rejects_unknown_format(cli_runner: CliRunner, telemetry_events: Path) -> None:
    destination = telemetry_events.with_suffix(".json")

    result = cli_runner.invoke(
        monitoring_cli.app,
        ["export", str(telemetry_events), str(destination), "--fmt", "json"],
    )

    assert result.exit_code != 0, "Result must not be empty"
    assert "unsupported format" in result.stdout or "unsupported format" in result.stderr, "Result must not be empty"
