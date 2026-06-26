"""
Test Chat Session Exit

Test module for chat session exit.
"""

import os

import pytest

from codex.chat import ChatSession


def test_env_var_removed_when_log_event_raises(monkeypatch):
    """The ``CODEX_SESSION_ID`` env var is removed even if logging fails."""

    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)

    def boom(session_id, role, message, **kwargs):
        if message == "session_end":
            raise RuntimeError("boom")

    monkeypatch.setattr("codex.chat.log_event", boom)
    cs = ChatSession("boom")

    with pytest.raises(RuntimeError), cs:
        pass

    assert "CODEX_SESSION_ID" not in os.environ, "Condition must be true"


def test_env_cleared_when_body_and_log_fail(monkeypatch):
    """Environment variable cleared if body and logging both fail."""

    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)

    def boom(session_id, role, message, **kwargs):
        if message == "session_end":
            raise RuntimeError("boom")

    monkeypatch.setattr("codex.chat.log_event", boom)

    with pytest.raises(RuntimeError), ChatSession("boom"):
        pass

    assert "CODEX_SESSION_ID" not in os.environ, "Condition must be true"
