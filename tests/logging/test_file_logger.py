from __future__ import annotations

import json
from pathlib import Path

from codex_ml.logging.file_logger import FileLogger


def test_file_logger_writes_ndjson_and_csv(tmp_path: Path) -> None:
    logger = FileLogger(root=tmp_path, formats=("ndjson", "csv"), filename_stem="metrics")
    logger.log({"step": 1, "loss": 0.5})
    logger.log({"step": 2, "loss": 0.4})

    paths = logger.paths()
    ndjson_path = paths["ndjson"]
    csv_path = paths["csv"]

    assert ndjson_path is not None and ndjson_path.exists()
    assert csv_path is not None and csv_path.exists()

    with ndjson_path.open("r", encoding="utf-8") as fh:
        lines = [json.loads(line) for line in fh.read().strip().splitlines()]
    assert lines == [{"step": 1, "loss": 0.5}, {"step": 2, "loss": 0.4}]

    csv_rows = csv_path.read_text(encoding="utf-8").strip().splitlines()
    assert csv_rows[0].split(",") == ["step", "loss"]
    assert csv_rows[1:] == ["1,0.5", "2,0.4"]
