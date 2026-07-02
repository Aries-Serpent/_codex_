"""
pytest.importorskip("tensorboard")
Test Metrics Writers

Test module for metrics writers.
"""

import pytest

pytest.importorskip("numpy", reason="numpy required for training module")

from pathlib import Path

from training.engine_hf_trainer import CSVMetricsWriter, NDJSONMetricsWriter


def test_csv_metrics_writer(tmp_path: Path):
    writer = CSVMetricsWriter(str(tmp_path / "metrics.csv"))
    writer.write({"step": 1, "loss": 0.5})
    writer.write({"step": 2, "loss": 0.4})
    lines = (tmp_path / "metrics.csv").read_text(encoding="utf-8").strip().splitlines()
    assert lines[0].replace(" ", "") in {"loss,step", "step,loss"}
    assert len(lines) == 3, "Lines must not be empty"


def test_ndjson_metrics_writer(tmp_path: Path):
    writer = NDJSONMetricsWriter(str(tmp_path / "metrics.ndjson"))
    writer.write({"accuracy": 0.9})
    contents = (tmp_path / "metrics.ndjson").read_text(encoding="utf-8").strip().splitlines()
    assert contents and "accuracy" in contents[0], "Content must not be empty"
