"""W2 acceptance: prove the Stage 2 -> 3 connection end-to-end offline.

A signal produced by :class:`ImprovementPipeline` (Stage 2) is fed
directly into :class:`IsolatedExecutor` (Stage 3): the actionable
proposal is applied inside a disposable git worktree, quality gates
run, authority policy is enforced, and idempotency is preserved —
all without network access or credentials, and without touching the
source tree.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope, AuthorityLimits
from codex.cognitive_brain.improvement_pipeline import (
    ImprovementPipeline,
    signal_from_pda_record,
)
from codex.cognitive_brain.isolated_execution import (
    IdempotencyLedger,
    IsolatedExecutor,
)

# Stage 2 fixture data: the pattern store matches the failure record's
# symptoms lexically so ``process_signal`` returns an actionable decision
# whose proposal targets the allowed path ``src/codex/ci_config.py``.
PATTERN_STORE = {
    "patterns": {
        "ci_timeout": {
            "id": "RP-019",
            "category": "ci_cd",
            "symptoms": [
                "ci job failure timeout",
                "workflow timeout minutes",
                "job timed out",
                "pytest",
            ],
            "solutions": ["jobs:\n  test:\n    timeout-minutes: 30"],
            "success_rate": 0.9,
            "times_applied": 3,
        }
    }
}

TARGET_FILE = "src/codex/ci_config.py"
FIX_CONTENT = 'TIMEOUT_MINUTES = 30\nBUDGET = {"jobs": 12}\n'


def _failure_record() -> dict:
    return {
        "type": "failure",
        "timestamp": "2026-10-19T00:00:00+00:00",
        "pattern_id": "RP-019",
        "workflow": "ci",
        "error_text": "job timed out after 360 minutes",
        "root_cause": "ci job failure timeout on workflow timeout minutes",
        "fix_template": FIX_CONTENT,
        "files": [TARGET_FILE],
        "verification_cmd": "nox -s tests",
    }


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Offline temp git repo with one committed file (Stage 3 pattern)."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    return tmp_path


def _make_new_file_diff(path: str, content: str) -> str:
    """Pure helper: render new-file *content* as an ``git apply``-able unified diff."""
    lines = content.splitlines()
    body = "\n".join("+" + line for line in lines)
    return (
        f"diff --git a/{path} b/{path}\n"
        "new file mode 100644\n"
        "index 0000000..0000000\n"
        "--- /dev/null\n"
        f"+++ b/{path}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
        f"{body}\n"
    )


def _brain(tmp_path: Path) -> AgentBrainInterface:
    store_dir = tmp_path / ".codex" / "cognitive_brain"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "pattern_learning_store.json").write_text(json.dumps(PATTERN_STORE))
    return AgentBrainInterface(agent_id="w2-test-agent", repo_root=tmp_path, auto_register=False)


def _pipeline(tmp_path: Path, authority: AuthorityEnvelope) -> ImprovementPipeline:
    return ImprovementPipeline(
        repo="Aries-Serpent/_codex_",
        ref="refs/heads/main",
        sha="cd47831318fe",  # pragma: allowlist secret
        brain_interface=_brain(tmp_path),
        authority=authority,
    )


def _executor(repo: Path, authority: AuthorityEnvelope, **kwargs: Any) -> IsolatedExecutor:
    return IsolatedExecutor(
        repo,
        authority=authority,
        ledger=IdempotencyLedger(repo / "ledger.jsonl"),
        **kwargs,
    )


def _run_pipeline(
    tmp_path: Path,
    authority: AuthorityEnvelope,
    record: Optional[dict] = None,
    *,
    human_approved: bool = False,
):
    signal = signal_from_pda_record(record or _failure_record())
    return _pipeline(tmp_path, authority).process_signal(signal, human_approved=human_approved)


def _git_status(repo: Path) -> str:
    """Porcelain status of the tracked source tree.

    Executor artifacts (``ledger.jsonl``) and the brain's ``.codex/``
    store are untracked byproducts of the run, not source-tree changes,
    so they are excluded from the cleanliness check.
    """
    out = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return "".join(
        line for line in out.splitlines(keepends=True) if ".codex" not in line and "ledger" not in line
    )


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Measure the action, not ambient CI secret-metadata variables.
    monkeypatch.setattr(os, "environ", {})


def test_actionable_proposal_executes_verified(repo: Path, tmp_path: Path) -> None:
    authority = AuthorityEnvelope(require_human_approval=True)
    decision = _run_pipeline(tmp_path, authority, human_approved=True)

    assert decision.actionable, decision.reason
    event = decision.event
    assert event.proposal is not None
    assert event.proposal.files == (TARGET_FILE,)

    patch = _make_new_file_diff(TARGET_FILE, FIX_CONTENT)
    before = (repo / "src" / "ok.py").read_text()

    outcome = _executor(repo, authority).execute(
        event_id=event.event_id,
        patch_content=patch,
        files=event.proposal.files,
        diff_lines=event.proposal.diff_lines,
        human_approved=True,
    )

    assert outcome.status == "verified", outcome.reason
    assert outcome.artifact_hash
    assert [log.returncode for log in outcome.gate_logs] == [0]
    # The patch applied only inside the disposable worktree.
    assert (repo / "src" / "ok.py").read_text() == before
    assert not (repo / TARGET_FILE).exists()
    assert _git_status(repo) == ""


def test_gate_failure_rejected_and_tree_unchanged(repo: Path, tmp_path: Path) -> None:
    authority = AuthorityEnvelope(require_human_approval=True)
    decision = _run_pipeline(tmp_path, authority, human_approved=True)
    assert decision.actionable, decision.reason
    event = decision.event
    assert event.proposal is not None

    # Same path as the proposal, but the content cannot compile.
    patch = _make_new_file_diff(TARGET_FILE, "def broken(:\n")
    before = (repo / "src" / "ok.py").read_text()

    outcome = _executor(repo, authority).execute(
        event_id=event.event_id,
        patch_content=patch,
        files=event.proposal.files,
        diff_lines=event.proposal.diff_lines,
        human_approved=True,
    )

    assert outcome.status == "rejected"
    assert "gates failed" in outcome.reason
    assert any(log.name == "compile" and log.returncode != 0 for log in outcome.gate_logs)
    assert (repo / "src" / "ok.py").read_text() == before
    assert not (repo / TARGET_FILE).exists()
    assert _git_status(repo) == ""


def test_denied_path_rejected_at_both_stages(repo: Path, tmp_path: Path) -> None:
    authority = AuthorityEnvelope(require_human_approval=True)
    record = _failure_record()
    record["files"] = [".github/workflows/x.yml"]

    # Stage 2 authority gate fails closed on the denied path.
    decision = _run_pipeline(tmp_path, authority, record, human_approved=True)
    assert not decision.actionable
    assert "authority denied" in decision.reason
    event = decision.event
    assert event.proposal is not None  # proposal exists but is not authorized

    # Even if the unauthorized proposal is pushed into Stage 3 anyway,
    # the executor's authority envelope rejects it before any worktree runs.
    patch = _make_new_file_diff(".github/workflows/x.yml", "on: push\n")
    outcome = _executor(repo, authority).execute(
        event_id=event.event_id,
        patch_content=patch,
        files=event.proposal.files,
        diff_lines=event.proposal.diff_lines,
        human_approved=True,
    )
    assert outcome.status == "rejected"
    assert outcome.authority is not None and not outcome.authority.authorized
    assert any("path denied by policy" in r for r in outcome.authority.reasons)
    assert not (repo / ".github" / "workflows" / "x.yml").exists()
    assert _git_status(repo) == ""


def test_oversized_proposal_rejected(repo: Path, tmp_path: Path) -> None:
    authority = AuthorityEnvelope(
        limits=AuthorityLimits(max_diff_lines=5),
        require_human_approval=False,
    )
    # diff_lines = 2 lines of content + 1 = 3 at the pipeline stage: authorized.
    decision = _run_pipeline(tmp_path, authority, human_approved=True)
    assert decision.actionable, decision.reason
    event = decision.event
    assert event.proposal is not None

    # The executed diff is far larger than the declared proposal: rejected.
    outcome = _executor(repo, authority).execute(
        event_id=event.event_id,
        patch_content=_make_new_file_diff(TARGET_FILE, FIX_CONTENT),
        files=event.proposal.files,
        diff_lines=500,
        human_approved=True,
    )
    assert outcome.status == "rejected"
    assert "diff too large" in outcome.reason
    assert not (repo / TARGET_FILE).exists()
    assert _git_status(repo) == ""


def test_same_event_id_is_duplicate(repo: Path, tmp_path: Path) -> None:
    authority = AuthorityEnvelope(require_human_approval=True)
    decision = _run_pipeline(tmp_path, authority, human_approved=True)
    assert decision.actionable, decision.reason
    event = decision.event
    assert event.proposal is not None

    patch = _make_new_file_diff(TARGET_FILE, FIX_CONTENT)
    executor = _executor(repo, authority)
    first = executor.execute(
        event_id=event.event_id,
        patch_content=patch,
        files=event.proposal.files,
        diff_lines=event.proposal.diff_lines,
        human_approved=True,
    )
    second = executor.execute(
        event_id=event.event_id,
        patch_content=patch,
        files=event.proposal.files,
        diff_lines=event.proposal.diff_lines,
        human_approved=True,
    )
    assert first.status == "verified", first.reason
    assert second.status == "duplicate"
    assert not (repo / TARGET_FILE).exists()
    assert _git_status(repo) == ""


def test_human_approval_required_by_default(repo: Path, tmp_path: Path) -> None:
    # Default envelope: require_human_approval=True.
    authority = AuthorityEnvelope()
    decision = _run_pipeline(tmp_path, authority)  # no approval granted
    assert not decision.actionable
    assert "authority denied" in decision.reason
    assert "human approval" in decision.reason
