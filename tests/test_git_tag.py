# BEGIN: CODEX_TEST_GIT_TAG
"""Tests for git commit tagging utilities."""

# BEGIN: CODEX_TEST_GIT_TAG
import subprocess

import pytest

from codex_ml.tracking.git_tag import current_commit


def test_current_commit_success(monkeypatch):
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **k: "abc123\n", raising=False
    )
    assert current_commit() == "abc123"


def test_current_commit_failure(monkeypatch):
    def boom(*a, **k):
        raise subprocess.CalledProcessError(1, "git")

    monkeypatch.setattr(subprocess, "check_output", boom, raising=False)
    assert current_commit() is None


@pytest.mark.parametrize(
    "stderr_msg", ["fatal: not a git repository", "git: command not found"]
)
def test_current_commit_handles_missing_repo_or_git(monkeypatch, stderr_msg):
    class Err(subprocess.CalledProcessError):
        def __init__(self) -> None:  # pragma: no cover - trivial
            super().__init__(2, ["git"], output=b"", stderr=stderr_msg.encode())

    def boom(*a, **k):  # pragma: no cover - trivial
        raise Err()

    monkeypatch.setattr(subprocess, "check_output", boom, raising=False)
    assert current_commit() is None


# END: CODEX_TEST_GIT_TAG
