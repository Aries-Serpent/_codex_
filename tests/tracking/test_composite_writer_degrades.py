import json
import time
from pathlib import Path

from codex_ml.tracking.writers import CompositeWriter, NdjsonWriter


class FailingWriter:
    def log(self, row: dict) -> None:
        raise RuntimeError("boom")

    def close(self) -> None:
        pass


def test_composite_writer_degrades(tmp_path: Path) -> None:
    ndjson = NdjsonWriter(tmp_path / "metrics.ndjson")
    writer = CompositeWriter([ndjson, FailingWriter()])
    row = {
        "ts": time.time(),
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
    assert json.loads((tmp_path / "metrics.ndjson").read_text().strip())["metric"] == "acc"
