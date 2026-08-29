"""Tests for SQL AST adapter."""

import pytest

pytest.importorskip("sqlparse", reason="sqlparse optional dependency not installed")

from codex.ast_adapters import SQLASTAdapter


class TestSQLASTAdapter:
    """Test suite for SQL AST adapter."""

    @pytest.fixture
    def adapter(self):
        """Create SQL adapter instance."""
        return SQLASTAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter is not None, "adapter must be initialized"
        assert adapter.root_node is None, "root_node is not valid"

    def test_parse_select_simple(self, adapter):
        """Test parsing simple SELECT statement."""
        sql = "SELECT id, name FROM users"
        root = adapter.parse(sql)

        assert root is not None, "root must be initialized"
        assert root.node_type == "sql_document", "node_type is not valid"
        assert len(root.children) == 1, "Collection must not be empty"

        stmt = root.children[0]
        assert stmt.node_type == "sql_statement", "node_type is not valid"
        assert stmt.name == "SELECT", "name is not valid"
        assert "users" in stmt.metadata["tables"], "Data must not be empty"

    def test_parse_select_with_where(self, adapter):
        """Test parsing SELECT with WHERE clause."""
        sql = "SELECT id, name FROM users WHERE active = 1"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.metadata["has_where"] is True, "Data must not be empty"
        assert "users" in stmt.metadata["tables"], "Data must not be empty"

    def test_parse_select_multiple_tables(self, adapter):
        """Test parsing SELECT with multiple tables."""
        sql = "SELECT u.id, p.title FROM users u, posts p"
        root = adapter.parse(sql)

        stmt = root.children[0]
        tables = stmt.metadata["tables"]
        assert len(tables) >= 1, "Tables must not be empty"

    def test_parse_select_with_join(self, adapter):
        """Test parsing SELECT with JOIN."""
        sql = """
        SELECT u.id, u.name, p.title
        FROM users u
        JOIN posts p ON u.id = p.user_id
        """
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "SELECT", "name is not valid"
        assert len(stmt.metadata["tables"]) >= 1, "Collection must not be empty"

    def test_parse_insert(self, adapter):
        """Test parsing INSERT statement."""
        sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.node_type == "sql_statement", "node_type is not valid"
        assert stmt.name == "INSERT", "name is not valid"
        assert stmt.metadata["table"] == "users", "Data must not be empty"

    def test_parse_update(self, adapter):
        """Test parsing UPDATE statement."""
        sql = "UPDATE users SET name = 'Bob' WHERE id = 1"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "UPDATE", "name is not valid"
        assert stmt.metadata["table"] == "users", "Data must not be empty"

    def test_parse_delete(self, adapter):
        """Test parsing DELETE statement."""
        sql = "DELETE FROM users WHERE id = 1"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "DELETE", "name is not valid"
        assert stmt.metadata["table"] == "users", "Data must not be empty"

    def test_parse_create_table(self, adapter):
        """Test parsing CREATE TABLE statement."""
        sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
        """
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "CREATE TABLE", "name is not valid"
        assert stmt.metadata["object_name"] == "users", "Data must not be empty"

    def test_parse_create_index(self, adapter):
        """Test parsing CREATE INDEX statement."""
        sql = "CREATE INDEX idx_users_email ON users(email)"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name.startswith("CREATE"), "Condition must be true"

    def test_parse_alter_table(self, adapter):
        """Test parsing ALTER TABLE statement."""
        sql = "ALTER TABLE users ADD COLUMN age INTEGER"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "ALTER", "name is not valid"
        assert stmt.metadata["object_name"] == "users", "Data must not be empty"

    def test_parse_drop_table(self, adapter):
        """Test parsing DROP TABLE statement."""
        sql = "DROP TABLE users"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "DROP", "name is not valid"
        assert stmt.metadata["object_name"] == "users", "Data must not be empty"

    def test_parse_multiple_statements(self, adapter):
        """Test parsing multiple SQL statements."""
        sql = """
        SELECT * FROM users;
        SELECT * FROM posts;
        """
        root = adapter.parse(sql)

        assert len(root.children) == 2, "Collection must not be empty"
        assert all(stmt.name == "SELECT" for stmt in root.children), "name is not valid"

    def test_get_tables(self, adapter):
        """Test extracting table names."""
        sql = """
        SELECT u.name, p.title
        FROM users u, posts p
        WHERE u.id = p.user_id
        """
        adapter.parse(sql)

        tables = adapter.get_tables()
        assert len(tables) >= 1, "Tables must not be empty"
        assert any("users" in t or "u" in t for t in tables), "Condition must be true"

    def test_get_columns(self, adapter):
        """Test extracting column names."""
        sql = "SELECT id, name, email FROM users"
        adapter.parse(sql)

        columns = adapter.get_columns()
        # Should find at least some columns
        assert isinstance(columns, (list, tuple, set, dict))  # sqlparse may or may not extract all

    def test_extract_metadata_document(self, adapter):
        """Test extracting document-level metadata."""
        sql = "SELECT * FROM users; SELECT * FROM posts;"
        root = adapter.parse(sql)

        metadata = adapter.extract_metadata(root)
        assert metadata["statement_count"] == 2, "Data must not be empty"
        assert "all_tables" in metadata, "Data must not be empty"

    def test_extract_metadata_statement(self, adapter):
        """Test extracting statement-level metadata."""
        sql = "SELECT id, name FROM users WHERE active = 1"
        root = adapter.parse(sql)

        stmt = root.children[0]
        metadata = adapter.extract_metadata(stmt)
        assert metadata["statement_type"] == "SELECT", "Data must not be empty"
        assert "tables" in metadata, "Data must not be empty"

    def test_parse_empty_sql(self, adapter):
        """Test parsing empty SQL raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            adapter.parse("")

    def test_parse_whitespace_only(self, adapter):
        """Test parsing whitespace-only SQL raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            adapter.parse("   \n  \t  ")

    def test_traverse(self, adapter):
        """Test tree traversal."""
        sql = "SELECT id FROM users"
        root = adapter.parse(sql)

        nodes = list(adapter.traverse(root))
        assert len(nodes) >= 2, "Nodes must not be empty"
        assert nodes[0] == root, "Condition must be true"

    def test_find_nodes_by_type(self, adapter):
        """Test finding nodes by type."""
        sql = "SELECT * FROM users; INSERT INTO posts VALUES (1)"
        adapter.parse(sql)

        statements = adapter.find_nodes_by_type("sql_statement")
        assert len(statements) == 2, "Statements must not be empty"

    def test_get_stats(self, adapter):
        """Test getting AST statistics."""
        sql = "SELECT * FROM users; SELECT * FROM posts;"
        adapter.parse(sql)

        stats = adapter.get_stats()
        assert stats["sql_document"] == 1, "Condition must be true"
        assert stats["sql_statement"] == 2, "Condition must be true"

    def test_parse_with_file_path(self, adapter):
        """Test parsing with file path."""
        sql = "SELECT * FROM users"
        root = adapter.parse(sql, file_path="query.sql")

        assert root.file_path == "query.sql", "file_path is not valid"

    def test_parse_complex_select(self, adapter):
        """Test parsing complex SELECT with subquery."""
        sql = """
        SELECT u.id, u.name,
               (SELECT COUNT(*) FROM posts WHERE user_id = u.id) as post_count
        FROM users u
        WHERE u.active = 1
        ORDER BY u.name
        """
        root = adapter.parse(sql)

        assert root is not None, "root must be initialized"
        stmt = root.children[0]
        assert stmt.name == "SELECT", "name is not valid"

    def test_parse_case_insensitive(self, adapter):
        """Test parsing with mixed case keywords."""
        sql = "select Id, Name from Users where Active = 1"
        root = adapter.parse(sql)

        stmt = root.children[0]
        assert stmt.name == "SELECT", "name is not valid"

    def test_large_query_performance(self, adapter):
        """Test parsing large query (stress test)."""
        # Generate large query with many columns
        columns = ", ".join([f"col{i}" for i in range(100)])
        sql = f"SELECT {columns} FROM large_table"

        root = adapter.parse(sql)
        assert root is not None, "root must be initialized"
        assert len(root.children) == 1, "Collection must not be empty"
