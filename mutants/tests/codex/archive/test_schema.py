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
        
        bundle = SchemaBundle(
            name="test",
            statements=("CREATE TABLE t1", "CREATE TABLE t2")
        )
        
        assert bundle.name == "test"
        assert len(bundle.statements) == 2
        assert "CREATE TABLE t1" in bundle.statements

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
        
        assert bundle.statements == ()


class TestPostgresBundle:
    """Tests for POSTGRES_BUNDLE constant."""

    def test_exists(self):
        """Test POSTGRES_BUNDLE exists."""
        from codex.archive.schema import POSTGRES_BUNDLE
        
        assert POSTGRES_BUNDLE is not None
        assert POSTGRES_BUNDLE.name == "postgres"

    def test_has_statements(self):
        """Test POSTGRES_BUNDLE has statements."""
        from codex.archive.schema import POSTGRES_BUNDLE
        
        assert len(POSTGRES_BUNDLE.statements) > 0

    def test_contains_artifact_table(self):
        """Test POSTGRES_BUNDLE contains artifact table."""
        from codex.archive.schema import POSTGRES_BUNDLE
        
        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "artifact" in statements.lower()

    def test_contains_item_table(self):
        """Test POSTGRES_BUNDLE contains item table."""
        from codex.archive.schema import POSTGRES_BUNDLE
        
        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "item" in statements.lower()


class TestSqliteBundle:
    """Tests for SQLITE_BUNDLE constant."""

    def test_exists(self):
        """Test SQLITE_BUNDLE exists."""
        from codex.archive.schema import SQLITE_BUNDLE
        
        assert SQLITE_BUNDLE is not None
        assert SQLITE_BUNDLE.name == "sqlite"

    def test_has_statements(self):
        """Test SQLITE_BUNDLE has statements."""
        from codex.archive.schema import SQLITE_BUNDLE
        
        assert len(SQLITE_BUNDLE.statements) > 0


class TestMariadbBundle:
    """Tests for MARIADB_BUNDLE constant."""

    def test_exists(self):
        """Test MARIADB_BUNDLE exists."""
        from codex.archive.schema import MARIADB_BUNDLE
        
        assert MARIADB_BUNDLE is not None
        assert MARIADB_BUNDLE.name == "mariadb"

    def test_has_statements(self):
        """Test MARIADB_BUNDLE has statements."""
        from codex.archive.schema import MARIADB_BUNDLE
        
        assert len(MARIADB_BUNDLE.statements) > 0
