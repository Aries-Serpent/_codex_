"""
Test Session Logger

Test module for session logger.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from codex_ml.logging.session_logger import SessionLogger


class DummyRedactor:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def redact_dict(self, value: dict[str, str]) -> dict[str, str]:
        self.calls.append(value)
        cleaned: dict[str, str] = {}
        for key, val in value.items():
            if isinstance(val, dict):
                cleaned[key] = {inner: f"redacted-{inner_val}" for inner, inner_val in val.items()}
            else:
                cleaned[key] = f"redacted-{val}"
        return cleaned


def test_session_logger_writes_events(tmp_path):
    logger = SessionLogger(session_id="test-session", log_dir=tmp_path, redactor=DummyRedactor())

    path = logger.log_event("info", {"msg": "hello"}, role="user")

    assert path.exists(), "Condition must be true"
    content = path.read_text(encoding="utf-8").strip().splitlines()
    assert content, "log file should contain entries"
    event = json.loads(content[0])
    assert event["session_id"] == "test-session", "Condition must be true"
    assert event["role"] == "user", "Condition must be true"
    assert event["event_type"] == "info", "Condition must be true"
    assert event["data"]["msg"] == "redacted-hello", "Data must not be empty"


def test_session_logger_error_logging(tmp_path):
    redactor = DummyRedactor()
    logger = SessionLogger(log_dir=tmp_path, redactor=redactor)

    logger.log_error(RuntimeError("boom"), context={"details": "secret"}, role="assistant")

    content = (logger.session_file).read_text(encoding="utf-8").splitlines()
    assert content, "error log should be recorded"
    record = json.loads(content[0])
    assert record["event_type"] == "error", "Error should be raised or set"
    assert record["data"]["context"]["details"].startswith("redacted-"), "Data must not be empty"


def test_prune_old_logs_respects_retention(tmp_path):
    old = tmp_path / "session_old.jsonl"
    old.write_text("{}\n", encoding="utf-8")
    older_than_week = (datetime.now(timezone.utc) - timedelta(days=8)).timestamp()
    os.utime(old, (older_than_week, older_than_week))

    logger = SessionLogger(log_dir=tmp_path, retention_days=7, max_history_files=1)
    logger.log_event("info", {"msg": "fresh"})
    logger._prune_old_logs()

    assert not old.exists(), "Condition must be true"
    assert logger.session_file.exists(), "Condition must be true"
