"""Legacy PDA shape and evidence integrity, with no real log/DB writes."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from detect_secrets.core.scan import scan_line
from detect_secrets.settings import transient_settings


@pytest.mark.parametrize(
    ("session", "field", "kind", "fingerprint"),
    [
        (
            "pr-5746-review-5729914229",
            "git_sha",
            "Hex High Entropy String",
            "abfc8ac80e5b1d0a464a0496cb7c401f3d8ec039",  # pragma: allowlist secret
        ),
        (
            "AGENT-SELF-IMPROVEMENT-001/draft-review-continuation",  # pragma: allowlist secret
            "git_sha",
            "Hex High Entropy String",
            "3924e2a3fe68c06e76746a82529638d4999276ce",  # pragma: allowlist secret
        ),
        (
            "AGENT-SELF-IMPROVEMENT-001/draft-review-continuation",  # pragma: allowlist secret
            "session",
            "Base64 High Entropy String",
            "dc4c17bda613551cb6a4f3c9eafa11006f55128e",  # pragma: allowlist secret
        ),
        (
            "pr-5763-archive-review-followup",
            "git_sha",
            "Hex High Entropy String",
            "0e192e272c9ca215f6bb9843411c7264d42c099d",  # pragma: allowlist secret
        ),
        (
            "pr-5765-readiness-20261109",
            "git_sha",
            "Hex High Entropy String",
            "03044088fb6f83e02c1fbc389069206c9aa6d364",  # pragma: allowlist secret
        ),
    ],
)
def test_pda_provenance_baseline_is_value_specific(session, field, kind, fingerprint):
    root = Path(__file__).resolve().parents[2]
    filename = ".codex/aftermath/pda_iterations.jsonl"
    baseline = json.loads((root / ".secrets.baseline").read_text())
    records = [json.loads(line) for line in (root / filename).read_text().splitlines()]
    record = next(row for row in records if row.get("session") == session)
    entries = [
        row
        for row in baseline["results"][filename]
        if row["type"] == kind and row["hashed_secret"] == fingerprint
    ]
    assert len(entries) == 1
    assert entries[0]["is_secret"] is False
    assert entries[0]["is_verified"] is False
    value = record[field]
    with transient_settings(baseline):
        original = list(scan_line(json.dumps({field: value})))
        changed = list(scan_line(json.dumps({field: value[::-1]})))
    assert any(row.type == kind and row.secret_hash == fingerprint for row in original)
    known = {(row["type"], row["hashed_secret"]) for row in baseline["results"][filename]}
    assert any(row.type == kind and (row.type, row.secret_hash) not in known for row in changed)


@pytest.fixture
def adapter(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[2] / "scripts/ci/pda_failure_logger.py"
    spec = importlib.util.spec_from_file_location("pda_integrity_adapter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "_PDA_LOG", tmp_path / "records.jsonl")
    monkeypatch.setattr(module, "_SOLUTIONS_YAML", tmp_path / "solutions.yaml")
    monkeypatch.setattr(module, "_RECORDER", tmp_path / "absent_recorder.py")
    monkeypatch.setattr(module, "_DB_PATH", "")
    monkeypatch.setattr(module, "_GIT_SHA", "")
    monkeypatch.setattr(module, "_RUN_ID", "")
    return module


def write_records(adapter, entries):
    adapter._PDA_LOG.write_text(
        "".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8"
    )


def event(kind, **fields):
    return {
        "type": kind,
        "pattern_id": "RP-STRING-001",
        "session": "fixture-session",
        "git_sha": "a" * 40,
        "workflow_run_id": "fixture-run-one",
        "timestamp": (
            "2026-10-01T00:00:01Z"
            if kind in {"result", "verification_result"}
            else "2026-10-01T00:00:00Z"
        ),
        **fields,
    }


def test_legacy_cli_roundtrip(adapter, capsys):
    assert (
        adapter.main(
            [
                "log-failure",
                "--session",
                "fixture-session",
                "--pattern-id",
                "RP-STRING-001",
                "--pr",
                "12",
                "--workflow",
                "fixture-workflow",
                "--root-cause",
                "fixture-cause",
                "--fix-template",
                "fixture-template",
            ]
        )
        == 0
    )
    assert (
        adapter.main(
            [
                "log-fix",
                "--session",
                "fixture-session",
                "--pattern-id",
                "RP-STRING-001",
                "--pr",
                "12",
                "--fix-applied",
                "fixture-fix",
                "--verification-cmd",
                "fixture-command",
                "--verification-passed",
            ]
        )
        == 0
    )
    assert (
        adapter.main(
            [
                "log-session",
                "--session",
                "fixture-session",
                "--pr",
                "12",
                "--patterns-fixed",
                "RP-STRING-001",
                "--workflows-checked",
                "one,two",
            ]
        )
        == 0
    )
    entries = adapter._read_log()
    assert [entry["type"] for entry in entries] == ["failure", "fix", "session"]
    assert all(entry["schema_version"] == 1 for entry in entries)
    assert entries[0]["pattern_id"] == "RP-STRING-001"
    assert entries[0]["timestamp"].endswith("Z")
    assert "T" in entries[0]["timestamp"] and ":" in entries[0]["timestamp"]
    assert entries[2]["plan"]["workflows_checked"] == ["one", "two"]
    assert adapter.main(["summarize", "--pattern-id", "RP-STRING-001"]) == 0
    output = capsys.readouterr().out
    assert "caller-labelled only" in output
    assert "0/0 rate=unknown" in output
    adapter.main(["dump", "--session", "fixture-session", "--pr", "12"])
    assert json.loads(capsys.readouterr().out) == entries


def test_no_verification_flag_does_not_pass(adapter):
    adapter.main(["log-fix", "--pattern-id", "RP-STRING-001"])
    patterns, _ = adapter._aggregate(adapter._read_log())
    rec = patterns["RP-STRING-001"]
    assert rec["fixes_attempted"] == 1
    assert rec["fixes_passed"] == 0
    assert rec["caller_labelled_success_rate"] == 0
    assert rec["fix_success_rate"] is None


@pytest.mark.parametrize(
    "timestamp",
    [
        "0001-01-01T00:00:00+23:59",
        "9999-12-31T23:59:59-23:59",
        "not-a-timestamp",
        "2026-10-01T00:00:00",
        None,
        [],
    ],
)
def test_invalid_or_overflowing_timestamp_stays_unknown(adapter, timestamp):
    patterns, counts = adapter._aggregate([event("failure", timestamp=timestamp)])
    assert counts["unknown_timestamp"] == 1
    assert patterns["RP-STRING-001"]["last_seen"] == ""


def test_mixed_shapes_are_visible_and_raw_data_preserved(adapter, capsys):
    entries = [
        event("failure", timestamp="2026-10-01T01-00Z"),
        {"pattern_id": "RP-STRING-001", "timestamp": None},
        event("fix", verification_passed=True, timestamp=123),
        event("fix", timestamp={}),
        event("session", pattern_id=["not-a-pattern"]),
        event("test", verification_passed=True),
        event("enhancement"),
        event("failure", pattern_id=["unhashable"]),
        event("failure", workflow=["unhashable"], root_cause={"not": "text"}),
        event("fix", verification_passed="false"),
        None,
        [],
        7,
    ]
    write_records(adapter, entries)
    with adapter._PDA_LOG.open("a", encoding="utf-8") as stream:
        stream.write("{invalid-json\n")
    original = adapter._PDA_LOG.read_bytes()
    patterns, counts = adapter._aggregate(adapter._read_log())
    assert counts["failure"] == 2
    assert counts["caller_labelled_repair"] == 2
    assert counts["unknown"] == 2
    assert counts["malformed"] == 6
    assert counts["session"] == counts["test"] == 1
    assert counts["unknown_timestamp"] == 7
    assert sum(v for k, v in counts.items() if k != "unknown_timestamp") == 14
    rec = patterns["RP-STRING-001"]
    assert rec["fixes_passed"] == 1
    assert rec["caller_labelled_success_rate"] == 0.5
    assert rec["fix_success_rate"] is None
    assert rec["last_seen"] == "2026-10-01T01:00:00Z"
    assert adapter.main(["summarize"]) == 0
    assert "malformed" in capsys.readouterr().out
    adapter.main(["dump"])
    dumped = json.loads(capsys.readouterr().out)
    assert dumped[:-1] == entries
    assert dumped[-1]["raw_record"] == "{invalid-json"
    assert adapter._PDA_LOG.read_bytes() == original


@pytest.mark.parametrize("value", [False, True, 0, 2, "1", {}, []])
def test_unsupported_schema_never_contributes_success(adapter, value):
    records = [event("fix", schema_version=value, verification_passed=True)]
    patterns, counts = adapter._aggregate(records)
    assert counts["unsupported_schema"] == 1
    assert patterns == {}


@pytest.mark.parametrize("fields", [{}, {"verification_passed": False}, {"success": False}])
def test_absent_or_failed_caller_outcome_is_not_success(adapter, fields):
    patterns, _ = adapter._aggregate([event("repair_success", **fields)])
    rec = patterns["RP-STRING-001"]
    assert rec["fixes_passed"] == 0
    assert rec["fix_success_rate"] is None


def test_unique_linked_results_have_bounded_denominators(adapter):
    records = []
    for attempt_id, success in (("one", True), ("two", False)):
        records.extend(
            [
                event("repair_attempt", attempt_id=attempt_id, schema_version=1),
                event(
                    "verification_result",
                    attempt_id=attempt_id,
                    schema_version=1,
                    verified=True,
                    success=success,
                ),
            ]
        )
    records.append(event("fix", verification_passed=True))
    patterns, counts = adapter._aggregate(records)
    rec = patterns["RP-STRING-001"]
    assert counts["verified_result"] == 2
    assert rec["verified_attempts"] == 2
    assert rec["verified_successes"] == 1
    assert rec["fix_success_rate"] == 0.5
    assert rec["caller_labelled_success_rate"] == 1.0
    assert rec["classification"] == "verified_result"
    for key in ("fix_success_rate", "caller_labelled_success_rate"):
        assert 0 <= rec[key] <= 1


@pytest.mark.parametrize(
    "change",
    [
        {"verified": False},
        {"verified": None},
        {"success": None},
        {"success": "true"},
        {"verification_passed": False},
        {"session": "other"},
        {"pattern_id": "RP-OTHER"},
        {"attempt_id": "other"},
    ],
)
def test_missing_invalid_or_mismatched_verification_stays_unknown(adapter, change):
    records = [
        event("attempt", attempt_id="one"),
        event("result", attempt_id="one", verified=True, success=True),
    ]
    records[1].update(change)
    patterns, counts = adapter._aggregate(records)
    assert counts["verified_result"] == 0
    assert all(rec["fix_success_rate"] is None for rec in patterns.values())


@pytest.mark.parametrize("duplicate", ["attempt", "result"])
def test_duplicate_attempt_or_result_is_not_counted_twice(adapter, duplicate):
    records = [
        event("attempt", attempt_id="one"),
        event("result", attempt_id="one", verified=True, success=True),
    ]
    records.append(records[0 if duplicate == "attempt" else 1].copy())
    patterns, counts = adapter._aggregate(records)
    assert counts["verified_result"] == 0
    assert patterns["RP-STRING-001"]["fix_success_rate"] is None


@pytest.mark.parametrize("record_index", [0, 1])
@pytest.mark.parametrize(
    "field,value",
    [
        ("git_sha", "b" * 40),
        ("workflow_run_id", "fixture-run-two"),
        ("git_sha", None),
        ("git_sha", ""),
        ("workflow_run_id", None),
        ("workflow_run_id", 12),
        ("workflow_run_id", []),
        ("session", ""),
    ],
)
def test_replayed_or_invalid_execution_identity_is_unverified(adapter, record_index, field, value):
    records = [
        event("attempt", attempt_id="one"),
        event("result", attempt_id="one", verified=True, success=True),
    ]
    records[record_index][field] = value
    write_records(adapter, records)
    original = adapter._PDA_LOG.read_bytes()
    patterns, counts = adapter._aggregate(adapter._read_log())
    assert counts["verified_result"] == 0
    assert counts["unverified_result"] == 1
    assert patterns["RP-STRING-001"]["verified_attempts"] == 0
    assert patterns["RP-STRING-001"]["fix_success_rate"] is None
    assert adapter._PDA_LOG.read_bytes() == original


@pytest.mark.parametrize("field", ["git_sha", "workflow_run_id", "session"])
def test_both_missing_execution_identities_do_not_authenticate_a_join(adapter, field):
    records = [
        event("attempt", attempt_id="one"),
        event("result", attempt_id="one", verified=True, success=True),
    ]
    for record in records:
        record.pop(field)
    patterns, counts = adapter._aggregate(records)
    assert counts["verified_result"] == 0
    assert patterns["RP-STRING-001"]["fix_success_rate"] is None


@pytest.mark.parametrize(
    "attempt_time,result_time",
    [
        ("2026-10-01T00:00:02Z", "2026-10-01T00:00:01Z"),
        ("2026-10-01T00:00:01Z", "2026-10-01T00:00:01Z"),
        ("2026-10-01T00:00:00.000002Z", "2026-10-01T00:00:00.000001Z"),
        ("2026-10-01T00:00:00-02:00", "2026-10-01T01:00:00Z"),
        ("2026-10-01T00:00:00", "2026-10-01T00:00:01Z"),
        ("2026-10-01T00:00:00Z", "2026-10-01T00:00:01"),
        (None, "2026-10-01T00:00:01Z"),
        ("2026-10-01T00:00:00Z", None),
        ("not-a-date", "2026-10-01T00:00:01Z"),
        ("2026-10-01T00:00:00Z", "9999-12-31T23:59:59-23:59"),
    ],
)
def test_invalid_equal_or_reversed_chronology_is_unverified(adapter, attempt_time, result_time):
    records = [
        event("attempt", attempt_id="one", timestamp=attempt_time),
        event("result", attempt_id="one", verified=True, success=True, timestamp=result_time),
    ]
    write_records(adapter, records)
    original = adapter._PDA_LOG.read_bytes()
    patterns, counts = adapter._aggregate(adapter._read_log())
    assert counts["verified_result"] == 0
    assert counts["unverified_result"] == 1
    assert patterns["RP-STRING-001"]["fix_success_rate"] is None
    assert adapter._PDA_LOG.read_bytes() == original


def test_timezone_offsets_and_subsecond_order_preserve_valid_results(adapter):
    patterns, counts = adapter._aggregate(
        [
            event("attempt", attempt_id="one", timestamp="2026-10-01T02:00:00.000001+02:00"),
            event(
                "result",
                attempt_id="one",
                verified=True,
                success=True,
                timestamp="2026-10-01T00:00:00.000002Z",
            ),
        ]
    )
    assert counts["verified_result"] == 1
    assert patterns["RP-STRING-001"]["verified_attempts"] == 1
    assert patterns["RP-STRING-001"]["fix_success_rate"] == 1.0


@pytest.mark.parametrize("json_fallback", [False, True])
def test_export_roundtrip_schema_and_string_ids(adapter, capsys, monkeypatch, json_fallback):
    write_records(
        adapter,
        [
            event("failure", root_cause="fixture-cause", fix_template="fixture-template"),
            event("fix", verification_passed=True),
            {"pattern_id": "RP-LEGACY-STRING", "timestamp": None},
            None,
        ],
    )
    original = adapter._PDA_LOG.read_bytes()
    if json_fallback:
        monkeypatch.setitem(sys.modules, "yaml", None)
    assert adapter.main(["export-solutions"]) == 0
    output = adapter._SOLUTIONS_YAML
    if json_fallback:
        output = output.with_suffix(".json")
        payload = json.loads(output.read_text())
    else:
        import yaml

        payload = yaml.safe_load(output.read_text())
    assert str(output) in capsys.readouterr().out
    assert payload["schema_version"] == 1
    assert payload["classification"] == "solution_export"
    assert payload["record_counts"]["unknown"] == 1
    assert payload["record_counts"]["malformed"] == 1
    assert payload["total_records"] == 4
    rec = payload["solutions"][0]
    assert rec["pattern_id"] == "RP-STRING-001"
    assert rec["fix_success_rate"] is None
    assert rec["classification"] == "unknown"
    assert rec["caller_labelled_success_rate"] == 1
    assert rec["verified_attempts"] == rec["verified_successes"] == 0
    assert rec["root_cause"] == "fixture-cause"
    assert rec["fix_template"] == "fixture-template"
    assert adapter._aggregate([payload])[1]["export"] == 1
    assert adapter._PDA_LOG.read_bytes() == original


def test_empty_and_filtered_cli_compatibility(adapter, capsys):
    assert adapter.main(["summarize"]) == 0
    assert "No PDA entries found" in capsys.readouterr().out
    write_records(adapter, [event("failure"), None])
    assert adapter.main(["summarize", "--pattern-id", "RP-NOT-FOUND"]) == 0
    assert "No entries for pattern" in capsys.readouterr().out
    assert adapter.main(["dump", "--session", "other"]) == 0
    assert json.loads(capsys.readouterr().out) == []
