"""
Integration tests for archive.dal module.

Tests database operations with temporary SQLite databases.
"""
import tempfile
from pathlib import Path

import pytest


class TestArchiveDALBasics:
    """Test basic archive DAL operations."""

    def test_dal_imports(self):
        """Test DAL module imports successfully."""
        from codex.archive.dal import ArchiveDAL, SqliteDAL
        
        assert ArchiveDAL is not None
        assert SqliteDAL is not None

    def test_sqlite_dal_creates_database(self, tmp_path):
        """Test SqliteDAL creates database file."""
        from codex.archive.dal import SqliteDAL
        
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        
        assert db_path.exists()
        dal.conn.close()

    def test_dal_from_env_factory(self, tmp_path, monkeypatch):
        """Test ArchiveDAL.from_env factory method."""
        from codex.archive.dal import ArchiveDAL
        
        db_path = tmp_path / "test_archive.db"
        monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
        monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path}")
        
        dal = ArchiveDAL.from_env()
        
        assert dal is not None
        assert hasattr(dal, 'conn')
        dal.conn.close()

    def test_dal_schema_tables_exist(self, tmp_path):
        """Test that schema creates required tables."""
        from codex.archive.dal import SqliteDAL
        
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        
        # Check that main tables exist
        cursor = dal.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        # Should have at least these tables
        assert "item" in tables
        assert "artifact" in tables
        
        dal.conn.close()

    def test_dal_artifact_table_structure(self, tmp_path):
        """Test artifact table has expected columns."""
        from codex.archive.dal import SqliteDAL
        
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        
        # Check artifact table structure
        cursor = dal.conn.execute("PRAGMA table_info(artifact)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Should have key columns
        assert "id" in columns
        assert "content_sha256" in columns
        assert "storage_driver" in columns
        
        dal.conn.close()


class TestArchiveDALTransactions:
    """Test transaction handling."""

    def test_transaction_context_manager(self, tmp_path):
        """Test transaction context manager works."""
        from codex.archive.dal import SqliteDAL
        
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        
        # Test that txn() returns a context manager
        txn = dal.txn()
        assert hasattr(txn, '__enter__')
        assert hasattr(txn, '__exit__')
        
        # Test using it
        with dal.txn():
            # Should not raise
            pass
        
        dal.conn.close()

    def test_multiple_transactions(self, tmp_path):
        """Test multiple sequential transactions."""
        from codex.archive.dal import SqliteDAL
        
        db_path = tmp_path / "test_archive.db"
        url = f"sqlite:///{db_path}"
        dal = SqliteDAL.from_url(url)
        
        # Multiple transactions should work
        with dal.txn():
            pass
        
        with dal.txn():
            pass
        
        with dal.txn():
            pass
        
        dal.conn.close()
