from __future__ import annotations

import csv
from pathlib import Path

from codex_ml.cli import ndjson_summary
from codex_ml.logging.ndjson_logger import NDJSONLogger


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_ndjson_summary_wrapper_produces_csv(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    logger = NDJSONLogger(run_dir / "metrics.ndjson", max_bytes=128, backup_count=2)
    for step in range(3):
        logger.log({"metric": "loss", "step": step, "value": 1.0 - 0.1 * step})
    logger.log({"metric": "accuracy", "step": 3, "value": 0.9})
    logger.close()

    output = ndjson_summary.summarize(run_dir, "csv")
    assert output.exists()
    rows = _read_csv(output)
    metrics = {row["metric"] for row in rows}
    assert metrics == {"loss", "accuracy"}
    loss_row = next(row for row in rows if row["metric"] == "loss")
    assert loss_row["count"] == "3"
