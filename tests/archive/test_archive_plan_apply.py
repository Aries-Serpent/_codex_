from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

from click.testing import CliRunner


def _reload_archive_cli() -> tuple[Any, Any]:
    for name in ("codex.cli_archive", "codex.archive.api"):
        if name in sys.modules:
            sys.modules.pop(name)
    cli_archive = importlib.import_module("codex.cli_archive")
    archive_api = importlib.import_module("codex.archive.api")
    return cli_archive, archive_api


def test_apply_plan_then_restore(tmp_path: Path, monkeypatch) -> None:
    evidence_dir = tmp_path / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_path / ".codex" / "archive.sqlite"

    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CODEX_ACTOR", "cli-test")
    monkeypatch.chdir(tmp_path)

    cli_archive, archive_api = _reload_archive_cli()

    target_file = tmp_path / "legacy_module.py"
    original_text = (
        '"""Legacy module slated for archival."""\n\n'
        "def legacy_feature():\n"
        '    return "legacy-value"\n'
    )
    target_file.write_text(original_text, encoding="utf-8")
    original_bytes = target_file.read_bytes()

    plan_data = {
        "entries": [
            {
                "path": target_file.as_posix(),
                "reason": "cleanup",
                "commit_sha": "deadbeef",
            }
        ]
    }
    plan_file = tmp_path / "artifacts" / "archive_plan.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(json.dumps(plan_data), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        cli_archive.app,
        [
            "apply-plan",
            plan_file.as_posix(),
            "--repo",
            "demo-repo",
            "--by",
            "cli-test",
        ],
    )
    assert result.exit_code == 0, result.output

    payload = json.loads(result.stdout)
    assert payload["applied"], "expected at least one applied entry"
    entry = next(
        (item for item in payload["applied"] if item.get("path") == target_file.as_posix()),
        payload["applied"][0],
    )
    tombstone = entry["tombstone"]
    sha256 = entry["sha256"]

    stub_text = target_file.read_text(encoding="utf-8")
    assert f"# Tombstone: {tombstone}" in stub_text
    assert f"# SHA256: {sha256}" in stub_text

    restored = archive_api.restore(tombstone)
    assert restored["bytes"] == original_bytes
    assert restored["sha256"] == sha256

    evidence_file = evidence_dir / "archive_ops.jsonl"
    assert evidence_file.exists(), "expected evidence log to exist"
    events = [json.loads(line) for line in evidence_file.read_text(encoding="utf-8").splitlines()]

    plan_apply_events = [
        event
        for event in events
        if event.get("action") == "PLAN_APPLY" and event.get("tombstone") == tombstone
    ]
    assert plan_apply_events, "PLAN_APPLY event missing from evidence log"

    restore_events = [
        event
        for event in events
        if event.get("action") == "RESTORE" and event.get("tombstone") == tombstone
    ]
    assert restore_events, "RESTORE event missing from evidence log"

    assert plan_apply_events[0]["tombstone"] == restore_events[0]["tombstone"]


def test_apply_plan_multiple_entries(tmp_path: Path, monkeypatch) -> None:
    evidence_dir = tmp_path / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_path / ".codex" / "archive.sqlite"

    monkeypatch.setenv("CODEX_EVIDENCE_DIR", evidence_dir.as_posix())
    monkeypatch.setenv("CODEX_ARCHIVE_BACKEND", "sqlite")
    monkeypatch.setenv("CODEX_ARCHIVE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CODEX_ACTOR", "cli-test")
    monkeypatch.chdir(tmp_path)

    cli_archive, archive_api = _reload_archive_cli()

    targets = {
        tmp_path / "legacy_one.py": "print('legacy-one')\n",
        tmp_path / "pkg" / "legacy_two.py": "value = 42\n",
    }

    for path, contents in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")

    original_bytes = {path: path.read_bytes() for path in targets}

    plan_data = {
        "entries": [
            {
                "path": path.as_posix(),
                "reason": "cleanup",
                "commit_sha": f"deadbeef{i}",
            }
            for i, path in enumerate(targets, start=1)
        ]
    }
    plan_file = tmp_path / "artifacts" / "archive_plan.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(json.dumps(plan_data), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        cli_archive.app,
        [
            "apply-plan",
            plan_file.as_posix(),
            "--repo",
            "demo-repo",
            "--by",
            "cli-test",
        ],
    )
    assert result.exit_code == 0, result.output

    payload = json.loads(result.stdout)
    applied_paths = {item["path"] for item in payload["applied"]}
    assert applied_paths == {path.as_posix() for path in targets}

    tombstone_by_path: dict[str, str] = {}
    sha_by_path: dict[str, str] = {}
    for item in payload["applied"]:
        tombstone_by_path[item["path"]] = item["tombstone"]
        sha_by_path[item["path"]] = item["sha256"]

    for path, _ in targets.items():
        stub_text = path.read_text(encoding="utf-8")
        path_key = path.as_posix()
        assert f"# Tombstone: {tombstone_by_path[path_key]}" in stub_text
        assert f"# SHA256: {sha_by_path[path_key]}" in stub_text

    evidence_file = evidence_dir / "archive_ops.jsonl"
    assert evidence_file.exists(), "expected evidence log to exist"
    events = [json.loads(line) for line in evidence_file.read_text(encoding="utf-8").splitlines()]

    for path in targets:
        path_key = path.as_posix()
        tombstone = tombstone_by_path[path_key]
        plan_events = [
            event
            for event in events
            if event.get("action") == "PLAN_APPLY" and event.get("tombstone") == tombstone
        ]
        archive_events = [
            event
            for event in events
            if event.get("action") == "ARCHIVE" and event.get("tombstone") == tombstone
        ]
        assert plan_events, f"PLAN_APPLY event missing for {path_key}"
        assert archive_events, f"ARCHIVE event missing for {path_key}"

    for path, contents in original_bytes.items():
        restored = archive_api.restore(tombstone_by_path[path.as_posix()])
        assert restored["bytes"] == contents
