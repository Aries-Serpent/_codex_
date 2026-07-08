"""Ensure chat session environment variables are cleared after use."""

import os

from codex.chat import ChatSession


def test_chat_env_cleanup(tmp_path, monkeypatch):
    """`CODEX_SESSION_ID` should not persist after the session exits."""

    db = tmp_path / "chat.db"
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    with ChatSession(session_id="cleanup", db_path=str(db)):
        assert os.getenv("CODEX_SESSION_ID") == "cleanup", "Condition must be true"
    assert os.getenv("CODEX_SESSION_ID") is None, "Condition must be true"
