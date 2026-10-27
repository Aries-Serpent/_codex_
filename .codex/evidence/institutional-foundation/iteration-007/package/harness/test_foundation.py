"""Frozen safety expectations for inactive institutional candidates.

This harness is also runnable outside the checkout against an installed wheel.
"""

from __future__ import annotations

import copy
import gzip
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from codex.institutional import core, storage
from codex.institutional.__main__ import main

NOW = datetime(2026, 10, 24, 20, 7, 5, tzinfo=timezone.utc)


def clock():
    return NOW


def seal(value):
    value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    return value


@pytest.fixture
def target(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    (root / "agent.py").write_text("print('inert')\n")
    return root


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Runtime must not access network")

    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_fixed_clock_canonical_candidate(target):
    first = core.candidate(target, "fixture", clock)
    assert first == core.candidate(target, "fixture", clock)
    assert core.inspect_candidate(first) == []
    assert core.verify(first, target) == []
    assert first["created_at"] == "2026-10-24T20:07:05Z"
    assert first["payload"]["gates"]["G5"] == "NOT_RUN"
    assert first["payload"]["records"][-1]["payload"]["outcomes"] == "unknown"
    assert core.canonical({"b": 1, "a": 2}) == b'{"a":2,"b":1}'
    with pytest.raises(core.Rejected, match="NAIVE_CLOCK"):
        core.candidate(target, "fixture", lambda: datetime(2026, 1, 1))


@pytest.mark.parametrize(
    "schema",
    [
        "codex.decision.v1",
        "codex.institution.v1",
        "codex.experience.v2",
        "codex.amendment.v1",
        "codex.dissent.v1",
        "codex.knowledge-lifecycle.v1",
        "codex.capability-package.v1",
    ],
)
def test_unsupported_critical_records_reported_individually(target, schema):
    value = core.candidate(target, "fixture", clock)
    value["payload"]["records"].append({"schema": schema})
    seal(value)
    findings = core.inspect_candidate(value)
    assert "record[7]:UNSUPPORTED_SCHEMA" in findings
    with pytest.raises(core.Rejected, match="INVALID_CANDIDATE"):
        storage.plan(target, value)
    assert not (target / core.NAMESPACE).exists()


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r.update(lifecycle="Active"),
        lambda r: r.update(authority_refs=["self-approved"]),
        lambda r: r.update(hook="execute"),
        lambda r: r["payload"].update(hook="execute"),
        lambda r: r.update(created_at="yesterday"),
        lambda r: r["producer"].update(assurance="authenticated"),
    ],
)
def test_poisoned_record_cannot_be_operational(target, change):
    value = core.candidate(target, "fixture", clock)
    change(value)
    seal(value)
    with pytest.raises(core.Rejected, match="MALFORMED_RECORD"):
        core.validate(value)


def test_integrity_and_identity_are_not_authorization(target):
    value = core.candidate(target, "fixture", clock)
    value["payload"]["session_id"] = "tampered"
    with pytest.raises(core.Rejected, match="INTEGRITY_MISMATCH"):
        core.validate(value)
    seal(value)
    core.validate(value)
    claim = dict(
        proposer="a",
        implementer="b",
        verifier="c",
        approver="d",
        artifact=core.digest(value),
        target=str(target),
        operation="activate",
        revoked=False,
        expires="2999-01-01T00:00:00Z",
    )
    reasons = core.authority_diagnostics(claim, core.digest(value), str(target))
    assert "TRUSTED_IDENTITY_UNAVAILABLE" in reasons
    assert "ACTIVATION_UNSUPPORTED" in reasons
    assert "EXPIRY_UNVERIFIED" in reasons
    assert "ACTOR_COLLISION" not in reasons
    claim.update(approver="a", artifact="old", target="other", revoked=True)
    reasons = core.authority_diagnostics(claim, core.digest(value), str(target))
    assert {
        "ACTOR_COLLISION",
        "ARTIFACT_BINDING_MISMATCH",
        "OPERATION_TARGET_MISMATCH",
        "REVOCATION_UNVERIFIED",
    } <= set(reasons)
    assert "MISSING_ACTORS" in core.authority_diagnostics({}, "", "")
    value["id"] = "invented"
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    with pytest.raises(core.Rejected, match="IDENTITY_MISMATCH"):
        core.validate(value)


def test_inventory_reconciliation_and_safe_paths(target):
    for name in (
        "src/agent/a.py",
        ".github/prompts/a.txt",
        ".github/workflows/a.txt",
        ".codex/governance/a.txt",
        "memory.txt",
        "registry.txt",
        "docs/adr/choice.json",
        "security.txt",
        "pyproject.toml",
        "AGENTS.md",
    ):
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("data")
    inv = core.inventory(target, clock)
    payload = inv["payload"]
    assert sum(payload["counts"].values()) == len(payload["entries"]) == 11
    assert all(e["depth"] == "metadata_only" for e in payload["entries"])
    assert payload["counts"]["agent"] == 1
    bad = copy.deepcopy(inv)
    bad["payload"]["entries"][0]["path"] = "../unsafe"
    seal(bad)
    with pytest.raises(core.Rejected, match="UNSAFE_INVENTORY_PATH"):
        core.validate(bad)
    bad = copy.deepcopy(inv)
    bad["payload"]["counts"]["agent"] = 2
    seal(bad)
    with pytest.raises(core.Rejected, match="CENSUS_RECONCILIATION_FAILED"):
        core.validate(bad)
    bad = copy.deepcopy(inv)
    bad["payload"]["entries"].reverse()
    seal(bad)
    with pytest.raises(core.Rejected, match="UNORDERED_OR_DUPLICATE_PATHS"):
        core.validate(bad)


def test_git_census_immutable_reference_and_dirty_drift(target):
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(target),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    value = core.candidate(target, "git-fixture", clock)
    inv = value["payload"]["records"][1]
    assert inv["payload"]["coverage"] == "git-tree"
    assert inv["payload"]["entries"][0]["source_digest"].startswith("git-object:")
    (target / "agent.py").write_text("changed")
    assert "WORKTREE_DRIFT" in core.verify(value, target)
    with pytest.raises(core.Rejected, match="SOURCE_REFERENCE_UNAVAILABLE"):
        core.inventory(target, source_ref="missing-reference")


def test_git_does_not_execute_target_fsmonitor(target, tmp_path):
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(target),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    marker = tmp_path / "callback-ran"
    callback = tmp_path / "fsmonitor"
    callback.write_text(f"#!/bin/sh\nprintf invoked > '{marker}'\nprintf '\\0'\n")
    callback.chmod(0o700)
    subprocess.run(
        ["git", "-C", str(target), "config", "core.fsmonitor", str(callback)],
        check=True,
    )
    core.candidate(target, "fixture", clock)
    assert not marker.exists()


def test_git_transport_and_optional_writes_are_disabled(target, monkeypatch):
    def observed(command, **kwargs):
        assert command[:3] == ["git", "-c", "core.fsmonitor=false"]
        assert "core.hooksPath=" + os.devnull in command
        env = kwargs["env"]
        assert env["GIT_ALLOW_PROTOCOL"] == ""
        assert env["GIT_NO_LAZY_FETCH"] == "1"
        assert env["GIT_OPTIONAL_LOCKS"] == "0"
        assert env["GIT_TERMINAL_PROMPT"] == "0"
        return b"observed"

    monkeypatch.setattr(core, "capture", observed)
    assert core.git(target, "rev-parse", "HEAD") == "observed"


def test_preview_write_history_and_compare_and_swap(target):
    value = core.candidate(target, "fixture", clock)
    before = snapshot(target)
    preview = storage.plan(target, value)
    assert snapshot(target) == before
    storage.apply(target, value, preview)
    checkpoint = target / core.NAMESPACE / "checkpoint.json"
    assert core.load(checkpoint) == value
    assert core.verify(value, target) == []
    with pytest.raises(core.Rejected, match="CONCURRENT_MODIFICATION"):
        storage.apply(target, value, preview)
    next_value = core.candidate(target, "fixture", clock)
    next_value["payload"].update(predecessor=core.digest(value), sequence=2)
    next_value["supersedes"] = value["id"]
    seal(next_value)
    next_plan = storage.plan(target, next_value, core.digest(value))
    storage.apply(target, next_value, next_plan)
    history = checkpoint.parent / f"previous-{core.digest(value)}.json"
    assert core.load(history) == value
    assert core.load(checkpoint) == next_value
    assert storage.disengage(target)["integrations_enabled"] is False
    saved = snapshot(target)
    storage.disengage(target)
    assert snapshot(target) == saved


def test_interrupted_replacement_retains_last_checkpoint(target, monkeypatch):
    value = core.candidate(target, "fixture", clock)
    storage.apply(target, value, storage.plan(target, value))
    updated = copy.deepcopy(value)
    updated["payload"].update(sequence=2, predecessor=core.digest(value))
    seal(updated)
    preview = storage.plan(target, updated, core.digest(value))

    def fail(*args, **kwargs):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError, match="disk failure"):
        storage.apply(target, updated, preview)
    ns = target / core.NAMESPACE
    assert core.load(ns / "checkpoint.json") == value
    assert not list(ns.glob(".pending-*"))
    assert (ns / f"previous-{core.digest(value)}.json").exists()


def test_lock_contention_detected(target):
    import fcntl

    value = core.candidate(target, "fixture", clock)
    storage.apply(target, value, storage.plan(target, value))
    updated = copy.deepcopy(value)
    updated["payload"].update(sequence=2, predecessor=core.digest(value))
    seal(updated)
    preview = storage.plan(target, updated, core.digest(value))
    with (target / core.NAMESPACE / ".lock").open("r+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(core.Rejected, match="CONCURRENT_MODIFICATION"):
            storage.apply(target, updated, preview)


@pytest.mark.parametrize(
    "field,reason",
    [
        ("sequence", "SEQUENCE_MISMATCH"),
        ("predecessor", "PREDECESSOR_MISMATCH"),
        ("session_id", "SESSION_MISMATCH"),
    ],
)
def test_checkpoint_lineage_constraints(target, field, reason):
    value = core.candidate(target, "fixture", clock)
    storage.apply(target, value, storage.plan(target, value))
    updated = copy.deepcopy(value)
    updated["payload"].update(sequence=2, predecessor=core.digest(value))
    updated["payload"][field] = 8 if field == "sequence" else "wrong"
    seal(updated)
    with pytest.raises(core.Rejected, match=reason):
        storage.plan(target, updated, core.digest(value))


def test_extension_preservation_required(target):
    value = core.candidate(target, "fixture", clock)
    value["extensions"] = {"historical_command": "never execute this"}
    seal(value)
    storage.apply(target, value, storage.plan(target, value))
    updated = copy.deepcopy(value)
    updated["payload"].update(sequence=2, predecessor=core.digest(value))
    updated["extensions"] = {}
    seal(updated)
    with pytest.raises(core.Rejected, match="EXTENSION_LOSS_PROHIBITED"):
        storage.plan(target, updated, core.digest(value))


def test_drift_rejects_apply_without_mutation(target):
    value = core.candidate(target, "fixture", clock)
    preview = storage.plan(target, value)
    (target / "agent.py").write_text("same path, changed bytes")
    before = snapshot(target)
    assert "STALE_CHECKPOINT" in core.verify(value, target)
    with pytest.raises(core.Rejected, match="STALE_OR_INVALID"):
        storage.apply(target, value, preview)
    assert snapshot(target) == before
    modified = copy.deepcopy(preview)
    modified["candidate_digest"] = "tampered"
    with pytest.raises(core.Rejected, match="STALE_PREVIEW"):
        storage.apply(target, value, modified)


def test_namespace_collisions_and_symlink_containment(target, tmp_path):
    value = core.candidate(target, "fixture", clock)
    namespace = target / core.NAMESPACE
    namespace.parent.mkdir()
    namespace.mkdir()
    (namespace / "user.txt").write_text("preserve")
    with pytest.raises(core.Rejected, match="AMBIGUOUS_OWNERSHIP"):
        storage.plan(target, value)
    assert (namespace / "user.txt").read_text() == "preserve"
    (namespace / "ownership.json").write_text("{}")
    with pytest.raises(core.Rejected, match="OWNERSHIP_OR_VERSION"):
        storage.plan(target, value)
    other = tmp_path / "other"
    other.mkdir()
    (other / ".codex").symlink_to(namespace, target_is_directory=True)
    with pytest.raises(core.Rejected, match="UNSAFE_NAMESPACE"):
        storage.plan(other, core.candidate(other, "fixture", clock))


@pytest.mark.parametrize(
    "classification",
    [
        "Unknown",
        "Secret",
        "Restricted",
        "Repository-Internal",
        "Prohibited-From-Export",
    ],
)
def test_disclosure_denies_unclassified_or_unauthorized(target, tmp_path, classification):
    value = core.candidate(target, "fixture", clock)
    with pytest.raises(core.Rejected, match="DISCLOSURE_DENIED"):
        storage.export_plan(value, tmp_path / "export", classification, "basis", "assessor")
    assert not (tmp_path / "export").exists()


def test_public_export_manifest_and_tampering(target, tmp_path):
    value = core.candidate(target, "fixture", clock)
    destination = tmp_path / "export"
    preview = storage.export_plan(value, destination, "Public", "disposable fixture", "tester")
    storage.export(value, preview)
    assert not destination.exists()
    changed = copy.deepcopy(value)
    changed["extensions"] = {"poison": "inert instruction"}
    seal(changed)
    with pytest.raises(core.Rejected, match="STALE_EXPORT_PREVIEW"):
        storage.export(changed, preview, write=True)
    storage.export(value, preview, write=True)
    manifest = json.loads((destination / "manifest.json").read_text())
    assert manifest["artifacts"][0]["digest"] == core.digest(
        core.load(destination / "candidate.json")
    )
    with pytest.raises(core.Rejected, match="EXPORT_COLLISION"):
        storage.export(value, preview, write=True)
    with pytest.raises(core.Rejected, match="UNSAFE_EXPORT_PATH"):
        storage.export_plan(value, tmp_path / "missing" / "export", "Public", "basis", "tester")


def test_load_limits_duplicates_and_malformed_data(target, monkeypatch):
    path = target / "bad.json"
    for content in ('{"schema": "a", "schema": "b"}', "not-json", "[]"):
        path.write_text(content)
        with pytest.raises(core.Rejected):
            core.load(path)
    value = core.candidate(target, "fixture", clock)
    path.write_bytes(core.canonical(value))
    monkeypatch.setattr(core, "MAX_BYTES", 1)
    with pytest.raises(core.Rejected, match="BLOCKED_RESOURCE_LIMIT"):
        core.load(path)
    monkeypatch.setattr(core, "MAX_PATHS", 0)
    with pytest.raises(core.Rejected, match="BLOCKED_RESOURCE_LIMIT"):
        core.inventory(target)


def test_missing_nested_records_are_not_success(target):
    value = core.candidate(target, "fixture", clock)
    value["payload"]["records"] = []
    seal(value)
    findings = core.inspect_candidate(value)
    assert "REQUIRED_INVENTORY_MISSING" in findings
    assert "REQUIRED_REVIEW_MISSING" in findings
    value = core.candidate(target, "fixture", clock)
    value["payload"]["records"].append(value["payload"]["records"][0])
    seal(value)
    assert "DUPLICATE_RECORD_ID" in core.inspect_candidate(value)
    value = core.candidate(target, "fixture", clock)
    value["payload"]["candidate_ref"] = "0" * 64
    seal(value)
    assert "CANDIDATE_BINDING_MISMATCH" in core.inspect_candidate(value)


def test_multiple_evidence_records_cannot_bypass_binding(target):
    value = core.candidate(target, "fixture", clock)
    extra = copy.deepcopy(value["payload"]["records"][0])
    extra["payload"]["digest"] = "0" * 64
    seal(extra)
    value["payload"]["records"].append(extra)
    seal(value)
    assert "REQUIRED_SINGLE_EVIDENCE" in core.inspect_candidate(value)
    with pytest.raises(core.Rejected, match="INVALID_CANDIDATE"):
        storage.plan(target, value)


def test_symlink_swap_does_not_write_outside_target(target, tmp_path, monkeypatch):
    value = core.candidate(target, "fixture", clock)
    preview = storage.plan(target, value)
    outside = tmp_path / "outside"
    outside.mkdir()
    original = os.mkdir

    def swap(path, *args, **kwargs):
        original(path, *args, **kwargs)
        if path == ".codex":
            (target / ".codex").rmdir()
            (target / ".codex").symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(os, "mkdir", swap)
    with pytest.raises(OSError):
        storage.apply(target, value, preview)
    assert list(outside.iterdir()) == []


def test_compressed_import_and_evidence_lineage(target, tmp_path, monkeypatch):
    first = core.candidate(target, "fixture", clock)
    path = tmp_path / "candidate.json.gz"
    path.write_bytes(gzip.compress(core.canonical(first), mtime=0))
    assert core.load(path) == first
    old = first["payload"]["records"][0]
    (target / "agent.py").write_text("changed")
    second = core.candidate(target, "fixture", clock, previous_evidence=old)
    new = second["payload"]["records"][0]
    assert new["payload"]["predecessor"] == old["id"]
    third = core.candidate(target, "fixture", clock, previous_evidence=new)
    assert third["payload"]["records"][0]["id"] == new["id"]
    monkeypatch.setattr(core, "MAX_BYTES", path.stat().st_size + 1)
    with pytest.raises(core.Rejected, match="BLOCKED_RESOURCE_LIMIT"):
        core.load(path)


def test_cli_end_to_end_and_stable_results(target, tmp_path, capsys):
    assert main(["inventory", "--root", str(target)]) == 0
    inv = json.loads(capsys.readouterr().out)
    input_path = tmp_path / "inventory.json"
    input_path.write_bytes(core.canonical(inv))
    assert main(["assess", "--input", str(input_path)]) == 0
    capsys.readouterr()
    assert main(["candidate", "--root", str(target), "--write", "--session", "test"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["written"]
    checkpoint = target / core.NAMESPACE / "checkpoint.json"
    for command in ("verify", "status", "challenge"):
        assert main([command, "--root", str(target), "--input", str(checkpoint)]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["independent_reproduction"] == "NOT_RUN"
    assert main(["verify", "--root", str(target), "--input", str(checkpoint), "--strict"]) == 9
    capsys.readouterr()
    assert main(["activate", "--root", str(target), "--input", str(checkpoint)]) == 3
    capsys.readouterr()
    for command in ("migrate", "downgrade"):
        assert main([command, "--input", str(checkpoint)]) == 6
        capsys.readouterr()
    assert main(["export", "--input", str(checkpoint), "--destination", str(tmp_path / "out")]) == 3
    capsys.readouterr()
    assert main(["verify"]) == 5
    capsys.readouterr()
    assert main(["export", "--input", str(checkpoint)]) == 5
    capsys.readouterr()
    assert main(["disengage", "--root", str(target)]) == 0
    capsys.readouterr()
