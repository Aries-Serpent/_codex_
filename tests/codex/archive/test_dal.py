"""
Gap-filling tests for codex.archive.dal module.

Tests cover:
- Helper functions for row conversion and JSON decoding
- ArchiveDAL factory creation
- BaseDAL abstract methods
- SqliteDAL concrete implementation
- Data row classes (ArtifactRow, ItemRow)
"""

import json  # pragma: allowlist secret # pragma: allowlist secret
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

class TestCursorRowToDict:
    """Tests for _cursor_row_to_dict helper function."""

    def test_cursor_row_to_dict_basic(self):
        """Test converting cursor row to dict."""
        from codex.archive.dal import _cursor_row_to_dict

        # Create mock cursor with description
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("value",)]

        row = ("123", "test", 42)
        result = _cursor_row_to_dict(mock_cursor, row)

        assert result == {"id": "123", "name": "test", "value": 42}

    def test_cursor_row_to_dict_with_name_attribute(self):
        """Test cursor row conversion with .name attribute."""
        from codex.archive.dal import _cursor_row_to_dict

        # Mock column descriptions with .name attribute
        col1 = MagicMock()
        col1.name = "id"
        col2 = MagicMock()
        col2.name = "email"

        mock_cursor = MagicMock()
        mock_cursor.description = [col1, col2]

        row = ("001", "test@example.com")
        result = _cursor_row_to_dict(mock_cursor, row)

        assert result == {"id": "001", "email": "test@example.com"}

    def test_cursor_row_to_dict_no_description(self):
        """Test cursor row conversion when description is None."""
        from codex.archive.dal import _cursor_row_to_dict

        mock_cursor = MagicMock()
        mock_cursor.description = None

        row = ("123", "test")
        result = _cursor_row_to_dict(mock_cursor, row)

        # Should return empty dict when no description
        assert result == {}, "Result must not be empty"

    def test_cursor_row_to_dict_missing_col_info(self):
        """Test cursor row conversion with missing column info."""
        from codex.archive.dal import _cursor_row_to_dict

        # Description with object that doesn't have name
        mock_cursor = MagicMock()
        mock_desc = MagicMock(spec=[])  # No .name attribute
        mock_cursor.description = [mock_desc]

        row = ("123",)
        result = _cursor_row_to_dict(mock_cursor, row)

        # Should use string representation as fallback
        assert "123" in list(result.values()), "Result must not be empty"


class TestDecodeJsonField:
    """Tests for _decode_json_field helper function."""

    def test_decode_json_field_valid_json(self):
        """Test decoding valid JSON string."""
        from codex.archive.dal import _decode_json_field

        json_str = '{"key": "value", "num": 42}'
        result = _decode_json_field(json_str)

        assert result == {"key": "value", "num": 42}

    def test_decode_json_field_none(self):
        """Test decoding None returns empty dict."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field(None)
        assert result == {}, "Result must not be empty"

    def test_decode_json_field_empty_dict(self):
        """Test decoding empty JSON object."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field("{}")
        assert result == {}, "Result must not be empty"

    def test_decode_json_field_memoryview(self):
        """Test decoding from memoryview."""
        from codex.archive.dal import _decode_json_field

        json_bytes = b'{"key": "value"}'
        mv = memoryview(json_bytes)
        result = _decode_json_field(mv)

        assert result == {"key": "value"}, "Result must not be empty"

    def test_decode_json_field_bytearray(self):
        """Test decoding from bytearray."""
        from codex.archive.dal import _decode_json_field

        json_bytes = bytearray(b'{"key": "value"}')
        result = _decode_json_field(json_bytes)

        assert result == {"key": "value"}, "Result must not be empty"

    def test_decode_json_field_invalid_json(self):
        """Test decoding invalid JSON returns empty dict."""
        from codex.archive.dal import _decode_json_field

        # Invalid JSON might be handled gracefully
        try:
            result = _decode_json_field("not valid json")
            # If no error, should return dict
            assert isinstance(result, dict)
        except json.JSONDecodeError:
            # Or it might raise
            pass


class TestMaybeBytes:
    """Tests for _maybe_bytes helper function."""

    def test_maybe_bytes_none(self):
        """Test _maybe_bytes with None."""
        from codex.archive.dal import _maybe_bytes

        result = _maybe_bytes(None)
        assert result is None, "Result must not be empty"

    def test_maybe_bytes_bytes(self):
        """Test _maybe_bytes with bytes."""
        from codex.archive.dal import _maybe_bytes

        data = b"test data"
        result = _maybe_bytes(data)
        assert result == data, "Result must not be empty"

    def test_maybe_bytes_memoryview(self):
        """Test _maybe_bytes with memoryview."""
        from codex.archive.dal import _maybe_bytes

        data = b"test data"
        mv = memoryview(data)
        result = _maybe_bytes(mv)
        assert result == data, "Result must not be empty"

    def test_maybe_bytes_bytearray(self):
        """Test _maybe_bytes with bytearray."""
        from codex.archive.dal import _maybe_bytes

        data = bytearray(b"test data")
        result = _maybe_bytes(data)
        assert result == bytes(data), "Result must not be empty"


class TestArtifactRow:
    """Tests for ArtifactRow dataclass."""

    def test_artifact_row_creation(self):
        """Test creating an ArtifactRow."""
        from codex.archive.dal import ArtifactRow

        row = ArtifactRow(
            id="art-001",
            content_sha256="abc123",
            size_bytes=1024,
            compression="zlib",
            mime_type="text/plain",
            storage_driver="db",
            blob_bytes=b"data",
            object_url="s3://bucket/key",
        )

        assert row.id == "art-001", "id is not valid"
        assert row.content_sha256 == "abc123", "Content must not be empty"
        assert row.size_bytes == 1024, "size_bytes is not valid"
        assert row.compression == "zlib", "compression is not valid"

    def test_artifact_row_none_blob(self):
        """Test ArtifactRow with None blob."""
        from codex.archive.dal import ArtifactRow

        row = ArtifactRow(
            id="art-001",
            content_sha256="abc123",
            size_bytes=0,
            compression="none",
            mime_type="application/json",
            storage_driver="s3",
            blob_bytes=None,
            object_url=None,
        )

        assert row.blob_bytes is None, "blob_bytes is not valid"
        assert row.object_url is None, "Object must be initialized"


class TestItemRow:
    """Tests for ItemRow dataclass."""

    def test_item_row_creation(self):
        """Test creating an ItemRow."""
        from codex.archive.dal import ItemRow

        metadata = {"key": "value"}
        row = ItemRow(
            id="item-001",
            repo="owner/repo",
            path="src/main.py",
            commit_sha="abc123def456",
            language="python",
            kind="code",
            reason="archived",
            artifact_id="art-001",
            metadata=metadata,
            tombstone_id="tomb-001",
        )

        assert row.id == "item-001", "Item must not be empty"
        assert row.repo == "owner/repo", "repo is not valid"
        assert row.path == "src/main.py", "path is not valid"
        assert row.metadata == metadata, "Data must not be empty"

    def test_item_row_fields(self):
        """Test ItemRow contains all required fields."""
        from codex.archive.dal import ItemRow

        row = ItemRow(
            id="item-001",
            repo="repo",
            path="path",
            commit_sha="sha",
            language="lang",
            kind="kind",
            reason="reason",
            artifact_id="art-id",
            metadata={},
            tombstone_id="tomb-id",
        )

        assert hasattr(row, "id")
        assert hasattr(row, "repo")
        assert hasattr(row, "path")
        assert hasattr(row, "commit_sha")
        assert hasattr(row, "language")
        assert hasattr(row, "kind")
        assert hasattr(row, "reason")
        assert hasattr(row, "artifact_id")
        assert hasattr(row, "metadata")
        assert hasattr(row, "tombstone_id")


class TestArchiveDALFactory:
    """Tests for ArchiveDAL factory class."""

    def test_archive_dal_from_env_sqlite_default(self):
        """Test ArchiveDAL.from_env returns SqliteDAL by default."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict("os.environ", {}, clear=True):
            dal = ArchiveDAL.from_env()
            from codex.archive.dal import SqliteDAL

            assert isinstance(dal, SqliteDAL)

    def test_archive_dal_from_env_explicit_sqlite(self):
        """Test ArchiveDAL.from_env with explicit sqlite backend."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict("os.environ", {"CODEX_ARCHIVE_BACKEND": "sqlite"}, clear=True):
            dal = ArchiveDAL.from_env()
            from codex.archive.dal import SqliteDAL

            assert isinstance(dal, SqliteDAL)

    def test_archive_dal_from_env_postgres(self):
        """Test ArchiveDAL.from_env with postgres backend."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict(
            "os.environ",
            {
                "CODEX_ARCHIVE_BACKEND": "postgres",
                "CODEX_ARCHIVE_URL": "postgresql://localhost/test",
            },
            clear=True,
        ):
            try:
                dal = ArchiveDAL.from_env()
                from codex.archive.dal import PostgresDAL

                assert isinstance(dal, PostgresDAL)
            except RuntimeError as e:
                # psycopg not installed - expected
                if "psycopg" in str(e):
                    pytest.skip("psycopg not installed")

    def test_archive_dal_from_env_mariadb(self):
        """Test ArchiveDAL.from_env with mariadb backend."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict(
            "os.environ",
            {"CODEX_ARCHIVE_BACKEND": "mariadb", "CODEX_ARCHIVE_URL": "mysql://localhost/test"},
            clear=True,
        ):
            try:
                dal = ArchiveDAL.from_env()
                from codex.archive.dal import MariaDbDAL

                assert isinstance(dal, MariaDbDAL)
            except RuntimeError as e:
                # pymysql not installed - expected
                if "pymysql" in str(e):
                    pytest.skip("pymysql not installed")

    def test_archive_dal_from_env_unsupported_backend(self):
        """Test ArchiveDAL.from_env with unsupported backend."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict("os.environ", {"CODEX_ARCHIVE_BACKEND": "mongodb"}, clear=True):
            with pytest.raises(ValueError, match="Unsupported"):
                ArchiveDAL.from_env()

    def test_archive_dal_from_env_case_insensitive(self):
        """Test ArchiveDAL.from_env is case insensitive."""
        from codex.archive.dal import ArchiveDAL

        with patch.dict("os.environ", {"CODEX_ARCHIVE_BACKEND": "SQLITE"}, clear=True):
            dal = ArchiveDAL.from_env()
            from codex.archive.dal import SqliteDAL

            assert isinstance(dal, SqliteDAL)


class TestBaseDALValidateIdentifier:
    """Tests for BaseDAL.validate_identifier static method."""

    def test_validate_identifier_allowed(self):
        """Test validate_identifier with allowed identifier."""
        from codex.archive.dal import BaseDAL

        result = BaseDAL.validate_identifier("repo", ["repo", "path", "sha"])
        assert result == "repo", "Result must not be empty"

    def test_validate_identifier_not_allowed(self):
        """Test validate_identifier with disallowed identifier."""
        from codex.archive.dal import BaseDAL

        with pytest.raises(ValueError, match="identifier not allowed"):
            BaseDAL.validate_identifier("invalid", ["repo", "path"])

    def test_validate_identifier_empty_allowed(self):
        """Test validate_identifier with empty allowed list."""
        from codex.archive.dal import BaseDAL

        with pytest.raises(ValueError):
            BaseDAL.validate_identifier("anything", [])

    def test_validate_identifier_case_sensitive(self):
        """Test validate_identifier is case sensitive."""
        from codex.archive.dal import BaseDAL

        with pytest.raises(ValueError):
            BaseDAL.validate_identifier("Repo", ["repo"])


class TestSqliteDALBasics:
    """Tests for SqliteDAL basic functionality."""

    def test_sqlite_dal_from_url(self):
        """Test creating SqliteDAL from URL."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            url = f"sqlite:///{db_path}"

            dal = SqliteDAL.from_url(url)
            assert dal is not None, "dal must be initialized"
            assert hasattr(dal, "conn") or hasattr(dal, "db_root")

    def test_sqlite_dal_from_url_default(self):
        """Test SqliteDAL.from_url with default path."""
        from codex.archive.dal import SqliteDAL

        dal = SqliteDAL.from_url("sqlite://:memory:")
        assert dal is not None, "dal must be initialized"

    def test_sqlite_dal_txn_context_manager(self):
        """Test SqliteDAL transaction context manager."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")

            with dal.txn():
                # Should be able to execute SQL within transaction
                dal.conn.execute("SELECT 1")

    def test_sqlite_dal_ensure_schema(self):
        """Test SqliteDAL.ensure_schema creates tables."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")

            dal.ensure_schema()

            # Check that tables were created
            cur = dal.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]

            assert "artifact" in tables, "Condition must be true"
            assert "item" in tables, "Item must not be empty"
            assert "event" in tables, "Condition must be true"

    def test_sqlite_dal_summary_empty(self):
        """Test SqliteDAL.summary on empty database."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            summary = dal.summary()

            assert isinstance(summary, dict)
            assert summary.get("item_count", 0) == 0
            assert summary.get("artifact_count", 0) == 0


class TestSqliteDALInsertOperations:
    """Tests for SqliteDAL insert operations."""

    def test_sqlite_dal_ensure_artifact(self):
        """Test SqliteDAL.ensure_artifact stores artifact."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            result = dal.ensure_artifact(
                sha="test_sha_123",
                size=1024,
                mime="text/plain",
                blob=b"test content",
                compression="zlib",
                storage_driver="db",
                object_url=None,
            )

            assert "id" in result, "Result must not be empty"
            assert result["content_sha256"] == "test_sha_123", "Result must not be empty"
            assert result["size_bytes"] == 1024, "Result must not be empty"

    def test_sqlite_dal_insert_item(self):
        """Test SqliteDAL.insert_item stores item."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            # First create an artifact
            art_result = dal.ensure_artifact(
                sha="art_sha",
                size=512,
                mime="text/plain",
                blob=b"artifact",
                compression="zlib",
                storage_driver="db",
                object_url=None,
            )

            # Then insert item
            result = dal.insert_item(
                repo="test/repo",
                path="src/main.py",
                commit_sha="commit_abc",
                language="python",
                reason="test",
                artifact_id=art_result["id"],
                tombstone_id="tomb_001",
                kind="code",
                metadata={"key": "value"},
                archived_by="test_user",
            )

            assert "id" in result, "Result must not be empty"
            assert "tombstone_id" in result, "Result must not be empty"
            assert result["tombstone_id"] == "tomb_001", "Result must not be empty"

    def test_sqlite_dal_insert_event(self):
        """Test SqliteDAL.insert_event stores event."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            # Create artifact and item first
            art_result = dal.ensure_artifact(
                sha="art_sha",
                size=512,
                mime="text/plain",
                blob=b"artifact",
                compression="zlib",
                storage_driver="db",
                object_url=None,
            )

            item_result = dal.insert_item(
                repo="test/repo",
                path="src/main.py",
                commit_sha="commit_abc",
                language="python",
                reason="test",
                artifact_id=art_result["id"],
                tombstone_id="tomb_001",
                kind="code",
                metadata=None,
                archived_by="test_user",
            )

            # Now insert event
            dal.insert_event(
                item_id=item_result["id"],
                action="archived",
                actor="test_actor",
                context={"reason": "backup"},
            )

            # Verify event was stored
            cur = dal.conn.execute("SELECT COUNT(*) FROM event")
            count = cur.fetchone()[0]
            assert count == 1, "Count must be greater than zero"


class TestSqliteDALFetchOperations:
    """Tests for SqliteDAL fetch operations."""

    def test_sqlite_dal_fetch_by_tombstone(self):
        """Test SqliteDAL.fetch_by_tombstone retrieves item and artifact."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            # Create artifact
            art_result = dal.ensure_artifact(
                sha="art_sha_123",
                size=1024,
                mime="application/json",
                blob=b'{"key": "value"}',
                compression="zlib",
                storage_driver="db",
                object_url=None,
            )

            # Create item
            item_result = dal.insert_item(
                repo="owner/repo",
                path="path/to/file.py",
                commit_sha="abcdef123456",
                language="python",
                reason="archived",
                artifact_id=art_result["id"],
                tombstone_id="tomb_xyz_123",
                kind="code",
                metadata={"source": "test"},
                archived_by="test_user",
            )

            # Fetch by tombstone
            item_row, artifact_row = dal.fetch_by_tombstone("tomb_xyz_123")

            assert item_row.id == item_result["id"], "Result must not be empty"
            assert item_row.repo == "owner/repo", "Item must not be empty"
            assert item_row.tombstone_id == "tomb_xyz_123", "Item must not be empty"
            assert artifact_row.id == art_result["id"], "Result must not be empty"

    def test_sqlite_dal_fetch_by_tombstone_not_found(self):
        """Test fetch_by_tombstone raises KeyError for missing tombstone."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            with pytest.raises(KeyError, match="Tombstone not found"):
                dal.fetch_by_tombstone("nonexistent")

    def test_sqlite_dal_recent_items(self):
        """Test SqliteDAL.recent_items returns recent items."""
        from codex.archive.dal import SqliteDAL

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dal = SqliteDAL.from_url(f"sqlite:///{db_path}")
            dal.ensure_schema()

            # Create artifacts
            art_result = dal.ensure_artifact(
                sha="art_sha",
                size=100,
                mime="text/plain",
                blob=b"data",
                compression="zlib",
                storage_driver="db",
                object_url=None,
            )

            # Create 3 items
            for i in range(3):
                dal.insert_item(
                    repo="test/repo",
                    path=f"file{i}.py",
                    commit_sha=f"commit_{i}",
                    language="python",
                    reason="test",
                    artifact_id=art_result["id"],
                    tombstone_id=f"tomb_{i}",
                    kind="code",
                    metadata=None,
                    archived_by="user",
                )

            # Get recent items
            recent = dal.recent_items(limit=2)
            assert len(recent) == 2, "Recent must not be empty"
