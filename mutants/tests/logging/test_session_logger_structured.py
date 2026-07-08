"""Tests for the session-aware structured logger."""

from __future__ import annotations

import json

from codex_ml.logging.session_logger import SessionLogger


def test_session_logger_redacts_sensitive_fields(tmp_path):
    logger = SessionLogger(session_id="test-session", log_dir=tmp_path)
    logfile = logger.log_event(
        "inference_request",
        {"api_key": "sk-abc123", "nested": {"password": "hunter2"}},  # pragma: allowlist secret
        role="assistant",
    )

    records = [
        json.loads(line)
        for line in logfile.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 1, "Records must not be empty"
    record = records[0]
    assert record["session_id"] == "test-session", "rec is not valid"
    assert record["role"] == "assistant", "rec is not valid"
    assert record["event_type"] == "inference_request", "rec is not valid"
    payload = record["data"]
    assert payload["api_key"].startswith("[REDACTED_API_KEY]"), "Condition must be true"
    assert payload["nested"]["password"].startswith("[REDACTED_PASSWORD]"), "Condition must be true"
