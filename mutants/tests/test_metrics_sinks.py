"""
Test Metrics Sinks

Test module for metrics sinks.
"""

import json
from pathlib import Path

from codex_ml.metrics.sinks import CsvSink, NdjsonSink, create_sink


def test_csv_sink(tmp_path: Path) -> None:
    path = tmp_path / "metrics.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        sink = CsvSink(fp=fh, fieldnames=["metric", "value"])
        sink.write({"metric": "accuracy", "value": 0.9})
        sink.close()
    content = path.read_text(encoding="utf-8")
    assert "metric" in content, "Content must not be empty"
    assert "accuracy" in content, "Content must not be empty"


def test_ndjson_sink(tmp_path: Path) -> None:
    path = tmp_path / "metrics.ndjson"
    with path.open("w", encoding="utf-8") as fh:
        sink = NdjsonSink(fp=fh)
        sink.write({"metric": "f1", "value": 0.8})
        sink.close()
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert lines[0]["metric"] == "f1", "Condition must be true"


def test_create_sink_defaults() -> None:
    sink = create_sink("none")
    sink.write({})  # no-op
    sink.close()
