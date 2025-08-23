import os

import pytest

from src.codex.chat import ChatSession


def test_env_var_removed_when_log_event_raises(monkeypatch):
    """The ``CODEX_SESSION_ID`` env var is removed even if logging fails."""

    def boom(session_id, role, message, **kwargs):
        if message == "session_end":
            raise RuntimeError("boom")

    monkeypatch.setattr("src.codex.chat.log_event", boom)
    cs = ChatSession("boom")

    with pytest.raises(RuntimeError):
        with cs:
            pass

    assert "CODEX_SESSION_ID" not in os.environ  # nosec B101
