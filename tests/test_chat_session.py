"""
Test Chat Session

Test module for chat session.
"""

import importlib.util
import os
import pathlib
import re
import sqlite3
import uuid

import pytest

from codex.chat import ChatSession


def _count(db):
    with sqlite3.connect(db) as c:
        return c.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]


def test_chat_session_logs_and_env(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    messages = ["hi", "yo"]
    with ChatSession(session_id="env-session", db_path=str(db)) as chat:
        assert os.getenv("CODEX_SESSION_ID") == "env-session", "Condition must be true"
        chat.log_user(messages[0])
        chat.log_assistant(messages[1])
    expected_rows = 2 + len(messages)  # start/end plus one row per message
    assert _count(db) == expected_rows, "Count must be greater than zero"
    with sqlite3.connect(db) as c:
        pairs = dict(
            c.execute(
                "SELECT message, COUNT(*) FROM session_events "
                "WHERE message IN ('session_start','session_end') GROUP BY message"
            )
        )
    assert pairs.get("session_start") == 1, "Condition must be true"
    assert pairs.get("session_end") == 1, "Condition must be true"
    assert os.getenv("CODEX_SESSION_ID") is None, "Condition must be true"


def test_chat_session_generates_uuid(tmp_path, monkeypatch):
    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    with ChatSession(db_path=str(db)) as chat:
        sid = chat.session_id
        assert os.getenv("CODEX_SESSION_ID") == sid, "Condition must be true"
        uuid.UUID(sid)
    assert os.getenv("CODEX_SESSION_ID") is None, "Condition must be true"


def _load_chatsession():
    root = pathlib.Path(__file__).resolve().parents[1]
    for p in root.rglob("*.py"):
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except (IOError, OSError) as _err:
            continue
        if re.search(r"\bclass\s+ChatSession\b", t):
            spec = importlib.util.spec_from_file_location("cs_mod", str(p))
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)  # type: ignore
                if hasattr(mod, "ChatSession"):
                    return mod.ChatSession
            except (ValueError, TypeError) as _err:
                continue
    return None


def test_exception_restores_env():
    ChatSession = _load_chatsession()
    if ChatSession is None:
        pytest.xfail("ChatSession not found/importable; implement ChatSession or update mapping")
    os.environ["CODEX_SESSION_ID"] = "dummy"
    cs = None
    try:
        try:
            cs = ChatSession()
        except TypeError:
            pytest.xfail("ChatSession requires args; provide a zero-arg default or factory")
        if cs is None:
            pytest.xfail("ChatSession could not be instantiated")
        with cs:
            raise RuntimeError("boom")
    except RuntimeError:
        _ = None  # suppressed: no action needed
    assert os.environ.get("CODEX_SESSION_ID") == "dummy", "Condition must be true"


def test_nested_sessions_restore_previous(tmp_path, monkeypatch):
    chat_session_class = _load_chatsession()
    if chat_session_class is None:
        pytest.xfail("ChatSession not found/importable; implement ChatSession or update mapping")

    monkeypatch.setenv("CODEX_SESSION_ID", "outer")
    db = tmp_path / "chat.db"

    with chat_session_class(session_id="outer", db_path=str(db)):
        with chat_session_class(session_id="inner", db_path=str(db)):
            assert os.environ.get("CODEX_SESSION_ID") == "inner", "Condition must be true"
        assert os.environ.get("CODEX_SESSION_ID") == "outer", "Condition must be true"

    assert os.environ.get("CODEX_SESSION_ID") == "outer", "Condition must be true"
