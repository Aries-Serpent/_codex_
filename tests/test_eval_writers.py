from __future__ import annotations

import csv
import json
from pathlib import Path

from src.evaluation.writers import write_csv, write_ndjson


def test_write_ndjson(tmp_path: Path):
    path = tmp_path / "rows.ndjson"
    rows = [{"a": 1}, {"a": 2, "b": "x"}]
    write_ndjson(rows, path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["a"] == 1
    assert json.loads(lines[1])["b"] == "x"


def test_write_csv(tmp_path: Path):
    path = tmp_path / "rows.csv"
    rows = [{"a": 1}, {"a": 2, "b": "x"}]
    write_csv(rows, path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = list(csv.DictReader(handle))
    assert reader[0]["a"] == "1"
    assert reader[1]["b"] == "x"
