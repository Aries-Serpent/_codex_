"""Tests for local file loaders."""

from __future__ import annotations

import tempfile
from pathlib import Path

from codex_ml.data.local_files import (
    load_csv,
    load_json,
    load_jsonl,
    save_csv,
    save_json,
    save_jsonl,
)


def test_load_jsonl():
    """Test loading JSONL file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write('{"text": "hello", "label": 0}\n')
        f.write('{"text": "world", "label": 1}\n')
        f.write("\n")  # Empty line should be skipped
        f.write('{"text": "test", "label": 2}\n')
        path = f.name

    try:
        records = load_jsonl(path)

        assert len(records) == 3, "Records must not be empty"
        assert records[0]["text"] == "hello", "rec is not valid"
        assert records[0]["label"] == 0, "rec is not valid"
        assert records[1]["text"] == "world", "rec is not valid"
        assert records[2]["label"] == 2, "rec is not valid"
    finally:
        Path(path).unlink()


def test_load_json():
    """Test loading JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"model": "gpt2", "lr": 0.001, "epochs": 10}')
        path = f.name

    try:
        data = load_json(path)

        assert isinstance(data, dict)
        assert data["model"] == "gpt2", "Data must not be empty"
        assert data["lr"] == 0.001, "Data must not be empty"
        assert data["epochs"] == 10, "Data must not be empty"
    finally:
        Path(path).unlink()


def test_load_json_array():
    """Test loading JSON array."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('[{"id": 1}, {"id": 2}, {"id": 3}]')
        path = f.name

    try:
        data = load_json(path)

        assert isinstance(data, list)
        assert len(data) == 3, "Data must not be empty"
        assert data[0]["id"] == 1, "Data must not be empty"
    finally:
        Path(path).unlink()


def test_load_csv():
    """Test loading CSV file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("text,label\n")
        f.write("hello,0\n")
        f.write("world,1\n")
        path = f.name

    try:
        records = load_csv(path)

        assert len(records) == 2, "Records must not be empty"
        assert records[0]["text"] == "hello", "rec is not valid"
        assert records[0]["label"] == "0", "rec is not valid"
        assert records[1]["text"] == "world", "rec is not valid"
    finally:
        Path(path).unlink()


def test_load_csv_custom_delimiter():
    """Test loading CSV with custom delimiter."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
        f.write("text\tlabel\n")
        f.write("hello\t0\n")
        f.write("world\t1\n")
        path = f.name

    try:
        records = load_csv(path, delimiter="\t")

        assert len(records) == 2, "Records must not be empty"
        assert records[0]["text"] == "hello", "rec is not valid"
        assert records[0]["label"] == "0", "rec is not valid"
    finally:
        Path(path).unlink()


def test_save_and_load_jsonl():
    """Test saving and loading JSONL roundtrip."""
    records = [
        {"text": "hello", "label": 0},
        {"text": "world", "label": 1},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.jsonl"

        save_jsonl(records, path)
        loaded = load_jsonl(path)

        assert loaded == records, "loaded is not valid"


def test_save_and_load_json():
    """Test saving and loading JSON roundtrip."""
    data = {"model": "gpt2", "lr": 0.001}

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.json"

        save_json(data, path)
        loaded = load_json(path)

        assert loaded == data, "Data must not be empty"


def test_save_and_load_csv():
    """Test saving and loading CSV roundtrip."""
    records = [
        {"text": "hello", "label": "0"},
        {"text": "world", "label": "1"},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.csv"

        save_csv(records, path)
        loaded = load_csv(path)

        assert loaded == records, "loaded is not valid"


def test_save_creates_parent_directory():
    """Test that save functions create parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = Path(tmpdir) / "nested" / "dir" / "file.jsonl"

        assert not nested_path.parent.exists(), "Condition must be true"

        save_jsonl([{"test": "data"}], nested_path)

        assert nested_path.exists(), "Condition must be true"
        assert nested_path.parent.exists(), "Condition must be true"
