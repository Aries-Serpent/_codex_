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
    main(["summarize", "--input", str(tmp_path), "--output", "csv", "--destination", str(dest)])
    assert dest.exists()
    data = list(csv.DictReader(dest.open(encoding="utf-8")))
    assert [float(row["value"]) for row in data] == [0.5, 0.4]
    assert data[0]["step"] == "1"
    assert data[1]["step"] == "2"
