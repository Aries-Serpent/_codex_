"""Archive-specific utility functions and helpers.

This module provides utilities for:
- Archive path validation and management
- Archive schema utilities
- Common query builders for archive operations
- Archive-specific helper functions
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_archive_path(path: str | Path) -> Path:
    """Validate and normalize an archive path.

    Parameters
    ----------
    path : str | Path
        Path to validate

    Returns
    -------
    Path
        Normalized path

    Raises
    ------
    ValueError
        If the path is invalid
    """
    try:
        p = Path(path).expanduser().resolve()
        return p
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid archive path: {path}") from e


def ensure_archive_directory(path: str | Path) -> Path:
    """Ensure an archive directory exists, creating it if necessary.

    Parameters
    ----------
    path : str | Path
        Directory path

    Returns
    -------
    Path
        The directory path

    Raises
    ------
    OSError
        If the directory cannot be created
    """
    p = validate_archive_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def parse_database_url(url: str) -> dict[str, Any]:
    """Parse a database connection URL.

    Supports sqlite, postgres, mariadb, mysql URLs.

    Parameters
    ----------
    url : str
        Database connection URL

    Returns
    -------
    dict[str, Any]
        Parsed URL components: backend, host, port, database, user, password

    Raises
    ------
    ValueError
        If the URL cannot be parsed
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid database URL: {url}") from e

    scheme = parsed.scheme.lower()

    # Map common database schemes to backend names
    if scheme == "sqlite":
        return {
            "backend": "sqlite",
            "path": parsed.path or parsed.netloc,
        }

    if scheme in ("postgres", "postgresql"):
        return {
            "backend": "postgres",
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/") if parsed.path else "",
            "user": parsed.username,
            "password": parsed.password,
        }

    if scheme in ("mysql", "mariadb"):
        return {
            "backend": scheme,
            "host": parsed.hostname,
            "port": parsed.port or 3306,
            "database": parsed.path.lstrip("/") if parsed.path else "",
            "user": parsed.username,
            "password": parsed.password,
        }

    raise ValueError(f"Unsupported database backend: {scheme}")


def get_database_backend(url: str) -> str:
    """Extract the database backend type from a connection URL.

    Parameters
    ----------
    url : str
        Database connection URL

    Returns
    -------
    str
        Backend type: 'sqlite', 'postgres', or 'mariadb'

    Raises
    ------
    ValueError
        If the backend cannot be determined
    """
    parsed = parse_database_url(url)
    return parsed.get("backend", "").lower()


def validate_table_name(name: str) -> str:
    """Validate that a string is a safe SQL table name.

    Only allows alphanumeric characters and underscores.
    Must start with a letter or underscore.

    Parameters
    ----------
    name : str
        Table name to validate

    Returns
    -------
    str
        The validated table name

    Raises
    ------
    ValueError
        If the table name contains invalid characters
    """
    import re

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        raise ValueError(
            f"Invalid table name: {name}. Must start with letter/underscore "
            "and contain only alphanumeric/underscore characters."
        )
    return name


def build_sqlite_path(base_dir: str | Path, db_name: str = "archive.db") -> Path:
    """Build a SQLite database path under a base directory.

    Parameters
    ----------
    base_dir : str | Path
        Base directory for the database
    db_name : str, optional
        Database filename (default: 'archive.db')

    Returns
    -------
    Path
        Full path to the database file

    Raises
    ------
    ValueError
        If base_dir is invalid
    """
    base = ensure_archive_directory(base_dir)
    db_path = base / db_name

    if not db_path.suffix:
        db_path = db_path.with_suffix(".db")

    return db_path


def safe_query_builder(
    table: str,
    fields: list[str],
    where_clause: str = "",
    limit: Optional[int] = None,
) -> str:
    """Build a safe SELECT query with basic validation.

    Parameters
    ----------
    table : str
        Table name
    fields : list[str]
        Column names to select
    where_clause : str, optional
        WHERE clause without the WHERE keyword
    limit : int, optional
        LIMIT clause value

    Returns
    -------
    str
        SQL SELECT query

    Raises
    ------
    ValueError
        If table name or fields are invalid
    """
    table = validate_table_name(table)

    # Validate field names
    for field in fields:
        validate_table_name(field)

    # Build query
    fields_str = ", ".join(fields)
    query = f"SELECT {fields_str} FROM {table}"

    if where_clause:
        query += f" WHERE {where_clause}"

    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError(f"Invalid LIMIT value: {limit}")
        query += f" LIMIT {limit}"

    return query


def archive_schema_for_backend(backend: str) -> Optional[list[str]]:
    """Get the schema statements for a specific database backend.

    Parameters
    ----------
    backend : str
        Database backend type

    Returns
    -------
    list[str] | None
        SQL statements for schema creation, or None if not supported
    """
    backend = backend.lower()

    # Base schema for both SQLite and SQL databases
    common_tables = [
        "CREATE TABLE IF NOT EXISTS archive_metadata ("
        "  id INTEGER PRIMARY KEY,"
        "  key TEXT UNIQUE NOT NULL,"
        "  value TEXT,"
        "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")",
        "CREATE TABLE IF NOT EXISTS archive_entries ("
        "  id INTEGER PRIMARY KEY,"
        "  path TEXT UNIQUE NOT NULL,"
        "  size_bytes INTEGER,"
        "  hash TEXT,"
        "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  archived_at TIMESTAMP"
        ")",
    ]

    if backend == "sqlite":
        return common_tables

    if backend in ("postgres", "mysql", "mariadb"):
        # Return generic SQL - backends will adapt
        return common_tables

    logger.warning(f"Unknown backend {backend}, returning generic schema")
    return common_tables
