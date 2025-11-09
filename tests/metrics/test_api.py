"""Tests for metrics API module."""

from __future__ import annotations

import json
import sqlite3

import pytest

from codex_ml.metrics.api import (
    exact_match,
    f1,
    get_metric,
    init_metric_plugins,
    list_metrics,
    load_ndjson_logs,
    perplexity,
    register_metric,
    summarize_ndjson_to_csv,
    summarize_ndjson_to_sqlite,
    token_accuracy,
)


class TestRegistryFunctions:
    """Tests for metric registry functions."""

    def test_register_metric(self):
        """Test registering a custom metric."""

        def custom_metric(preds, targets, **kwargs):
            return 0.5

        # Register the metric
        register_metric("test_custom", custom_metric)

        # Verify it's registered
        assert "test_custom" in list_metrics()

        # Get and verify
        retrieved = get_metric("test_custom")
        assert retrieved([1, 2], [1, 2]) == 0.5

    def test_get_nonexistent_metric_raises_error(self):
        """Test that getting a non-existent metric raises KeyError."""
        with pytest.raises(KeyError):
            get_metric("nonexistent_metric_xyz")

    def test_list_metrics(self):
        """Test listing all metrics."""
        metrics = list_metrics()

        # Should be a list
        assert isinstance(metrics, list)

        # Should contain some built-in metrics
        assert len(metrics) > 0

    def test_init_metric_plugins(self):
        """Test initializing metric plugins."""
        # Should not raise an error
        count = init_metric_plugins()

        # Should return a number
        assert isinstance(count, int)
        assert count >= 0


class TestBuiltInMetrics:
    """Tests for built-in metric functions."""

    def test_token_accuracy_basic(self):
        """Test basic token accuracy calculation."""
        preds = [1, 2, 3, 4, 5]
        targets = [1, 2, 3, 4, 5]

        # Perfect accuracy
        result = token_accuracy(preds, targets)
        assert isinstance(result, (int, float))
        assert result == 1.0

    def test_token_accuracy_partial(self):
        """Test partial token accuracy."""
        preds = [1, 2, 3, 4, 5]
        targets = [1, 2, 0, 4, 0]

        result = token_accuracy(preds, targets)
        assert isinstance(result, (int, float))
        assert 0.0 <= result <= 1.0
        assert result == 0.6  # 3 out of 5 correct

    def test_perplexity_basic(self):
        """Test perplexity metric."""
        # Note: perplexity implementation details vary
        # Just verify it returns a numeric value
        preds = [1, 2, 3]
        targets = [1, 2, 3]

        result = perplexity(preds, targets)
        assert isinstance(result, (int, float))
        assert result >= 0

    def test_exact_match_perfect(self):
        """Test exact match with perfect matches."""
        preds = [[1, 2, 3], [4, 5, 6]]
        targets = [[1, 2, 3], [4, 5, 6]]

        result = exact_match(preds, targets)
        assert result == 1.0

    def test_exact_match_partial(self):
        """Test exact match with partial matches."""
        preds = [[1, 2, 3], [4, 5, 6]]
        targets = [[1, 2, 3], [4, 5, 0]]

        result = exact_match(preds, targets)
        assert result == 0.5  # 1 out of 2 match

    def test_f1_basic(self):
        """Test F1 score calculation."""
        preds = [1, 1, 0, 1, 0]
        targets = [1, 0, 0, 1, 0]

        result = f1(preds, targets)
        assert isinstance(result, (int, float))
        assert 0.0 <= result <= 1.0


class TestNDJSONLoading:
    """Tests for NDJSON log loading."""

    def test_load_ndjson_logs_basic(self, tmp_path):
        """Test loading NDJSON logs from a file."""
        # Create test NDJSON file
        ndjson_file = tmp_path / "test.ndjson"
        logs = [
            {"epoch": 1, "loss": 0.5, "accuracy": 0.8},
            {"epoch": 2, "loss": 0.3, "accuracy": 0.9},
            {"epoch": 3, "loss": 0.2, "accuracy": 0.95},
        ]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        # Load logs
        loaded = load_ndjson_logs(ndjson_file)

        assert len(loaded) == 3
        assert loaded[0]["epoch"] == 1
        assert loaded[1]["loss"] == 0.3
        assert loaded[2]["accuracy"] == 0.95

    def test_load_ndjson_logs_nonexistent_file(self, tmp_path):
        """Test loading from non-existent file returns empty list."""
        result = load_ndjson_logs(tmp_path / "nonexistent.ndjson")
        assert result == []

    def test_load_ndjson_logs_with_empty_lines(self, tmp_path):
        """Test that empty lines are skipped."""
        ndjson_file = tmp_path / "test.ndjson"

        with ndjson_file.open("w") as f:
            f.write('{"a": 1}\n')
            f.write('\n')  # Empty line
            f.write('{"a": 2}\n')

        loaded = load_ndjson_logs(ndjson_file)
        assert len(loaded) == 2

    def test_load_ndjson_logs_with_malformed_json(self, tmp_path):
        """Test that malformed JSON lines are skipped."""
        ndjson_file = tmp_path / "test.ndjson"

        with ndjson_file.open("w") as f:
            f.write('{"a": 1}\n')
            f.write('not valid json\n')  # Malformed line
            f.write('{"a": 2}\n')

        loaded = load_ndjson_logs(ndjson_file)
        assert len(loaded) == 2
        assert loaded[0]["a"] == 1
        assert loaded[1]["a"] == 2


class TestNDJSONToCSV:
    """Tests for NDJSON to CSV conversion."""

    def test_summarize_ndjson_to_csv_basic(self, tmp_path):
        """Test basic NDJSON to CSV conversion."""
        # Create test NDJSON file
        ndjson_file = tmp_path / "test.ndjson"
        csv_file = tmp_path / "output.csv"

        logs = [
            {"epoch": 1, "loss": 0.5, "accuracy": 0.8},
            {"epoch": 2, "loss": 0.3, "accuracy": 0.9},
        ]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        # Convert to CSV
        count = summarize_ndjson_to_csv(ndjson_file, csv_file)

        assert count == 2
        assert csv_file.exists()

        # Verify CSV content
        import csv
        with csv_file.open("r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["epoch"] == "1"
        assert rows[1]["loss"] == "0.3"

    def test_summarize_ndjson_to_csv_custom_columns(self, tmp_path):
        """Test CSV conversion with custom columns."""
        ndjson_file = tmp_path / "test.ndjson"
        csv_file = tmp_path / "output.csv"

        logs = [
            {"epoch": 1, "loss": 0.5, "accuracy": 0.8, "extra": "data"},
            {"epoch": 2, "loss": 0.3, "accuracy": 0.9, "extra": "more"},
        ]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        # Convert with specific columns
        count = summarize_ndjson_to_csv(ndjson_file, csv_file, columns=["epoch", "loss"])

        assert count == 2

        # Verify only specified columns in CSV
        import csv
        with csv_file.open("r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert list(rows[0].keys()) == ["epoch", "loss"]

    def test_summarize_ndjson_to_csv_empty_file(self, tmp_path):
        """Test CSV conversion with empty NDJSON file."""
        ndjson_file = tmp_path / "empty.ndjson"
        csv_file = tmp_path / "output.csv"

        # Create empty file
        ndjson_file.write_text("", encoding="utf-8")

        count = summarize_ndjson_to_csv(ndjson_file, csv_file)

        assert count == 0
        assert csv_file.exists()
        # Empty CSV file
        assert csv_file.read_text(encoding="utf-8") == ""


class TestNDJSONToSQLite:
    """Tests for NDJSON to SQLite conversion."""

    def test_summarize_ndjson_to_sqlite_basic(self, tmp_path):
        """Test basic NDJSON to SQLite conversion."""
        ndjson_file = tmp_path / "test.ndjson"
        db_file = tmp_path / "output.db"

        logs = [
            {"epoch": 1, "loss": 0.5, "accuracy": 0.8},
            {"epoch": 2, "loss": 0.3, "accuracy": 0.9},
        ]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        # Convert to SQLite
        count = summarize_ndjson_to_sqlite(ndjson_file, db_file)

        assert count == 2
        assert db_file.exists()

        # Verify database content
        conn = sqlite3.connect(str(db_file))
        try:
            cursor = conn.execute("SELECT * FROM metrics")
            rows = cursor.fetchall()
            assert len(rows) == 2
        finally:
            conn.close()

    def test_summarize_ndjson_to_sqlite_custom_table(self, tmp_path):
        """Test SQLite conversion with custom table name."""
        ndjson_file = tmp_path / "test.ndjson"
        db_file = tmp_path / "output.db"

        logs = [{"epoch": 1, "loss": 0.5}]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        # Convert with custom table name
        count = summarize_ndjson_to_sqlite(ndjson_file, db_file, table_name="custom_table")

        assert count == 1

        # Verify custom table exists
        conn = sqlite3.connect(str(db_file))
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "custom_table" in tables
        finally:
            conn.close()

    def test_summarize_ndjson_to_sqlite_empty_file(self, tmp_path):
        """Test SQLite conversion with empty NDJSON file."""
        ndjson_file = tmp_path / "empty.ndjson"
        db_file = tmp_path / "output.db"

        ndjson_file.write_text("", encoding="utf-8")

        count = summarize_ndjson_to_sqlite(ndjson_file, db_file)

        assert count == 0
        # Database file should not be created for empty input
        assert not db_file.exists()

    def test_summarize_ndjson_to_sqlite_complex_values(self, tmp_path):
        """Test SQLite conversion with complex nested values."""
        ndjson_file = tmp_path / "test.ndjson"
        db_file = tmp_path / "output.db"

        logs = [
            {"epoch": 1, "config": {"lr": 0.01, "batch_size": 32}},
            {"epoch": 2, "config": {"lr": 0.005, "batch_size": 32}},
        ]

        with ndjson_file.open("w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        count = summarize_ndjson_to_sqlite(ndjson_file, db_file)

        assert count == 2

        # Verify nested values are JSON serialized
        conn = sqlite3.connect(str(db_file))
        try:
            cursor = conn.execute("SELECT config FROM metrics WHERE epoch='1'")
            row = cursor.fetchone()
            # Should be JSON string
            config = json.loads(row[0])
            assert config["lr"] == 0.01
        finally:
            conn.close()
