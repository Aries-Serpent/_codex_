from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _write_ndjson(path: Path) -> None:
    records = [
        {"epoch": 0, "loss": 2.0, "acc": 0.30},
        {"epoch": 1, "loss": 1.5, "acc": 0.35},
    ]
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record) + "\n")


def test_ingest_to_csv_and_summary(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "metrics.ndjson"
    _write_ndjson(ndjson_path)

    csv_path = tmp_path / "metrics.csv"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "codex_ml.cli",
            "metrics",
            "ingest",
            "--input",
            str(ndjson_path),
            "--out-csv",
            str(csv_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["rows"] == 4
    assert Path(payload["csv"]).exists()

    proc_summary = subprocess.run(
        [
            sys.executable,
            "-m",
            "codex_ml.cli",
            "metrics",
            "summary",
            "--input",
            str(ndjson_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    summary = json.loads(proc_summary.stdout)
    assert summary["last"]["acc"] == 0.35
    assert summary["min"]["loss"] == 1.5
    assert summary["epochs"] == [0, 1]
