"""
Tests for Metric Storage

Tests dual JSON + SQLite storage implementation.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from codex.metrics.duplication import (
    DuplicateBlock,
    DuplicationRatio,
)
from codex.metrics.storage import MetricStorage


class TestMetricStorage:
    """Test metric storage class"""

    def test_init_defaults(self):
        """Test initialization with defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_dir = Path(tmpdir) / "json"
            sqlite_path = Path(tmpdir) / "test.db"

            storage = MetricStorage(
                json_dir=json_dir,
                sqlite_path=sqlite_path,
            )

            assert storage.json_dir == json_dir, "json_dir is not valid"
            assert storage.sqlite_path == sqlite_path, "sqlite_path is not valid"
            assert storage.enable_json is True, "enable_json is not valid"
            assert storage.enable_sqlite is True, "enable_sqlite is not valid"
            assert json_dir.exists(), "Condition must be true"
            assert sqlite_path.exists(), "Condition must be true"

    def test_init_json_only(self):
        """Test initialization with JSON only"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=True,
                enable_sqlite=False,
            )

            assert storage.enable_json is True, "enable_json is not valid"
            assert storage.enable_sqlite is False, "enable_sqlite is not valid"

    def test_init_sqlite_only(self):
        """Test initialization with SQLite only"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=False,
                enable_sqlite=True,
            )

            assert storage.enable_json is False, "enable_json is not valid"
            assert storage.enable_sqlite is True, "enable_sqlite is not valid"

    def test_save_json(self):
        """Test saving metrics to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=True,
                enable_sqlite=False,
            )

            ratio = DuplicationRatio(
                ratio=0.15,
                total_lines=1000,
                duplicate_lines=150,
                files_scanned=10,
                files_with_duplicates=3,
            )

            result = storage.save(ratio, commit_sha="abc123")

            assert "json_path" in result, "Result must not be empty"
            json_path = Path(result["json_path"])
            assert json_path.exists(), "Condition must be true"

            # Verify JSON content
            with open(json_path) as f:
                data = json.load(f)

            assert data["duplication_ratio"] == 0.15, "Data must not be empty"
            assert data["total_lines"] == 1000, "Data must not be empty"
            assert data["duplicate_lines"] == 150, "Data must not be empty"
            assert data["commit_sha"] == "abc123", "Data must not be empty"

    def test_save_sqlite(self):
        """Test saving metrics to SQLite"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=False,
                enable_sqlite=True,
            )

            block = DuplicateBlock(
                hash="test123",
                lines=(10, 15),
                occurrences=[
                    {"file": "file1.py", "start": 10, "end": 15},
                    {"file": "file2.py", "start": 20, "end": 25},
                ],
                severity="medium",
                clone_type="Type-1",
            )

            ratio = DuplicationRatio(
                ratio=0.20,
                total_lines=500,
                duplicate_lines=100,
                duplicate_blocks=[block],
                files_scanned=5,
                files_with_duplicates=2,
            )

            result = storage.save(ratio, commit_sha="def456")

            assert "sqlite_id" in result, "Result must not be empty"
            metric_id = result["sqlite_id"]
            assert metric_id > 0, "metric_id must be greater than zero"

            # Verify SQLite content
            conn = sqlite3.connect(storage.sqlite_path)
            try:
                cursor = conn.cursor()

                # Check metric
                cursor.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
                row = cursor.fetchone()
                assert row is not None, "row must be initialized"
                assert row[2] == "def456", "Condition must be true"
                assert row[3] == 0.20, "Condition must be true"

                # Check blocks
                cursor.execute("SELECT * FROM duplicate_blocks WHERE metric_id = ?", (metric_id,))
                blocks = cursor.fetchall()
                assert len(blocks) == 1, "Blocks must not be empty"
                assert blocks[0][2] == "test123", "Condition must be true"

                # Check occurrences
                block_id = blocks[0][0]
                cursor.execute("SELECT * FROM occurrences WHERE block_id = ?", (block_id,))
                occs = cursor.fetchall()
                assert len(occs) == 2, "Occs must not be empty"

            finally:
                conn.close()

    def test_save_dual(self):
        """Test saving to both JSON and SQLite"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
            )

            ratio = DuplicationRatio(
                ratio=0.10,
                total_lines=2000,
                duplicate_lines=200,
            )

            result = storage.save(ratio)

            assert "json_path" in result, "Result must not be empty"
            assert "sqlite_id" in result, "Result must not be empty"
            assert Path(result["json_path"]).exists(), "Result must not be empty"

    def test_load_latest_empty(self):
        """Test loading from empty database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
            )

            latest = storage.load_latest()
            assert latest is None, "latest is not valid"

    def test_load_latest_with_data(self):
        """Test loading most recent metric"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
            )

            # Save two metrics
            ratio1 = DuplicationRatio(ratio=0.10, total_lines=1000, duplicate_lines=100)
            storage.save(ratio1, timestamp="2025-01-01T00:00:00Z")

            ratio2 = DuplicationRatio(ratio=0.15, total_lines=1000, duplicate_lines=150)
            storage.save(ratio2, timestamp="2025-01-02T00:00:00Z")

            # Load latest
            latest = storage.load_latest()

            assert latest is not None, "latest must be initialized"
            assert latest["ratio"] == 0.15, "Condition must be true"
            assert latest["timestamp"] == "2025-01-02T00:00:00Z", "Condition must be true"

    def test_query_history(self):
        """Test querying historical metrics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
            )

            # Save multiple metrics
            for i in range(5):
                ratio = DuplicationRatio(
                    ratio=0.10 + i * 0.05,
                    total_lines=1000,
                    duplicate_lines=100 + i * 50,
                )
                storage.save(ratio, timestamp=f"2025-01-0{i+1}T00:00:00Z")

            # Query all
            history = storage.query_history(limit=10)
            assert len(history) == 5, "History must not be empty"

            # Query limited
            history = storage.query_history(limit=2)
            assert len(history) == 2, "History must not be empty"

            # Query since timestamp
            history = storage.query_history(since="2025-01-03T00:00:00Z")
            assert len(history) == 3, "History must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
