"""
Unit tests for CLI report generation and determinism checking.

Tests cover:
- Report aggregation from NDJSON
- Determinism comparison
- Exit codes
- Error handling
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("typer")


def test_report_aggregates_metrics(tmp_path):
    """Test report command aggregates NDJSON metrics."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    # Create test NDJSON file
    metrics_file = tmp_path / "metrics.ndjson"
    records = [
        {"type": "batch", "batch_index": 0, "loss": 1.0, "count": 10},
        {"type": "batch", "batch_index": 1, "loss": 0.5, "count": 10},
        {
            "type": "epoch",
            "loss": 0.75,
            "count": 20,
            "metrics": {"accuracy": 0.85},
            "batches": 2,
            "duration_sec": 1.23,
        },
    ]
    metrics_file.write_text("\n".join(json.dumps(r) for r in records))

    # Run report command
    result = runner.invoke(app, ["report", "--input", str(metrics_file), "--json"])

    assert result.exit_code == 0, "Result must not be empty"
    output = json.loads(result.stdout)
    assert output["loss"] == 0.75, "Condition must be true"
    assert output["count"] == 20, "Count must be greater than zero"
    assert output["metrics"]["accuracy"] == 0.85, "Condition must be true"
    assert output["batches"] == 2, "Condition must be true"


def test_report_determinism_match(tmp_path):
    """Test report comparison with matching results."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    # Create two identical NDJSON files
    epoch_record = {
        "type": "epoch",
        "loss": 0.75,
        "count": 20,
        "metrics": {"accuracy": 0.85},
        "batches": 2,
        "duration_sec": 1.23,
    }

    metrics_file1 = tmp_path / "metrics1.ndjson"
    metrics_file1.write_text(json.dumps(epoch_record))

    metrics_file2 = tmp_path / "metrics2.ndjson"
    metrics_file2.write_text(json.dumps(epoch_record))

    # Run report with comparison
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(metrics_file1),
            "--compare",
            str(metrics_file2),
            "--json",
        ],
    )

    assert result.exit_code == 0, "Result must not be empty"
    output = json.loads(result.stdout)
    assert output["determinism_match"] is True, "Condition must be true"


def test_report_determinism_mismatch(tmp_path):
    """Test report comparison with mismatched results (exit code 4)."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    # Create two different NDJSON files
    metrics_file1 = tmp_path / "metrics1.ndjson"
    metrics_file1.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.75,
                "count": 20,
                "metrics": {"accuracy": 0.85},
                "batches": 2,
                "duration_sec": 1.23,
            }
        )
    )

    metrics_file2 = tmp_path / "metrics2.ndjson"
    metrics_file2.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.80,  # Different loss
                "count": 20,
                "metrics": {"accuracy": 0.85},
                "batches": 2,
                "duration_sec": 1.23,
            }
        )
    )

    # Run report with comparison
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(metrics_file1),
            "--compare",
            str(metrics_file2),
            "--json",
        ],
    )

    # Should exit with code 4 for determinism mismatch
    assert result.exit_code == 4, "Result must not be empty"
    # JSON output should be present before error message
    # Split by the error message to extract JSON
    stdout_parts = result.stdout.split("Determinism mismatch detected.")
    json_part = stdout_parts[0].strip()
    output = json.loads(json_part)
    assert output["determinism_match"] is False, "Condition must be true"


def test_report_missing_input_file(tmp_path):
    """Test report with missing input file (exit code 2)."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    result = runner.invoke(
        app,
        ["report", "--input", str(tmp_path / "nonexistent.ndjson")],
    )

    assert result.exit_code == 2, "Result must not be empty"


def test_report_no_epoch_records(tmp_path):
    """Test report with no epoch records (exit code 3)."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    # Create NDJSON with only batch records
    metrics_file = tmp_path / "metrics.ndjson"
    records = [
        {"type": "batch", "batch_index": 0, "loss": 1.0, "count": 10},
        {"type": "batch", "batch_index": 1, "loss": 0.5, "count": 10},
    ]
    metrics_file.write_text("\n".join(json.dumps(r) for r in records))

    result = runner.invoke(app, ["report", "--input", str(metrics_file)])

    assert result.exit_code == 3, "Result must not be empty"


def test_report_human_readable_output(tmp_path):
    """Test report with human-readable (non-JSON) output."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    metrics_file = tmp_path / "metrics.ndjson"
    metrics_file.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.75,
                "count": 20,
                "metrics": {"accuracy": 0.85},
                "batches": 2,
                "duration_sec": 1.23,
            }
        )
    )

    result = runner.invoke(app, ["report", "--input", str(metrics_file)])

    assert result.exit_code == 0, "Result must not be empty"
    assert "loss=" in result.stdout, "Result must not be empty"
    assert "0.75" in result.stdout or "0.7500" in result.stdout, "Result must not be empty"


def test_report_missing_compare_file(tmp_path):
    """Test report with missing compare file (exit code 2)."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    metrics_file = tmp_path / "metrics.ndjson"
    metrics_file.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.75,
                "count": 20,
                "metrics": {},
                "batches": 2,
                "duration_sec": 1.23,
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(metrics_file),
            "--compare",
            str(tmp_path / "nonexistent.ndjson"),
        ],
    )

    assert result.exit_code == 2, "Result must not be empty"


def test_report_compare_no_epoch_records(tmp_path):
    """Test report comparison when compare file has no epoch records."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    metrics_file1 = tmp_path / "metrics1.ndjson"
    metrics_file1.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.75,
                "count": 20,
                "metrics": {},
                "batches": 2,
                "duration_sec": 1.23,
            }
        )
    )

    metrics_file2 = tmp_path / "metrics2.ndjson"
    metrics_file2.write_text(json.dumps({"type": "batch", "loss": 1.0}))

    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(metrics_file1),
            "--compare",
            str(metrics_file2),
        ],
    )

    assert result.exit_code == 3, "Result must not be empty"


def test_report_handles_empty_metrics(tmp_path):
    """Test report handles records with empty metrics dict."""
    from typer.testing import CliRunner

    from codex_ml.evaluation.cli import app

    runner = CliRunner()

    metrics_file = tmp_path / "metrics.ndjson"
    metrics_file.write_text(
        json.dumps(
            {
                "type": "epoch",
                "loss": 0.5,
                "count": 10,
                "metrics": {},  # Empty metrics
                "batches": 1,
                "duration_sec": 0.5,
            }
        )
    )

    result = runner.invoke(app, ["report", "--input", str(metrics_file), "--json"])

    assert result.exit_code == 0, "Result must not be empty"
    output = json.loads(result.stdout)
    assert output["metrics"] == {}, "Condition must be true"
