import subprocess
import pytest


def test_current_commit_happy_path(monkeypatch):
    from codex_ml.tracking import git_tag

    def fake_check_output(cmd, **kw):
        assert "git" in cmd[0]
        return "abc123def456\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert git_tag.current_commit() == "abc123def456"


def test_current_commit_error_returns_none(monkeypatch):
    from codex_ml.tracking import git_tag

    def boom(*a, **k):
        raise subprocess.CalledProcessError(128, cmd=["git", "rev-parse", "HEAD"])

    monkeypatch.setattr(subprocess, "check_output", boom)
    assert git_tag.current_commit() is None


@pytest.mark.parametrize(
    "stderr_msg", ["fatal: not a git repository", "git: command not found"]
)
def test_handles_missing_repo_or_git(monkeypatch, stderr_msg):
    from codex_ml.tracking import git_tag

    class Err(subprocess.CalledProcessError):
        def __init__(self):
            super().__init__(2, ["git"], output=b"", stderr=stderr_msg.encode())

    monkeypatch.setattr(
        subprocess,
        "check_output",
        lambda *a, **k: (_ for _ in ()).throw(Err()),
    )
    assert git_tag.current_commit() is None

