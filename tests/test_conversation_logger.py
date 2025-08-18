import sqlite3
import sys
from pathlib import Path

# ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from codex.logging.conversation_logger import (
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
    start_session(sid, db_path=str(db))
    log_message(sid, "user", "hi", db_path=str(db))
    log_message(sid, "assistant", "yo", db_path=str(db))
    end_session(sid, db_path=str(db))
    assert _count(db) == 4
