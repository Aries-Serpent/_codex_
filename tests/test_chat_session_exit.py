import os
import pytest

from src.codex.chat import ChatSession


def test_env_cleared_on_log_failure(monkeypatch):
    """Environment variable cleared even if logging fails on exit."""

    def boom(session_id, role, message, **kwargs):
        if message == "session_end":
            raise RuntimeError("boom")

    monkeypatch.setattr("src.codex.chat.log_event", boom)
    cs = ChatSession("boom")

    with pytest.raises(RuntimeError):
        with cs:
            pass

    assert "CODEX_SESSION_ID" not in os.environ
