from __future__ import annotations

import io
import json
import logging
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
    assert output["message"] == "hello"
    assert output["extra"]["tombstone"] == "abc"


def test_setup_logging_text_format() -> None:
    buffer = io.StringIO()
    cfg = LoggingConfig(level="debug", format="text")
    logger = logging_config.setup_logging(cfg, stream=buffer)
    logger.debug("example", extra={"status": "OK"})
    output = buffer.getvalue().strip()
    assert "[DEBUG] example" in output
    assert "status=OK" in output


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
    assert payload["actor"] == "tester"
    assert payload["status"] == "SUCCESS"
    assert "***@" in payload["detail"]
    assert payload["metrics"]["duration_ms"] >= 0


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
    assert evidence_file.exists() is False
