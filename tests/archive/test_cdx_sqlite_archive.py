from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path

import pytest
from defusedxml import ElementTree as ET

from scripts.archive import cdx_common, codex_packer, codex_rehydrate
from scripts.archive.cdx_common import compute_merkle_root
from scripts.archive.codex_query import CodexArchiveQuery
from scripts.archive.codex_rehydrate import (
    _decompress,
    compare_trees,
    rehydrate_archive,
    validate_safe_rel_path,
    validate_symlink_target,
    verify_archive,
)


@pytest.fixture
def packed_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, bool]:
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    (source / "empty").mkdir(parents=True)
    (source / "pkg").mkdir()
    python_file = source / "pkg" / "sample.py"
    python_file.write_bytes(
        b"class Greeter:\r\n"
        b"    def greet(self, name: str) -> str:\r\n"
        b'        return "hello " + name\r\n'
        b"\r\n"
        b"def call_greeter(greeter):\r\n"
        b'    return greeter.greet("sample")\r\n'
    )
    os.chmod(python_file, 0o600)
    (source / "copy.txt").write_bytes(python_file.read_bytes())
    (source / "binary.dat").write_bytes(b"\x00\xff\x10")
    (source / "utf16.txt").write_bytes("text\r\n".encode("utf-16"))
    timestamp = 1_700_000_000_123_456_789
    for path in (python_file, source / "copy.txt", source / "binary.dat", source / "utf16.txt"):
        os.utime(path, ns=(timestamp, timestamp))
    for path in (source / "pkg", source / "empty", source):
        os.utime(path, ns=(timestamp, timestamp))
    symlink_mtime_supported = False
    try:
        os.symlink("../copy.txt", source / "pkg" / "copy-link")
        os.utime(
            source / "pkg" / "copy-link",
            ns=(timestamp, timestamp),
            follow_symlinks=False,
        )
        symlink_mtime_supported = (source / "pkg" / "copy-link").lstat().st_mtime_ns == timestamp
    except (NotImplementedError, OSError):
        # Some platforms do not support symlink creation or timestamp updates.
        pass
    for path in (source / "pkg", source / "empty", source):
        os.utime(path, ns=(timestamp, timestamp))
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    return source, archive, symlink_mtime_supported


def test_pack_indexes_text_ast_and_deduplicates_content(packed_tree):
    source, archive, _ = packed_tree
    with CodexArchiveQuery(archive) as query:
        info = query.get_archive_info()
        expected_entries = 7 if (source / "pkg" / "copy-link").is_symlink() else 6
        assert info["entry_count"] == expected_entries
        assert info["blob_count"] == 3
        assert query.read_file_bytes("pkg/sample.py").endswith(b"\r\n")
        assert query.read_file_text("pkg/sample.py", 2, 2).startswith("    def greet")
        entries = {item["path"]: item for item in query.list_tree()}
        assert entries["pkg/sample.py"]["line_endings"] == "CRLF"
        assert entries["utf16.txt"]["text_encoding"] == "utf-16"
        assert query.query_symbols("greet")[0]["qualified_name"].endswith("Greeter.greet")
        graph = query.query_call_graph("greet")
        assert graph["callers"] == [
            {"path": "pkg/sample.py", "qualified_name": "sample.call_greeter"}
        ]
        assert query.search_fts("hello")[0]["path"] in {"pkg/sample.py", "copy.txt"}
        context = query.build_llm_context(symbols=("greet",), budget_tokens=200)
        assert "<codex_context>" in context["content"]
        assert context["estimated_tokens"] <= 200
        with pytest.raises(sqlite3.OperationalError):
            query.connection.execute("DELETE FROM tree_entries")
    assert verify_archive(archive)["integrity_check"] == "ok"


def test_archive_rehydrates_byte_and_metadata_exactly(packed_tree, tmp_path: Path):
    source, archive, symlink_mtime_supported = packed_tree
    destination = tmp_path / "rehydrated"
    rehydrate_archive(archive, destination)
    result = compare_trees(source, destination, check_mtime=symlink_mtime_supported)
    assert result["identical"], result
    original = source / "pkg" / "sample.py"
    restored = destination / "pkg" / "sample.py"
    assert stat.S_IMODE(restored.stat().st_mode) == stat.S_IMODE(original.stat().st_mode)
    assert restored.stat().st_mtime_ns == original.stat().st_mtime_ns
    link = source / "pkg" / "copy-link"
    if link.is_symlink():
        restored_link = destination / "pkg" / "copy-link"
        assert os.readlink(restored_link) == os.readlink(link)
        if symlink_mtime_supported:
            assert restored_link.lstat().st_mtime_ns == link.lstat().st_mtime_ns


def test_pack_is_reproducible_and_excludes_large_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "small.txt").write_text("ok\n", encoding="utf-8")
    (source / "large.bin").write_bytes(b"x" * 10)
    (source / "excluded").mkdir()
    (source / "excluded" / "inside.txt").write_text("skip\n", encoding="utf-8")
    (source / ".worktrees").mkdir()
    (source / ".worktrees" / "work.txt").write_text("skip\n", encoding="utf-8")
    first = tmp_path / "first.cdx.sqlite"
    second = tmp_path / "second.cdx.sqlite"
    first_result = codex_packer.pack_archive(source, first, max_file_bytes=5, exclude=("excluded",))
    second_result = codex_packer.pack_archive(
        source, second, max_file_bytes=5, exclude=("excluded",)
    )
    assert first_result["merkle_root_sha256"] == second_result["merkle_root_sha256"]
    with CodexArchiveQuery(first) as query:
        assert [item["path"] for item in query.list_tree()] == ["small.txt"]


def test_prefix_listing_includes_supplementary_unicode_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    (source / "pkg").mkdir(parents=True)
    (source / "pkg" / "a.py").write_text("a\n", encoding="utf-8")
    (source / "pkg" / "😀.py").write_text("emoji\n", encoding="utf-8")
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        assert [item["path"] for item in query.list_tree("pkg")] == [
            "pkg",
            "pkg/a.py",
            "pkg/😀.py",
        ]


def test_context_output_is_well_formed_xml_for_control_characters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / 'quote"name.txt').write_bytes(b"<tag>&\x01\n")
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        context = query.build_llm_context(paths=('quote"name.txt',))
    parsed = ET.fromstring(context["content"])
    assert parsed.find("file").text.strip() == "<tag>&\ufffd"


def test_markdown_context_cannot_be_escaped_by_archive_text_or_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "`\n## injected heading").write_text(
        "source\n```\n# injected content\n", encoding="utf-8"
    )
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        markdown = query.build_llm_context(paths=("*",), output_format="markdown")["content"]
    lines = markdown.splitlines()
    assert lines[0].startswith("### `` ")
    assert r"\n## injected heading" in lines[0]
    fences = [line for line in lines if line and set(line) == {"`"}]
    assert len(fences) == 3
    assert len(fences[0]) == 4
    assert fences[1] == "```"
    assert fences[0] == fences[2]


def test_scanner_failure_never_replaces_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "source"
    source.mkdir()
    output = tmp_path / "existing.cdx.sqlite"
    output.write_bytes(b"existing")

    def reject_scan(*_args, **_kwargs):
        raise RuntimeError("secret scan flagged files; archive creation blocked")

    monkeypatch.setattr(codex_packer, "run_secret_scanners", reject_scan)
    with pytest.raises(RuntimeError, match="blocked"):
        codex_packer.pack_archive(source, output)
    assert output.read_bytes() == b"existing"


def test_packer_scans_and_packs_the_same_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "source"
    source.mkdir()
    original = source / "data.txt"
    original.write_text("scanned bytes\n", encoding="utf-8")
    output = tmp_path / "snapshot.cdx.sqlite"

    def mutate_original_after_scan(snapshot: Path, *_args, **_kwargs):
        assert snapshot != source
        original.write_text("changed after snapshot\n", encoding="utf-8")

    monkeypatch.setattr(codex_packer, "run_secret_scanners", mutate_original_after_scan)
    codex_packer.pack_archive(source, output)
    with CodexArchiveQuery(output) as query:
        assert query.read_file_bytes("data.txt") == b"scanned bytes\n"


def test_packer_rejects_snapshot_changes_after_scanning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source = tmp_path / "source"
    source.mkdir()
    (source / "data.txt").write_text("before scan\n", encoding="utf-8")
    output = tmp_path / "snapshot.cdx.sqlite"

    def mutate_snapshot_after_scan(snapshot: Path, *_args, **_kwargs):
        (snapshot / "data.txt").write_text("changed during scan\n", encoding="utf-8")

    monkeypatch.setattr(codex_packer, "run_secret_scanners", mutate_snapshot_after_scan)
    with pytest.raises(RuntimeError, match="scanned snapshot"):
        codex_packer.pack_archive(source, output)
    assert not output.exists()


def test_packer_rejects_replacement_symlink_during_snapshot_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source = tmp_path / "source"
    source.mkdir()
    selected = source / "data.txt"
    selected.write_text("inside\n", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    output = tmp_path / "snapshot.cdx.sqlite"
    original_iter = codex_packer.iter_deterministic_tree

    def replace_before_read(root, *args, **kwargs):
        for path, relative, info in original_iter(root, *args, **kwargs):
            if relative == "data.txt":
                path.unlink()
                path.symlink_to(outside)
            yield path, relative, info

    monkeypatch.setattr(codex_packer, "iter_deterministic_tree", replace_before_read)
    monkeypatch.setattr(
        codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: pytest.fail("scanner ran")
    )
    with pytest.raises((OSError, ValueError)):
        codex_packer.pack_archive(source, output)
    assert not output.exists()


def test_packer_scanners_receive_only_allowlisted_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "synthetic-test-secret")
    captured = {}

    def capture_environment(*_args, **kwargs):
        captured.update(kwargs["scanner_environment"])

    monkeypatch.setattr(codex_packer, "run_secret_scanners", capture_environment)
    codex_packer.pack_archive(source, tmp_path / "snapshot.cdx.sqlite")
    assert set(captured) == {
        "PATH",
        "HOME",
        "LC_ALL",
        "PYTHONNOUSERSITE",
        "PYTHONDONTWRITEBYTECODE",
    }
    assert captured["PATH"] == os.environ.get("PATH", "")
    assert captured["HOME"] != str(Path.home())
    assert "CDX_FINDING_HMAC_KEY" not in captured


def test_query_call_graph_joins_symbol_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "graph.py").write_text(
        "def callee():\n    return None\n\ndef caller():\n    return callee()\n",
        encoding="utf-8",
    )
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        expected = [{"path": "graph.py", "qualified_name": "graph.caller"}]
        assert query.query_call_graph("callee")["callers"] == expected
        assert query.query_call_graph("graph.callee")["callers"] == expected


def test_ast_call_targets_exclude_nested_function_and_lambda_bodies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "graph.py").write_text(
        "def callee():\n"
        "    return None\n"
        "\n"
        "def outer():\n"
        "    def inner():\n"
        "        callee()\n"
        "    callback = lambda: callee()\n"
        "    return callback\n",
        encoding="utf-8",
    )
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        symbols = {item["symbol_name"]: item for item in query.query_symbols(path="graph.py")}
        assert "callee" not in symbols["outer"]["call_targets"]
        assert symbols["inner"]["call_targets"] == ["callee"]
        assert query.query_call_graph("callee")["callers"] == [
            {"path": "graph.py", "qualified_name": "graph.outer.inner"}
        ]


def test_symbol_lookup_uses_literal_and_glob_qualified_suffixes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "sample.py").write_text(
        "class Greeter:\n"
        "    def greet(self):\n"
        "        return None\n"
        "\n"
        "def do_work():\n"
        "    return None\n"
        "\n"
        "def doXwork():\n"
        "    return None\n",
        encoding="utf-8",
    )
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        exact = query.query_symbols("do_work")
        assert [item["symbol_name"] for item in exact] == ["do_work"]
        assert query.query_symbols("Do_work") == []
        globbed = query.query_symbols("Greeter.*", glob=True)
        assert [item["qualified_name"] for item in globbed] == ["sample.Greeter.greet"]


def test_context_skips_oversized_search_and_symbol_candidates_before_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "large.py").write_text(
        "def target():\n    return None\n# " + ("x" * (1024 * 1024)),
        encoding="utf-8",
    )
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        original_read_file_text = query.read_file_text
        read_paths = []

        def guarded_read(path, *args, **kwargs):
            read_paths.append(path)
            if path == "large.py":
                raise AssertionError("oversized candidate was read")
            return original_read_file_text(path, *args, **kwargs)

        monkeypatch.setattr(query, "read_file_text", guarded_read)
        context = query.build_llm_context(
            query="target",
            symbols=("target",),
            budget_tokens=64,
        )
    assert read_paths == []
    assert context["included_items"] == 0
    assert set(context["omitted_items"]) == {"large.py:large.target", "large.py"}


def test_markdown_context_budget_counts_double_newline_separators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    for index in range(4):
        (source / f"{index}.txt").write_text(f"content {index}\n", encoding="utf-8")
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    with CodexArchiveQuery(archive) as query:
        context = query.build_llm_context(
            paths=("*.txt",),
            budget_tokens=57,
            output_format="markdown",
        )
    assert context["included_items"] == 3
    assert context["estimated_tokens"] <= 57


def test_secret_scanner_requires_exact_dispositions_and_emits_redacted_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "source"
    root.mkdir()
    (root / "secret.txt").write_text("synthetic fixture\n", encoding="utf-8")
    monkeypatch.setattr(cdx_common.shutil, "which", lambda name: name)
    monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "local-test-key-" * 3)

    def fake_run(command, **_kwargs):
        if command[0] == "gitleaks" and command[1] == "version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "8.30.1\n", "")
        if command[0] == "detect-secrets" and command[1] == "--version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "1.5.0\n", "")
        if command[0] == "gitleaks":
            assert command[1] == "dir"
            assert "--redact=100" in command
            assert "--no-git" not in command
            report = Path(command[command.index("--report-path") + 1])
            report.write_text(
                json.dumps(
                    [
                        {
                            "File": str(root / "secret.txt"),
                            "RuleID": "generic-api-key",
                            "StartLine": 1,
                            "EndLine": 1,
                            "Fingerprint": "opaque-gitleaks-fingerprint",
                            "Secret": "REDACTED",  # pragma: allowlist secret
                        }
                    ]
                ),
                encoding="utf-8",
            )
            return cdx_common.subprocess.CompletedProcess(command, 2, "", "")
        if command[1] == "scan":
            assert command[2:4] == ["--no-verify", "--all-files"]
        return cdx_common.subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "results": {
                        os.path.relpath(root / "secret.txt", _kwargs["cwd"]): [
                            {
                                "type": "Secret Keyword",
                                "line_number": 1,
                                "hashed_secret": "opaque-detect-secrets-hash",  # pragma: allowlist secret
                            }
                        ]
                    }
                },
            ),
            "",
        )

    monkeypatch.setattr(cdx_common.subprocess, "run", fake_run)
    inventory = tmp_path / "findings.json"
    with pytest.raises(RuntimeError, match="unresolved"):
        cdx_common.run_secret_scanners(root, inventory_path=inventory)
    inventory_document = json.loads(inventory.read_text(encoding="utf-8"))
    assert len(inventory_document["findings"]) == 2
    assert "REDACTED" not in inventory.read_text(encoding="utf-8")
    dispositions = tmp_path / "dispositions.json"
    evidence = tmp_path / "review-evidence.txt"
    evidence.write_text("synthetic fixture verified as harmless\n", encoding="utf-8")
    evidence_sha256 = hashlib.sha256(evidence.read_bytes()).hexdigest()
    rows = []
    for finding in inventory_document["findings"]:
        rows.append(
            {
                field: finding[field]
                for field in (
                    "scanner",
                    "scanner_version",
                    "finding_id",
                    "path",
                    "file_sha256",
                    "rule",
                    "start_line",
                    "end_line",
                )
            }
            | {
                "disposition": "false_positive",
                "evidence_ref": str(evidence),
                "evidence_sha256": evidence_sha256,
                "reviewed_by": "test-reviewer",
            }
        )
    dispositions.write_text(
        json.dumps({"schema_version": 1, "dispositions": rows}),
        encoding="utf-8",
    )
    cdx_common.run_secret_scanners(root, dispositions_path=dispositions)


@pytest.mark.parametrize("change", ("digest", "version", "location"))
def test_secret_scanner_dispositions_expire_when_finding_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
):
    root = tmp_path / "source"
    root.mkdir()
    source_file = root / "secret.txt"
    source_file.write_text("synthetic fixture\n", encoding="utf-8")
    monkeypatch.setattr(cdx_common.shutil, "which", lambda name: name)
    monkeypatch.setenv("CDX_FINDING_HMAC_KEY", "local-test-key-" * 3)
    state = {"version": "8.30.1", "line": 1}

    def fake_run(command, **_kwargs):
        if command[0] == "gitleaks" and command[1] == "version":
            return cdx_common.subprocess.CompletedProcess(command, 0, state["version"], "")
        if command[0] == "detect-secrets" and command[1] == "--version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if command[0] == "gitleaks":
            report = Path(command[command.index("--report-path") + 1])
            report.write_text(
                json.dumps(
                    [
                        {
                            "File": str(source_file),
                            "RuleID": "generic-api-key",
                            "StartLine": state["line"],
                            "EndLine": state["line"],
                            "Fingerprint": "opaque-fingerprint",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            return cdx_common.subprocess.CompletedProcess(command, 2, "", "")
        return cdx_common.subprocess.CompletedProcess(command, 0, '{"results": {}}', "")

    monkeypatch.setattr(cdx_common.subprocess, "run", fake_run)
    inventory = tmp_path / "findings.json"
    with pytest.raises(RuntimeError, match="unresolved"):
        cdx_common.run_secret_scanners(root, inventory_path=inventory)
    finding = json.loads(inventory.read_text(encoding="utf-8"))["findings"][0]
    row = {
        field: finding[field]
        for field in (
            "scanner",
            "scanner_version",
            "finding_id",
            "path",
            "file_sha256",
            "rule",
            "start_line",
            "end_line",
        )
    }
    evidence = tmp_path / "review-evidence.txt"
    evidence.write_text("synthetic fixture review\n", encoding="utf-8")
    row.update(
        disposition="false_positive",
        evidence_ref=str(evidence),
        evidence_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest(),
        reviewed_by="test-reviewer",
    )
    dispositions = tmp_path / "dispositions.json"
    dispositions.write_text(
        json.dumps({"schema_version": 1, "dispositions": [row]}), encoding="utf-8"
    )
    if change == "digest":
        source_file.write_text("changed fixture\n", encoding="utf-8")
    elif change == "version":
        state["version"] = "8.30.2"
    else:
        state["line"] = 2
    with pytest.raises(RuntimeError, match="unresolved|stale|pinned"):
        cdx_common.run_secret_scanners(root, dispositions_path=dispositions)


def test_secret_scanner_rejects_malformed_reports_and_path_allowlists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "source"
    root.mkdir()
    monkeypatch.setattr(cdx_common.shutil, "which", lambda name: name)

    def fake_run(command, **_kwargs):
        if command[0] == "gitleaks" and command[1] == "version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "8.30.1", "")
        if command[0] == "detect-secrets" and command[1] == "--version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if command[0] == "gitleaks":
            report = Path(command[command.index("--report-path") + 1])
            report.write_text("{", encoding="utf-8")
            return cdx_common.subprocess.CompletedProcess(command, 2, "", "")
        return cdx_common.subprocess.CompletedProcess(command, 0, '{"results": {}}', "")

    monkeypatch.setattr(cdx_common.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="not supported"):
        cdx_common.run_secret_scanners(root, {"secret.txt"})
    with pytest.raises(RuntimeError, match="could not be completed"):
        cdx_common.run_secret_scanners(root)


def test_secret_scanner_rejects_malformed_detect_secrets_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "source"
    root.mkdir()
    monkeypatch.setattr(cdx_common.shutil, "which", lambda name: name)

    def fake_run(command, **_kwargs):
        if command[0] == "gitleaks" and command[1] == "version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "8.30.1", "")
        if command[0] == "detect-secrets" and command[1] == "--version":
            return cdx_common.subprocess.CompletedProcess(command, 0, "1.5.0", "")
        if command[0] == "gitleaks":
            report = Path(command[command.index("--report-path") + 1])
            report.write_text("[]", encoding="utf-8")
            return cdx_common.subprocess.CompletedProcess(command, 0, "", "")
        return cdx_common.subprocess.CompletedProcess(command, 0, "{", "")

    monkeypatch.setattr(cdx_common.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="could not be completed"):
        cdx_common.run_secret_scanners(root)


def test_secret_scanner_disposition_and_inventory_files_must_be_external(tmp_path: Path):
    root = tmp_path / "source"
    root.mkdir()
    with pytest.raises(RuntimeError, match="outside the source tree"):
        cdx_common.run_secret_scanners(root, inventory_path=root / "inventory.json")

    dispositions = root / "dispositions.json"
    dispositions.write_text('{"schema_version": 1, "dispositions": []}', encoding="utf-8")
    with pytest.raises(RuntimeError, match="outside the source tree"):
        cdx_common.run_secret_scanners(root, dispositions_path=dispositions)


def test_secret_scanner_missing_dependency_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(cdx_common.shutil, "which", lambda _name: None)
    with pytest.raises(RuntimeError, match="required"):
        cdx_common.run_secret_scanners(tmp_path)


def test_rehydrate_validates_paths_before_creating_destination(packed_tree, tmp_path: Path):
    _, archive, _ = packed_tree
    with sqlite3.connect(archive) as connection:
        connection.execute("UPDATE tree_entries SET path = '../outside' WHERE path = 'copy.txt'")
        connection.execute("UPDATE fts_documents SET path = '../outside' WHERE path = 'copy.txt'")
        merkle = compute_merkle_root(connection)
        connection.execute(
            "UPDATE archive_manifest SET merkle_root_sha256 = ? WHERE id = 1",
            (merkle,),
        )
    destination = tmp_path / "unsafe-restore"
    with pytest.raises(ValueError, match="traversal"):
        rehydrate_archive(archive, destination)
    assert not destination.exists()


def test_rehydrate_rejects_privileged_modes_before_writing(packed_tree, tmp_path: Path):
    _, archive, _ = packed_tree
    with sqlite3.connect(archive) as connection:
        connection.execute(
            "UPDATE tree_entries SET mode = mode | 2048 WHERE path = 'pkg/sample.py'"
        )
        merkle = compute_merkle_root(connection)
        connection.execute(
            "UPDATE archive_manifest SET merkle_root_sha256 = ? WHERE id = 1",
            (merkle,),
        )
    destination = tmp_path / "privileged-restore"
    with pytest.raises(ValueError, match="setuid/setgid"):
        rehydrate_archive(archive, destination)
    assert not destination.exists()


def test_rehydrate_does_not_follow_destination_root_replacement(
    packed_tree, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _, archive, _ = packed_tree
    destination = tmp_path / "restore"
    destination.mkdir()
    pinned_destination = tmp_path / "pinned-restore"
    outside = tmp_path / "outside"
    outside.mkdir()
    original_listdir = os.listdir
    replaced = False

    def replace_after_open(path):
        nonlocal replaced
        if isinstance(path, int) and not replaced:
            destination.rename(pinned_destination)
            destination.symlink_to(outside, target_is_directory=True)
            replaced = True
        return original_listdir(path)

    monkeypatch.setattr(codex_rehydrate.os, "listdir", replace_after_open)
    rehydrate_archive(archive, destination)
    assert replaced
    assert (pinned_destination / "copy.txt").is_file()
    assert list(outside.iterdir()) == []


def test_rehydrate_rejects_subdirectory_symlink_replacement(
    packed_tree, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _, archive, _ = packed_tree
    destination = tmp_path / "restore"
    moved_directory = tmp_path / "pinned-pkg"
    outside = tmp_path / "outside"
    outside.mkdir()
    original_open_directory = codex_rehydrate._open_extraction_directory
    replaced = False

    def replace_after_open(root_fd, components):
        nonlocal replaced
        directory_fd = original_open_directory(root_fd, components)
        if components == ("pkg",) and not replaced:
            (destination / "pkg").rename(moved_directory)
            (destination / "pkg").symlink_to(outside, target_is_directory=True)
            replaced = True
        return directory_fd

    monkeypatch.setattr(
        codex_rehydrate,
        "_open_extraction_directory",
        replace_after_open,
    )
    with pytest.raises(OSError):
        rehydrate_archive(archive, destination)
    assert replaced
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("root_type", ("missing", "file"))
def test_compare_trees_requires_existing_directory_roots(tmp_path: Path, root_type: str):
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    if root_type == "file":
        right.write_text("not a directory", encoding="utf-8")
        error = NotADirectoryError
    else:
        error = FileNotFoundError
    with pytest.raises(error):
        compare_trees(left, right)


def test_compare_trees_propagates_walk_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "tree"
    root.mkdir()

    def fail_walk(_root, *, topdown, followlinks, onerror):
        assert topdown
        assert not followlinks
        onerror(PermissionError("tree access denied"))
        yield

    monkeypatch.setattr(codex_rehydrate.os, "walk", fail_walk)
    with pytest.raises(PermissionError, match="tree access denied"):
        compare_trees(root, root)


def test_rehydrate_uses_verified_connection_after_atomic_archive_replacement(
    packed_tree, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source, archive, _ = packed_tree
    replacement = tmp_path / "replacement.cdx.sqlite"
    replacement.write_bytes(archive.read_bytes())
    with sqlite3.connect(replacement) as connection:
        connection.execute(
            "UPDATE tree_entries SET mode = mode | 2048 WHERE path = 'pkg/sample.py'"
        )
        connection.execute(
            "UPDATE archive_manifest SET merkle_root_sha256 = ? WHERE id = 1",
            (compute_merkle_root(connection),),
        )
    with pytest.raises(ValueError, match="setuid/setgid"):
        verify_archive(replacement)

    opened = []
    verified = []
    connect = codex_rehydrate._connect_readonly
    verify = codex_rehydrate.verify_archive_connection

    def track_connection(path):
        connection = connect(path)
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        opened.append(connection)
        return connection

    def replace_after_verification(connection, **kwargs):
        result = verify(connection, **kwargs)
        verified.append(connection)
        os.replace(replacement, archive)
        return result

    monkeypatch.setattr(codex_rehydrate, "_connect_readonly", track_connection)
    monkeypatch.setattr(codex_rehydrate, "verify_archive_connection", replace_after_verification)
    destination = tmp_path / "verified-restore"
    result = rehydrate_archive(archive, destination)
    assert result["integrity_check"] == "ok"
    assert len(opened) == 1
    assert verified == opened
    assert compare_trees(source, destination, check_mtime=False)["identical"]
    restored = destination / "pkg" / "sample.py"
    assert stat.S_IMODE(restored.stat().st_mode) == 0o600
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        opened[0].execute("SELECT 1")


def test_blob_readers_enforce_the_configured_size_ceiling(packed_tree):
    _, archive, _ = packed_tree
    with pytest.raises(ValueError, match="size ceiling"):
        verify_archive(archive, max_blob_bytes=2)
    with pytest.raises(ValueError, match="size ceiling"):
        CodexArchiveQuery(archive, max_blob_bytes=2)
    with pytest.raises(ValueError, match="size ceiling"):
        CodexArchiveQuery(archive, max_text_bytes=2)


def test_decompressor_rejects_negative_declared_sizes():
    with pytest.raises(ValueError, match="must not be negative"):
        _decompress("zlib", b"", -1)


def test_text_index_is_bound_to_the_raw_blob_and_merkle_metadata(packed_tree):
    _, archive, _ = packed_tree
    forged_text = "forged text"
    forged_hash = hashlib.sha256(forged_text.encode("utf-8")).hexdigest()
    with sqlite3.connect(archive) as connection:
        connection.execute("""
            UPDATE text_documents SET utf8_text = 'forged text'
            WHERE entry_id = (
                SELECT entry_id FROM tree_entries WHERE path = 'pkg/sample.py'
            )
            """)
        connection.execute(
            "UPDATE tree_entries SET text_sha256 = ? WHERE path = 'pkg/sample.py'",
            (forged_hash,),
        )
        merkle = compute_merkle_root(connection)
        connection.execute(
            "UPDATE archive_manifest SET merkle_root_sha256 = ? WHERE id = 1",
            (merkle,),
        )
    with pytest.raises(ValueError, match="text index"):
        CodexArchiveQuery(archive)
    with pytest.raises(ValueError, match="text index"):
        verify_archive(archive)


def test_ast_index_is_validated_against_archived_source(packed_tree):
    _, archive, _ = packed_tree
    with sqlite3.connect(archive) as connection:
        connection.execute(
            "UPDATE ast_symbols SET qualified_name = 'forged.name' WHERE symbol_name = 'greet'"
        )
    with pytest.raises(ValueError, match="AST index"):
        verify_archive(archive)


def test_ast_index_verification_handles_multiple_python_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(codex_packer, "run_secret_scanners", lambda *_args, **_kwargs: None)
    source = tmp_path / "source"
    source.mkdir()
    (source / "first.py").write_text("class First:\n    def run(self):\n        return 1\n")
    (source / "second.py").write_text("def invoke():\n    return 2\n")
    archive = tmp_path / "snapshot.cdx.sqlite"
    codex_packer.pack_archive(source, archive)
    assert verify_archive(archive)["integrity_check"] == "ok"


def test_fts_external_content_is_validated(packed_tree):
    _, archive, _ = packed_tree
    with sqlite3.connect(archive) as connection:
        connection.execute(
            "UPDATE fts_documents SET content = 'forged' WHERE document_type = 'file'"
        )
    with pytest.raises(ValueError, match="search index"):
        CodexArchiveQuery(archive)


def test_fts_postings_are_validated(packed_tree):
    _, archive, _ = packed_tree
    with sqlite3.connect(archive) as connection:
        connection.execute("INSERT INTO fts_code_index(fts_code_index) VALUES ('delete-all')")
    with pytest.raises(ValueError, match="FTS postings"):
        CodexArchiveQuery(archive)


@pytest.mark.parametrize("path", ("../outside", "/absolute", "C:/outside", "a\\b", ""))
def test_rehydration_rejects_unsafe_paths(path: str):
    with pytest.raises(ValueError):
        validate_safe_rel_path(path)


def test_rehydration_blocks_external_symlink_targets():
    with pytest.raises(ValueError, match="escapes"):
        validate_symlink_target("nested/link", "../../outside")
    with pytest.raises(ValueError, match="not allowed"):
        validate_symlink_target("link", "/outside")
    validate_symlink_target("nested/link", "../sibling")
    with pytest.raises(ValueError, match="another archived symlink"):
        validate_symlink_target(
            "link",
            "dir/../outside",
            archive_symlinks={"dir"},
        )


def test_external_symlink_option_still_validates_relative_targets():
    validate_symlink_target("nested/link", "../sibling", allow_external=True)
    with pytest.raises(ValueError, match="escapes"):
        validate_symlink_target("nested/link", "../../outside", allow_external=True)
    with pytest.raises(ValueError, match="another archived symlink"):
        validate_symlink_target(
            "nested/link",
            "sibling",
            allow_external=True,
            archive_symlinks={"nested/sibling"},
        )
