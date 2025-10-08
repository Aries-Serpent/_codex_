"""Tests for the NDJSON training logger callback."""

from __future__ import annotations

import json

from codex_ml.callbacks.ndjson_logger import NDJSONLogger


def test_ndjson_logger_writes_lines(tmp_path):
    """Logger appends one line per epoch with recorded metrics."""

    log_path = tmp_path / "m.ndjson"
    logger = NDJSONLogger(str(log_path))
    logger.on_epoch_end(0, {"loss": 1.23}, {})
    logger.on_epoch_end(1, {"acc": 0.9}, {})

    data = log_path.read_text(encoding="utf-8").splitlines()
    assert len(data) == 2

    first, second = map(json.loads, data)
    assert first["epoch"] == 0 and "loss" in first
    assert second["epoch"] == 1 and "acc" in second
