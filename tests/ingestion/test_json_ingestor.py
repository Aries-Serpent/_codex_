"""Smoke tests for :mod:`ingestion.json_ingestor`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_json_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample.json"
    path.write_text(json.dumps([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]))
    return path


@pytest.fixture
def sample_jsonl_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample.jsonl"
    path.write_text("\n".join([json.dumps({"id": i, "text": f"row {i}"}) for i in range(3)]))
    return path


def test_json_ingestor_reads_list(sample_json_file: Path) -> None:
    from ingestion import json_ingestor

    rows = json_ingestor.load_json(sample_json_file)
    assert len(rows) == 2, "Rows must not be empty"
    assert rows[0]["id"] == 1, "Condition must be true"


def test_json_ingestor_reads_jsonl(sample_jsonl_file: Path) -> None:
    from ingestion import json_ingestor

    with pytest.raises(Exception):
        json_ingestor.load_json(sample_jsonl_file)
