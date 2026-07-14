"""Smoke tests for :mod:`codex.chat` chat session helper."""

from __future__ import annotations

import os
from typing import Any


def test_chat_session_records_events(monkeypatch, tmp_path):
    """ChatSession should emit start/end and message events while restoring env."""
    events: list[tuple[str, str, str, Any]] = []

    def fake_log(session_id: str, role: str, message: str, db_path=None, meta=None):
        events.append((session_id, role, message, db_path))

    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(tmp_path / "log.db"))
    monkeypatch.setattr("codex.chat.log_event", fake_log)
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)

    from codex.chat import ChatSession

    with ChatSession("session-123") as chat:
        assert os.environ.get("CODEX_SESSION_ID") == "session-123", "Condition must be true"
        chat.log_user("hello")
        chat.log_assistant("world")

    # Environment restored
    assert os.environ.get("CODEX_SESSION_ID") is None, "Condition must be true"
    # Events captured: start, two messages, end
    roles = [role for _, role, _, _ in events]
    assert "system" in roles and "user" in roles and "assistant" in roles
    assert roles.count("system") == 2, "Count must be greater than zero"
