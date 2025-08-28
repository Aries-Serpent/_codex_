# BEGIN: CODEX_TEST_GIT_TAG
import subprocess

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
# END: CODEX_TEST_GIT_TAG
