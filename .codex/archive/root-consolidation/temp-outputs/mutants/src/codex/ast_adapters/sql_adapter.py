"""SQL AST Adapter using sqlparse.

This module provides SQL parsing capabilities for the AST framework,
supporting both DML (SELECT, INSERT, UPDATE, DELETE) and DDL
(CREATE, ALTER, DROP) statements.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

try:
    import sqlparse
    import sqlparse.sql as _sqlparse_sql
    import sqlparse.tokens as _sqlparse_tokens

    Identifier = _sqlparse_sql.Identifier
    IdentifierList = _sqlparse_sql.IdentifierList
    Keyword = _sqlparse_tokens.Keyword

    _SQLPARSE_AVAILABLE = True
except ImportError:  # pragma: no cover
    sqlparse = None
    Identifier = IdentifierList = Keyword = None
    _SQLPARSE_AVAILABLE = False

if TYPE_CHECKING:
    from sqlparse.sql import Statement
else:
    Statement = None

from .base_adapter import BaseASTAdapter, StandardizedASTNode


class SQLASTAdapter(BaseASTAdapter):
    """SQL AST adapter using sqlparse library.

    Parses SQL queries and DDL statements into standardized AST nodes.
    Supports:
    - DML: SELECT, INSERT, UPDATE, DELETE
    - DDL: CREATE, ALTER, DROP
    - Extracts tables, columns, conditions, and query structure

    Example:
        >>> adapter = SQLASTAdapter()
        >>> root = adapter.parse("SELECT id, name FROM users WHERE active = 1")
        >>> tables = adapter.get_tables()
        >>> columns = adapter.get_columns()
    """

    def __init__(self) -> None:
        """Initialize SQL adapter."""
        if not _SQLPARSE_AVAILABLE:  # pragma: no cover
            raise ImportError(
                "sqlparse is required for SQLASTAdapter. Install it with: pip install sqlparse>=0.4"
            )
        super().__init__()
        self._tables: list[str] = []
        self._columns: list[str] = []

    def parse(self, source: str, file_path: Optional[str] = None) -> StandardizedASTNode:
        """Parse SQL source into standardized AST.

        Args:
            source: SQL source code to parse
            file_path: Optional file path for the source

        Returns:
            Root node of the standardized AST

        Raises:
            ValueError: If SQL source is invalid
        """
        if not source or not source.strip():
            raise ValueError("SQL source cannot be empty")

        # Reset state
        self._tables = []
        self._columns = []

        # Parse SQL statements
        try:
            parsed = sqlparse.parse(source)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to parse SQL: {e}") from e

        if not parsed:
            raise ValueError("No SQL statements found")

        # Create document root
        root = StandardizedASTNode(
            node_id=str(uuid.uuid4()),
            node_type="sql_document",
            name="root",
            file_path=file_path,  # type: ignore[arg-type]
            line_start=1,
            line_end=len(source.splitlines()),
            column_start=0,
            column_end=0,
            children=[],
            metadata={"statement_count": len(parsed), "source_length": len(source)},
        )

        self.root_node = root

        # Process each statement
        for idx, stmt in enumerate(parsed):
            stmt_node = self._process_statement(stmt, idx + 1)
            if stmt_node:
                stmt_node.parent = root
                root.children.append(stmt_node)

        return root

    def _process_statement(
        self, stmt: Statement, line_number: int
    ) -> Optional[StandardizedASTNode]:
        """Process a single SQL statement.

        Args:
            stmt: sqlparse Statement object
            line_number: Line number in source

        Returns:
            AST node for the statement
        """
        # Identify statement type
        stmt_type = self._get_statement_type(stmt)

        node = StandardizedASTNode(
            node_id=str(uuid.uuid4()),
            node_type="sql_statement",
            name=stmt_type,
            line_start=line_number,
            line_end=line_number,
            column_start=0,
            column_end=0,
            children=[],
            metadata={"statement_type": stmt_type, "sql": str(stmt).strip()},
        )

        # Extract components based on statement type
        if stmt_type == "SELECT":
            self._extract_select_components(stmt, node)
        elif stmt_type == "INSERT":
            self._extract_insert_components(stmt, node)
        elif stmt_type == "UPDATE":
            self._extract_update_components(stmt, node)
        elif stmt_type == "DELETE":
            self._extract_delete_components(stmt, node)
        elif stmt_type.startswith("CREATE") or stmt_type in ("ALTER", "DROP"):
            self._extract_ddl_components(stmt, node)

        return node

    def _get_statement_type(self, stmt: Statement) -> str:
        """Get the type of SQL statement.

        Args:
            stmt: sqlparse Statement object

        Returns:
            Statement type (e.g., 'SELECT', 'INSERT', 'CREATE TABLE')
        """
        # Get first significant token
        first_token = stmt.token_first(skip_ws=True, skip_cm=True)
        if not first_token:
            return "UNKNOWN"

        # Get the keyword value
        keyword = first_token.value.upper()

        # For CREATE, get the object type
        if keyword == "CREATE":
            tokens = list(stmt.flatten())
            for i, token in enumerate(tokens):
                if token.value.upper() == "CREATE" and i + 1 < len(tokens):
                    # Skip whitespace
                    j = i + 1
                    while j < len(tokens) and tokens[j].is_whitespace:
                        j += 1
                    if j < len(tokens):
                        return f"CREATE {tokens[j].value.upper()}"
            return "CREATE"

        return keyword

    def _extract_select_components(self, stmt: Statement, node: StandardizedASTNode) -> None:
        """Extract components from SELECT statement.

        Args:
            stmt: sqlparse Statement object
            node: AST node to populate
        """
        tables = []
        columns = []
        has_where = False

        # Check for WHERE clause in flattened tokens
        for token in stmt.flatten():
            if token.ttype is Keyword and token.value.upper() == "WHERE":
                has_where = True
                break

        # Find FROM clause
        from_seen = False

        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
                continue

            if token.ttype is Keyword and token.value.upper() == "WHERE":
                from_seen = False
                continue

            # Extract table names from FROM clause
            if from_seen:
                if isinstance(token, Identifier):
                    table_name = token.get_real_name()
                    if table_name:
                        tables.append(table_name)
                        self._tables.append(table_name)
                elif isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        table_name = identifier.get_real_name()
                        if table_name:
                            tables.append(table_name)
                            self._tables.append(table_name)

        # Extract column names (simplified - gets from SELECT clause)
        select_seen = False
        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == "SELECT":
                select_seen = True
                continue

            if select_seen and token.ttype is Keyword:
                break

            if select_seen:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        col_name = str(identifier).strip()
                        if col_name and col_name != "*":
                            columns.append(col_name)
                            self._columns.append(col_name)
                elif isinstance(token, Identifier):
                    col_name = str(token).strip()
                    if col_name and col_name != "*":
                        columns.append(col_name)
                        self._columns.append(col_name)

        node.metadata.update({"tables": tables, "columns": columns, "has_where": has_where})

    def _extract_insert_components(self, stmt: Statement, node: StandardizedASTNode) -> None:
        """Extract components from INSERT statement.

        Args:
            stmt: sqlparse Statement object
            node: AST node to populate
        """
        table_name = None
        columns: list[Any] = []

        # Find table name - look for identifier or function (table with columns)
        for token in stmt.tokens:
            if isinstance(token, Identifier) or hasattr(token, "get_real_name"):
                name = token.get_real_name() if hasattr(token, "get_real_name") else None
                if name:
                    table_name = name
                    self._tables.append(table_name)
                    break

        node.metadata.update({"table": table_name, "columns": columns})

    def _extract_update_components(self, stmt: Statement, node: StandardizedASTNode) -> None:
        """Extract components from UPDATE statement.

        Args:
            stmt: sqlparse Statement object
            node: AST node to populate
        """
        table_name = None

        # Find table name - first identifier after UPDATE
        for token in stmt.tokens:
            if isinstance(token, Identifier):
                table_name = token.get_real_name()
                if table_name:
                    self._tables.append(table_name)
                    break

        node.metadata.update({"table": table_name})

    def _extract_delete_components(self, stmt: Statement, node: StandardizedASTNode) -> None:
        """Extract components from DELETE statement.

        Args:
            stmt: sqlparse Statement object
            node: AST node to populate
        """
        table_name = None

        # Find table name (after FROM)
        from_seen = False
        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
                continue

            if from_seen and isinstance(token, Identifier):
                table_name = token.get_real_name()
                if table_name:  # Guard against None
                    self._tables.append(table_name)
                break

        node.metadata.update({"table": table_name})

    def _extract_ddl_components(self, stmt: Statement, node: StandardizedASTNode) -> None:
        """Extract components from DDL statement.

        Args:
            stmt: sqlparse Statement object
            node: AST node to populate
        """
        object_name = None

        # Find object name (table, index, etc.)
        for token in stmt.tokens:
            if isinstance(token, Identifier):
                object_name = token.get_real_name()
                break

        node.metadata.update({"object_name": object_name})

    def get_tables(self) -> list[str]:
        """Get list of tables referenced in parsed SQL.

        Returns:
            List of table names
        """
        return list(set(self._tables))

    def get_columns(self) -> list[str]:
        """Get list of columns referenced in parsed SQL.

        Returns:
            List of column names
        """
        return list(set(self._columns))

    def extract_metadata(self, node: StandardizedASTNode) -> dict[str, Any]:
        """Extract SQL-specific metadata from a node.

        Args:
            node: AST node to extract metadata from

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        if node.node_type == "sql_document":
            metadata["statement_count"] = node.metadata.get("statement_count", 0)
            metadata["all_tables"] = self.get_tables()
            metadata["all_columns"] = self.get_columns()
        elif node.node_type == "sql_statement":
            metadata["statement_type"] = node.metadata.get("statement_type", "UNKNOWN")
            metadata["tables"] = node.metadata.get("tables", [])
            metadata["columns"] = node.metadata.get("columns", [])

        return metadata
