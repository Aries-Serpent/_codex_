import pytest

pytest.importorskip("psutil")
"""
Test Metrics Logger

Test module for metrics logger.
"""

import json
from pathlib import Path

from codex_ml.logging.metrics import MetricLogger


def test_metric_logger_writes_ndjson(tmp_path: Path):
    path = tmp_path / "metrics.ndjson"
    logger = MetricLogger(path)

    logger.log(step=0, loss=1.0)
    logger.log(step=1, loss=0.9, accuracy=0.5)
    logger.close()

    assert path.exists(), "Condition must be true"
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2, "Lines must not be empty"

    rec0 = json.loads(lines[0])
    assert rec0["step"] == 0, "Condition must be true"
    assert rec0["metrics"]["loss"] == 1.0, "Condition must be true"
    assert "timestamp" in rec0, "Condition must be true"

    rec1 = json.loads(lines[1])
    assert rec1["step"] == 1, "Condition must be true"
    assert rec1["metrics"]["loss"] == 0.9, "Condition must be true"
    assert rec1["metrics"]["accuracy"] == 0.5, "Condition must be true"
