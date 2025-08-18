import json, os, sqlite3, subprocess, sys, time
from pathlib import Path

import pytest

from codex.logging.session_logger import SessionLogger, log_message

def _all_events(db):
    con = sqlite3.connect(db)
    try:
        cur = con.cursor()
        return list(cur.execute("SELECT role, message FROM session_events ORDER BY ts ASC"))
    finally:
        con.close()

def test_context_manager_start_end(tmp_path, monkeypatch):
    db = tmp_path/"test.db"
    sid = "T1"
    with SessionLogger(session_id=sid, db_path=db):
        pass
    rows = _all_events(db)
    messages = [m for r,m in rows if r == "system"]
    assert any("session_start" in m for m in messages)
    assert any("session_end" in m for m in messages)

def test_log_message_helper(tmp_path):
    db = tmp_path/"test2.db"
    sid = "T2"
    log_message(sid, "user", "hi", db_path=db)
    log_message(sid, "assistant", "hello", db_path=db)
    rows = _all_events(db)
    assert ("user", "hi") in rows
    assert ("assistant", "hello") in rows

def test_cli_query_returns_rows(tmp_path, monkeypatch):
    db = tmp_path/"test3.db"
    sid = "T3"
    log_message(sid, "user", "hi", db_path=db)
    log_message(sid, "assistant", "yo", db_path=db)
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    env = os.environ.copy()
    env["CODEX_LOG_DB_PATH"] = str(db)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run([sys.executable, "-m", "codex.logging.session_query", "--session-id", sid, "--last", "1"], capture_output=True, text=True, env=env, cwd=tmp_path)
    assert proc.returncode == 0
    out = proc.stdout.strip()
    assert "assistant" in out and "yo" in out
