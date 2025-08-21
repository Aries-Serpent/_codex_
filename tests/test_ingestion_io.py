"""Tests for file-based ingestion."""

from pathlib import Path

import pytest

from ingestion import Ingestor


def test_ingest_reads_file(tmp_path: Path) -> None:
    """Ingestor.ingest should return the contents of a text file."""

    file_path = tmp_path / "example.txt"
    file_path.write_text("hello world")

    ingestor = Ingestor()
    assert ingestor.ingest(file_path) == "hello world"


def test_ingest_missing_file(tmp_path: Path) -> None:
    """Ingestor.ingest should raise FileNotFoundError for missing files."""

    missing_path = tmp_path / "missing.txt"
    ingestor = Ingestor()

    with pytest.raises(FileNotFoundError):
        ingestor.ingest(missing_path)
