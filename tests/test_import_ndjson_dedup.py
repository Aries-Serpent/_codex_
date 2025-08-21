import json
import os
import sqlite3
from pathlib import Path

from src.codex.logging import import_ndjson, session_hooks
from src.codex.logging.session_hooks import session


def test_importer_deduplicates_start_end(tmp_path, monkeypatch):
    log_dir = tmp_path / "sessions"
    db_path = tmp_path / "logs.db"
    monkeypatch.setenv("CODEX_SESSION_LOG_DIR", str(log_dir))
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db_path))
    monkeypatch.setattr(session_hooks, "LOG_DIR", log_dir)
    session_hooks.LOG_DIR.mkdir(parents=True, exist_ok=True)
    with session() as s:
        sid = s.sid
    # reimport should not duplicate start/end
    count_before = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM session_events"
    ).fetchone()[0]
    import_ndjson.import_session(sid, log_dir=log_dir, db_path=db_path)
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            "SELECT message, COUNT(*) FROM session_events WHERE message IN ('session_start','session_end') GROUP BY message"
        ).fetchall()
    pairs = dict(rows)
    assert pairs.get("session_start") == 1
    assert pairs.get("session_end") == 1
    # ensure no extra rows created beyond original two
    total = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM session_events"
    ).fetchone()[0]
    assert total == count_before
