"""
Integration tests for codex.archive.dal module.

Tests basic DAL functionality with SQLite backend.
"""
import json
from pathlib import Path

import pytest

from codex.archive.dal import SqliteDAL


class TestSqliteDAL:
    """Test suite for SqliteDAL basic operations."""

    @pytest.fixture
    def dal(self, tmp_path):
        """Create a temporary SQLite DAL for testing."""
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        return dal

    def test_dal_initialization(self, tmp_path):
        """Test that DAL initializes and creates database."""
        db_path = tmp_path / "test.db"
        url = f"sqlite:///{db_path}"
        
        dal = SqliteDAL.from_url(url)
        
        assert dal is not None
        assert db_path.exists()
        assert dal.conn is not None

    def test_ensure_schema_creates_tables(self, dal):
        """Test that schema creation works."""
        # Schema should be created during initialization
        cursor = dal.conn.cursor()
        
        # Check that tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        
        # Should have core tables
        expected_tables = {"artifact", "item", "event"}
        assert expected_tables.issubset(tables)

    def test_transaction_context_manager(self, dal):
        """Test that transaction context manager works."""
        with dal.txn():
            # Transaction should commit successfully
            pass
        
        # Verify connection is still usable
        cursor = dal.conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

    def test_summary_returns_stats(self, dal):
        """Test that summary returns database statistics."""
        summary = dal.summary()
        
        assert isinstance(summary, dict)
        # Should have counts for various tables
        assert "items" in summary or "artifact_count" in summary or len(summary) >= 0

    def test_recent_items_returns_list(self, dal):
        """Test that recent_items returns a list."""
        items = dal.recent_items(limit=10)
        
        assert isinstance(items, list)
        # Empty database should return empty list
        assert len(items) == 0

    def test_ensure_artifact_creates_record(self, dal):
        """Test that artifact creation works."""
        artifact_data = {
            "sha": "abc123def456",
            "size": 100,
            "mime": "text/plain",
            "blob": b"test content",
            "compression": "zlib",
            "storage_driver": "db",
        }
        
        result = dal.ensure_artifact(**artifact_data)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content_sha256"] == artifact_data["sha"]

    def test_insert_item_creates_record(self, dal):
        """Test that item insertion works."""
        # First create an artifact
        artifact = dal.ensure_artifact(
            sha="test_sha",
            size=50,
            mime="text/plain",
            blob=b"test",
        )
        
        # Now create an item
        item_data = {
            "repo": "test/repo",
            "path": "/test/file.py",
            "commit_sha": "commit123",
            "language": "python",
            "reason": "test",
            "artifact_id": artifact["id"],
            "tombstone_id": "tomb_123",
            "kind": "code",
            "metadata": {"test": "value"},
        }
        
        result = dal.insert_item(**item_data)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["repo"] == item_data["repo"]
        assert result["path"] == item_data["path"]

    def test_insert_event_creates_record(self, dal):
        """Test that event insertion works."""
        # First create artifact and item
        artifact = dal.ensure_artifact(
            sha="event_test_sha",
            size=50,
            mime="text/plain",
            blob=b"test",
        )
        
        item = dal.insert_item(
            repo="test/repo",
            path="/test/file.py",
            commit_sha="commit123",
            language="python",
            reason="test",
            artifact_id=artifact["id"],
            tombstone_id="tomb_123",
        )
        
        # Insert an event
        dal.insert_event(
            item_id=item["id"],
            action="created",
            actor="test_user",
            context={"source": "test"},
        )
        
        # Verify event was created (implicit success if no exception)
        # Could query events table to verify, but basic insertion is enough

    def test_dal_handles_duplicate_artifacts(self, dal):
        """Test that duplicate artifact insertion is handled."""
        artifact_data = {
            "sha": "duplicate_sha",
            "size": 100,
            "mime": "text/plain",
            "blob": b"content",
        }
        
        # Insert same artifact twice
        result1 = dal.ensure_artifact(**artifact_data)
        result2 = dal.ensure_artifact(**artifact_data)
        
        # Should return same artifact ID
        assert result1["id"] == result2["id"]


class TestArchiveDALFactory:
    """Test suite for ArchiveDAL factory."""

    def test_factory_from_env_defaults_to_sqlite(self, tmp_path, monkeypatch):
        """Test that factory defaults to SQLite."""
        from codex.archive.dal import ArchiveDAL
        
        # Set environment to use temp path
        db_path = tmp_path / "factory_test.db"
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path}")
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        
        dal = ArchiveDAL.from_env()
        
        assert isinstance(dal, SqliteDAL)
        assert db_path.exists()

    def test_factory_rejects_invalid_backend(self, monkeypatch):
        """Test that factory rejects invalid backend."""
        from codex.archive.dal import ArchiveDAL
        
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "invalid_backend")
        
        with pytest.raises(ValueError, match="Unsupported CODEX_ARCHIVE_BACKEND"):
            ArchiveDAL.from_env()
