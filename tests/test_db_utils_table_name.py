"""Tests for database utility table-name inference."""

import sqlite3

from src.codex.logging.db_utils import infer_probable_table


def test_db_utils_table_name() -> None:
    """`infer_probable_table` should select the expected table."""

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE other (id INTEGER)")
    con.execute("CREATE TABLE session_events (session_id TEXT, message TEXT)")
    table = infer_probable_table(con)
    assert table == "session_events"

