"""Ensure fetch_messages handles absent databases gracefully."""

import logging
import sqlite3

from src.codex.logging.fetch_messages import fetch_messages


def test_missing_db_returns_empty_list(tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    missing = tmp_path / "nope.db"
    result = fetch_messages("SID", db_path=missing)
    assert result == []
    assert caplog.text == ""


def test_missing_table_returns_empty_list(tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    db = tmp_path / "empty.db"
    # create SQLite database without session_events table
    sqlite3.connect(db).close()

    result = fetch_messages("SID", db_path=db)
    assert result == []
    assert caplog.text == ""
