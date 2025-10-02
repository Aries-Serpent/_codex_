from __future__ import annotations

import json
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

    runner = CliRunner()
    result = runner.invoke(
        codex,
        ["evaluate", "--config", str(config_path)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    summary = json.loads(result.output)
    metrics_path = Path(summary["metrics_path"])
    assert metrics_path.exists()
    rows = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines()]
    assert {row["metric"] for row in rows} == {"accuracy"}
    values = [row["value"] for row in rows]
    assert len(values) == 1
    assert values[0] == pytest.approx(0.5)
