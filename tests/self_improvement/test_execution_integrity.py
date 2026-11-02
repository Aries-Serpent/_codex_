"""Synthetic local candidate regressions; none are production observations."""

from __future__ import annotations

import hashlib
import multiprocessing
import subprocess
import sys
from pathlib import Path

import pytest

from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.isolated_execution import IdempotencyLedger, IsolatedExecutor

PATCH = """diff --git a/src/value.py b/src/value.py
new file mode 100644
--- /dev/null
+++ b/src/value.py
@@ -0,0 +1 @@
+value = 2
"""


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "fixture"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "fixture@example.test"], check=True
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "old.py").write_text("value = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_value.py").write_text(
        "import unittest,runpy\nclass Value(unittest.TestCase):\n"
        " def test_repair(self): self.assertEqual(runpy.run_path('src/value.py')['value'],2)\n"
    )
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "synthetic baseline"], check=True)
    return tmp_path


def execute(repo, **kwargs):
    executor = IsolatedExecutor(
        repo,
        authority=AuthorityEnvelope(require_human_approval=False),
        ledger=IdempotencyLedger(repo / ".codex" / "claims.jsonl"),
    )
    for name in ("gates",):
        if name in kwargs:
            setattr(executor, name, kwargs.pop(name))
    return executor.execute(
        event_id="fixture",
        patch_content=PATCH,
        files=kwargs.pop("files", ("src/value.py",)),
        diff_lines=1,
        **kwargs,
    )


def test_undeclared_path_rejected_before_gates(repo):
    outcome = execute(repo, files=("src/old.py",))
    assert outcome.status == "rejected"
    assert "paths differ" in outcome.reason
    assert not outcome.gate_logs
    assert not (repo / "src/value.py").exists()
    assert list((repo / ".codex/improvement/artifacts").rglob("proposal.patch"))


@pytest.mark.parametrize(
    "gates",
    [
        (),
        (("compile", (sys.executable, "-V")),),
        (("unknown", (sys.executable, "-V")),),
        (({}, ("python",)),),
    ],
)
def test_invalid_required_gates_never_verify(repo, gates):
    assert execute(repo, gates=gates).status == "rejected"


def test_hash_mismatch_rejected(repo):
    outcome = execute(repo, patch_hash="0" * 64)
    assert outcome.reason == "patch hash mismatch"
    assert list(Path(outcome.artifact_path).glob("*-identity-error.json"))
    assert (Path(outcome.artifact_path) / "proposal.patch").read_text() == PATCH


def test_symbolic_base_rejected(repo):
    assert execute(repo, base_sha="HEAD").status == "rejected"


def test_supported_interpreter_and_retained_patch(repo, monkeypatch):
    monkeypatch.setattr("os.environ", {})
    digest = hashlib.sha256(PATCH.encode()).hexdigest()
    outcome = execute(repo, patch_hash=digest)
    assert outcome.status == "verified", outcome.reason
    assert outcome.patch_hash == digest
    assert len(outcome.base_sha) == 40
    assert all(log.command[0] == sys.executable for log in outcome.gate_logs)
    assert any(log.status == "failed" for log in outcome.baseline_gate_logs)
    for log in (*outcome.gate_logs, *outcome.baseline_gate_logs):
        assert hashlib.sha256(Path(log.output_path).read_bytes()).hexdigest() == log.output_hash
    assert (Path(outcome.artifact_path) / "proposal.patch").read_text() == PATCH


def test_launch_error_is_not_timeout(repo):
    outcome = execute(repo, gates=(("behavior", ("/nonexistent/fixture-interpreter",)),))
    assert outcome.status == "rejected"
    assert outcome.gate_logs[0].returncode == 127
    assert outcome.gate_logs[0].status == "launch_error"


def test_gate_cannot_change_candidate(repo):
    outcome = execute(
        repo,
        gates=(
            (
                "behavior",
                (
                    sys.executable,
                    "-c",
                    "from pathlib import Path; Path('src/old.py').write_text('changed')",
                ),
            ),
        ),
    )
    assert outcome.status == "rejected"
    assert "gates failed" in outcome.reason or "gate changed" in outcome.reason
    assert (repo / "src/old.py").read_text() == "value = 1\n"


def test_behavior_passing_before_repair_is_not_verification(repo):
    outcome = execute(repo, gates=(("behavior", (sys.executable, "-c", "pass")),))
    assert outcome.status == "rejected"
    assert outcome.reason == "no demonstrated failing baseline behavior"
    assert not (repo / "src/value.py").exists()


def test_gates_cannot_read_or_write_shared_source_metadata(repo):
    original_config = (repo / ".git/config").read_bytes()
    command = (
        "from pathlib import Path; import runpy\n"
        f"source=Path({str(repo)!r})\n"
        "for target,operation in [(source/'.git/config','read'),"
        "(source/'src/old.py','write')]:\n"
        " try:\n"
        "  target.read_bytes() if operation=='read' else target.write_text('unauthorized')\n"
        " except PermissionError: pass\n"
        " else: raise AssertionError('source access escaped confinement')\n"
        "assert runpy.run_path('src/value.py')['value']==2\n"
    )
    outcome = execute(repo, gates=(("behavior", (sys.executable, "-c", command)),))
    assert outcome.status == "verified", outcome.reason
    assert (repo / ".git/config").read_bytes() == original_config
    assert (repo / "src/old.py").read_text() == "value = 1\n"


def test_unsupported_confinement_is_explicit_error(repo, monkeypatch):
    monkeypatch.setattr("platform.machine", lambda: "unsupported-fixture")
    outcome = execute(repo)
    assert outcome.status == "error"
    assert "snapshot creation failed" in outcome.reason
    assert not (repo / "src/value.py").exists()


def test_gate_cannot_hide_content_change_in_private_index(repo):
    command = (
        "from pathlib import Path; import subprocess\n"
        "assert Path('src/value.py').read_text()=='value = 2\\n'\n"
        "subprocess.run(['git','update-index','--assume-unchanged','src/value.py'],check=True)\n"
        "Path('src/value.py').write_text('value = 99\\n')\n"
    )
    outcome = execute(repo, gates=(("behavior", (sys.executable, "-c", command)),))
    assert outcome.status == "rejected"
    assert "gates failed" in outcome.reason or "gate changed" in outcome.reason
    assert not (repo / "src/value.py").exists()


def test_restarted_breaker_blocks_proposal_selection(tmp_path):
    from types import SimpleNamespace

    from codex.cognitive_brain.evidence_store import EvidenceStore
    from codex.cognitive_brain.improvement_pipeline import ImprovementPipeline, SignalEvidence

    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, allow_synthetic=True)
    for index in range(3):
        store.record_outcome(
            event_id=f"failure-{index}",
            pattern_id="timeout",
            patch_hash="a" * 64,
            merged=True,
            outcome="regression",
            observation_id=f"synthetic-{index}",
            synthetic=True,
        )
    restarted = EvidenceStore(path, allow_synthetic=True)
    assert not restarted.pattern_enabled("timeout")
    match = SimpleNamespace(
        pattern_id="timeout", times_applied=3, success_rate=0.9, solutions=["TIMEOUT = 30"]
    )
    pipeline = ImprovementPipeline(
        repo="fixture/repo",
        ref="fixture",
        sha="b" * 40,
        brain_interface=SimpleNamespace(query_patterns=lambda symptoms: [match]),
        authority=AuthorityEnvelope(require_human_approval=False),
        evidence_store=restarted,
    )
    signal = SignalEvidence(
        source="ci_workflow",
        kind="ci_job_failure",
        measured_at="2026-11-01T00:00:00Z",
        availability="measured",
        summary="timeout",
        details={"files": ["src/value.py"]},
    )
    decision = pipeline.process_signal(signal)
    assert not decision.actionable
    assert decision.event.proposal is None


def _claim(path, start, results):
    ledger = IdempotencyLedger(Path(path))
    start.wait()
    results.put(ledger.claim("event", "a" * 64, "b" * 40))


def test_atomic_claim_and_restart(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    context = multiprocessing.get_context("spawn")
    start, results = context.Event(), context.Queue()
    path = tmp_path / "claims.jsonl"
    workers = [context.Process(target=_claim, args=(str(path), start, results)) for _ in range(2)]
    for worker in workers:
        worker.start()
    start.set()
    claims = [results.get(timeout=10) for _ in workers]
    for worker in workers:
        worker.join(timeout=10)
        assert worker.exitcode == 0
    assert sum(claim is not None for claim in claims) == 1
    assert IdempotencyLedger(path).claim("event", "a" * 64, "b" * 40) is None


@pytest.mark.parametrize("tail", ['{"event_id":"broken"}\n', "{", "[]\n"])
def test_corrupt_claim_ledger_is_explicit_and_preserved(tmp_path, tail):
    path = tmp_path / "claims.jsonl"
    path.write_text(tail)
    with pytest.raises(ValueError, match="invalid execution ledger"):
        IdempotencyLedger(path)
    assert path.read_text() == tail


def test_invalid_claim_identity_cannot_be_written(tmp_path):
    path = tmp_path / "claims.jsonl"
    ledger = IdempotencyLedger(path)
    with pytest.raises(ValueError):
        ledger.claim("event", "wrong-hash", "HEAD")
    assert path.read_text() == ""


@pytest.mark.parametrize("path", ["src/../outside", "src\\outside", "src//outside", "/outside"])
def test_noncanonical_authority_paths(path):
    assert AuthorityEnvelope().check_paths((path,))


@pytest.mark.parametrize(
    "record",
    [
        [],
        None,
        "failure",
        {"type": "failure", "timestamp": None},
        {"type": "failure", "timestamp": "2026-11-01"},
        {"type": "failure", "timestamp": "not-a-time"},
        {"type": "failure", "timestamp": "2026-11-01T00:00:00Z", "files": "src/value.py"},
    ],
)
def test_pda_adapter_rejects_invalid_records(record):
    from codex.cognitive_brain.improvement_pipeline import signal_from_pda_record

    with pytest.raises(ValueError):
        signal_from_pda_record(record)
