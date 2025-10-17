"""Tests for structured logging configuration."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from codex.archive.logging_config import (
    StructuredFormatter,
    StructuredLogRecord,
    log_restore,
    setup_logging,
)


class TestStructuredLogRecord:
    def test_to_dict_includes_optional_fields(self) -> None:
        record = StructuredLogRecord(
            timestamp="2020-01-01T00:00:00Z",
            level="info",
            action="RESTORE",
            actor="tester",
            tombstone="abc",
            duration_ms=123.0,
            backend="sqlite",
            url="sqlite:///test.db",
            extra={"foo": "bar"},
        )
        payload = record.to_dict()
        assert payload["action"] == "RESTORE"
        assert payload["foo"] == "bar"
        assert payload["tombstone"] == "abc"

    def test_to_json_serializes_payload(self) -> None:
        record = StructuredLogRecord(
            timestamp="2020-01-01T00:00:00Z",
            level="info",
            action="RESTORE",
        )
        data = json.loads(record.to_json())
        assert data["action"] == "RESTORE"


class TestStructuredFormatter:
    def test_json_format_uses_extra_fields(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = logging.getLogger("codex.archive.test")
        logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter(format_type="json"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        with caplog.at_level(logging.INFO, logger="codex.archive.test"):
            logger.info("RESTORE", extra={"extra_fields": {"actor": "tester"}})
        record = caplog.records[0]
        assert record.extra_fields["actor"] == "tester"

    def test_text_format_outputs_plain_message(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = logging.getLogger("codex.archive.test.text")
        logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter(format_type="text"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        with caplog.at_level(logging.INFO, logger="codex.archive.test.text"):
            logger.info("hello")
        assert "hello" in caplog.records[0].message


class TestSetupLogging:
    def test_setup_logging_configures_handlers(self, tmp_path: Path) -> None:
        log_file = tmp_path / "archive.log"
        logger = setup_logging(level="info", format_type="json", log_file=log_file.as_posix())
        assert logger.name == "codex.archive"
        assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
        assert log_file.exists()


class TestLogRestore:
    def test_log_restore_records_redacted_url(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = setup_logging(level="info", format_type="json")
        with caplog.at_level(logging.INFO, logger=logger.name):
            log_restore(
                logger,
                "RESTORE",
                tombstone="abc",
                actor="tester",
                backend="sqlite",
                url="sqlite://token@localhost/db",
                duration_ms=12.0,
                extra={"foo": "bar"},
            )
        record = caplog.records[0]
        assert record.extra_fields["url"].startswith("sqlite://***@")
        assert record.extra_fields["foo"] == "bar"
