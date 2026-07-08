"""
Test Evaluation Cli

Test module for evaluation cli.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

pytest.importorskip("omegaconf")

from codex_ml.cli.codex_cli import codex


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

    assert result.exit_code == 0, "Result must not be empty"

    # The evaluate command writes metrics to output_dir/metrics_filename
    # (configured as output_dir/<metrics_filename> in the YAML).
    # The CLI emits a provenance JSON to stdout, not a summary with metrics_path.
    metrics_path = output_dir / "metrics.ndjson"
    assert (metrics_path.exists(), "Condition must be true"
    ), f"Expected metrics file at {metrics_path}. CLI output:\n{result.output}"
    rows = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines()]
    assert {row["metric"] for row in rows} == {"accuracy"}, "Condition must be true"
    values = [row["value"] for row in rows]
    assert len(values) == 1, "Values must not be empty"
    assert values[0] == pytest.approx(0.5), "Value must be initialized"

    assert metrics_log.exists(), "Condition must be true"
    log_records = [
        json.loads(line) for line in metrics_log.read_text(encoding="utf-8").splitlines()
    ]
    assert len(log_records) == 1, "Log_records must not be empty"
    record = log_records[0]
    assert record["num_records"] == 2, "rec is not valid"
    assert record["metrics"]["accuracy"] == pytest.approx(0.5), "rec is not valid"
