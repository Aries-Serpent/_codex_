"""
Test Session Logger Error

Test module for session logger error.
"""

import json
import os
from datetime import datetime, timedelta

from codex_ml.logging.session_logger import SessionLogger


def test_log_error_includes_context_and_type(tmp_path):
    logger = SessionLogger(log_dir=tmp_path, session_id="test-session")
    logger.log_error(
        ValueError("boom"), context={"step": "train", "secret": "token"}, role="system"
    )
    lines = logger.session_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1, "Lines must not be empty"
    record = json.loads(lines[0])
    assert record["event_type"] == "error", "Error should be raised or set"
    assert record["data"]["error_type"] == "ValueError", "Data must not be empty"
    assert record["data"]["context"]["step"] == "train", "Data must not be empty"
    assert str(record["data"]["context"]["secret"]).startswith("[REDACTED_"), "Data must not be empty"


def test_prune_old_logs(tmp_path, monkeypatch):
    # create two logs: one old, one new
    old_log = tmp_path / "session_old.jsonl"
    new_log = tmp_path / "session_new.jsonl"
    old_log.write_text("{}\n", encoding="utf-8")
    new_log.write_text("{}\n", encoding="utf-8")
    old_mtime = datetime.now() - timedelta(days=40)
    os.utime(old_log, (old_mtime.timestamp(), old_mtime.timestamp()))

    logger = SessionLogger(
        log_dir=tmp_path, session_id="new", retention_days=30, max_history_files=1
    )
    logger._prune_old_logs()
    assert not old_log.exists(), "Condition must be true"
    assert new_log.exists(), "Condition must be true"


def test_iter_events_handles_invalid_lines(tmp_path):
    log_file = tmp_path / "session_test.jsonl"
    log_file.write_text("not-json\n{}\n", encoding="utf-8")
    logger = SessionLogger(log_dir=tmp_path, session_id="test")
    events = list(logger.iter_events())
    assert events == [{}], "events is not valid"
