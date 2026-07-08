"""Regression tests for tamper-evident audit logger."""

from __future__ import annotations

import json
from pathlib import Path

from security.audit_logger import AuditLogger, log_audit_event

# ---------------------------------------------------------------------------
# AuditLogger construction
# ---------------------------------------------------------------------------


def test_audit_logger_with_explicit_path(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(path=log_path)
    assert al.path == log_path, "path is not valid"


def test_audit_logger_with_log_dir(tmp_path: Path) -> None:
    al = AuditLogger(log_dir=tmp_path)
    assert al.path == tmp_path / "audit.log", "path is not valid"


def test_audit_logger_default_path() -> None:
    al = AuditLogger()
    assert "audit.log" in str(al.path), "Condition must be true"


# ---------------------------------------------------------------------------
# Core append + verify_chain
# ---------------------------------------------------------------------------


def test_audit_logger_appends_and_verifies(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)

    first = al.append({"action": "create"}, ts=0)
    second = al.append({"action": "update"}, ts=1)

    assert first["hash"] != second["hash"], "Condition must be true"
    assert al.verify_chain() is True, "Condition must be true"


def test_audit_logger_detects_tampering(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.append({"action": "create"}, ts=0)

    # Tamper with last line
    contents = log_path.read_text(encoding="utf-8").splitlines()
    contents[-1] = contents[-1].replace("create", "tamper")
    log_path.write_text("\n".join(contents), encoding="utf-8")

    assert al.verify_chain() is False, "Condition must be true"


def test_verify_chain_empty_log(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    # No file exists yet
    assert al.verify_chain() is True, "Condition must be true"


def test_verify_chain_with_empty_lines(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.append({"action": "create"}, ts=0)
    # Add blank lines between records
    existing = log_path.read_text(encoding="utf-8")
    log_path.write_text("\n" + existing + "\n\n", encoding="utf-8")
    assert al.verify_chain() is True, "Condition must be true"


def test_verify_chain_detects_wrong_prev_hash(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.append({"action": "first"}, ts=0)
    al.append({"action": "second"}, ts=1)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    # Corrupt the prev_hash field of the second record
    rec = json.loads(lines[1])
    rec["prev_hash"] = "wronghash"
    lines[1] = json.dumps(rec, sort_keys=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert al.verify_chain() is False, "Condition must be true"


def test_verify_chain_detects_missing_hash_field(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.append({"action": "first"}, ts=0)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[0])
    del rec["hash"]  # Remove hash field
    lines[0] = json.dumps(rec, sort_keys=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert al.verify_chain() is False, "Condition must be true"


def test_audit_logger_multiple_records_chain(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)

    for i in range(5):
        al.append({"seq": i}, ts=float(i))

    assert al.verify_chain() is True, "Condition must be true"
    assert log_path.exists(), "Condition must be true"


def test_append_uses_current_time_when_ts_not_provided(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    record = al.append({"action": "test"})
    assert record["ts"] > 0, "rec must be greater than zero"


# ---------------------------------------------------------------------------
# log_event helper method
# ---------------------------------------------------------------------------


def test_log_event_writes_structured_entry(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.log_event(
        event_type="authentication",
        resource="/api/login",
        action="login",
        user="testuser",
    )
    assert log_path.exists(), "Condition must be true"
    data = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert data["event"]["event_type"] == "authentication", "Data must not be empty"
    assert data["event"]["user"] == "testuser", "Data must not be empty"
    assert data["event"]["action"] == "login", "Data must not be empty"
    assert data["event"]["resource"] == "/api/login", "Data must not be empty"


def test_log_event_chain_is_valid(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    al.log_event("auth", "/api/login", "login", "alice")
    al.log_event("access", "/api/data", "read", "alice")
    assert al.verify_chain() is True, "Condition must be true"


# ---------------------------------------------------------------------------
# log_audit_event standalone function
# ---------------------------------------------------------------------------


def test_log_audit_event_creates_file(tmp_path: Path) -> None:
    log_audit_event("authentication", "testuser", "login", success=True, log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    assert log_file.exists(), "Condition must be true"


def test_log_audit_event_records_content(tmp_path: Path) -> None:
    log_audit_event("authentication", "alice", "login", success=True, log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    content = log_file.read_text(encoding="utf-8")
    data = json.loads(content.strip())
    assert data["event"]["user"] == "alice", "Data must not be empty"
    assert data["event"]["action"] == "login", "Data must not be empty"
    assert data["event"]["type"] == "authentication", "Data must not be empty"
    assert data["event"]["success"] is True, "Data must not be empty"


def test_log_audit_event_failure_recorded(tmp_path: Path) -> None:
    log_audit_event("authentication", "bob", "login", success=False, log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    data = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert data["event"]["success"] is False, "Data must not be empty"


def test_log_audit_event_default_success(tmp_path: Path) -> None:
    log_audit_event("access", "user1", "read", log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    data = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert data["event"]["success"] is True, "Data must not be empty"


# ---------------------------------------------------------------------------
# _last_hash edge cases
# ---------------------------------------------------------------------------


def test_last_hash_nonexistent_file(tmp_path: Path) -> None:
    log_path = tmp_path / "nonexistent.log"
    al = AuditLogger(log_path)
    # _last_hash called internally via append; verify prev_hash is zeros
    record = al.append({"action": "first"}, ts=0)
    assert record["prev_hash"] == "0" * 64, "rec is not valid"


def test_last_hash_record_without_hash_field(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    al = AuditLogger(log_path)
    # Write a line that has no "hash" field
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text('{"ts": 1.0, "event": {}, "prev_hash": "abc"}\n', encoding="utf-8")
    # Should fall back to zeros
    record = al.append({"action": "after"}, ts=2)
    assert record["prev_hash"] == "0" * 64, "rec is not valid"
