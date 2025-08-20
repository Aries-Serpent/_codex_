import sqlite3

from src.codex.logging.conversation_logger import (
    end_session,
    log_message,
    start_session,
)


def _count(db):
    with sqlite3.connect(db) as c:
        return c.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]


def test_wrapper_logs_messages(tmp_path):
    db = tmp_path / "conv.db"
    sid = "wrapper-session"
    messages = ["hi", "yo"]
    start_session(sid, db_path=str(db))
    log_message(sid, "user", messages[0], db_path=str(db))
    log_message(sid, "assistant", messages[1], db_path=str(db))
    end_session(sid, db_path=str(db))
    expected_rows = 2 + len(messages)  # start/end plus one row per message
    assert _count(db) == expected_rows
