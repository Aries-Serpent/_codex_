"""Offline, real-process composition; caller review is not hosted authority."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.evidence_store import EvidenceStore
from codex.cognitive_brain.improvement_loop_runner import compose_local_improvement
from codex.cognitive_brain.improvement_pipeline import ImprovementPipeline
from codex.cognitive_brain.isolated_execution import IdempotencyLedger, IsolatedExecutor

TARGET = "src/repair.py"
BAD = "def bounded(value):\n    return min(value, 9)\n"
GOOD = "def bounded(value):\n    return max(0, min(value, 9))\n"
CHECKS = (
    ("negative", "assert bounded(-1) == 0"),
    ("boundary", "assert bounded(10) == 9"),
    ("regression", "assert bounded(3) == 3"),
)
GATES = tuple(
    (
        "regression" if kind == "negative" else ("tests" if kind == "boundary" else "behavior"),
        (sys.executable, "-c", f"from src.repair import bounded; {assertion}"),
    )
    for kind, assertion in CHECKS
)


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True).stdout


@pytest.fixture
def local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(os, "environ", {})
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "offline fixture")
    (repo / "src").mkdir()
    (repo / TARGET).write_text(BAD)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "disposable fixture base")
    sha = git(repo, "rev-parse", "HEAD").decode().strip()
    (repo / TARGET).write_text(GOOD)
    patch = git(repo, "diff", "--", TARGET)
    (repo / TARGET).write_text(BAD)
    patterns = repo / ".codex" / "cognitive_brain"
    patterns.mkdir(parents=True)
    (patterns / "pattern_learning_store.json").write_text(
        json.dumps(
            {
                "patterns": {
                    "bounded": {
                        "id": "local-boundary",
                        "category": "repair",
                        "symptoms": ["negative value boundary regression"],
                        "solutions": ["Advisory template; NOT a unified diff"],
                        "success_rate": 0.8,
                        "times_applied": 3,
                    }
                }
            }
        )
    )
    authority = AuthorityEnvelope()
    store = EvidenceStore(repo / ".codex" / "improvement" / "evidence.jsonl")
    pipeline = ImprovementPipeline(
        repo="offline/fixture",
        ref="refs/heads/fixture",
        sha=sha,
        brain_interface=AgentBrainInterface(
            agent_id="local-composition-fixture", repo_root=repo, auto_register=False
        ),
        authority=authority,
        evidence_store=store,
    )
    work = repo / "disposable-work"
    work.mkdir()
    executor = IsolatedExecutor(
        repo,
        authority=authority,
        ledger=IdempotencyLedger(repo / ".codex" / "improvement" / "ledger.jsonl"),
        work_root=work,
        gates=GATES,
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {
        "repo": pipeline.repo,
        "sha": sha,
        "author": "fixture-author",
        "signal": {
            "source": "pda_failure_log",
            "kind": "ci_job_failure",
            "measured_at": now,
            "availability": "measured",
            "summary": "negative value boundary regression",
            "details": {"files": [TARGET], "baseline_metric": 1},
        },
        "brief": {
            "module": TARGET,
            "hypothesis": "Clamp negative values without changing upper bounds",
            "baseline_metric": 1,
            "expected_metric": 0,
            "confidence": 0.8,
            "risk": "low",
            "acceptance_criteria": ["Negative, boundary and regression checks pass"],
            "verification_commands": [list(command) for _, command in GATES],
            "lane_id": "local-fixture",
            "write_paths": [TARGET],
            "dependencies": [],
            "budget_seconds": 30,
            "stop_condition": "One local attempt; at most three correction cycles",
            "falsification": "Any boundary or regression check fails",
        },
    }
    return repo, pipeline, executor, record, patch


def compose(local, **kwargs):
    _, pipeline, executor, record, patch = local
    return compose_local_improvement(
        record,
        pipeline=pipeline,
        executor=executor,
        patch_bytes=patch,
        patch_hash=hashlib.sha256(patch).hexdigest(),
        base_sha=pipeline.sha,
        **kwargs,
    )


def reviewed(local):
    """Independently apply exact bytes, measure checks, restore the fixture source."""
    repo, _, _, record, patch = local
    result = compose(local, human_approved=True)
    event = result["event"]
    binding = {
        "base_sha": record["sha"],
        "proposal_id": result["proposal"]["proposal_id"],
        "patch_hash": event["proposal"]["patch_hash"],
        "evidence_digest": result["evidence_digest"],
    }
    subprocess.run(["git", "apply", "-"], cwd=repo, input=patch, check=True)
    checks = []
    try:
        for (kind, _), (_, command) in zip(CHECKS, GATES, strict=True):
            process = subprocess.run(command, cwd=repo, capture_output=True, check=False)
            assert process.returncode == 0, process.stderr
            checks.append(
                {
                    **binding,
                    "name": kind,
                    "kind": kind,
                    "completed": True,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "command": list(command),
                    "returncode": process.returncode,
                    "evidence_ref": "sha256:" + hashlib.sha256(process.stdout).hexdigest(),
                }
            )
    finally:
        (repo / TARGET).write_text(BAD)
        # Python subprocess imports are fixture evidence, not source artifacts.
        import shutil

        shutil.rmtree(repo / "src" / "__pycache__", ignore_errors=True)
    record["validation"] = {
        **binding,
        "author": record["author"],
        "observer": "independent-local-fixture",
        "required_checks": ["negative", "boundary", "regression"],
        "checks": checks,
    }
    record["local_review"] = {
        **binding,
        "event_id": event["event_id"],
        "files": event["proposal"]["files"],
        "objective": result["review"]["objective"],
        "author": record["author"],
        "observer": record["validation"]["observer"],
        "decision": "pass",
        "timestamp": checks[-1]["timestamp"],
        "answers": {
            question: "Exact diff only clamps negative input; independent boundary checks pass."
            for question in result["review"]["questions"]
        },
    }
    return result


def fixture_verifier(local):
    """Trusted test-only injection authenticates exact fixture review bindings."""
    _, pipeline, _, record, patch = local
    expected = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def verify(binding):
        return (
            binding["synthetic"] is True
            and binding["canonical_record"] == expected
            and binding["record_digest"] == hashlib.sha256(expected).hexdigest()
            and binding["evidence_digest"] == record["local_review"]["evidence_digest"]
            and binding["author"] == "fixture-author"
            and binding["observer"] == "independent-local-fixture"
            and binding["base_sha"] == pipeline.sha
            and binding["patch_hash"] == hashlib.sha256(patch).hexdigest()
            and binding["event_id"] == record["local_review"]["event_id"]
        )

    return verify


def test_default_is_read_only_and_binds_actual_diff(local):
    _, pipeline, _, _, patch = local
    result = reviewed(local)
    before = deepcopy(local[3])
    prepared = compose(local, human_approved=True)
    assert prepared["task_review_supplied"]
    assert not prepared["task_review_passed"]
    assert prepared["review_scope"] == "unverified-human-review"
    assert prepared["status"] == "ready-for-human-review"
    assert not prepared["execution_authorized"]
    assert not pipeline.evidence_store.path.exists()
    assert local[3] == before
    proposal = result["event"]["proposal"]
    assert proposal["patch_hash"] == hashlib.sha256(patch).hexdigest()
    assert proposal["files"] == [TARGET]
    assert proposal["diff_lines"] == 2
    assert (
        proposal["patch_hash"]
        != hashlib.sha256(b"Advisory template; NOT a unified diff").hexdigest()
    )


def test_real_process_attempt_is_durable_partial_handoff_and_no_replay(local):
    repo, pipeline, _, _, patch = local
    reviewed(local)
    before = git(repo, "diff")
    verifier = fixture_verifier(local)
    result = compose(
        local,
        human_approved=True,
        execute_authorized=True,
        synthetic=True,
        review_verifier=verifier,
    )
    assert result["status"] == "verified", result
    handoff = result["handoff"]
    assert handoff["patch_hash"] == hashlib.sha256(patch).hexdigest()
    assert handoff["base_sha"] == pipeline.sha
    assert handoff["attempt_id"]
    artifact = Path(handoff["artifact_path"])
    assert (artifact / "proposal.patch").read_bytes() == patch
    assert handoff["artifact_hash"] and handoff["candidate_tree_hash"]
    assert any(gate["returncode"] > 0 for gate in handoff["baseline_gate_logs"])
    assert all(gate["returncode"] == 0 for gate in handoff["gate_logs"])
    assert handoff["required_gates"] == [name for name, _ in GATES]
    assert result["evaluation"]["verdict"] == "partial"
    assert result["evaluation"]["links"]["gates"]
    assert result["evaluation"]["missing"] == ("pr", "post_merge_measurement", "confidence_update")
    assert not result["integration_authorized"]
    assert not handoff["learning_performed"]
    assert handoff["synthetic"] and result["review_scope"] == "synthetic-fixture"
    execution = result["execution"]
    assert execution == pipeline.evidence_store.audit_trail(handoff["event_id"])[1]["payload"]
    assert execution["event_id"] == handoff["event_id"]
    assert execution["base_sha"] == handoff["base_sha"]
    assert execution["patch_hash"] == handoff["patch_hash"]
    assert execution["attempt_id"] == handoff["attempt_id"]
    assert execution["artifact_path"] == handoff["artifact_path"]
    assert execution["pattern_id"] == "local-boundary"
    assert execution["synthetic"] is True
    assert git(repo, "diff") == before
    assert (repo / TARGET).read_text() == BAD
    journal = pipeline.evidence_store.path.read_bytes()
    reloaded = EvidenceStore(pipeline.evidence_store.path)
    pipeline.evidence_store = reloaded
    replay = compose(
        local,
        human_approved=True,
        execute_authorized=True,
        synthetic=True,
        review_verifier=verifier,
    )
    assert replay["status"] == "duplicate"
    assert reloaded.path.read_bytes() == journal
    assert [r["kind"] for r in reloaded.audit_trail()] == ["event", "execution"]
    assert not list((repo / "disposable-work").iterdir())


@pytest.mark.parametrize("scenario", ["text", "mode-only", "hash", "base"])
def test_malformed_noop_and_identity_fail_closed(local, scenario):
    _, pipeline, _, record, patch = local
    if scenario == "text":
        patch = b"Template text is not a patch\n"
    elif scenario == "mode-only":
        patch = b"diff --git a/src/repair.py b/src/repair.py\nold mode 100644\nnew mode 100755\n"
    digest = hashlib.sha256(patch).hexdigest()
    with pytest.raises(ValueError):
        compose_local_improvement(
            record,
            pipeline=pipeline,
            patch_bytes=patch,
            patch_hash="0" * 64 if scenario == "hash" else digest,
            base_sha="0" * 40 if scenario == "base" else pipeline.sha,
            execute_authorized=True,
            human_approved=True,
        )
    assert not pipeline.evidence_store.path.exists()


@pytest.mark.parametrize(
    "scenario",
    ["denied", "approval", "review", "stale", "review-hash", "disabled", "gates", "cycle"],
)
def test_denied_stale_unreviewed_and_ineligible_never_execute(local, scenario, monkeypatch):
    _, pipeline, _, record, _ = local
    reviewed(local)
    if scenario == "denied":
        record["brief"]["write_paths"] = ["tests"]
    elif scenario == "review":
        record["local_review"]["answers"] = {}
    elif scenario == "stale":
        record["signal"]["measured_at"] = "2020-01-01T00:00:00Z"
    elif scenario == "review-hash":
        record["local_review"]["patch_hash"] = "0" * 64
    elif scenario == "disabled":
        monkeypatch.setattr(EvidenceStore, "pattern_enabled", lambda self, pattern_id: False)
    elif scenario == "gates":
        local[2].gates = (("behavior", (sys.executable, "-c", "assert False")),)
    elif scenario == "cycle":
        record["correction_cycle"] = 4
    if scenario == "cycle":
        with pytest.raises(ValueError):
            compose(local, human_approved=True, execute_authorized=True)
    else:
        result = compose(
            local,
            human_approved=scenario != "approval",
            execute_authorized=True,
            synthetic=True,
            review_verifier=fixture_verifier(local),
        )
        assert not result["execution_authorized"]
    assert not pipeline.evidence_store.path.exists()


@pytest.mark.parametrize("verification", ["absent", "false", "truthy", "exception"])
def test_trusted_verifier_required_exact_true_and_fail_closed(local, verification):
    reviewed(local)
    calls = []

    def verify(binding):
        calls.append(binding)
        with pytest.raises(TypeError):
            binding["author"] = "forged"
        assert isinstance(binding["canonical_record"], bytes)
        if verification == "exception":
            raise RuntimeError("unavailable trusted review source")
        return 1 if verification == "truthy" else False

    result = compose(
        local,
        human_approved=True,
        execute_authorized=True,
        review_verifier=None if verification == "absent" else verify,
    )
    assert result["status"] == "blocked"
    assert result["task_review_supplied"]
    assert not result["task_review_passed"]
    assert not result["execution_authorized"]
    assert len(calls) == (0 if verification == "absent" else 1)
    assert not local[1].evidence_store.path.exists()


def test_production_clock_cannot_be_injected_and_fixture_never_authorizes(local):
    clock = datetime(2020, 1, 1, tzinfo=timezone.utc)
    local[3]["signal"]["measured_at"] = clock.isoformat()
    with pytest.raises(ValueError, match="clock injection"):
        compose(local, human_approved=True, observed_at=clock)
    production = compose(local, human_approved=True)
    assert "event" not in production
    fixture = compose(local, human_approved=True, observed_at=clock, synthetic=True)
    assert fixture["pipeline_actionable"] and fixture["synthetic"]
    assert not fixture["execution_authorized"]
    assert not fixture["handoff"]["learning_performed"]
    assert not local[1].evidence_store.path.exists()


def test_recorded_event_crash_requires_manual_reconciliation_not_retry(local, monkeypatch):
    reviewed(local)
    verifier = fixture_verifier(local)
    calls = []

    def crash(**kwargs):
        calls.append(kwargs)
        raise RuntimeError("interrupted before executor claim")

    monkeypatch.setattr(local[2], "execute", crash)
    with pytest.raises(RuntimeError, match="interrupted"):
        compose(
            local,
            human_approved=True,
            execute_authorized=True,
            synthetic=True,
            review_verifier=verifier,
        )
    assert [r["kind"] for r in local[1].evidence_store.audit_trail()] == ["event"]
    result = compose(
        local,
        human_approved=True,
        execute_authorized=True,
        synthetic=True,
        review_verifier=verifier,
    )
    assert result["status"] == "duplicate"
    assert result["manual_reconciliation_required"]
    assert "manual reconciliation" in result["reason"]
    assert len(calls) == 1
    assert not result["execution_authorized"]


def test_concurrent_event_recording_never_attempts_execution(local, monkeypatch):
    reviewed(local)
    monkeypatch.setattr(EvidenceStore, "record_event", lambda self, event: False)
    monkeypatch.setattr(
        local[2], "execute", lambda **kwargs: pytest.fail("duplicate must not execute")
    )
    result = compose(
        local,
        human_approved=True,
        execute_authorized=True,
        synthetic=True,
        review_verifier=fixture_verifier(local),
    )
    assert result["status"] == "duplicate"
    assert result["manual_reconciliation_required"]
    assert not result["execution_authorized"]
