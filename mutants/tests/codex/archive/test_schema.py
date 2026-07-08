"""
Tests for codex.archive.schema module.

This module contains tests for database schema definitions.
"""

import pytest


class TestSchemaBundle:
    """Tests for SchemaBundle dataclass."""

    def test_basic_creation(self):
        """Test SchemaBundle basic creation."""
        from codex.archive.schema import SchemaBundle

        bundle = SchemaBundle(name="test", statements=("CREATE TABLE t1", "CREATE TABLE t2"))

        assert bundle.name == "test", "name is not valid"
        assert len(bundle.statements) == 2, "Collection must not be empty"
        assert "CREATE TABLE t1" in bundle.statements, "Condition must be true"

    def test_frozen(self):
        """Test SchemaBundle is frozen (immutable)."""
        from codex.archive.schema import SchemaBundle

        bundle = SchemaBundle(name="test", statements=())

        with pytest.raises(AttributeError):
            bundle.name = "changed"

    def test_empty_statements(self):
        """Test SchemaBundle with empty statements."""
        from codex.archive.schema import SchemaBundle

        bundle = SchemaBundle(name="empty", statements=())

        assert bundle.statements == (), "statements is not valid"


class TestPostgresBundle:
    """Tests for POSTGRES_BUNDLE constant."""

    def test_exists(self):
        """Test POSTGRES_BUNDLE exists."""
        from codex.archive.schema import POSTGRES_BUNDLE

        assert POSTGRES_BUNDLE is not None, "POSTGRES_BUNDLE must be initialized"
        assert POSTGRES_BUNDLE.name == "postgres", "name is not valid"

    def test_has_statements(self):
        """Test POSTGRES_BUNDLE has statements."""
        from codex.archive.schema import POSTGRES_BUNDLE

        assert len(POSTGRES_BUNDLE.statements) > 0, "Collection must not be empty"

    def test_contains_artifact_table(self):
        """Test POSTGRES_BUNDLE contains artifact table."""
        from codex.archive.schema import POSTGRES_BUNDLE

        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "artifact" in statements.lower(), "Condition must be true"

    def test_contains_item_table(self):
        """Test POSTGRES_BUNDLE contains item table."""
        from codex.archive.schema import POSTGRES_BUNDLE

        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "item" in statements.lower(), "Item must not be empty"


class TestSqliteBundle:
    """Tests for SQLITE_BUNDLE constant."""

    def test_exists(self):
        """Test SQLITE_BUNDLE exists."""
        from codex.archive.schema import SQLITE_BUNDLE

        assert SQLITE_BUNDLE is not None, "SQLITE_BUNDLE must be initialized"
        assert SQLITE_BUNDLE.name == "sqlite", "name is not valid"

    def test_has_statements(self):
        """Test SQLITE_BUNDLE has statements."""
        from codex.archive.schema import SQLITE_BUNDLE

        assert len(SQLITE_BUNDLE.statements) > 0, "Collection must not be empty"


class TestMariadbBundle:
    """Tests for MARIADB_BUNDLE constant."""

    def test_exists(self):
        """Test MARIADB_BUNDLE exists."""
        from codex.archive.schema import MARIADB_BUNDLE

        assert MARIADB_BUNDLE is not None, "MARIADB_BUNDLE must be initialized"
        assert MARIADB_BUNDLE.name == "mariadb", "name is not valid"

    def test_has_statements(self):
        """Test MARIADB_BUNDLE has statements."""
        from codex.archive.schema import MARIADB_BUNDLE

        assert len(MARIADB_BUNDLE.statements) > 0, "Collection must not be empty"
