"""Verify metrics sinks utilities."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_csv_sink_writes_header_and_rows():
    from codex_ml.metrics.sinks import CsvSink

    buffer = io.StringIO()
    sink = CsvSink(fp=buffer, fieldnames=["metric", "value"])
    sink.write({"metric": "loss", "value": 0.5})
    sink.write({"metric": "loss", "value": 0.4})
    sink.close()

    content = buffer.getvalue().splitlines()
    assert content[0] == "metric,value"
    assert "loss,0.4" in content[-1]


def test_ndjson_sink_serializes_rows_and_factory(tmp_path):
    from codex_ml.metrics.sinks import NdjsonSink, create_sink, get_sink

    buffer = io.StringIO()
    sink = NdjsonSink(fp=buffer)
    sink.write({"metric": "acc", "value": 0.9})
    sink.close()
    assert json.loads(buffer.getvalue().strip())["metric"] == "acc", "Value must be initialized"

    # Factory helpers
    csv_sink = create_sink("csv", fp=io.StringIO(), fieldnames=["metric", "value", "step"])
    csv_sink.write({"metric": "acc", "value": 1, "step": 1})

    ndjson_path = tmp_path / "metrics.ndjson"
    sink_from_path = get_sink("ndjson", path=ndjson_path)
    assert sink_from_path is not None, "sink_from_path must be initialized"
    sink_from_path.write({"metric": "loss", "value": 0.1})
