# Auto-generated tests for db_utils.py
import sqlite3

# Try both namespaces for imports
try:
    from src.codex.logging.db_utils import (
        infer_columns,
        infer_probable_table,
        list_tables,
    )
except Exception:
    from codex.logging.db_utils import (
        infer_columns,
        infer_probable_table,
        list_tables,
    )


def test_infer_on_session_events_minimal():
    con = sqlite3.connect(":memory:")
    con.executescript("""
        CREATE TABLE session_events(
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            created_at TEXT,
            content TEXT
        );
    """)
    try:
        assert "session_events" in list_tables(con)
        t = infer_probable_table(con, candidates=("session_events", "logs"))
        assert t == "session_events"
        cols = infer_columns(con, t)
        assert cols["session_id"] in ("session_id",)
        assert cols["timestamp"] in ("created_at",)
        assert cols["message"] in ("content",)
    finally:
        con.close()


def test_infer_on_logs_variants():
    con = sqlite3.connect(":memory:")
    con.executescript("""
        CREATE TABLE logs(
            ts REAL, sid TEXT, message TEXT, level TEXT
        );
    """)
    try:
        t = infer_probable_table(con, candidates=("session_events", "logs"))
        assert t == "logs"
        cols = infer_columns(con, t)
        assert cols["timestamp"] in ("ts",)
        assert cols["session_id"] in ("sid",)
        assert cols["message"] in ("message",)
        assert cols["level"] in ("level",)
    finally:
        con.close()
