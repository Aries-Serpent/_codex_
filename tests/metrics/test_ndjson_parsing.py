"""
Test Ndjson Parsing

Test module for ndjson parsing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.metrics.api import summarize_ndjson_logs


def test_summarize_ndjson(tmp_path: Path) -> None:
    log_file = tmp_path / "metrics.ndjson"
    lines = [
        {"loss": 0.5, "epoch": 1},
        {"loss": 0.3, "epoch": 2},
        {"metrics": {"accuracy": 0.8}},
    ]
    log_file.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
    summary = summarize_ndjson_logs(log_file)
    assert pytest.approx(summary["loss"], rel=1e-6) == (0.5 + 0.3) / 2
    assert summary["metrics.accuracy"] == 0.8, "Condition must be true"


def test_invalid_json_raises(tmp_path: Path) -> None:
    log_file = tmp_path / "invalid.ndjson"
    log_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        summarize_ndjson_logs(log_file)
