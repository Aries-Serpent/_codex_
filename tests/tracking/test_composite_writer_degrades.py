import json
import time
from pathlib import Path

from codex_ml.tracking.writers import CompositeWriter, NdjsonWriter


class FailingWriter:
    def log(self, row: dict) -> None:
        raise RuntimeError("boom")

    def close(self) -> None:
        pass


class DisabledWriter:
    def __init__(self) -> None:
        self._disabled_reason = "dummy:unavailable"

    def log(self, row: dict) -> None:
        pass

    def close(self) -> None:
        pass


def test_composite_writer_degrades(tmp_path: Path, capsys) -> None:
    ndjson = NdjsonWriter(tmp_path / "metrics.ndjson")
    writer = CompositeWriter([ndjson, FailingWriter(), DisabledWriter()])
    captured = capsys.readouterr()
    assert "[tracking] degraded writers:" in captured.err
    assert "dummy (unavailable)" in captured.err
    assert writer.disabled_components == (("dummy", "unavailable"),)
    row = {
        "timestamp": time.time(),
        "run_id": "r1",
        "step": 0,
        "split": "train",
        "metric": "acc",
        "value": 0.1,
        "dataset": None,
        "tags": {},
    }
    writer.log(row)
    writer.close()
    data = (tmp_path / "metrics.ndjson").read_text(encoding="utf-8").strip().splitlines()
    record = json.loads(data[0])
    assert record["metric"] == "acc"
    assert record["schema_version"] == "v1"
