import os
import sqlite3
import uuid

from src.codex.chat import ChatSession


def _count(db):
    with sqlite3.connect(db) as c:
        return c.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]


def test_chat_session_logs_and_env(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    with ChatSession(session_id="env-session", db_path=str(db)) as chat:
        assert os.getenv("CODEX_SESSION_ID") == "env-session"
        chat.log_user("hi")
        chat.log_assistant("yo")
    assert _count(db) == 4
    assert os.getenv("CODEX_SESSION_ID") is None


def test_chat_session_generates_uuid(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    with ChatSession(db_path=str(db)) as chat:
        sid = chat.session_id
        assert os.getenv("CODEX_SESSION_ID") == sid
        uuid.UUID(sid)
    assert os.getenv("CODEX_SESSION_ID") is None
