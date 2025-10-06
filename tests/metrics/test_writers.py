from __future__ import annotations

import json
from pathlib import Path

from codex_ml.metrics.writers import CSVMetricsWriter, MetricsRecord, NDJSONMetricsWriter


def test_ndjson_writer_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "metrics.ndjson"
    writer = NDJSONMetricsWriter(path)
    writer.write({"metric": "loss", "value": 1.23, "step": 1, "split": "train"})
    writer.write(MetricsRecord(metric="acc", value=0.9, step=2, split="eval"))
    data = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert data[0]["metric"] == "loss"
    assert data[1]["metric"] == "acc"
    assert data[1]["split"] == "eval"


def test_csv_writer_writes_header_once(tmp_path: Path) -> None:
    path = tmp_path / "metrics.csv"
    writer = CSVMetricsWriter(path)
    writer.write({"metric": "loss", "value": 0.5, "step": 1})
    writer.write({"metric": "loss", "value": 0.25, "step": 2, "split": "eval"})
    lines = path.read_text().splitlines()
    assert lines[0].startswith("metric,value,step,split,ts")
    assert len(lines) == 3
