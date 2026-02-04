"""Tests for database utility table-name inference and sanitization."""

import sqlite3

import pytest

from src.codex.logging.db_utils import get_columns, infer_probable_table


def test_db_utils_table_name() -> None:
    """`infer_probable_table` should select the expected table."""

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE other (id INTEGER)")
    con.execute("CREATE TABLE session_events (session_id TEXT, message TEXT)")
    table = infer_probable_table(con)
    assert table == "session_events"


def test_get_columns_rejects_invalid_name() -> None:
    con = sqlite3.connect(":memory:")
    try:
        with pytest.raises(ValueError):
            get_columns(con, "bad;DROP TABLE other;")
    finally:
        con.close()
