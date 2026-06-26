"""Smoke tests for codex.logging.session_logger."""

from __future__ import annotations

from pathlib import Path

from codex.logging import session_logger


def test_session_logger_context_records(tmp_path: Path) -> None:
    db_path = tmp_path / "logs.db"
    with session_logger.SessionLogger(session_id="test-session", db_path=db_path) as logger:
        logger.log("user", "hello")
        logger.log("assistant", "hi")
    messages = session_logger.fetch_messages("test-session", db_path=db_path)
    assert len(messages) >= 2, "Messages must not be empty"


def test_log_message_rejects_invalid_role(tmp_path: Path) -> None:
    db_path = tmp_path / "logs.db"
    try:
        session_logger.log_message("sid", "invalid", "msg", db_path=db_path)
    except ValueError:
        return
    assert False, "log_message should reject invalid role"
