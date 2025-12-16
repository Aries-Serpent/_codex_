"""Regression tests for tamper-evident audit logger."""

from __future__ import annotations

from pathlib import Path

import pytest

from security.audit_logger import AuditLogger


def test_audit_logger_appends_and_verifies(tmp_path: Path):
    log_path = tmp_path / "audit.log"
    logger = AuditLogger(log_path)

    first = logger.append({"action": "create"}, ts=0)
    second = logger.append({"action": "update"}, ts=1)

    assert first["hash"] != second["hash"]
    assert logger.verify_chain() is True


def test_audit_logger_detects_tampering(tmp_path: Path):
    log_path = tmp_path / "audit.log"
    logger = AuditLogger(log_path)
    logger.append({"action": "create"}, ts=0)

    # Tamper with last line
    contents = log_path.read_text(encoding="utf-8").splitlines()
    contents[-1] = contents[-1].replace("create", "tamper")
    log_path.write_text("\n".join(contents), encoding="utf-8")

    assert logger.verify_chain() is False
