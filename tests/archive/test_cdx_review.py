from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.archive import cdx_common, cdx_review, codex_packer


@pytest.fixture
def inventory():
    return {
        "schema_version": 1,
        "findings": [
            {
                "scanner": "gitleaks",
                "scanner_version": "8.30.1",
                "finding_id": "a" * 64,
                "file_sha256": "b" * 64,
                "path": "fixture.txt",
                "rule": "synthetic-rule",
                "start_line": 1,
                "end_line": 1,
            }
        ],
    }


@pytest.fixture
def bindings():
    return {
        field: "c" * (32 if field == "run_namespace" else 64) for field in cdx_review.BINDING_FIELDS
    } | {"identity_version": cdx_common.FINDING_IDENTITY_VERSION}


def test_snapshot_identity_is_root_independent_and_observation_specific(tmp_path):
    results = []
    for name in ("first", "second"):
        root = tmp_path / name
        root.mkdir()
        path = root / "fixture.txt"
        path.write_text("synthetic fixture only\n")
        for scanner, record in (
            (
                "gitleaks",
                {
                    "File": str(path),
                    "RuleID": "synthetic-rule",
                    "StartLine": 1,
                    "EndLine": 1,
                    "StartColumn": 1,
                    "Fingerprint": f"{path}:synthetic-rule:1",
                },
            ),
            (
                "detect-secrets",
                {
                    "File": str(path),
                    "type": "synthetic-rule",
                    "line_number": 1,
                    "hashed_secret": "synthetic-opaque-identifier",
                },
            ),
        ):
            finding = cdx_common._scanner_finding(
                root, scanner, cdx_common.SECRET_SCANNER_VERSIONS[scanner], record
            )
            key = b"synthetic fixture key only" * 2
            identity = cdx_common._finding_id(key, finding)
            if name == "first":
                results.append(identity)
            else:
                assert identity == results.pop(0)
            assert identity != cdx_common._finding_id(key + b"changed", finding)
            changed = copy.deepcopy(finding)
            changed["_record"]["distinct_observation"] = 2
            assert identity != cdx_common._finding_id(key, changed)
            reversed_finding = dict(reversed(list(finding.items())))
            assert identity == cdx_common._finding_id(key, reversed_finding)
            legacy = hmac.new(
                key,
                json.dumps(
                    finding, ensure_ascii=True, sort_keys=True, separators=(",", ":")
                ).encode(),
                hashlib.sha256,
            ).hexdigest()
            assert identity != legacy


@pytest.mark.parametrize("raw", ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'))
def test_scanner_json_rejects_ambiguous_reports(raw):
    with pytest.raises(ValueError):
        cdx_common._scanner_json(raw)


@pytest.mark.parametrize(
    "change",
    (
        "duplicate",
        "version",
        "digest",
        "boolean",
        "traversal",
        "extra",
        "schema",
    ),
)
def test_inventory_rejects_invalid_exact_bindings(inventory, change):
    row = inventory["findings"][0]
    if change == "duplicate":
        inventory["findings"].append(dict(row))
    elif change == "version":
        row["scanner_version"] = "0.0.0"
    elif change == "digest":
        row["finding_id"] = "invalid"
    elif change == "boolean":
        row["start_line"] = True
    elif change == "traversal":
        row["path"] = "../outside"
    elif change == "extra":
        row["source_line"] = "must never enter queue"
    else:
        inventory["schema_version"] = True
    with pytest.raises(ValueError):
        cdx_review.validate_inventory(inventory)


def test_resume_preserves_conservative_states_and_overlap(inventory, bindings):
    second = dict(
        inventory["findings"][0],
        scanner="detect-secrets",
        scanner_version="1.5.0",
        finding_id="d" * 64,
    )
    inventory["findings"].append(second)
    queue = cdx_review.build_queue(inventory, "e" * 64, bindings)
    queue["observations"][0]["state"] = "suspected_sensitive"
    resumed = cdx_review.build_queue(inventory, "e" * 64, bindings, previous=queue)
    summary = cdx_review.queue_summary(resumed)
    assert summary["observed_total"] == 2
    assert summary["by_scanner"] == {"gitleaks": 1, "detect-secrets": 1}
    assert sum(summary["by_state"].values()) == 2
    assert summary["by_state"]["suspected_sensitive"] == 1
    assert summary["by_state"]["accepted_exact_false_positive"] == 0
    assert summary["clearance"] == "not_evaluated"


@pytest.mark.parametrize(
    "attack",
    (
        "forged_reviewer",
        "irrelevant_evidence",
        "accepted",
        "awaiting_review",
        "missing",
        "extra",
        "duplicate",
        "stale_id",
        "source",
        "version",
        "synthetic",
    ),
)
def test_resume_never_treats_claims_as_approval(inventory, bindings, attack):
    queue = cdx_review.build_queue(inventory, "e" * 64, bindings)
    row = queue["observations"][0]
    if attack == "forged_reviewer":
        row["reviewed_by"] = "fabricated-label"
    elif attack == "irrelevant_evidence":
        row["evidence_sha256"] = hashlib.sha256(b"irrelevant fixture").hexdigest()
    elif attack == "accepted":
        row["state"] = "accepted_exact_false_positive"
    elif attack == "awaiting_review":
        row["state"] = "evidenced_false_positive_awaiting_review"
    elif attack == "missing":
        queue["observations"] = []
    elif attack in {"extra", "duplicate"}:
        queue["observations"].append(dict(row))
    elif attack == "stale_id":
        row["finding_id"] = "f" * 64
    elif attack == "source":
        queue["bindings"]["source_sha256"] = "f" * 64
    elif attack == "version":
        row["scanner_version"] = "0.0.0"
    else:
        queue["source_kind"] = "synthetic"
    with pytest.raises(ValueError):
        cdx_review.build_queue(inventory, "e" * 64, bindings, previous=queue)


def test_private_io_and_atomic_history(tmp_path, inventory, monkeypatch):
    tmp_path.chmod(0o700)
    path = tmp_path / "001.json"
    digest = cdx_review.write_checkpoint(path, inventory)
    assert path.stat().st_mode & 0o777 == 0o600
    assert cdx_review.read_private_json(path) == (inventory, digest)
    with pytest.raises(FileExistsError):
        cdx_review.write_checkpoint(path, {"replacement": True})
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    def interrupt(_fd):
        raise OSError("synthetic interruption")

    monkeypatch.setattr(cdx_review.os, "fsync", interrupt)
    with pytest.raises(OSError):
        cdx_review.write_checkpoint(tmp_path / "002.json", inventory)
    assert not (tmp_path / "002.json").exists()
    assert not list(tmp_path.glob(".cdx-checkpoint-*"))


def test_interrupted_two_link_checkpoint_requires_regeneration(tmp_path, inventory):
    tmp_path.chmod(0o700)
    original = tmp_path / "001.json"
    cdx_review.write_checkpoint(original, inventory)
    os.link(original, tmp_path / ".cdx-checkpoint-interrupted")
    with pytest.raises(ValueError):
        cdx_review.read_private_json(original)
    regenerated = tmp_path / "002.json"
    cdx_review.write_checkpoint(regenerated, inventory)
    assert cdx_review.read_private_json(regenerated)[0] == inventory
    assert original.exists()


@pytest.mark.parametrize("unsafe", ("symlink", "ancestor", "hardlink", "fifo", "mode", "size"))
def test_private_reads_reject_unsafe_files(tmp_path, unsafe, monkeypatch):
    tmp_path.chmod(0o700)
    original = tmp_path / "original.json"
    original.write_text("{}")
    original.chmod(0o600)
    target = tmp_path / "input.json"
    if unsafe == "symlink":
        target.symlink_to(original)
    elif unsafe == "ancestor":
        link = tmp_path / "alias"
        link.symlink_to(tmp_path, target_is_directory=True)
        target = link / original.name
    elif unsafe == "hardlink":
        os.link(original, target)
    elif unsafe == "fifo":
        os.mkfifo(target, 0o600)
    elif unsafe == "mode":
        target = original
        target.chmod(0o644)
    else:
        target = original
        monkeypatch.setattr(cdx_review, "MAX_DOCUMENT_BYTES", 1)
    with pytest.raises((OSError, ValueError)):
        cdx_review.read_private_json(target)


def test_unresolved_scan_does_not_create_database(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "fixture.txt").write_text("synthetic\n")
    output = tmp_path / "never.cdx.sqlite"

    def reject(*_args):
        raise RuntimeError("unresolved synthetic observations")

    monkeypatch.setattr(codex_packer, "run_secret_scanners", reject)
    with pytest.raises(RuntimeError, match="unresolved"):
        codex_packer.pack_archive(source, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "failure",
    (
        "status",
        "duplicate_json",
        "timeout",
        "detect_failure",
        "detect_partial",
        "missing_key",
        "wrong_version",
        "ambiguous_duplicate",
    ),
)
def test_scanner_failures_leave_database_absent(tmp_path, monkeypatch, failure):
    source = tmp_path / "source"
    source.mkdir()
    (source / "fixture.txt").write_text("synthetic fixture only\n")
    output = tmp_path / "never.cdx.sqlite"
    monkeypatch.setattr(cdx_common.shutil, "which", lambda name: name)
    monkeypatch.setattr(codex_packer, "git_blob_oids", lambda _root: {})
    if failure == "missing_key":
        monkeypatch.delenv("CDX_FINDING_HMAC_KEY", raising=False)
    else:
        monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "synthetic-only-test-key" * 2)

    def fake_run(command, **kwargs):
        assert kwargs["timeout"] == cdx_common.SECRET_SCANNER_TIMEOUT_SECONDS
        if command[1] == "version":
            version = "8.30.2" if failure == "wrong_version" else "8.30.1"
            return subprocess.CompletedProcess(command, 0, version, "")
        if command[1] == "--version":
            return subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 1, output="must remain private")
        if command[0] == "gitleaks":
            root = Path(command[-1])
            record = {
                "File": str(root / "fixture.txt"),
                "RuleID": "synthetic-rule",
                "StartLine": 1,
                "EndLine": 1,
            }
            records = [record, record] if failure == "ambiguous_duplicate" else [record]
            raw = json.dumps(records)
            if failure == "status":
                raw = "[]"
            elif failure == "duplicate_json":
                raw = '[{"File":"first","File":"second"}]'
            Path(command[command.index("--report-path") + 1]).write_text(raw)
            return subprocess.CompletedProcess(command, 1, "", "")
        assert command[1:4] == ["scan", "--no-verify", "--all-files"]
        return subprocess.CompletedProcess(
            command,
            2 if failure == "detect_failure" else 0,
            "{}" if failure == "detect_partial" else '{"results": {}}',
            "",
        )

    monkeypatch.setattr(cdx_common.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError):
        codex_packer.pack_archive(source, output)
    assert not output.exists()


def test_queue_cli_outputs_only_aggregates(tmp_path, inventory, bindings, capsys):
    tmp_path.chmod(0o700)
    source = tmp_path / "source"
    source.mkdir()
    inventory_path = tmp_path / "inventory.json"
    binding_path = tmp_path / "bindings.json"
    cdx_review.write_checkpoint(inventory_path, inventory)
    cdx_review.write_checkpoint(binding_path, bindings)
    arguments = [
        "--source",
        str(source),
        "--inventory",
        str(inventory_path),
        "--bindings",
        str(binding_path),
        "--output",
        str(tmp_path / "001.json"),
    ]
    assert cdx_review.main(arguments) == 0
    printed = capsys.readouterr().out
    assert "fixture.txt" not in printed
    assert "a" * 64 not in printed
    assert json.loads(printed)["observed_total"] == 1
    assert cdx_review.main(arguments) == 2
    assert "BLOCKED" in capsys.readouterr().out
    arguments[-1] = str(source / "inside.json")
    assert cdx_review.main(arguments) == 2
    assert not (source / "inside.json").exists()
