"""Regression tests for tamper-evident audit logger."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from security.audit_logger import AuditLogger, log_audit_event


def _rehash(record: dict[str, object]) -> None:
    encoded = json.dumps(
        {key: value for key, value in record.items() if key != "hash"}, sort_keys=True
    ).encode("utf-8")
    record["hash"] = hashlib.sha256(encoded).hexdigest()

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


def test_audit_logger_emits_canonical_envelope_with_extensions_in_payload(
    tmp_path: Path,
) -> None:
    al = AuditLogger(tmp_path / "audit.log")

    record = al.append({"action": "create", "tenant": "example"}, ts=0)

    event = record["event"]
    assert set(event) == {
        "schema_version",
        "event_id",
        "emitted_at",
        "kind",
        "source",
        "source_version",
        "correlation_id",
        "payload",
    }
    assert event["schema_version"] == "1.0"
    assert event["kind"] == "security.audit"
    assert event["payload"] == {"action": "create", "tenant": "example"}
    assert "tenant" not in event


def test_verify_chain_accepts_legacy_event_dictionary(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    record: dict[str, object] = {
        "ts": 0.0,
        "event": {"action": "legacy"},
        "prev_hash": "0" * 64,
    }
    _rehash(record)
    log_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")

    assert AuditLogger(log_path).verify_chain() is True


def test_verify_chain_accepts_legacy_payload_schema_version(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    record: dict[str, object] = {
        "ts": 0.0,
        "event": {"action": "legacy", "schema_version": "legacy-v2"},
        "prev_hash": "0" * 64,
    }
    _rehash(record)
    log_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")

    assert AuditLogger(log_path).verify_chain() is True


def test_verify_chain_negotiates_versions_and_rejects_envelope_extensions(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "audit.log"
    logger = AuditLogger(log_path)
    logger.append({"action": "create"}, ts=0)

    assert AuditLogger(log_path, accepted_event_versions={"2.0"}).verify_chain() is False

    record = json.loads(log_path.read_text(encoding="utf-8"))
    record["event"]["tenant"] = "not-allowed-at-envelope-level"
    _rehash(record)
    log_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")

    assert logger.verify_chain() is False


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


def test_concurrent_appends_preserve_every_record_and_chain(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    event_count = 40

    def append_event(sequence: int) -> None:
        AuditLogger(log_path).append({"sequence": sequence}, ts=float(sequence))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(append_event, range(event_count)))

    records = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(records) == event_count
    assert {record["event"]["payload"]["sequence"] for record in records} == set(
        range(event_count)
    )
    assert AuditLogger(log_path).verify_chain() is True


def test_separate_process_appends_preserve_every_record_and_chain(tmp_path: Path) -> None:
    """Spawned OS processes must serialize complete hash-chain updates."""

    log_path = tmp_path / "audit.log"
    process_count = 4
    events_per_process = 10
    start_path = tmp_path / "start"
    child_script = """
import sys
import time
from pathlib import Path
from security.audit_logger import AuditLogger

log_path, start_path, ready_path = map(Path, sys.argv[1:4])
worker_id, event_count = map(int, sys.argv[4:6])
ready_path.touch()
deadline = time.monotonic() + 10
while not start_path.exists():
    if time.monotonic() >= deadline:
        raise TimeoutError("audit contention start signal was not received")
    time.sleep(0.01)
logger = AuditLogger(log_path)
for sequence in range(event_count):
    logger.append(
        {"worker_id": worker_id, "sequence": sequence},
        ts=float(worker_id * event_count + sequence),
    )
"""
    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-c",
                child_script,
                str(log_path),
                str(start_path),
                str(tmp_path / f"ready-{worker_id}"),
                str(worker_id),
                str(events_per_process),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for worker_id in range(process_count)
    ]

    try:
        ready_deadline = time.monotonic() + 10
        while not all(
            (tmp_path / f"ready-{worker_id}").exists()
            for worker_id in range(process_count)
        ):
            assert time.monotonic() < ready_deadline, "audit writers did not become ready"
            time.sleep(0.01)
        start_path.touch()
        for process in processes:
            _stdout, stderr = process.communicate(timeout=20)
            assert process.returncode == 0, stderr
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)

    records = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    observed = {
        (
            record["event"]["payload"]["worker_id"],
            record["event"]["payload"]["sequence"],
        )
        for record in records
    }
    expected = {
        (worker_id, sequence)
        for worker_id in range(process_count)
        for sequence in range(events_per_process)
    }
    assert len(records) == process_count * events_per_process
    assert observed == expected
    assert AuditLogger(log_path).verify_chain() is True


@pytest.mark.parametrize(
    "corrupt_content",
    [
        b'{"event": ',
        b"\xff\xfe\n",
        b"null\n",
    ],
    ids=["truncated-json", "invalid-utf8", "non-object"],
)
def test_verify_chain_returns_false_for_corrupt_content(
    tmp_path: Path, corrupt_content: bytes
) -> None:
    log_path = tmp_path / "audit.log"
    log_path.write_bytes(corrupt_content)

    assert AuditLogger(log_path).verify_chain() is False


def test_verify_chain_propagates_io_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_path = tmp_path / "audit.log"
    log_path.write_text("{}\n", encoding="utf-8")

    def fail_read(*args: object, **kwargs: object) -> str:
        raise OSError("storage unavailable")

    monkeypatch.setattr(Path, "read_text", fail_read)

    with pytest.raises(OSError, match="storage unavailable"):
        AuditLogger(log_path).verify_chain()


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
    payload = data["event"]["payload"]
    assert payload["event_type"] == "authentication", "Data must not be empty"
    assert payload["user"] == "testuser", "Data must not be empty"
    assert payload["action"] == "login", "Data must not be empty"
    assert payload["resource"] == "/api/login", "Data must not be empty"


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
    payload = data["event"]["payload"]
    assert payload["user"] == "alice", "Data must not be empty"
    assert payload["action"] == "login", "Data must not be empty"
    assert payload["type"] == "authentication", "Data must not be empty"
    assert payload["success"] is True, "Data must not be empty"


def test_log_audit_event_failure_recorded(tmp_path: Path) -> None:
    log_audit_event("authentication", "bob", "login", success=False, log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    data = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert data["event"]["payload"]["success"] is False, "Data must not be empty"


def test_log_audit_event_default_success(tmp_path: Path) -> None:
    log_audit_event("access", "user1", "read", log_dir=tmp_path)
    log_file = tmp_path / "audit.log"
    data = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert data["event"]["payload"]["success"] is True, "Data must not be empty"


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
