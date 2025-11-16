"""Tests for the session-aware structured logger."""

from __future__ import annotations

import json
import sqlite3

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
    assert len(records) == 1
    record = records[0]
    assert record["session_id"] == "test-session"
    assert record["role"] == "assistant"
    assert record["event_type"] == "inference_request"
    payload = record["data"]
    assert payload["api_key"].startswith("[REDACTED_API_KEY]")
    assert payload["nested"]["password"].startswith("[REDACTED_PASSWORD]")


def test_session_logger_mirrors_metrics_to_sqlite(tmp_path):
    db_path = tmp_path / "metrics.db"
    logger = SessionLogger(
        session_id="mirror-test",
        log_dir=tmp_path,
        metrics_db_path=db_path,
        mirror_metrics=True,
    )

    logger.log_event("epoch", {"epoch": 5, "metrics": {"loss": 0.25, "acc": 0.9}})

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT metric, value, epoch FROM metric_records ORDER BY metric"
        ).fetchall()
    finally:
        conn.close()

    assert rows == [("acc", 0.9, 5), ("loss", 0.25, 5)]
