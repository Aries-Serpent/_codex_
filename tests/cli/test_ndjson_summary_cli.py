import csv
import json
from pathlib import Path

from codex_ml.cli.ndjson_summary import main


def _write_ndjson(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_summarize_rotated_shards_csv(tmp_path):
    base = tmp_path / "metrics.ndjson"
    rotated = tmp_path / "metrics.ndjson.1"
    rows_old = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "run_id": "r1",
            "step": 1,
            "metric": "loss",
            "value": 0.5,
        },
    ]
    rows_new = [
        {
            "timestamp": "2024-01-01T00:01:00Z",
            "run_id": "r1",
            "step": 2,
            "metric": "loss",
            "value": 0.4,
        },
    ]
    _write_ndjson(rotated, rows_old)
    _write_ndjson(base, rows_new)
    dest = tmp_path / "summary.csv"
    exit_code = main(
        [
            "summarize",
            "--input",
            str(tmp_path),
            "--output",
            "csv",
            "--dest",
            str(dest),
        ]
    )
    assert exit_code == 0
    assert dest.exists()
    data = list(csv.DictReader(dest.open(encoding="utf-8")))
    assert len(data) == 1
    row = data[0]
    assert row["run_id"] == "r1"
    assert row["metric"] == "loss"
    assert row["count"] == "2"
    assert row["first_step"] == "1"
    assert row["last_step"] == "2"
    assert row["first_timestamp"] == "2024-01-01T00:00:00Z"
    assert row["last_timestamp"] == "2024-01-01T00:01:00Z"
    assert row["first_value"] == "0.5"
    assert float(row["mean_value"]) == 0.45
    assert row["last_value"] == "0.4"
    assert row["first_phase"] == ""
    assert row["last_phase"] == ""
