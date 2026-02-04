"""
Tests for Metric Storage

Tests dual JSON + SQLite storage implementation.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.codex.metrics.duplication import (
    DuplicateBlock,
    DuplicationRatio,
)
from src.codex.metrics.storage import MetricStorage


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

            assert storage.json_dir == json_dir
            assert storage.sqlite_path == sqlite_path
            assert storage.enable_json is True
            assert storage.enable_sqlite is True
            assert json_dir.exists()
            assert sqlite_path.exists()

    def test_init_json_only(self):
        """Test initialization with JSON only"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=True,
                enable_sqlite=False,
            )

            assert storage.enable_json is True
            assert storage.enable_sqlite is False

    def test_init_sqlite_only(self):
        """Test initialization with SQLite only"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
                enable_json=False,
                enable_sqlite=True,
            )

            assert storage.enable_json is False
            assert storage.enable_sqlite is True

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

            assert "json_path" in result
            json_path = Path(result["json_path"])
            assert json_path.exists()

            # Verify JSON content
            with open(json_path) as f:
                data = json.load(f)

            assert data["duplication_ratio"] == 0.15
            assert data["total_lines"] == 1000
            assert data["duplicate_lines"] == 150
            assert data["commit_sha"] == "abc123"

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

            assert "sqlite_id" in result
            metric_id = result["sqlite_id"]
            assert metric_id > 0

            # Verify SQLite content
            conn = sqlite3.connect(storage.sqlite_path)
            try:
                cursor = conn.cursor()

                # Check metric
                cursor.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
                row = cursor.fetchone()
                assert row is not None
                assert row[2] == "def456"  # commit_sha
                assert row[3] == 0.20  # ratio

                # Check blocks
                cursor.execute("SELECT * FROM duplicate_blocks WHERE metric_id = ?", (metric_id,))
                blocks = cursor.fetchall()
                assert len(blocks) == 1
                assert blocks[0][2] == "test123"  # hash

                # Check occurrences
                block_id = blocks[0][0]
                cursor.execute("SELECT * FROM occurrences WHERE block_id = ?", (block_id,))
                occs = cursor.fetchall()
                assert len(occs) == 2

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

            assert "json_path" in result
            assert "sqlite_id" in result
            assert Path(result["json_path"]).exists()

    def test_load_latest_empty(self):
        """Test loading from empty database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = MetricStorage(
                json_dir=Path(tmpdir),
                sqlite_path=Path(tmpdir) / "test.db",
            )

            latest = storage.load_latest()
            assert latest is None

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

            assert latest is not None
            assert latest["ratio"] == 0.15
            assert latest["timestamp"] == "2025-01-02T00:00:00Z"

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
            assert len(history) == 5

            # Query limited
            history = storage.query_history(limit=2)
            assert len(history) == 2

            # Query since timestamp
            history = storage.query_history(since="2025-01-03T00:00:00Z")
            assert len(history) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
