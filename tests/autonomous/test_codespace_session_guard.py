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


def test_historical_handoff_is_not_loaded_as_current_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    handoff_path = tmp_path / ".codex" / "session_handoff.json"
    handoff_path.parent.mkdir()
    handoff_path.write_text(
        json.dumps({"schema_version": 2, "artifact_state": "historical"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_path)

    handoff, error = guard.load_handoff()

    assert handoff is None
    assert error == "historical"


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


def test_worktree_entries_decode_quoted_and_renamed_paths(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    spaced = tmp_path / "my config"
    spaced.mkdir()
    secret = spaced / ".env"
    secret.write_text("SECRET=value\n", encoding="utf-8")

    entries = guard.worktree_entries(tmp_path)

    assert "my config/.env" in entries["created"]


def test_worktree_entries_include_deleted_rename_path(tmp_path: Path) -> None:
    initialize_repo(tmp_path)
    old = tmp_path / "old.env"
    old.write_text("SECRET=value\n", encoding="utf-8")
    git(tmp_path, "add", "old.env")
    git(tmp_path, "commit", "-q", "-m", "add old env")
    git(tmp_path, "mv", "old.env", "new.txt")

    entries = guard.worktree_entries(tmp_path)

    assert "old.env" in entries["deleted"]
    assert "new.txt" in entries["created"]


def test_sensitive_bundle_paths_are_refused() -> None:
    assert guard.validate_bundle_paths(
        {
            "created": [".env", "config/private_key.pem", "secrets.txt"],
            "modified": [],
            "deleted": ["config/deleted_private_key.pem", ".env"],
        }
    ) == [
        ".env",
        "config/deleted_private_key.pem",
        "config/private_key.pem",
        "secrets.txt",
    ]


def test_conventional_ssh_private_keys_are_sensitive() -> None:
    for name in (
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_ed25519_sk",
        "id_ecdsa_sk",
    ):
        assert guard.is_sensitive_path(f".ssh/{name}")


def test_bundle_rejects_symlinks_and_outside_targets(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("private target\n", encoding="utf-8")
    symlink = tmp_path / "notes.txt"
    symlink.symlink_to(outside)

    blocked = guard.validate_bundle_paths(
        {"created": ["notes.txt"], "modified": [], "deleted": []},
        tmp_path,
    )

    assert blocked == ["outside_repo:notes.txt"] or blocked == ["symlink:notes.txt"]


def test_repo_checkpoint_is_found_when_runtime_root_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    handoff_dir = tmp_path / ".codex"
    handoff_dir.mkdir()
    monkeypatch.setattr(guard, "HANDOFF_PATH", handoff_dir / "session_handoff.json")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", handoff_dir / "NEXT_CONTINUATION_PROMPT.md")
    monkeypatch.setattr(guard, "CHECKPOINT_ROOT", tmp_path / ".codex" / "checkpoints")

    checkpoint = guard.create_checkpoint(
        tmp_path,
        tmp_path / "runtime-empty",
        session_id="repo-fallback-test",
        task="Test repository fallback",
        completed=[],
        pending=[],
        active_issue=5857,
        active_pr=5857,
        checkpoint_in_repo=True,
    )
    assert checkpoint["created"] is True

    runtime_dir = tmp_path / "runtime-missing"
    resume = guard.resume_report(tmp_path, runtime_dir, checkpoint["checkpoint_id"])

    assert resume["resumed"] is True
    assert resume["mode"] == "checkpoint"


def test_corrupt_checkpoint_is_not_reported_as_verified_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initialize_repo(tmp_path)
    runtime_dir = tmp_path / "runtime"
    checkpoint = guard.create_checkpoint(
        tmp_path,
        runtime_dir,
        session_id="corruption-test",
        task="Test corruption",
        completed=[],
        pending=[],
        active_issue=5857,
        active_pr=5857,
        checkpoint_in_repo=False,
    )
    assert checkpoint["created"] is True

    checkpoint_path = Path(checkpoint["path"])
    checkpoint_path.write_bytes(b"not a valid gzip checkpoint")
    monkeypatch.setattr(guard, "CONTINUATION_PATH", tmp_path / "NEXT_CONTINUATION_PROMPT.md")

    resume = guard.resume_report(tmp_path, runtime_dir, checkpoint["checkpoint_id"])

    assert resume["resumed"] is False
    assert resume["reason"] == "checkpoint_failed_validation"


def test_reindex_failure_has_missing_safe_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = tmp_path / "session-store.db"
    store.write_bytes(b"")
    monkeypatch.setattr(guard, "find_local_session_store", lambda _repo: store)
    monkeypatch.setattr(
        guard.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, "", "reindex failed"),
    )

    result = guard.reindex_session_store(tmp_path, tmp_path / "runtime")

    assert result["reindexed"] is False
    assert result["reason"] == "reindex_failed"


def test_closeout_propagates_required_operation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    monkeypatch.setattr(guard, "HANDOFF_PATH", tmp_path / ".codex" / "session_handoff.json")
    monkeypatch.setattr(
        guard, "CONTINUATION_PATH", tmp_path / ".codex" / "NEXT_CONTINUATION_PROMPT.md"
    )
    monkeypatch.setattr(
        guard,
        "create_checkpoint",
        lambda *_args, **_kwargs: {"created": False, "reason": "checkpoint_failed"},
    )

    exit_code = guard.main(
        [
            "closeout",
            "--no-bundle",
            "--no-reindex",
            "--runtime-dir",
            str(tmp_path / "runtime"),
        ]
    )

    assert exit_code == 1


def test_supported_and_unsupported_session_sync_settings_are_distinct() -> None:
    settings = (guard.ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")

    assert '"github.copilot.chat.localIndex.enabled": true' in settings
    assert "chat.sessionSync.enabled" not in settings
