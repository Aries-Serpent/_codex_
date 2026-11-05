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
    assert before["content_identity_version"] == 1
    assert len(before["content_sha256"]) == 64
    assert preflight.FULL_SELECTION["exclusions"] == []
    assert preflight.digest_document(preflight.FULL_SELECTION) != preflight.digest_document(
        preflight.PACKER_SELECTION
    )
    (source / "large.sqlite").write_bytes(b"changed-content")
    assert preflight.measure_tree(source) != before
    assert preflight.measure_tree(snapshot) == before


@pytest.mark.parametrize("kind", ["file", "dir", "symlink"])
def test_timestamp_drift_changes_only_live_digest(tmp_path, kind):
    entry = tmp_path / "entry"
    if kind == "file":
        entry.write_bytes(b"synthetic-only")
    elif kind == "dir":
        entry.mkdir()
    else:
        entry.symlink_to("missing-internal-target")
    before = preflight.measure_tree(tmp_path)
    info = entry.lstat()
    os.utime(entry, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000), follow_symlinks=False)
    after = preflight.measure_tree(tmp_path)
    assert after["sha256"] != before["sha256"]
    assert after["content_sha256"] == before["content_sha256"]
    assert after["content_identity_version"] == before["content_identity_version"] == 1


@pytest.mark.parametrize(
    "change", ["bytes", "size", "path", "mode", "dir_mode", "symlink_target", "empty_dir", "type"]
)
def test_content_digest_binds_tree_content_and_structure(tmp_path, change):
    entry = tmp_path / "entry"
    entry.write_bytes(b"synthetic-one")
    entry.chmod(0o600)
    directory = tmp_path / "empty"
    directory.mkdir(mode=0o700)
    link = tmp_path / "link"
    link.symlink_to("entry")
    before = preflight.measure_tree(tmp_path)
    if change == "bytes":
        entry.write_bytes(b"synthetic-two")
    elif change == "size":
        entry.write_bytes(b"synthetic-one-more")
    elif change == "path":
        entry.rename(tmp_path / "renamed")
    elif change == "mode":
        entry.chmod(0o700)
    elif change == "dir_mode":
        directory.chmod(0o755)
    elif change == "symlink_target":
        link.unlink()
        link.symlink_to("empty")
    elif change == "empty_dir":
        directory.rmdir()
    else:
        entry.unlink()
        entry.mkdir(mode=0o600)
    assert preflight.measure_tree(tmp_path)["content_sha256"] != before["content_sha256"]


def test_content_digest_is_independent_of_creation_order_and_timestamps(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    for root, names, timestamp in (
        (first, ["z", "a"], 1_000_000_000),
        (second, ["a", "z"], 2_000_000_000),
    ):
        root.mkdir()
        for name in names:
            directory = root / name
            directory.mkdir(mode=0o700)
            (directory / "file").write_bytes(name.encode())
            (directory / "file").chmod(0o600)
            os.utime(directory / "file", ns=(timestamp, timestamp))
            os.utime(directory, ns=(timestamp, timestamp))
    before = preflight.measure_tree(first)
    after = preflight.measure_tree(second)
    assert before["sha256"] != after["sha256"]
    assert before["content_sha256"] == after["content_sha256"]


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


@pytest.mark.parametrize(
    "kind",
    ["external_link", "fifo", "privileged_file", "privileged_dir", "entry_budget", "byte_budget"],
)
def test_tree_measurement_blocks_instead_of_skipping(tmp_path, monkeypatch, kind):
    if kind == "external_link":
        (tmp_path / "link").symlink_to("/etc/passwd")
    elif kind == "fifo":
        os.mkfifo(tmp_path / "fifo")
    elif kind == "privileged_file":
        (tmp_path / "file").write_bytes(b"synthetic-only")
        (tmp_path / "file").chmod(0o4600)
    elif kind == "privileged_dir":
        (tmp_path / "dir").mkdir()
        (tmp_path / "dir").chmod(0o2700)
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
    assert result["source"] == preflight.measure_tree(source)
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


@pytest.mark.parametrize(
    "drift",
    [
        "source",
        "snapshot",
        "source_timestamp",
        "snapshot_timestamp",
        "config",
        "ignore",
        "tool",
        "partial",
    ],
)
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
            elif drift in {"source_timestamp", "snapshot_timestamp"}:
                tree = source if drift == "source_timestamp" else root
                before = preflight.measure_tree(tree)
                path = tree / "fixture"
                info = path.stat()
                os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000))
                assert preflight.measure_tree(tree)["content_sha256"] == before["content_sha256"]
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
    measurement = preflight.measure_tree(tmp_path)
    assert measurement["sha256"] == expected
    content_row = row[:3] + row[4:]
    content_expected = hashlib.sha256(
        json.dumps(content_row, ensure_ascii=True, separators=(",", ":")).encode() + b"\n"
    ).hexdigest()
    assert measurement["content_sha256"] == content_expected
    assert measurement["content_identity_version"] == 1


@pytest.mark.parametrize(
    "change",
    [
        "record",
        "key",
        "source",
        "source_timestamp",
        "snapshot_timestamp",
        "config",
        "tool",
        "inventory",
    ],
)
def test_current_bundle_rejects_stale_context(produced, monkeypatch, change):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    if change == "tool":
        monkeypatch.setattr(preflight, "measure_toolchain", lambda: {"changed": True})
    elif change == "source":
        (source / "fixture").write_text("different")
    elif change in {"source_timestamp", "snapshot_timestamp"}:
        tree = source if change == "source_timestamp" else private / "snapshot"
        before = preflight.measure_tree(tree)
        path = tree / "fixture"
        info = path.stat()
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000))
        assert preflight.measure_tree(tree)["content_sha256"] == before["content_sha256"]
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


@pytest.mark.parametrize("change", ["legacy", "content_digest", "content_version"])
def test_loader_rejects_missing_or_changed_content_identity(produced, change):
    source, private, _ = produced
    complete = preflight.run_preflight(source, private)
    original_live_digest = complete["source"]["sha256"]
    if change == "legacy":
        del complete["source"]["content_sha256"]
        del complete["source"]["content_identity_version"]
    elif change == "content_digest":
        complete["source"]["content_sha256"] = "0" * 64
    else:
        complete["source"]["content_identity_version"] += 1
    (private / "complete.json").write_text(json.dumps(complete))
    assert preflight.measure_tree(source)["sha256"] == original_live_digest
    with pytest.raises(ValueError, match="current private run binding mismatch"):
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


@pytest.mark.parametrize("scanner", ["gitleaks", "detect-secrets"])
def test_scanner_relative_paths_use_child_cwd_not_parent_cwd(tmp_path, monkeypatch, scanner):
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    root = private / "snapshot"
    root.mkdir()
    (root / "fixture").write_text("exact synthetic source\n")
    unrelated = tmp_path / "parent"
    unrelated.mkdir()
    (unrelated / "snapshot").mkdir()
    (unrelated / "snapshot" / "fixture").write_text("unrelated synthetic source\n")
    # Neither a parent-cwd lookalike nor a root-relative lookalike may be selected.
    (root / "snapshot").mkdir()
    (root / "snapshot" / "fixture").write_text("wrong root-relative synthetic source\n")
    monkeypatch.chdir(unrelated)
    monkeypatch.setattr(common.shutil, "which", lambda name: name)
    monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "synthetic-only-key" * 3)
    captured = []

    def run(command, **options):
        assert options["cwd"] == private
        if command[1] == "version":
            return subprocess.CompletedProcess(command, 0, "8.30.1", "")
        if command[1] == "--version":
            return subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if command[1] == "dir":
            report = (
                [{"File": "snapshot/fixture", "RuleID": "synthetic", "StartLine": 1}]
                if scanner == "gitleaks"
                else []
            )
            Path(command[command.index("--report-path") + 1]).write_text(json.dumps(report))
            return subprocess.CompletedProcess(command, 2 if report else 0, "", "")
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "results": (
                        {
                            "snapshot/fixture": [
                                {
                                    "type": "synthetic",
                                    "line_number": 1,
                                    "hashed_secret": "synthetic",
                                }
                            ]
                        }
                        if scanner == "detect-secrets"
                        else {}
                    )
                }
            ),
            "",
        )

    monkeypatch.setattr(common.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="unresolved"):
        common.run_secret_scanners(
            root,
            scanner_directory=private,
            observation_sink=lambda findings, _report: captured.extend(findings),
        )
    finding = captured[0]
    assert finding["path"] == "fixture"
    assert finding["file_sha256"] == hashlib.sha256((root / "fixture").read_bytes()).hexdigest()
    absolute = common._scanner_finding(
        root,
        scanner,
        common.SECRET_SCANNER_VERSIONS[scanner],
        dict(finding["_record"], File=str(root / "fixture")),
    )
    assert common._finding_id(b"synthetic-key", absolute) == common._finding_id(
        b"synthetic-key", {key: value for key, value in finding.items() if key != "finding_id"}
    )


@pytest.mark.parametrize("reference", ["../outside", "/etc/passwd", "fixture"])
def test_explicit_report_cwd_cannot_fallback_into_source(tmp_path, reference):
    private = tmp_path / "private"
    private.mkdir()
    root = private / "snapshot"
    root.mkdir()
    (root / "fixture").write_text("synthetic only\n")
    with pytest.raises(RuntimeError, match="out-of-root"):
        common._scanner_relative_path(root, reference, report_directory=private)


def test_failed_mapping_retains_exact_preparation_and_sanitized_reason(produced, monkeypatch):
    source, private, _ = produced

    def reject(_root, **_options):
        raise RuntimeError("secret scanner finding file could not be verified")

    monkeypatch.setattr(common, "run_secret_scanners", reject)
    with pytest.raises(RuntimeError):
        preflight.run_preflight(source, private)
    preparation, _ = review.read_private_json(private / "preparation.json")
    assert preparation["source"] == preflight.measure_tree(source)
    assert preparation["selection"] == preflight.FULL_SELECTION
    assert preparation["toolchain"] == {"synthetic": "test_only"}
    assert preparation["purpose"] == "pre_scan_measurements_not_completed_baseline"
    failure, _ = review.read_private_json(private / "failure.json")
    assert failure["reason_code"] == "observation_source_read_failure"
    assert not (private / "complete.json").exists()


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
@pytest.mark.parametrize("terminated", [False, True])
def test_gitleaks_private_span_uses_pinned_byte_columns(newline, terminated):
    # v8.30.1 location.go measures later-line columns from the preceding LF,
    # not from the byte after it. EndColumn is the inclusive byte column.
    raw = "é head".encode() + newline + "αVALUEω".encode()
    if terminated:
        raw += newline
    record = {
        "StartLine": 1,
        "EndLine": 2,
        "StartColumn": 4,
        "EndColumn": 8,
        "Secret": "REDACTED",
        "Match": "head" + newline.decode() + "αREDACTED",
    }
    span, status = common._gitleaks_private_span(raw, record, version="8.30.1")
    if terminated:
        assert span == b"head" + newline + "αVALUE".encode()
        assert status == "mapped_reported_match_not_secret"
    else:
        # The pinned implementation cannot emit usable multi-line end columns
        # beyond its final LF; do not extend its semantics.
        assert span is None
        assert status == "unsupported_unterminated_multiline"
    record.update(StartLine=2, StartColumn=4)
    span, status = common._gitleaks_private_span(raw, record, version="8.30.1")
    assert span == b"VALUE"
    assert status == "mapped_reported_match_not_secret"


@pytest.mark.parametrize(
    "raw,record,version",
    [
        (b"VALUE", {"StartColumn": 0}, "8.30.1"),
        (b"VALUE", {"EndColumn": 6}, "8.30.1"),
        (b"VALUE", {"StartColumn": True}, "8.30.1"),
        (b"VALUE", {"StartLine": 0}, "8.30.1"),
        (b"VALUE", {"EndLine": 2}, "8.30.1"),
        (b"VALUE", {"StartLine": 2, "EndLine": 1}, "8.30.1"),
        ("éVALUE".encode(), {"StartColumn": 2}, "8.30.1"),
        ("VALUEé".encode(), {"EndColumn": 6}, "8.30.1"),
        (b"VALUE", {"Tags": ["decoded:base64", "decode-depth:2"]}, "8.30.1"),
        (b"VALUE", {"Tags": ["Encoded"]}, "8.30.1"),
        (b"VALUE", {"Tags": ["Decoded"]}, "8.30.1"),
        (b"VALUE", {"Tags": ["decode-depth:1"]}, "8.30.1"),
        (b"VALUE", {"Tags": "plain"}, "8.30.1"),
        (b"VALUE", {"Encoded": False}, "8.30.1"),
        (b"VALUE", {"Decoded": "VALUE"}, "8.30.1"),
        (b"VALUE", {"Fragment": {"Raw": "VALUE"}}, "8.30.1"),
        (b"VALUE", {"File": "outer!inner"}, "8.30.1"),
        (b"VALUE\rnext", {}, "8.30.1"),
        (b"VALUE\x00", {}, "8.30.1"),
        (b"VALUE\xff", {}, "8.30.1"),
        (b"VALUE" + b"x" * 100_000, {}, "8.30.1"),
        (b"VALUE", {}, "8.30.2"),
        (b"VALUE", {"EndColumn": None}, "8.30.1"),
        (b"VALUE", {"StartColumn": 4, "EndColumn": 2}, "8.30.1"),
        (b"VALUE\r\n", {"EndColumn": 6}, "8.30.1"),
        (b"VALUE\n", {"EndColumn": 6}, "8.30.1"),
        (b"VALUE", {"Commit": "synthetic-commit"}, "8.30.1"),
        (b"VALUE", {"SymlinkFile": "synthetic-link"}, "8.30.1"),
        (b"VALUE" + b"x" * 99_995, {}, "8.30.1"),
    ],
)
def test_gitleaks_private_span_fails_closed(raw, record, version):
    coordinates = dict(StartLine=1, EndLine=1, StartColumn=1, EndColumn=5)
    coordinates.update(record)
    span, status = common._gitleaks_private_span(raw, coordinates, version=version)
    assert span is None
    assert status.startswith("unsupported_")


def test_gitleaks_lf_origin_is_not_a_character_column():
    raw = "é\nαVALUE\n".encode()
    record = dict(StartLine=2, EndLine=2, StartColumn=4, EndColumn=8)
    assert common._gitleaks_private_span(raw, record, version="8.30.1")[0] == b"VALUE"
    # Ordinary one-based character columns would point elsewhere; do not guess.
    record["StartColumn"] = 3
    assert common._gitleaks_private_span(raw, record, version="8.30.1")[0] is None


@pytest.mark.parametrize("newline", [b"", b"\n", b"\r\n"])
def test_gitleaks_first_line_inclusive_bytes_do_not_depend_on_masked_payload(newline):
    raw = "é = VALUEω".encode() + newline
    record = dict(
        StartLine=1,
        EndLine=1,
        StartColumn=6,
        EndColumn=10,
        Secret="REDACTED",
        Match="entirely different masked payload",
    )
    span, status = common._gitleaks_private_span(raw, record, version="8.30.1")
    assert span == b"VALUE"
    assert status == "mapped_reported_match_not_secret"


@pytest.mark.parametrize("decoded", [False, True])
def test_masked_report_mapping_is_never_secret_recovery(produced, monkeypatch, decoded):
    source, private, _ = produced
    (source / "fixture").write_bytes(b'password = "SYNTHETIC_VALUE"\n')

    def scan(root, **options):
        record = dict(
            File=str(root / "fixture"),
            RuleID="synthetic-only",
            StartLine=1,
            EndLine=1,
            StartColumn=1,
            EndColumn=28,
            Secret="REDACTED",
            Match='password = "REDACTED"',
            Tags=["decoded:base64", "decode-depth:2"] if decoded else [],
        )
        finding = common._scanner_finding(root, "gitleaks", "8.30.1", record)
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
    assert row["predicates"]["reported_match_span_available"] is (not decoded)
    assert row["predicates"]["report_payload_redaction_marker_present"]
    assert row["predicates"]["exact_secret_recovered"] is False
    assert row["candidate_origin_proof"] == row["candidate_use_proof"] == "unavailable"
    assert row["state"] == "indeterminate"
    assert result["accepted"] == result["semantic_false_positive_proofs"] == 0
    assert "SYNTHETIC_VALUE" not in json.dumps(batch)
    assert "password = " not in json.dumps(batch)


def test_numbered_assessments_resume_without_overwriting(produced):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    preflight.assess_batch(source, private)
    first = (private / "batch-001.json").read_bytes()
    assert preflight.assess_batch(source, private, batch_index=2)["assigned"] == 0
    assert (private / "batch-001.json").read_bytes() == first
    queue, _ = review.read_private_json(private / "queue-002.json")
    assert review.queue_summary(queue)["by_state"]["indeterminate"] == 2
    with pytest.raises(FileExistsError):
        preflight.assess_batch(source, private, batch_index=2)


@pytest.mark.parametrize("index", [0, -1, True, 1.5, 1000])
def test_numbered_assessments_reject_invalid_index(produced, index):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    with pytest.raises(ValueError):
        preflight.assess_batch(source, private, batch_index=index)
    assert not list(private.glob("batch-*.json"))


def test_numbered_assessments_require_previous_checkpoint(produced):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    with pytest.raises(FileNotFoundError):
        preflight.assess_batch(source, private, batch_index=2)
    assert not (private / "batch-002.json").exists()


@pytest.mark.parametrize("attack", ["stale", "duplicate", "accepted", "evidence"])
def test_numbered_assessments_reject_untrusted_resume_before_publication(produced, attack):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    preflight.assess_batch(source, private)
    path = private / "queue-001.json"
    queue, _ = review.read_private_json(path)
    if attack == "stale":
        queue["bindings"]["source_sha256"] = "f" * 64
    elif attack == "duplicate":
        queue["observations"].append(dict(queue["observations"][0]))
    elif attack == "accepted":
        queue["observations"][0]["state"] = "accepted_exact_false_positive"
    else:
        queue["observations"][0]["evidence_sha256"] = "f" * 64
    path.write_text(json.dumps(queue))
    with pytest.raises(ValueError):
        preflight.assess_batch(source, private, batch_index=2)
    assert not (private / "batch-002.json").exists()
    assert not (private / "queue-002.json").exists()


def test_numbered_batches_exhaust_exact_inventory_once(produced, monkeypatch):
    source, private, _ = produced
    (source / "fixture").write_text("synthetic-only " * 50 + "\n")

    def scan(root, **options):
        findings = []
        for index in range(35):
            for scanner, record in (
                (
                    "gitleaks",
                    dict(
                        RuleID="synthetic-only",
                        StartLine=1,
                        EndLine=1,
                        StartColumn=index + 1,
                        EndColumn=index + 1,
                        Secret="REDACTED",
                    ),
                ),
                (
                    "detect-secrets",
                    dict(type="synthetic-only", line_number=1, hashed_secret=f"synthetic-{index}"),
                ),
            ):
                finding = common._scanner_finding(
                    root,
                    scanner,
                    common.SECRET_SCANNER_VERSIONS[scanner],
                    dict(record, File=str(root / "fixture")),
                )
                finding["finding_id"] = common._finding_id(
                    os.environ["CDX_FINDING_HMAC_KEY"].encode(), finding
                )
                findings.append(finding)
        common._write_finding_inventory(options["inventory_path"], findings, [root])
        options["observation_sink"](
            findings,
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
    seen = set()
    for index, expected in enumerate((32, 32, 6, 0), 1):
        result = preflight.assess_batch(source, private, batch_index=index)
        assert result["assigned"] == result["assessed"] == expected
        assert result["accepted"] == result["semantic_false_positive_proofs"] == 0
        batch, _ = review.read_private_json(private / f"batch-{index:03d}.json")
        identities = {row["finding_id"] for row in batch["assessments"]}
        assert not identities.intersection(seen)
        assert all(row["state"] == "indeterminate" for row in batch["assessments"])
        seen.update(identities)
    assert len(seen) == 70
    assert result["counts"]["by_state"]["indeterminate"] == 70


def test_existing_queue_destination_never_publishes_partial_batch(produced):
    source, private, _ = produced
    preflight.run_preflight(source, private)
    review.write_checkpoint(private / "queue-001.json", {"synthetic": "existing"})
    before = (private / "queue-001.json").read_bytes()
    with pytest.raises(FileExistsError):
        preflight.assess_batch(source, private)
    assert (private / "queue-001.json").read_bytes() == before
    assert not (private / "batch-001.json").exists()
