"""
Test Ndjson To Csv

Test module for ndjson to csv.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from tools import ndjson_to_csv


def test_convert_file(tmp_path):
    ndjson_path = REPO_ROOT / "samples" / "metrics_sample.ndjson"
    csv_path = tmp_path / "metrics.csv"
    count, fields = ndjson_to_csv.convert_file(ndjson_path, csv_path)
    assert count == 2, "Count must be greater than zero"
    assert set(fields) >= {"epoch", "loss", "accuracy"}
    contents = csv_path.read_text(encoding="utf-8")
    assert "epoch" in contents, "Content must not be empty"
    assert "loss" in contents, "Content must not be empty"
    assert "accuracy" in contents, "Content must not be empty"
