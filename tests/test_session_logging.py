# pytest: tests for session logging
import sqlite3
import sys
from pathlib import Path

# ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

def _count_rows(db):
    with sqlite3.connect(db) as c:
        return c.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]

def test_insert_sample_conversation(tmp_path, monkeypatch):
    db = tmp_path / "test_log.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    # import after env to ensure module picks up the path
    from codex.logging.session_logger import init_db, log_event
    init_db()
    sid = "test-session-001"
    log_event(sid, "system", "session_start")
    log_event(sid, "user", "Hello")
    log_event(sid, "assistant", "Hi there!", model="gpt-4", tokens=3)
    log_event(sid, "system", "session_end")
    assert _count_rows(db) == 4
    with sqlite3.connect(db) as c:
        row = c.execute("SELECT model, tokens FROM session_events WHERE role='assistant'").fetchone()
    assert row == ("gpt-4", 3)

def test_idempotent_init(tmp_path, monkeypatch):
    db = tmp_path / "init.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    from codex.logging.session_logger import init_db
    init_db()
    init_db()  # second call should not fail
    with sqlite3.connect(db) as c:
        cols = [r[1] for r in c.execute("PRAGMA table_info(session_events)")]
    assert set(["session_id","timestamp","role","message","model","tokens"]).issubset(set(cols))

def test_migration_adds_columns(tmp_path):
    db = tmp_path / "mig.db"
    with sqlite3.connect(db) as c:
        c.execute("CREATE TABLE session_events(session_id TEXT NOT NULL, timestamp TEXT NOT NULL, role TEXT NOT NULL, message TEXT NOT NULL, PRIMARY KEY(session_id, timestamp))")
    from codex.logging.session_logger import init_db
    init_db(str(db))
    with sqlite3.connect(db) as c:
        cols = [r[1] for r in c.execute("PRAGMA table_info(session_events)")]
    assert "model" in cols and "tokens" in cols
