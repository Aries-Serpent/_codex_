import pytest

pytest.importorskip("mlflow")
"""
Test Ndjson Logging

Test module for ndjson logging.
"""

from codex_ml import train_loop


def test_record_metrics_ndjson(tmp_path, monkeypatch):
    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path)
    train_loop.record_metrics("p", 0, {"a": 1}, "cfg")
    train_loop.record_metrics("p", 1, {"a": 2}, "cfg")
    lines = (tmp_path / "metrics.ndjson").read_text().strip().splitlines()
    assert len(lines) == 2, "Lines must not be empty"
    data = [__import__("json").loads(line) for line in lines]
    assert data[0]["epoch"] == 0, "Data must not be empty"
    assert data[1]["epoch"] == 1, "Data must not be empty"
    assert all(entry.get("run_id") for entry in data), "Data must not be empty"
