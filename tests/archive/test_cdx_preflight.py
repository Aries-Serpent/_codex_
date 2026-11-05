from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.archive import cdx_common as common
from scripts.archive import cdx_preflight as preflight
from scripts.archive import cdx_review as review


def test_full_tree_snapshot_includes_packer_exclusions(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / ".git").mkdir()
    (source / ".git" / "hidden").write_bytes(b"synthetic-only")
    (source / "large.sqlite").write_bytes(b"synthetic-only")
    (source / "empty").mkdir()
    (source / "link").symlink_to("large.sqlite")
    before = preflight.measure_tree(source)
    snapshot = tmp_path / "snapshot"
    assert preflight.measure_tree(source, snapshot=snapshot) == before
    assert preflight.measure_tree(snapshot) == before
    assert before["entries"] == 5
    assert preflight.FULL_SELECTION["exclusions"] == []
    assert preflight.digest_document(preflight.FULL_SELECTION) != preflight.digest_document(
        preflight.PACKER_SELECTION
    )
    (source / "large.sqlite").write_bytes(b"changed-content")
    assert preflight.measure_tree(source) != before
    assert preflight.measure_tree(snapshot) == before


@pytest.mark.parametrize("kind", ["leaf", "ancestor", "fifo", "directory", "traversal", "size"])
def test_bounded_source_reads_reject_unsafe_references(tmp_path, kind):
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "file").write_bytes(b"synthetic-only")
    relative = "real/file"
    limit = 100
    if kind == "leaf":
        (tmp_path / "alias").symlink_to("real/file")
        relative = "alias"
    elif kind == "ancestor":
        (tmp_path / "alias").symlink_to("real", target_is_directory=True)
        relative = "alias/file"
    elif kind == "fifo":
        os.mkfifo(tmp_path / "fifo")
        relative = "fifo"
    elif kind == "directory":
        relative = "real"
    elif kind == "traversal":
        relative = "../outside"
    else:
        limit = 1
    with pytest.raises((OSError, ValueError)):
        preflight.read_source_file(tmp_path, relative, limit=limit)


@pytest.mark.parametrize("kind", ["external_link", "fifo", "entry_budget", "byte_budget"])
def test_tree_measurement_blocks_instead_of_skipping(tmp_path, monkeypatch, kind):
    if kind == "external_link":
        (tmp_path / "link").symlink_to("/etc/passwd")
    elif kind == "fifo":
        os.mkfifo(tmp_path / "fifo")
    else:
        (tmp_path / "file").write_bytes(b"synthetic-only")
        monkeypatch.setattr(
            preflight, "MAX_ENTRIES" if kind == "entry_budget" else "MAX_TREE_BYTES", 0
        )
    with pytest.raises(ValueError):
        preflight.measure_tree(tmp_path)


@pytest.fixture
def produced(tmp_path, monkeypatch):
    source = tmp_path / "source"
    private = tmp_path / "private"
    source.mkdir()
    private.mkdir(mode=0o700)
    (source / "fixture").write_text("synthetic-one synthetic-two\n")
    monkeypatch.setattr(preflight, "measure_toolchain", lambda: {"synthetic": "test_only"})

    def scan(root, **options):
        assert options["scanner_environment"].keys() == {
            "PATH",
            "HOME",
            "LC_ALL",
            "PYTHONNOUSERSITE",
            "PYTHONDONTWRITEBYTECODE",
        }
        assert "CDX_FINDING_HMAC_KEY" not in options["scanner_environment"]
        assert options["gitleaks_config"].read_text() == "[extend]\nuseDefault = true\n"
        assert options["gitleaks_ignore"].read_bytes() == b""
        key = os.environ["CDX_FINDING_HMAC_KEY"].encode()
        findings = []
        for column in (1, 15):
            finding = common._scanner_finding(
                root,
                "gitleaks",
                "8.30.1",
                {
                    "File": str(root / "fixture"),
                    "RuleID": "synthetic-only",
                    "StartLine": 1,
                    "StartColumn": column,
                    "Secret": "PRIVATE_CANARY",
                },
            )
            finding["finding_id"] = common._finding_id(key, finding)
            findings.append(finding)
        common._write_finding_inventory(options["inventory_path"], findings, [root])
        options["observation_sink"](
            findings,
            {
                "version": "1.5.0",
                "results": {},
                "plugins_used": [{"name": "synthetic-only"}],
                "filters_used": [],
            },
        )
        raise RuntimeError("secret scan findings are unresolved or dispositions are stale")

    monkeypatch.setattr(common, "run_secret_scanners", scan)
    return source, private, scan


def test_measured_producer_retains_distinct_observations_without_acceptance(produced, capsys):
    source, private, _ = produced
    result = preflight.run_preflight(source, private)
    assert result["scanner_execution"] == "both_completed"
    assert result["clearance"] == "BLOCKED_FINDINGS"
    assert not result["archive_created"]
    assert result["bindings"]["source_sha256"] == preflight.measure_tree(source)["sha256"]
    inventory, _ = review.read_private_json(private / "inventory.json")
    observations, _ = review.read_private_json(private / "observations.json")
    assert len({row["finding_id"] for row in inventory["findings"]}) == 2
    assert len(observations["findings"]) == 2
    assert "PRIVATE_CANARY" not in json.dumps(result)
    assert "PRIVATE_CANARY" not in (private / "inventory.json").read_text()
    assert capsys.readouterr().out == ""
    queue, _ = review.read_private_json(private / "queue.json")
    assert review.queue_summary(queue)["by_state"]["accepted_exact_false_positive"] == 0
    with pytest.raises((ValueError, RuntimeError)):
        preflight.run_preflight(source, private)


@pytest.mark.parametrize("drift", ["source", "snapshot", "config", "ignore", "tool", "partial"])
def test_drift_or_partial_run_never_publishes_completion(produced, monkeypatch, drift):
    source, private, scan = produced
    calls = 0

    def tools():
        nonlocal calls
        calls += 1
        return {"synthetic": calls}

    def changed(root, **options):
        if drift == "partial":
            raise RuntimeError("gitleaks scan failed")
        try:
            scan(root, **options)
        finally:
            if drift in {"source", "snapshot"}:
                ((source if drift == "source" else root) / "fixture").write_text("changed")
            elif drift in {"config", "ignore"}:
                options["gitleaks_config" if drift == "config" else "gitleaks_ignore"].write_text(
                    "changed"
                )

    if drift == "tool":
        monkeypatch.setattr(preflight, "measure_toolchain", tools)
    monkeypatch.setattr(common, "run_secret_scanners", changed)
    with pytest.raises((RuntimeError, ValueError)):
        preflight.run_preflight(source, private)
    assert not (private / "complete.json").exists()


def test_observation_sink_is_private_copy_and_rejects_partial_exit(tmp_path, monkeypatch):
    root = tmp_path / "source"
    root.mkdir()
    (root / "fixture").write_text("synthetic-only\n")
    monkeypatch.setattr(common.shutil, "which", lambda name: name)
    monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "synthetic-only-key" * 3)
    code = 1
    captured = []
    reports = {}

    def run(command, **_kwargs):
        if command[1] == "version":
            return subprocess.CompletedProcess(command, 0, "8.30.1", "")
        if command[1] == "--version":
            return subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if command[1] == "dir":
            assert command[command.index("--exit-code") + 1] == "2"
            report = [{"File": str(root / "fixture"), "RuleID": "synthetic", "StartLine": 1}]
            Path(command[command.index("--report-path") + 1]).write_text(json.dumps(report))
            return subprocess.CompletedProcess(command, code, "", "PRIVATE_DIAGNOSTIC")
        return subprocess.CompletedProcess(command, 0, '{"results": {}}', "")

    monkeypatch.setattr(common.subprocess, "run", run)

    def sink(findings, report):
        captured.append(copy.deepcopy(findings))
        findings.clear()

    with pytest.raises(RuntimeError, match="gitleaks scan failed"):
        common.run_secret_scanners(
            root,
            observation_sink=sink,
            report_sink=lambda stage, report: reports.update({stage: report}),
        )
    assert not captured
    assert reports["gitleaks"]["exit_code"] == 1
    assert reports["gitleaks"]["stderr"] == "PRIVATE_DIAGNOSTIC"
    assert reports["gitleaks"]["report"]
    code = 2
    with pytest.raises(RuntimeError, match="unresolved"):
        common.run_secret_scanners(root, observation_sink=sink)
    assert len(captured[0]) == 1


def test_fingerprint_matches_documented_record_bytes(tmp_path):
    path = tmp_path / "fixture"
    path.write_bytes(b"synthetic-only")
    info = path.stat()
    row = [
        "fixture",
        "file",
        info.st_mode & 0o7777,
        info.st_mtime_ns,
        info.st_size,
        hashlib.sha256(path.read_bytes()).hexdigest(),
    ]
    expected = hashlib.sha256(
        json.dumps(row, ensure_ascii=True, separators=(",", ":")).encode() + b"\n"
    ).hexdigest()
    assert preflight.measure_tree(tmp_path)["sha256"] == expected


@pytest.mark.parametrize("change", ["record", "key", "source", "config", "tool", "inventory"])
def test_current_bundle_rejects_stale_context(produced, monkeypatch, change):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    if change == "tool":
        monkeypatch.setattr(preflight, "measure_toolchain", lambda: {"changed": True})
    elif change == "source":
        (source / "fixture").write_text("different")
    elif change == "config":
        (private / "gitleaks.toml").write_text("different")
    else:
        name = {"record": "observations.json", "key": "key.json", "inventory": "inventory.json"}[
            change
        ]
        document, _ = review.read_private_json(private / name)
        if change == "record":
            document["findings"][0]["_record"]["StartColumn"] = 9
        elif change == "key":
            document["key"] = "changed-key" * 4
        else:
            document["findings"].pop()
        (private / name).write_text(json.dumps(document))
    with pytest.raises(ValueError):
        preflight.load_preflight(source, private)


def test_private_batch_is_exact_non_authorizing_and_create_only(produced):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    result = preflight.assess_batch(source, private)
    assert result["assigned"] == result["assessed"] == 2
    assert result["accepted"] == result["semantic_false_positive_proofs"] == 0
    assert result["counts"]["by_state"]["indeterminate"] == 2
    batch, _ = review.read_private_json(private / "batch-001.json")
    assert len({row["finding_id"] for row in batch["assessments"]}) == 2
    assert "PRIVATE_CANARY" not in json.dumps(batch)
    assert all(row["evidence_gap"] for row in batch["assessments"])
    with pytest.raises(FileExistsError):
        preflight.assess_batch(source, private)


def test_interrupted_publication_has_no_completion(produced, monkeypatch):
    source, private, _ = produced
    original = review.write_checkpoint

    def interrupt(path, document, **options):
        if path.name == "observations.json":
            raise OSError("synthetic interruption")
        return original(path, document, **options)

    monkeypatch.setattr(review, "write_checkpoint", interrupt)
    with pytest.raises(OSError):
        preflight.run_preflight(source, private)
    assert not (private / "complete.json").exists()
    failure, _ = review.read_private_json(private / "failure.json")
    assert failure["status"] == "BLOCKED"
    assert failure["exception_type"] == "OSError"


def test_offline_exact_detector_replay_never_verifies_credentials(produced, monkeypatch):
    import requests

    source, private, _ = produced
    (source / "fixture").write_text('password = "synthetic-only-password"\n')

    def forbid_network(*_args, **_kwargs):
        raise AssertionError("credential verification is forbidden")

    monkeypatch.setattr(requests.sessions.Session, "request", forbid_network)

    def scan(root, **options):
        finding = common._scanner_finding(
            root,
            "detect-secrets",
            "1.5.0",
            {
                "File": str(root / "fixture"),
                "type": "Secret Keyword",
                "line_number": 1,
                "hashed_secret": hashlib.sha1(b"synthetic-only-password").hexdigest(),
            },
        )
        finding["finding_id"] = common._finding_id(
            os.environ["CDX_FINDING_HMAC_KEY"].encode(), finding
        )
        common._write_finding_inventory(options["inventory_path"], [finding], [root])
        options["observation_sink"](
            [finding],
            {
                "version": "1.5.0",
                "results": {},
                "plugins_used": [{"name": "KeywordDetector"}],
                "filters_used": [],
            },
        )
        raise RuntimeError("secret scan findings are unresolved or dispositions are stale")

    monkeypatch.setattr(common, "run_secret_scanners", scan)
    preflight.run_preflight(source, private)
    result = preflight.assess_batch(source, private)
    batch, _ = review.read_private_json(private / "batch-001.json")
    row = batch["assessments"][0]
    assert row["predicates"]["detector_exact_replay_match"]
    assert row["predicates"]["credential_assignment_syntax"]
    assert row["state"] == "indeterminate"
    assert result["semantic_false_positive_proofs"] == 0
    assert "synthetic-only-password" not in json.dumps(batch)
