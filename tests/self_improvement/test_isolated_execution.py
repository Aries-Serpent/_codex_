"""Stage 3 acceptance: isolated execution, gates, idempotency."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from codex.cognitive_brain.authority import AuthorityEnvelope, AuthorityLimits
from codex.cognitive_brain.isolated_execution import (
    IdempotencyLedger,
    IsolatedExecutor,
    scrub_environment,
)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    return tmp_path


def _executor(repo: Path, **kwargs) -> IsolatedExecutor:
    return IsolatedExecutor(
        repo,
        authority=AuthorityEnvelope(
            limits=AuthorityLimits(max_diff_lines=100, max_files=5),
            require_human_approval=False,
        ),
        ledger=IdempotencyLedger(repo / "ledger.jsonl"),
        **kwargs,
    )


PATCH_OK = """diff --git a/src/new.py b/src/new.py
new file mode 100644
index 0000000..4850b51
--- /dev/null
+++ b/src/new.py
@@ -0,0 +1 @@
+y = 2
"""

PATCH_BAD_PY = """diff --git a/src/bad.py b/src/bad.py
new file mode 100644
index 0000000..4850b51
--- /dev/null
+++ b/src/bad.py
@@ -0,0 +1 @@
+def broken(:
"""


def test_verified_patch_leaves_source_tree_unchanged(repo: Path) -> None:
    before = (repo / "src" / "ok.py").read_text()
    outcome = _executor(repo).execute(
        event_id="evt-ok",
        patch_content=PATCH_OK,
        files=("src/new.py",),
        diff_lines=1,
    )
    assert outcome.status == "verified", outcome.reason
    assert outcome.artifact_hash
    # Source tree untouched by the isolated run.
    assert (repo / "src" / "ok.py").read_text() == before
    assert not (repo / "src" / "new.py").exists()


def test_failing_gate_blocks_and_records(repo: Path) -> None:
    outcome = _executor(repo).execute(
        event_id="evt-bad",
        patch_content=PATCH_BAD_PY,
        files=("src/bad.py",),
        diff_lines=1,
    )
    assert outcome.status == "rejected"
    assert "gates failed" in outcome.reason
    assert not (repo / "src" / "bad.py").exists()


def test_disallowed_path_blocks_before_execution(repo: Path) -> None:
    patch = PATCH_OK.replace("src/new.py", ".github/workflows/evil.yml")
    outcome = _executor(repo).execute(
        event_id="evt-evil",
        patch_content=patch,
        files=(".github/workflows/evil.yml",),
        diff_lines=1,
    )
    assert outcome.status == "rejected"
    assert "denied" in outcome.reason


def test_oversized_patch_blocks(repo: Path) -> None:
    outcome = _executor(repo).execute(
        event_id="evt-big",
        patch_content=PATCH_OK,
        files=("src/new.py",),
        diff_lines=500,
    )
    assert outcome.status == "rejected"
    assert "diff too large" in outcome.reason


def test_duplicate_event_is_deduplicated(repo: Path) -> None:
    executor = _executor(repo)
    first = executor.execute(
        event_id="evt-dup", patch_content=PATCH_OK, files=("src/new.py",), diff_lines=1
    )
    second = executor.execute(
        event_id="evt-dup", patch_content=PATCH_OK, files=("src/new.py",), diff_lines=1
    )
    assert first.status == "verified"
    assert second.status == "duplicate"


def test_gate_timeout_blocks(repo: Path) -> None:
    executor = _executor(
        repo,
        gates=(("slow", ("python", "-c", "import time; time.sleep(5)")),),
    )
    executor.authority = AuthorityEnvelope(
        limits=AuthorityLimits(timeout_seconds=1), require_human_approval=False
    )
    outcome = executor.execute(
        event_id="evt-slow", patch_content=PATCH_OK, files=("src/new.py",), diff_lines=1
    )
    assert outcome.status == "rejected"


def test_scrub_environment_removes_secrets() -> None:
    env = scrub_environment({"GITHUB_TOKEN": "x", "PATH": "/usr/bin", "AWS_SECRET_ACCESS_KEY": "y"})
    assert "GITHUB_TOKEN" not in env
    assert "AWS_SECRET_ACCESS_KEY" not in env
    assert env["PATH"] == "/usr/bin"
    assert env["GIT_TERMINAL_PROMPT"] == "0"


def test_secret_inherited_env_blocks_execution(repo: Path, monkeypatch) -> None:
    monkeypatch.setenv("CUSTOM_LIVE_API_TOKEN", "secret-value")
    # The pre-execution authority check evaluates the raw environment, so
    # a live credential blocks even though the sandbox scrubber would
    # have removed it before any command ran.
    from codex.cognitive_brain import isolated_execution as ie

    monkeypatch.setattr(ie, "scrub_environment", lambda env=None: dict(os.environ))
    outcome = _executor(repo).execute(
        event_id="evt-secret", patch_content=PATCH_OK, files=("src/new.py",), diff_lines=1
    )
    assert outcome.status == "rejected"
    assert "CUSTOM_LIVE_API_TOKEN" in outcome.reason
