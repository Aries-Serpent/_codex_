"""Tests for git commit tagging utilities."""

# ChatGPT Codex tailored Commented Task Prompt:
# - Task: Expand or harden the git_tag.current_commit test-suite when the
#   underlying git_tag implementation evolves.
# - Goals for Codex:
#   1. Ensure tests cover happy-path (git returns a commit), various error
#      modes (non-git repo, missing git binary, subprocess failures), and both
#      import styles used in the codebase:
#        - module-style: from codex_ml.tracking import git_tag; git_tag.current_commit()
#        - function-style: from codex_ml.tracking.git_tag import current_commit; current_commit()
#   2. Keep tests backward compatible with implementations that return either
#      bytes or str from subprocess.check_output.
#   3. Use monkeypatch fixture correctly (including `raising=False` where the
#      target attribute may not exist) and provide clear assertions/messages.
#   4. If codex_ml.tracking.git_tag.current_commit is not importable, skip the
#      direct-function tests while still running module-style tests if possible.
#
# Expandable items:
# - Add parametrized cases for various encodings and newline styles.
# - Add property-based tests (hypothesis) to validate robustness against
#   unexpected subprocess outputs (optional).

import subprocess
import pytest


def test_current_commit_happy_path(monkeypatch):
    """
    Module-style import happy path:
    - Replace subprocess.check_output with a fake that returns a commit string/bytes.
    - Ensure git_tag.current_commit() returns the decoded commit SHA without newline.
    """
    from codex_ml.tracking import git_tag

    def fake_check_output(cmd, **kw):
        # Typical invocation: ["git", "rev-parse", "HEAD"]
        assert isinstance(cmd, (list, tuple)), "git invocation should be a list/tuple"
        assert "git" in cmd[0]
        # Return bytes to emulate actual subprocess behavior
        return b"abc123def456\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert git_tag.current_commit() == "abc123def456"


def test_current_commit_happy_path_direct(monkeypatch):
    """
    Direct-function import happy path:
    - Skip the test if the direct function import is not available.
    """
    git_module = pytest.importorskip("codex_ml.tracking.git_tag")
    current_commit = git_module.current_commit

    def fake_check_output(cmd, **kw):
        assert isinstance(cmd, (list, tuple)), "git invocation should be a list/tuple"
        assert "git" in cmd[0]
        return b"abc123def456\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert current_commit() == "abc123def456"


def test_current_commit_error_returns_none(monkeypatch):
    """
    Module-style: when subprocess.check_output raises CalledProcessError, the
    function should return None.
    """
    from codex_ml.tracking import git_tag

    def boom(*a, **k):
        raise subprocess.CalledProcessError(128, cmd=["git", "rev-parse", "HEAD"])

    monkeypatch.setattr(subprocess, "check_output", boom)
    assert git_tag.current_commit() is None


def test_current_commit_error_returns_none_direct(monkeypatch):
    """
    Direct-function: skip if direct import not available. Ensure None is returned
    when subprocess.check_output raises CalledProcessError.
    """
    git_module = pytest.importorskip("codex_ml.tracking.git_tag")
    current_commit = git_module.current_commit

    def boom(*a, **k):
        raise subprocess.CalledProcessError(128, cmd=["git", "rev-parse", "HEAD"])

    # Use raising=False to avoid monkeypatch complaining in environments where
    # check_output might be a different object or missing (defensive).
    monkeypatch.setattr(subprocess, "check_output", boom, raising=False)
    assert current_commit() is None


@pytest.mark.parametrize(
    "stderr_msg", ["fatal: not a git repository", "git: command not found"]
)
def test_handles_missing_repo_or_git(monkeypatch, stderr_msg):
    """
    Module-style: When git is missing or the directory is not a git repo,
    CalledProcessError with an informative stderr should cause current_commit()
    to return None.
    """
    from codex_ml.tracking import git_tag

    class Err(subprocess.CalledProcessError):
        def __init__(self):
            # CalledProcessError signature: returncode, cmd, output=None, stderr=None
            super().__init__(2, ["git"], output=b"", stderr=stderr_msg.encode())

    # Use a lambda that raises Err to mimic subprocess.check_output behavior.
    monkeypatch.setattr(
        subprocess,
        "check_output",
        lambda *a, **k: (_ for _ in ()).throw(Err()),
    )
    assert git_tag.current_commit() is None


@pytest.mark.parametrize(
    "stderr_msg", ["fatal: not a git repository", "git: command not found"]
)
def test_current_commit_handles_missing_repo_or_git_direct(monkeypatch, stderr_msg):
    """
    Direct-function test for missing git/repo scenarios. Skips if direct import
    isn't available.
    """
    git_module = pytest.importorskip("codex_ml.tracking.git_tag")
    current_commit = git_module.current_commit

    class Err(subprocess.CalledProcessError):
        def __init__(self) -> None:  # pragma: no cover - trivial constructor
            super().__init__(2, ["git"], output=b"", stderr=stderr_msg.encode())

    def boom(*a, **k):  # pragma: no cover - trivial raiser
        raise Err()

    # Use raising=False to be tolerant of attribute presence/absence in different envs.
    monkeypatch.setattr(subprocess, "check_output", boom, raising=False)
    assert current_commit() is None
