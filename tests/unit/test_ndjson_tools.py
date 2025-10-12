from __future__ import annotations

import csv
from pathlib import Path

from common.ndjson_tools import append_event_ndjson, ndjson_to_csv


def test_ndjson_to_csv_roundtrip(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "events.ndjson"
    append_event_ndjson(ndjson_path, {"event": "a", "metrics": {"m1": 1, "m2": 2}})
    append_event_ndjson(ndjson_path, {"event": "b", "metrics": {"m1": 3}, "tag": "x"})

    out_csv = tmp_path / "out.csv"
    ndjson_to_csv(ndjson_path, out_csv)
    assert out_csv.exists()

    rows = list(csv.DictReader(out_csv.open()))
    assert len(rows) == 2
    assert "metrics.m1" in rows[0]
    assert "event" in rows[0]
