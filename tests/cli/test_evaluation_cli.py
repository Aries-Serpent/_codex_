"""
Test Evaluation Cli

Test module for evaluation cli.
"""

from __future__ import annotations

import json
import inspect
from pathlib import Path

import pytest
from click.testing import CliRunner

pytest.importorskip("omegaconf")

from codex_ml.cli.codex_cli import codex  # noqa: E402


def test_evaluate_cli_writes_metrics_log(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                json.dumps({"text": "hello", "prediction": "hello", "target": "hello"}),
                json.dumps({"text": "world", "prediction": "nope", "target": "hello"}),
            ]
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "eval_out"
    config_path = tmp_path / "eval.yaml"
    config_path.write_text(
        "\n".join(
            [
                "evaluation:",
                f"  dataset_path: {dataset}",
                "  dataset_format: jsonl",
                "  prediction_field: prediction",
                "  target_field: target",
                "  text_field: text",
                "  metrics:",
                "    - accuracy",
                f"  output_dir: {output_dir}",
                "  report_filename: summary.json",
                "  ndjson_filename: records.ndjson",
                "  metrics_filename: metrics.ndjson",
            ]
        ),
        encoding="utf-8",
    )

    metrics_log = tmp_path / "aggregate.ndjson"

    _runner_kwargs = (
        {"mix_stderr": False}
        if "mix_stderr" in inspect.signature(CliRunner.__init__).parameters
        else {}
    )
    runner = CliRunner(**_runner_kwargs)
    result = runner.invoke(
        codex,
        [
            "evaluate",
            "--config",
            str(config_path),
            "--log-metrics",
            str(metrics_log),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    # Parse output - handle potential NDJSON (multiple JSON objects)
    output_lines = result.output.strip().split('\n')
    # Try to parse as single JSON first, then as NDJSON
    try:
        summary = json.loads(result.output)
    except json.JSONDecodeError:
        # If single JSON fails, parse last non-empty line as the summary
        for line in reversed(output_lines):
            line = line.strip()
            if line:
                try:
                    summary = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        else:
            # If no valid JSON found, raise error with output for debugging
            raise AssertionError(f"No valid JSON found in output:\n{result.output}")

    metrics_path = Path(summary["metrics_path"])
    assert metrics_path.exists()
    rows = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines()]
    assert {row["metric"] for row in rows} == {"accuracy"}
    values = [row["value"] for row in rows]
    assert len(values) == 1
    assert values[0] == pytest.approx(0.5)

    assert metrics_log.exists()
    log_records = [
        json.loads(line) for line in metrics_log.read_text(encoding="utf-8").splitlines()
    ]
    assert len(log_records) == 1
    record = log_records[0]
    assert record["num_records"] == 2
    assert record["metrics"]["accuracy"] == pytest.approx(0.5)
