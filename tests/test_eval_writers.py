import csv
import json
from pathlib import Path

from src.evaluation.writers import write_csv, write_ndjson


def test_write_ndjson(tmp_path: Path):
    out = tmp_path / "r.ndjson"
    rows = [{"a": 1}, {"a": 2, "b": "x"}]
    write_ndjson(rows, out)
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    meta = json.loads(lines[0])
    assert meta["__meta__"]["schema_version"] == "v1"
    assert json.loads(lines[1])["a"] == 1
    assert json.loads(lines[2])["b"] == "x"


def test_write_csv(tmp_path: Path):
    out = tmp_path / "r.csv"
    rows = [{"a": 1}, {"a": 2, "b": "x"}]
    write_csv(rows, out)
    with out.open("r", encoding="utf-8", newline="") as f:
        r = list(csv.DictReader(f))
    assert r[0]["a"] == "1"
    assert r[1]["b"] == "x"
