"""
Tests for codex.archive.schema module.

This module contains tests for database schema definitions.
"""
        from codex.archive.schema import SchemaBundle
        from codex.archive.schema import SchemaBundle
        from codex.archive.schema import SchemaBundle
        from codex.archive.schema import POSTGRES_BUNDLE
        from codex.archive.schema import POSTGRES_BUNDLE
        from codex.archive.schema import POSTGRES_BUNDLE
        from codex.archive.schema import POSTGRES_BUNDLE
        from codex.archive.schema import SQLITE_BUNDLE
        from codex.archive.schema import SQLITE_BUNDLE
        from codex.archive.schema import MARIADB_BUNDLE
        from codex.archive.schema import MARIADB_BUNDLE



class TestSchemaBundle:
    """Tests for SchemaBundle dataclass."""

    def test_basic_creation(self):
        """Test SchemaBundle basic creation."""

        bundle = SchemaBundle(name="test", statements=("CREATE TABLE t1", "CREATE TABLE t2"))

        assert bundle.name == "test", "name is not valid"
        assert len(bundle.statements) == 2, "Collection must not be empty"
        assert "CREATE TABLE t1" in bundle.statements, "Condition must be true"

    def test_frozen(self):
        """Test SchemaBundle is frozen (immutable)."""

        bundle = SchemaBundle(name="test", statements=())

        with pytest.raises(AttributeError):
            bundle.name = "changed"

    def test_empty_statements(self):
        """Test SchemaBundle with empty statements."""

        bundle = SchemaBundle(name="empty", statements=())

        assert bundle.statements == (), "statements is not valid"


class TestPostgresBundle:
    """Tests for POSTGRES_BUNDLE constant."""

    def test_exists(self):
        """Test POSTGRES_BUNDLE exists."""

        assert POSTGRES_BUNDLE is not None, "POSTGRES_BUNDLE must be initialized"
        assert POSTGRES_BUNDLE.name == "postgres", "name is not valid"

    def test_has_statements(self):
        """Test POSTGRES_BUNDLE has statements."""

        assert len(POSTGRES_BUNDLE.statements) > 0, "Collection must not be empty"

    def test_contains_artifact_table(self):
        """Test POSTGRES_BUNDLE contains artifact table."""

        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "artifact" in statements.lower(), "Condition must be true"

    def test_contains_item_table(self):
        """Test POSTGRES_BUNDLE contains item table."""

        statements = " ".join(POSTGRES_BUNDLE.statements)
        assert "item" in statements.lower(), "Item must not be empty"


class TestSqliteBundle:
    """Tests for SQLITE_BUNDLE constant."""

    def test_exists(self):
        """Test SQLITE_BUNDLE exists."""

        assert SQLITE_BUNDLE is not None, "SQLITE_BUNDLE must be initialized"
        assert SQLITE_BUNDLE.name == "sqlite", "name is not valid"

    def test_has_statements(self):
        """Test SQLITE_BUNDLE has statements."""

        assert len(SQLITE_BUNDLE.statements) > 0, "Collection must not be empty"


class TestMariadbBundle:
    """Tests for MARIADB_BUNDLE constant."""

    def test_exists(self):
        """Test MARIADB_BUNDLE exists."""

        assert MARIADB_BUNDLE is not None, "MARIADB_BUNDLE must be initialized"
        assert MARIADB_BUNDLE.name == "mariadb", "name is not valid"

    def test_has_statements(self):
        """Test MARIADB_BUNDLE has statements."""

        assert len(MARIADB_BUNDLE.statements) > 0, "Collection must not be empty"
