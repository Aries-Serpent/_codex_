"""Comprehensive tests for codex_ml.cli.metrics_cli module.

Tests cover:
- NDJSON ingestion
- SQL identifier validation
- CSV/Parquet export
- SQLite storage
- Error handling
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import module under test
try:
    from codex_ml.cli import metrics_cli
except ImportError:
    pytest.skip("metrics_cli module not available", allow_module_level=True)


@pytest.fixture
def mock_metrics_data(tmp_path):
    """Create mock metrics NDJSON file."""
    metrics_file = tmp_path / "metrics.ndjson"
    metrics_file.write_text(
        '\n'.join([
            '{"epoch": 0, "loss": 2.5, "accuracy": 0.3}',
            '{"epoch": 1, "loss": 1.8, "accuracy": 0.5}',
            '{"epoch": 2, "loss": 1.2, "accuracy": 0.7}',
        ]),
        encoding="utf-8",
    )
    return metrics_file


class TestValidateTable:
    """Test _validate_table SQL identifier validation."""

    def test_validate_table_with_valid_name(self):
        """Test validation with valid table name."""
        if hasattr(metrics_cli, "_validate_table"):
            result = metrics_cli._validate_table("metrics_table")
            assert result == "metrics_table"

    def test_validate_table_with_underscores(self):
        """Test validation with underscores."""
        if hasattr(metrics_cli, "_validate_table"):
            result = metrics_cli._validate_table("my_metrics_table")
            assert result == "my_metrics_table"

    def test_validate_table_with_numbers(self):
        """Test validation with numbers."""
        if hasattr(metrics_cli, "_validate_table"):
            result = metrics_cli._validate_table("metrics123")
            assert result == "metrics123"

    def test_validate_table_with_invalid_name(self):
        """Test validation rejects invalid names."""
        if hasattr(metrics_cli, "_validate_table"):
            with pytest.raises(SystemExit):
                metrics_cli._validate_table("invalid-table-name")

    def test_validate_table_with_spaces(self):
        """Test validation rejects names with spaces."""
        if hasattr(metrics_cli, "_validate_table"):
            with pytest.raises(SystemExit):
                metrics_cli._validate_table("invalid table")

    def test_validate_table_with_special_chars(self):
        """Test validation rejects special characters."""
        if hasattr(metrics_cli, "_validate_table"):
            with pytest.raises(SystemExit):
                metrics_cli._validate_table("table$name")

    def test_validate_table_allow_unsafe(self):
        """Test validation with allow_unsafe flag."""
        if hasattr(metrics_cli, "_validate_table"):
            result = metrics_cli._validate_table("invalid-name", allow_unsafe=True)
            assert result == "invalid-name"


class TestIterNdjson:
    """Test _iter_ndjson NDJSON parsing."""

    def test_iter_ndjson_basic(self, mock_metrics_data):
        """Test basic NDJSON iteration."""
        if hasattr(metrics_cli, "_iter_ndjson"):
            records = list(metrics_cli._iter_ndjson(mock_metrics_data))
            assert len(records) == 3
            assert all(isinstance(r, dict) for r in records)

    def test_iter_ndjson_skips_empty_lines(self, tmp_path):
        """Test NDJSON iteration skips empty lines."""
        if hasattr(metrics_cli, "_iter_ndjson"):
            data_file = tmp_path / "data.ndjson"
            data_file.write_text(
                '{"a": 1}\n\n{"b": 2}\n',
                encoding="utf-8",
            )
            records = list(metrics_cli._iter_ndjson(data_file))
            assert len(records) == 2

    def test_iter_ndjson_with_empty_file(self, tmp_path):
        """Test NDJSON iteration with empty file."""
        if hasattr(metrics_cli, "_iter_ndjson"):
            empty_file = tmp_path / "empty.ndjson"
            empty_file.write_text("", encoding="utf-8")
            records = list(metrics_cli._iter_ndjson(empty_file))
            assert len(records) == 0


class TestFlattenRecords:
    """Test _flatten_records metric flattening."""

    def test_flatten_records_basic(self):
        """Test basic record flattening."""
        if hasattr(metrics_cli, "_flatten_records"):
            records = [{"epoch": 0, "loss": 1.5, "accuracy": 0.8}]
            rows = list(metrics_cli._flatten_records(records, "run_001"))
            assert len(rows) >= 2  # loss and accuracy
            assert all("key" in row for row in rows)
            assert all("value" in row for row in rows)

    def test_flatten_records_with_run_id(self):
        """Test flattening includes run_id."""
        if hasattr(metrics_cli, "_flatten_records"):
            records = [{"epoch": 0, "loss": 1.5}]
            rows = list(metrics_cli._flatten_records(records, "run_123"))
            assert all(row["run_id"] == "run_123" for row in rows)

    def test_flatten_records_with_none_run_id(self):
        """Test flattening with None run_id."""
        if hasattr(metrics_cli, "_flatten_records"):
            records = [{"epoch": 0, "loss": 1.5}]
            rows = list(metrics_cli._flatten_records(records, None))
            assert all(row["run_id"] is None for row in rows)


class TestCoerceEpoch:
    """Test _coerce_epoch type conversion."""

    def test_coerce_epoch_with_int(self):
        """Test epoch coercion with int."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch(5)
            assert result == 5

    def test_coerce_epoch_with_float(self):
        """Test epoch coercion with float."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch(5.0)
            assert result == 5.0

    def test_coerce_epoch_with_string_int(self):
        """Test epoch coercion with string int."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch("10")
            assert result == 10

    def test_coerce_epoch_with_string_float(self):
        """Test epoch coercion with string float."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch("10.5")
            assert result == 10.5

    def test_coerce_epoch_with_none(self):
        """Test epoch coercion with None."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch(None)
            assert result is None

    def test_coerce_epoch_with_empty_string(self):
        """Test epoch coercion with empty string."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch("")
            assert result is None

    def test_coerce_epoch_with_whitespace(self):
        """Test epoch coercion with whitespace."""
        if hasattr(metrics_cli, "_coerce_epoch"):
            result = metrics_cli._coerce_epoch("  ")
            assert result is None


class TestWriteCsv:
    """Test _write_csv CSV export."""

    def test_write_csv_basic(self, tmp_path):
        """Test basic CSV writing."""
        if hasattr(metrics_cli, "_write_csv"):
            rows = [
                {"run_id": "r1", "epoch": 0, "key": "loss", "value": 1.5},
                {"run_id": "r1", "epoch": 1, "key": "loss", "value": 1.0},
            ]
            output = tmp_path / "output.csv"
            written = metrics_cli._write_csv(rows, output)
            assert written == 2
            assert output.exists()

    def test_write_csv_creates_parent_dir(self, tmp_path):
        """Test CSV writing creates parent directories."""
        if hasattr(metrics_cli, "_write_csv"):
            rows = [{"run_id": "r1", "epoch": 0, "key": "loss", "value": 1.5}]
            output = tmp_path / "subdir" / "output.csv"
            metrics_cli._write_csv(rows, output)
            assert output.exists()

    def test_write_csv_empty_rows(self, tmp_path):
        """Test CSV writing with empty rows."""
        if hasattr(metrics_cli, "_write_csv"):
            output = tmp_path / "empty.csv"
            written = metrics_cli._write_csv([], output)
            assert written == 0
            assert output.exists()
