from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.autonomous import codespace_session_guard as guard


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "--no-pager", *args], cwd=repo, check=True, capture_output=True)


def initialize_repo(repo: Path) -> None:
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "seed")


def test_status_reports_v1_handoff_and_dirty_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    handoff_dir = tmp_path / ".codex"
    handoff_dir.mkdir()
    (handoff_dir / "session_handoff.json").write_text(
        json.dumps({"schema_version": 1, "branch": "0D_base_"}),
        encoding="utf-8",
    )
    (tmp_path / "work.txt").write_text("working\n", encoding="utf-8")

    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_dir / "session_handoff.json")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", handoff_dir / "NEXT_CONTINUATION_PROMPT.md")

    runtime_dir = tmp_path / "runtime"
    report = guard.status_report(tmp_path, runtime_dir, refresh=False)

    assert report["branch"] is not None
    assert report["head"] is not None
    assert report["handoff"]["loaded"] is True
    assert report["handoff"]["schema_version"] == 1
    assert "work.txt" in report["worktree"]["created"]


def test_write_handoff_creates_v2_and_continuation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    handoff_dir = tmp_path / ".codex"
    handoff_dir.mkdir()
    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_dir / "session_handoff.json")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", handoff_dir / "NEXT_CONTINUATION_PROMPT.md")

    handoff = guard.write_handoff(
        tmp_path,
        checkpoint_id="cp_test",
        checkpoint_path=".codex/checkpoints/v1/test/checkpoint_cp_test.json.gz",
        active_issue=5854,
        active_pr=None,
        completed=["Implementation branch created"],
        pending=["Add startup reconciliation"],
        objective="Implement Codespace continuity",
    )

    assert handoff["schema_version"] == 2
    assert handoff["active_issue"] == 5854
    assert handoff["checkpoint"]["checkpoint_id"] == "cp_test"
    assert json.loads((handoff_dir / "session_handoff.json").read_text())["schema_version"] == 2

    prompt = (handoff_dir / "NEXT_CONTINUATION_PROMPT.md").read_text(encoding="utf-8")
    assert "## Next Continuation Prompt" in prompt
    assert "Issue #5854" in prompt
    assert "Add startup reconciliation" in prompt


def test_runtime_checkpoint_and_cold_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    handoff_dir = tmp_path / ".codex"
    handoff_dir.mkdir()
    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_dir / "session_handoff.json")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", handoff_dir / "NEXT_CONTINUATION_PROMPT.md")

    runtime_dir = tmp_path / "runtime"
    checkpoint = guard.create_checkpoint(
        tmp_path,
        runtime_dir,
        session_id="test-session",
        task="Implement continuity",
        completed=["Settings updated"],
        pending=["Run tests"],
        active_issue=5854,
        active_pr=None,
        checkpoint_in_repo=False,
    )

    assert checkpoint["created"] is True
    assert checkpoint["checkpoint_id"].startswith("cp_")

    resume = guard.resume_report(tmp_path, runtime_dir, checkpoint["checkpoint_id"])
    assert resume["resumed"] is True
    assert resume["mode"] == "checkpoint"


def test_resume_without_checkpoint_is_cold_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    handoff_dir = tmp_path / ".codex"
    handoff_dir.mkdir()
    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_dir / "session_handoff.json")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", handoff_dir / "NEXT_CONTINUATION_PROMPT.md")

    resume = guard.resume_report(tmp_path, tmp_path / "runtime", None)

    assert resume["resumed"] is False
    assert resume["mode"] == "cold_bootstrap"
    assert resume["reason"] == "no_verified_checkpoint"


def test_sensitive_bundle_paths_are_refused() -> None:
    assert guard.validate_bundle_paths(
        {
            "created": [".env", "config/private_key.pem", "secrets.txt"],
            "modified": [],
            "deleted": [],
        }
    ) == [".env", "config/private_key.pem", "secrets.txt"]


def test_supported_and_unsupported_session_sync_settings_are_distinct() -> None:
    settings = (guard.ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")

    assert '"github.copilot.chat.localIndex.enabled": true' in settings
    assert "chat.sessionSync.enabled" not in settings
