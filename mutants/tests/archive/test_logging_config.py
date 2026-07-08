"""
Test Logging Config

Test module for logging config.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from codex.archive import logging_config
from codex.archive.config import LoggingConfig, PerformanceConfig
from codex.archive.perf import TimingMetrics


def test_setup_logging_json_format() -> None:
    buffer = io.StringIO()
    cfg = LoggingConfig(level="info", format="json")
    logger = logging_config.setup_logging(cfg, stream=buffer)
    logger.info("hello", extra={"tombstone": "abc"})
    output = json.loads(buffer.getvalue())
    assert output["message"] == "hello", "Condition must be true"
    assert output["extra"]["tombstone"] == "abc", "Condition must be true"


def test_setup_logging_text_format() -> None:
    buffer = io.StringIO()
    cfg = LoggingConfig(level="debug", format="text")
    logger = logging_config.setup_logging(cfg, stream=buffer)
    logger.debug("example", extra={"status": "OK"})
    output = buffer.getvalue().strip()
    assert "[DEBUG] example" in output, "Condition must be true"
    assert "status=OK" in output, "Condition must be true"


def test_setup_logging_reenables_existing_logger() -> None:
    initial_buffer = io.StringIO()
    cfg = LoggingConfig(level="info", format="json")
    logger = logging_config.setup_logging(cfg, stream=initial_buffer)
    logger.disabled = True

    buffer = io.StringIO()
    logger = logging_config.setup_logging(cfg, stream=buffer)
    logger.info("hello", extra={"tombstone": "abc"})

    payload = json.loads(buffer.getvalue())
    assert logger.disabled is False, "setup_logging() should re-enable the named logger"
    assert payload["message"] == "hello", "Condition must be true"


def test_log_restore_appends_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence_dir = tmp_path / "evidence"
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", str(evidence_dir))
    cfg = LoggingConfig(level="info", format="json")
    perf_cfg = PerformanceConfig(enabled=True, emit_to_evidence=True)
    logger = logging_config.setup_logging(cfg, stream=io.StringIO())

    metrics = TimingMetrics(name="restore:test", started_ns=0, finished_ns=100_000)
    logging_config.log_restore(
        logger,
        actor="tester",
        tombstone="abc",
        status="SUCCESS",
        detail="postgresql://user:***@localhost/db",
        metrics=metrics.to_dict(),
        logging_config=cfg,
        performance_config=perf_cfg,
    )

    evidence_file = evidence_dir / "archive_ops.jsonl"
    content = evidence_file.read_text().strip()
    payload = json.loads(content)
    assert payload["actor"] == "tester", "Condition must be true"
    assert payload["status"] == "SUCCESS", "Condition must be true"
    assert "***@" in payload["detail"], "Condition must be true"
    assert payload["metrics"]["duration_ms"] >= 0, "Value must be greater than zero"


def test_log_restore_respects_performance_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence_dir = tmp_path / "evidence"
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", str(evidence_dir))
    cfg = LoggingConfig(level="info", format="json")
    perf_cfg = PerformanceConfig(enabled=False, emit_to_evidence=False)
    logger = logging_config.setup_logging(cfg, stream=io.StringIO())

    logging_config.log_restore(
        logger,
        actor="tester",
        tombstone="abc",
        status="FAILED",
        detail="http://example",  # nothing to redact
        logging_config=cfg,
        performance_config=perf_cfg,
    )

    evidence_file = evidence_dir / "archive_ops.jsonl"
    assert evidence_file.exists() is False, "Condition must be true"


def test_log_restore_emits_structured_fields() -> None:
    buffer = io.StringIO()
    cfg = LoggingConfig(level="info", format="json")
    perf_cfg = PerformanceConfig(enabled=False, emit_to_evidence=False)
    logger = logging_config.setup_logging(cfg, stream=buffer)

    logging_config.log_restore(
        logger,
        actor="tester",
        tombstone="abc",
        status="SUCCESS",
        detail="http://example",  # nothing to redact
        logging_config=cfg,
        performance_config=perf_cfg,
    )

    payload = json.loads(buffer.getvalue())
    assert payload["message"] == "restore success", "Condition must be true"
    assert payload["extra"]["actor"] == "tester", "Condition must be true"
    assert payload["extra"]["tombstone"] == "abc", "Condition must be true"
    assert payload["extra"]["status"] == "SUCCESS", "Condition must be true"
