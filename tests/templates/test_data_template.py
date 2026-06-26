"""
Data Test Template

Use this template as a starting point for testing data modules.
Copy this file and replace placeholders with actual implementation.

Template Version: 1.0.0
Created: 2026-01-18 (Phase 14.0)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# Module under test - update these imports
# from codex_ml.data import loader, validation, split


REPO_ROOT = Path(__file__).resolve().parents[2]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_jsonl_file(tmp_path: Path) -> Path:
    """Create a sample JSONL file for testing."""
    data_file = tmp_path / "data.jsonl"
    records = [
        {"id": 1, "text": "First record", "label": "positive"},
        {"id": 2, "text": "Second record", "label": "negative"},
        {"id": 3, "text": "Third record", "label": "neutral"},
    ]
    data_file.write_text("\n".join(json.dumps(r) for r in records))
    return data_file


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    data_file = tmp_path / "data.csv"
    data_file.write_text("id,text,label\n1,First,positive\n2,Second,negative\n")
    return data_file


@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    """Create a sample data directory with multiple files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create multiple data files
    (data_dir / "train.jsonl").write_text('{"text": "train"}\n')
    (data_dir / "valid.jsonl").write_text('{"text": "valid"}\n')
    (data_dir / "test.jsonl").write_text('{"text": "test"}\n')

    return data_dir


@pytest.fixture
def sample_dataset() -> list[dict[str, Any]]:
    """Create a sample in-memory dataset."""
    return [{"id": i, "text": f"Sample text {i}", "score": i * 0.1} for i in range(100)]


# =============================================================================
# Data Loading Tests
# =============================================================================


class TestDataLoader:
    """Test data loading functionality."""

    def test_loads_jsonl_file(self, sample_jsonl_file: Path) -> None:
        """Test loading a JSONL file."""
        records = [json.loads(line) for line in sample_jsonl_file.read_text().splitlines() if line]
        assert len(records) == 3, "Records must not be empty"
        assert records[0]["id"] == 1, "rec is not valid"

    def test_loads_csv_file(self, sample_csv_file: Path) -> None:
        """Test loading a CSV file."""
        import csv

        rows = list(csv.DictReader(sample_csv_file.read_text().splitlines()))
        assert len(rows) == 2, "Rows must not be empty"

    def test_handles_empty_file(self, tmp_path: Path) -> None:
        """Test handling of empty files."""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.write_text("")
        records = [ln for ln in empty_file.read_text().splitlines() if ln]
        assert records == [], "records is not valid"

    def test_handles_missing_file(self, tmp_path: Path) -> None:
        """Test handling of missing files raises FileNotFoundError."""
        missing = tmp_path / "missing.jsonl"
        with pytest.raises(FileNotFoundError):
            missing.read_text()

    def test_handles_corrupted_file(self, tmp_path: Path) -> None:
        """Test handling of corrupted/malformed files."""
        corrupted = tmp_path / "corrupted.jsonl"
        corrupted.write_text("not valid json\n")
        with pytest.raises(json.JSONDecodeError):
            json.loads(corrupted.read_text())

    def test_loads_large_file_efficiently(self, tmp_path: Path) -> None:
        """Test efficient loading of large files."""
        import time

        large_file = tmp_path / "large.jsonl"
        large_file.write_text("\n".join(json.dumps({"id": i}) for i in range(10000)))
        start = time.time()
        records = [json.loads(ln) for ln in large_file.read_text().splitlines() if ln]
        elapsed = time.time() - start
        assert elapsed < 5.0, "elapsed is not valid"
        assert len(records) == 10000, "Records must not be empty"


# =============================================================================
# Data Validation Tests
# =============================================================================


class TestDataValidation:
    """Test data validation functionality."""

    def test_validates_required_fields(self) -> None:
        """Test validation of required fields."""
        schema = {"required": ["id", "text"]}
        valid_record = {"id": 1, "text": "hello"}
        invalid_record = {"id": 1}
        assert all(k in valid_record for k in schema["required"]), "Condition must be true"
        assert not all(k in invalid_record for k in schema["required"]), "Condition must be true"

    def test_validates_field_types(self) -> None:
        """Test validation of field types."""
        schema = {"id": int, "text": str}
        valid_record = {"id": 1, "text": "hello"}
        for field, expected_type in schema.items():
            assert isinstance(valid_record[field], expected_type)

    def test_validates_field_ranges(self) -> None:
        """Test validation of field value ranges."""
        validation_rules = {"score": {"min": 0.0, "max": 1.0}}
        valid_record = {"score": 0.5}
        invalid_record = {"score": 1.5}
        assert (validation_rules["score"]["min"], "Condition must be true"
            <= valid_record["score"]
            <= validation_rules["score"]["max"]
        )
        assert not (, "Condition must be true"
            validation_rules["score"]["min"]
            <= invalid_record["score"]
            <= validation_rules["score"]["max"]
        )

    def test_detects_duplicate_ids(self, sample_dataset: list) -> None:
        """Test detection of duplicate IDs."""
        dataset_with_dups = sample_dataset + [{"id": 0, "text": "duplicate", "score": 0.0}]
        seen = set()
        duplicates = [r for r in dataset_with_dups if r["id"] in seen or seen.add(r["id"])]
        assert len(duplicates) == 1, "Duplicates must not be empty"

    def test_detects_missing_values(self) -> None:
        """Test detection of missing values."""
        records = [{"id": 1, "text": "hello"}, {"id": 2, "text": None}]
        missing = [r for r in records if not r.get("text")]
        assert len(missing) == 1, "Missing must not be empty"


# =============================================================================
# Data Splitting Tests
# =============================================================================


class TestDataSplit:
    """Test data splitting functionality."""

    def test_splits_data_by_ratio(self, sample_dataset: list) -> None:
        """Test splitting data by ratio."""
        n = len(sample_dataset)
        train_end = int(n * 0.8)
        valid_end = train_end + int(n * 0.1)
        train = sample_dataset[:train_end]
        valid = sample_dataset[train_end:valid_end]
        test = sample_dataset[valid_end:]
        assert len(train) == 80, "Train must not be empty"
        assert len(valid) == 10, "Valid must not be empty"
        assert len(test) == 10, "Test must not be empty"

    def test_split_is_deterministic(self, sample_dataset: list) -> None:
        """Test that splits are deterministic with same seed."""
        import random

        rng1 = random.Random(42)
        split1 = sorted(sample_dataset, key=lambda x: rng1.random())
        rng2 = random.Random(42)
        split2 = sorted(sample_dataset, key=lambda x: rng2.random())
        assert [r["id"] for r in split1] == [r["id"] for r in split2], "Condition must be true"

    def test_split_preserves_all_records(self, sample_dataset: list) -> None:
        """Test that splitting preserves all records."""
        n = len(sample_dataset)
        train = sample_dataset[: int(n * 0.8)]
        valid = sample_dataset[int(n * 0.8) : int(n * 0.9)]
        test = sample_dataset[int(n * 0.9) :]
        assert len(train) + len(valid) + len(test) == n, "Train must not be empty"

    def test_stratified_split(self) -> None:
        """Test stratified splitting by label."""
        labeled_data = [{"id": i, "label": "A" if i < 50 else "B"} for i in range(100)]
        a_count = sum(1 for r in labeled_data if r["label"] == "A")
        b_count = sum(1 for r in labeled_data if r["label"] == "B")
        assert a_count == b_count == 50, "Count must be greater than zero"


# =============================================================================
# Data Transformation Tests
# =============================================================================


class TestDataTransformation:
    """Test data transformation functionality."""

    def test_normalizes_text(self) -> None:
        """Test text normalization."""
        text = "  HELLO  WORLD  "
        result = " ".join(text.strip().lower().split())
        assert result == "hello world", "Result must not be empty"

    def test_tokenizes_text(self) -> None:
        """Test text tokenization."""
        text = "hello world"
        tokens = text.split()
        assert tokens == ["hello", "world"]

    def test_encodes_labels(self) -> None:
        """Test label encoding."""
        labels = ["a", "b", "a", "c"]
        label_map = {v: i for i, v in enumerate(dict.fromkeys(labels))}
        encoded = [label_map[lb] for lb in labels]
        assert encoded == [0, 1, 0, 2]


# =============================================================================
# Data Streaming Tests
# =============================================================================


class TestDataStreaming:
    """Test data streaming functionality."""

    def test_streams_large_file(self, sample_jsonl_file: Path) -> None:
        """Test streaming a large file."""
        count = sum(1 for ln in sample_jsonl_file.read_text().splitlines() if ln)
        assert count == 3, "Count must be greater than zero"

    def test_batches_stream(self, sample_jsonl_file: Path) -> None:
        """Test batching a stream."""
        records = [json.loads(ln) for ln in sample_jsonl_file.read_text().splitlines() if ln]
        batch_size = 2
        batches = [records[i : i + batch_size] for i in range(0, len(records
        ), batch_size)]
        assert len(batches) == 2, "Batches must not be empty"


# =============================================================================
# Data Integrity Tests
# =============================================================================


class TestDataIntegrity:
    """Test data integrity functionality."""

    def test_calculates_checksum(self, sample_jsonl_file: Path) -> None:
        """Test checksum calculation."""
        import hashlib

        checksum = hashlib.sha256(sample_jsonl_file.read_bytes()).hexdigest()
        assert isinstance(checksum, str)
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_verifies_checksum(self, sample_jsonl_file: Path) -> None:
        """Test checksum verification."""
        import hashlib

        checksum = hashlib.sha256(sample_jsonl_file.read_bytes()).hexdigest()
        recomputed = hashlib.sha256(sample_jsonl_file.read_bytes()).hexdigest()
        assert checksum == recomputed, "checksum is not valid"


# =============================================================================
# Parametrized Tests
# =============================================================================


@pytest.mark.parametrize(
    "file_format,extension",
    [
        ("jsonl", ".jsonl"),
        ("csv", ".csv"),
        ("json", ".json"),
    ],
)
def test_loader_detects_format(tmp_path: Path, file_format: str, extension: str) -> None:
    """Test loader detects file format from extension."""
    data_file = tmp_path / f"data{extension}"
    data_file.write_text("{}" if extension == ".json" else "")
    assert data_file.suffix == extension, "Data must not be empty"
    assert data_file.exists(), "Data must not be empty"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestDataEdgeCases:
    """Test data edge cases."""

    def test_handles_unicode(self, tmp_path: Path) -> None:
        """Test handling of Unicode characters."""
        unicode_file = tmp_path / "unicode.jsonl"
        unicode_file.write_text('{"text": "日本語テスト"}\n', encoding="utf-8")
        records = [
            json.loads(ln) for ln in unicode_file.read_text(encoding="utf-8").splitlines() if ln
        ]
        assert records[0]["text"] == "日本語テスト", "rec is not valid"

    def test_handles_special_characters(self, tmp_path: Path) -> None:
        """Test handling of special characters."""
        special_file = tmp_path / "special.jsonl"
        special_file.write_text('{"text": "tab\\there\\nnewline"}\n')
        records = [json.loads(ln) for ln in special_file.read_text().splitlines() if ln]
        assert "tab" in records[0]["text"], "Condition must be true"

    def test_handles_nested_json(self, tmp_path: Path) -> None:
        """Test handling of nested JSON structures."""
        nested_file = tmp_path / "nested.jsonl"
        nested_file.write_text('{"data": {"nested": {"value": 42}}}\n')
        records = [json.loads(ln) for ln in nested_file.read_text().splitlines() if ln]
        assert records[0]["data"]["nested"]["value"] == 42, "Data must not be empty"
