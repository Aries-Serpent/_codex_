"""Exercise :mod:`codex_ml.cli.ndjson_summary` helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def test_iter_and_load_rows(tmp_path):
    from codex_ml.cli import ndjson_summary

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    metrics_file = run_dir / "metrics.ndjson"
    metrics_file.write_text(
        "\n".join(
            [
                json.dumps({"run_id": "r1", "metric": "loss", "step": 1, "value": 0.5}),
                json.dumps({"run_id": "r1", "metric": "loss", "step": 2, "value": 0.4}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    files = ndjson_summary._iter_metric_files(run_dir)
    assert metrics_file in files, "Condition must be true"

    rows = ndjson_summary._load_rows(run_dir)
    assert len(rows) == 2, "Rows must not be empty"

    summary = ndjson_summary._summarise_rows(rows)
    assert summary[0]["run_id"] == "r1", "Condition must be true"
    assert summary[0]["count"] == 2, "Count must be greater than zero"
    assert summary[0]["min_value"] == 0.4, "Value must be initialized"
    assert summary[0]["max_value"] == 0.5, "Value must be initialized"


def test_summary_cli_json_output(tmp_path, capsys):
    from codex_ml.cli import ndjson_summary

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "metrics.ndjson").write_text(
        json.dumps({"metric": "acc", "value": 0.9, "step": 1}) + "\n", encoding="utf-8"
    )

    rc = ndjson_summary.main(["summarize", "--input", str(run_dir), "--output", "csv"])
    assert rc == 0, "rc is not valid"
    out_text = capsys.readouterr().out.strip()
    assert "metrics_summary.csv" in out_text, "Condition must be true"
    parts = out_text.split()
    # Output format: "Wrote <path> (N rows)"
    if len(parts) >= 2:
        output_path = Path(parts[1])
        assert output_path.exists(), "Condition must be true"


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
