"""Tests for the read-only Codespace shutdown readiness audit."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts.autonomous import codespace_readiness


def initialize_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=path, check=True)


def test_clean_worktree_has_no_blockers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    initialize_repo(tmp_path)
    monkeypatch.setattr(codespace_readiness, "owned_processes", lambda _roots: [])
    monkeypatch.setattr(codespace_readiness, "temporary_candidates", lambda _roots: [])

    report = codespace_readiness.build_report([tmp_path], [])

    assert report["ready"] is True
    assert report["blockers"] == []
    assert report["worktrees"][0]["dirty"] is False


def test_dirty_worktree_and_untracked_file_block_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    (tmp_path / "local-note.txt").write_text("keep\n", encoding="utf-8")
    monkeypatch.setattr(codespace_readiness, "owned_processes", lambda _roots: [])
    monkeypatch.setattr(codespace_readiness, "temporary_candidates", lambda _roots: [])

    report = codespace_readiness.build_report([tmp_path], [])

    assert report["ready"] is False
    assert report["worktrees"][0]["status_entries"] == 2
    assert {item["code"] for item in report["blockers"]} == {"dirty_worktree"}


def test_repository_process_is_a_blocker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    initialize_repo(tmp_path)
    process = {
        "pid": 1234,
        "kind": "cognitive_app.src.server.cli_api_server:app",
        "cwd": str(tmp_path),
        "ports": [8765],
    }
    monkeypatch.setattr(codespace_readiness, "owned_processes", lambda _roots: [process])
    monkeypatch.setattr(codespace_readiness, "temporary_candidates", lambda _roots: [])

    report = codespace_readiness.build_report([tmp_path], [])

    assert report["ready"] is False
    assert report["blockers"] == [{"code": "repository_process_running", "path": str(tmp_path)}]
    assert "cmdline" not in report["repository_processes"][0]


def test_temporary_candidates_exclude_platform_secret_files(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    (tmp_path / "resume-note.txt").write_text("safe metadata\n", encoding="utf-8")

    candidates = codespace_readiness.temporary_candidates([tmp_path])

    assert [Path(item["path"]).name for item in candidates] == ["resume-note.txt"]
    assert "TOKEN=secret" not in json.dumps(candidates)


def test_strict_main_returns_failure_for_dirty_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    initialize_repo(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    monkeypatch.setattr(codespace_readiness, "owned_processes", lambda _roots: [])
    monkeypatch.setattr(codespace_readiness, "temporary_candidates", lambda _roots: [])

    exit_code = codespace_readiness.main(
        ["--strict", "--worktree", str(tmp_path), "--temp-root", str(tmp_path)]
    )

    assert exit_code == 1
    report: dict[str, Any] = json.loads(capsys.readouterr().out)
    assert report["ready"] is False
