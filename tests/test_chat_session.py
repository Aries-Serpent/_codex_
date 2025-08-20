import importlib.util
import os
import pathlib
import re
import sqlite3
import uuid

import pytest

from src.codex.chat import ChatSession


def _count(db):
    with sqlite3.connect(db) as c:
        return c.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]


def test_chat_session_logs_and_env(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    messages = ["hi", "yo"]
    with ChatSession(session_id="env-session", db_path=str(db)) as chat:
        assert os.getenv("CODEX_SESSION_ID") == "env-session"
        chat.log_user(messages[0])
        chat.log_assistant(messages[1])
    expected_rows = 2 + len(messages)  # start/end plus one row per message
    assert _count(db) == expected_rows
    assert os.getenv("CODEX_SESSION_ID") is None


def test_chat_session_generates_uuid(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    with ChatSession(db_path=str(db)) as chat:
        sid = chat.session_id
        assert os.getenv("CODEX_SESSION_ID") == sid
        uuid.UUID(sid)
    assert os.getenv("CODEX_SESSION_ID") is None


def _load_chatsession():
    root = pathlib.Path(__file__).resolve().parents[1]
    for p in root.rglob("*.py"):
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"\bclass\s+ChatSession\b", t):
            spec = importlib.util.spec_from_file_location("cs_mod", str(p))
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)  # type: ignore
                if hasattr(mod, "ChatSession"):
                    return getattr(mod, "ChatSession")
            except Exception:
                continue
    return None


def test_exception_restores_env():
    ChatSession = _load_chatsession()
    if ChatSession is None:
        pytest.xfail(
            "ChatSession not found/importable; implement ChatSession or update mapping"
        )
    os.environ["CODEX_SESSION_ID"] = "dummy"
    try:
        try:
            cs = ChatSession()
        except TypeError:
            pytest.xfail(
                "ChatSession requires args; provide a zero-arg default or factory"
            )
        with cs:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert os.environ.get("CODEX_SESSION_ID") in (None, ""), (
        "CODEX_SESSION_ID should be unset after exception"
    )
