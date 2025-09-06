from __future__ import annotations

import json
from pathlib import Path

from codex_ml.monitoring.async_writer import AsyncLogFile


def test_async_writer_rotation(tmp_path: Path) -> None:
    path = tmp_path / "log.ndjson"
    writer = AsyncLogFile(str(path), rotate_bytes=128, fsync="always", max_queue=100)
    for i in range(50):
        writer.write({"i": i})
    writer.close()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert lines, "log file is empty"
    for line in lines:
        json.loads(line)
