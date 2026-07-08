"""Smoke tests for :mod:`ingestion.csv_ingestor`."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    csv_path = tmp_path / "sample.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "name", "value"])
        writer.writerow(["1", "Alice", "100"])
        writer.writerow(["2", "Bob", "200"])
    return csv_path


def test_csv_ingestor_reads_rows(sample_csv_file: Path) -> None:
    from ingestion import csv_ingestor

    rows = csv_ingestor.load_csv(sample_csv_file)
    assert len(rows) == 3, "Rows must not be empty"
    assert rows[1][0] == "1", "Condition must be true"


def test_csv_ingestor_iterates_batches(sample_csv_file: Path) -> None:
    from ingestion import csv_ingestor

    # auto-detect encoding path
    rows = csv_ingestor.load_csv(sample_csv_file, encoding="auto")
    assert rows, "rows is not valid"
