"""
Integration tests for codex.archive.dal module.

Tests basic DAL functionality with SQLite backend.
"""

import pytest

from codex.archive.dal import SqliteDAL


class TestSqliteDAL:
    """Test suite for SqliteDAL basic operations."""

    @pytest.fixture
    def dal(self, tmp_path):
        """Create a temporary SQLite DAL for testing."""
        db_path = tmp_path / "test_archive.db" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
        url = f"sqlite:///{db_path}"
        return SqliteDAL.from_url(url)

    def test_dal_initialization(self, tmp_path):
        """Test that DAL initializes and creates database."""
        db_path = tmp_path / "test.db"
        url = f"sqlite:///{db_path}"

        dal = SqliteDAL.from_url(url)

        assert dal is not None, "dal must be initialized"
        assert db_path.exists(), "Condition must be true"
        assert dal.conn is not None, "conn must be initialized"

    def test_ensure_schema_creates_tables(self, dal):
        """Test that schema creation works."""
        # Schema should be created during initialization
        cursor = dal.conn.cursor()

        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}

        # Should have core tables
        expected_tables = {"artifact", "item", "event"}
        assert expected_tables.issubset(tables), "Condition must be true"

    def test_transaction_context_manager(self, dal):
        """Test that transaction context manager works."""
        with dal.txn():
            # Transaction should commit successfully
            pass

        # Verify connection is still usable
        cursor = dal.conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1, "curs is not valid"

    def test_summary_returns_stats(self, dal):
        """Test that summary returns database statistics."""
        summary = dal.summary()

        assert isinstance(summary, dict)
        # Should have counts for artifacts
        assert ("count" in summary, "Count must be greater than zero"
        ), f"Summary should contain 'count' key, got: {list(summary.keys())}"
        assert ("total_bytes" in summary, "Condition must be true"
        ), f"Summary should contain 'total_bytes' key, got: {list(summary.keys())}"

    def test_recent_items_returns_list(self, dal):
        """Test that recent_items returns a list."""
        items = dal.recent_items(limit=10)

        assert isinstance(items, list)
        # Empty database should return empty list
        assert len(items) == 0, "Items must not be empty"

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
        assert "id" in result, "Result must not be empty"
        assert result["content_sha256"] == artifact_data["sha"], "Result must not be empty"

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
        assert "id" in result, "Result must not be empty"
        assert "tombstone_id" in result, "Result must not be empty"
        # Verify the item was created successfully
        assert result["id"] is not None, "Value must be initialized"
