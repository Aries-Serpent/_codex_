"""Real local replay evidence is not authenticated review or release proof."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import threading
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pytest

from aries_serpent_core.skills import assurance
from aries_serpent_core.skills import retained_evidence as retained_module
from aries_serpent_core.skills.retained_evidence import read_retained_execution
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.isolated_execution import IdempotencyLedger, IsolatedExecutor

PATCH = """diff --git a/src/value.py b/src/value.py
--- a/src/value.py
+++ b/src/value.py
@@ -1,2 +1,4 @@
 def bounded(value):
-    return value
+    if type(value) is not int or not 0 <= value <= 10:
+        raise ValueError('outside domain')
+    return value * 2
"""

NEGATIVE = (
    "for value in (-1, 11, True, '1'):\n"
    " try: bounded(value)\n"
    " except ValueError: pass\n"
    " else: raise AssertionError('invalid input accepted')\n"
)
BOUNDARY = "assert bounded(0) == 0\nassert bounded(10) == 20\n"
REGRESSION = "for value in (1, 4, 9):\n assert bounded(value) == value * 2\n"


@pytest.fixture(scope="module")
def execution(tmp_path_factory):
    repo = tmp_path_factory.mktemp("retained-skill-replay")
    (repo / "src").mkdir()
    (repo / "src/value.py").write_text("def bounded(value):\n    return value\n")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "add", "src/value.py"], cwd=repo, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=local-fixture",
            "-c",
            "user.email=fixture@example.test",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-qm",
            "Disposable replay baseline",
        ],
        cwd=repo,
        check=True,
    )
    work = repo / "work"
    work.mkdir()
    gates = tuple(
        (
            name,
            (
                sys.executable,
                "-c",
                "import runpy\nbounded = runpy.run_path('src/value.py')['bounded']\n"
                + assertions
                + f"print({name!r}, 'substantive replay passed')\n",
            ),
        )
        for name, assertions in (
            ("behavior", NEGATIVE),
            ("tests", BOUNDARY),
            ("regression", REGRESSION),
        )
    )
    subject = IsolatedExecutor(
        repo,
        authority=AuthorityEnvelope(require_human_approval=False),
        ledger=IdempotencyLedger(repo / "claims.jsonl"),
        work_root=work,
        gates=gates,
    )
    # Keep even the existing executor's anonymous output files inside the fixture.
    previous = tempfile.tempdir
    tempfile.tempdir = str(work)
    try:
        outcome = subject.execute(
            event_id="local-retained-replay",
            patch_content=PATCH,
            files=("src/value.py",),
            diff_lines=4,
        )
    finally:
        tempfile.tempdir = previous
    assert outcome.status == "verified", outcome.reason
    return repo, subject, asdict(outcome)


def validation(repo, outcome):
    return {
        "author": "local-fixture-author",
        "observer": "local-process-observer-not-authenticated-reviewer",
        "base_sha": outcome["base_sha"],
        "required_checks": ["negative", "boundary", "regression"],
        "retained_evidence": {"repo_path": str(repo), "outcome": outcome},
        "checks": [
            {
                "name": kind,
                "kind": kind,
                "gate_name": log["name"],
                "command": list(log["command"]),
                "completed": True,
                "returncode": log["returncode"],
                "evidence_ref": log["output_path"],
                "base_sha": outcome["base_sha"],
                "timestamp": "2026-11-02T00:00:00Z",
            }
            for kind, log in zip(("negative", "boundary", "regression"), outcome["gate_logs"])
        ],
    }


def replay(repo, outcome):
    return {
        "retained_evidence": {"repo_path": str(repo), "outcome": outcome},
        "cases": [
            {
                "id": log["name"],
                "gate_name": log["name"],
                "command": list(log["command"]),
                "holdout": log["name"] == "tests",
                "expected": "pass",
                "baseline": "fail",
                "actual": "pass",
                "evidence_ref": log["output_path"],
                "human_interventions": 0,
                "runtime_seconds": log["duration_ms"] / 1000,
                # Fixture accounting only; not a measured hosted-service charge.
                "cost": 0,
            }
            for log in outcome["gate_logs"]
            if log["name"] in {"tests", "regression"}
        ],
    }


def test_real_retained_boundary_negative_regression_and_disjoint_holdout(execution):
    repo, _, outcome = execution
    evidence = read_retained_execution(repo, outcome)
    assert evidence["status"] == "pass", evidence
    assert evidence["authority_source"] == "retained-assertion-not-rederived"
    assert not evidence["execution_authorized"]
    assert all(log["returncode"] != 0 for log in evidence["baseline_gate_logs"])
    assert all(log["returncode"] == 0 for log in evidence["gate_logs"])
    assert assurance.adversarial_validation(validation(repo, outcome))["status"] == "pass"
    result = assurance.agent_regression_evaluation(replay(repo, outcome))
    assert result["status"] == "pass"
    assert not result["authenticated_review"] and not result["production_proof"]
    assert result["evidence_scope"] == "local-retained-execution"
    assert not assurance.rubber_duck_review({})["authenticated_review"]
    assert (repo / "src/value.py").read_text() == "def bounded(value):\n    return value\n"
    assert not list((repo / "work").iterdir())


@pytest.mark.parametrize("key", ["patch_hash", "base_sha", "attempt_id", "artifact_path"])
def test_outcome_identity_cannot_be_substituted(execution, key):
    repo, _, original = execution
    outcome = deepcopy(original)
    outcome[key] = "f" * len(outcome[key])
    assert read_retained_execution(repo, outcome)["status"] == "unknown"


@pytest.mark.parametrize(
    "target", ["patch", "identity", "manifest", "inventory", "output", "baseline_output"]
)
@pytest.mark.parametrize("damage", ["missing", "tampered", "symlink", "hardlink"])
def test_missing_tampered_and_aliased_files_never_pass(execution, target, damage):
    repo, _, outcome = execution
    directory = Path(outcome["artifact_path"])
    path = {
        "patch": directory / "proposal.patch",
        "identity": directory / f"{outcome['attempt_id']}-identity.json",
        "manifest": directory / f"{outcome['attempt_id']}.json",
        "inventory": directory / "inventory.json",
        "output": Path(outcome["gate_logs"][0]["output_path"]),
        "baseline_output": Path(outcome["baseline_gate_logs"][0]["output_path"]),
    }[target]
    original = path.read_bytes()
    alias = directory / "alias"
    try:
        path.unlink()
        if damage == "tampered":
            path.write_bytes(b"{}")
        elif damage in {"symlink", "hardlink"}:
            alias.write_bytes(original)
            if damage == "symlink":
                path.symlink_to(alias)
            else:
                path.hardlink_to(alias)
        assert read_retained_execution(repo, outcome)["status"] == "unknown"
        assert assurance.adversarial_validation(validation(repo, outcome))["status"] == "unknown"
    finally:
        path.unlink(missing_ok=True)
        alias.unlink(missing_ok=True)
        path.write_bytes(original)


@pytest.mark.parametrize("consumer", ["validation", "replay"])
def test_arbitrary_reference_and_gate_alias_are_not_retained_proof(execution, consumer):
    repo, _, outcome = execution
    if consumer == "validation":
        payload = validation(repo, outcome)
        evaluate = assurance.adversarial_validation
        observations = payload["checks"]
    else:
        payload = replay(repo, outcome)
        evaluate = assurance.agent_regression_evaluation
        observations = payload["cases"]
    observations[0]["evidence_ref"] = "arbitrary:not-proof"
    assert evaluate(payload)["status"] == "unknown"
    observations[0].update(
        evidence_ref=observations[1]["evidence_ref"],
        gate_name=observations[1]["gate_name"],
        command=observations[1]["command"],
    )
    assert evaluate(payload)["status"] == "unknown"


def test_before_after_and_scope_cannot_be_relabelled(execution):
    repo, _, outcome = execution
    payload = replay(repo, outcome)
    payload["cases"][0]["baseline"] = "pass"
    assert assurance.agent_regression_evaluation(payload)["status"] == "unknown"
    payload = validation(repo, outcome)
    payload["base_sha"] = "f" * 40
    assert assurance.adversarial_validation(payload)["status"] == "unknown"
    malformed = deepcopy(outcome)
    malformed["base_sha"] = None
    assert read_retained_execution(repo, malformed)["status"] == "unknown"


def test_missing_retained_mapping_and_unmapped_release_checks_are_unknown(execution):
    repo, _, outcome = execution
    payload = validation(repo, outcome)
    payload["retained_evidence"] = {}
    assert assurance.adversarial_validation(payload)["status"] == "unknown"
    result = assurance.pypi_release_assurance(validation(repo, outcome))
    assert result["status"] == "unknown"
    assert result["trusted_publisher"] == "unverified"
    assert not result["publication_authorized"]
    assert read_retained_execution(repo, outcome)["profile_mapping"] is None


def test_passed_handoff_cannot_substitute_an_unexecuted_path(execution):
    repo, _, outcome = execution
    contract = {
        "run_id": "retained-fixture",
        "base_sha": outcome["base_sha"],
        "lane_id": "C",
        "dependencies": [],
        "read_paths": ["src"],
        "write_paths": ["src"],
        "timeout_seconds": 60,
        "cost_budget": 0,
        "evidence_inputs": [outcome["artifact_path"]],
        "acceptance_criteria": ["bounded domain behavior"],
        "output_schema": {"type": "object"},
        "state": "pending",
    }
    observed = validation(repo, outcome)
    observed.update(run_id=contract["run_id"], lane_id=contract["lane_id"])
    for check in observed["checks"]:
        check.update(run_id=contract["run_id"], lane_id=contract["lane_id"])
    handoff = {
        "run_id": contract["run_id"],
        "base_sha": outcome["base_sha"],
        "lane_id": contract["lane_id"],
        "state": "passed",
        "changed_paths": ["src/value.py"],
        "validation": observed,
        "metrics": {},
        "risks": ["local process fixture, not authenticated reviewer proof"],
        "unresolved_questions": [],
        "artifact_refs": [outcome["artifact_path"]],
    }
    result = assurance.lane_contract_and_handoff({"contract": contract, "handoff": handoff})
    assert not result["authenticated_review"] and not result["production_proof"]
    handoff["changed_paths"] = ["src/unexecuted.py"]
    with pytest.raises(ValueError, match="retained patch"):
        assurance.lane_contract_and_handoff({"contract": contract, "handoff": handoff})


def test_denied_authority_and_cancellation_remain_non_success(execution):
    repo, subject, _ = execution
    denied = subject.execute(
        event_id="retained-denied",
        patch_content=PATCH,
        files=(".github/workflows/denied.yml",),
        diff_lines=4,
    )
    assert denied.status == "rejected"
    assert read_retained_execution(repo, denied)["status"] == "rejected"
    stop = threading.Event()
    stop.set()
    cancelled = subject.execute(
        event_id="retained-cancelled",
        patch_content=PATCH,
        files=("src/value.py",),
        diff_lines=4,
        cancellation_event=stop,
    )
    assert cancelled.status == "cancelled"
    assert read_retained_execution(repo, cancelled)["status"] == "cancelled"
    duplicate = subject.execute(
        event_id="retained-cancelled",
        patch_content=PATCH,
        files=("src/value.py",),
        diff_lines=4,
    )
    assert duplicate.status == "duplicate"
    assert read_retained_execution(repo, duplicate)["status"] == "unknown"


@pytest.mark.parametrize(
    "paths",
    [
        ["src/unrelated.py"],
        ["src/./value.py"],
        ["src/../src/value.py"],
        ["src/value.py", "src/value.py"],
    ],
)
def test_declared_scope_tampering_is_unknown(execution, paths):
    repo, _, original = execution
    directory = Path(original["artifact_path"])
    identity_path = directory / f"{original['attempt_id']}-identity.json"
    previous = identity_path.read_bytes()
    try:
        identity = json.loads(previous)
        identity["declared_files"] = paths
        identity_path.write_text(json.dumps(identity))
        assert read_retained_execution(repo, original)["status"] == "unknown"
    finally:
        identity_path.write_bytes(previous)
    assert original["patch_hash"] == hashlib.sha256(PATCH.encode()).hexdigest()


@pytest.mark.parametrize("damage", ["before-pass", "changed-command", "missing-gate"])
def test_internally_consistent_manifest_still_requires_real_replay_shape(execution, damage):
    repo, _, original = execution
    outcome = deepcopy(original)
    if damage == "before-pass":
        outcome["baseline_gate_logs"] = deepcopy(outcome["gate_logs"])
    elif damage == "changed-command":
        outcome["baseline_gate_logs"][0]["command"] = [sys.executable, "-c", "pass"]
    else:
        outcome["gate_logs"] = outcome["gate_logs"][:-1]
    path = Path(original["artifact_path"]) / f"{original['attempt_id']}.json"
    previous = path.read_bytes()
    try:
        path.write_text(json.dumps(outcome))
        assert read_retained_execution(repo, outcome)["status"] == "unknown"
    finally:
        path.write_bytes(previous)


def test_adapter_is_read_only_and_never_executes_or_retries(execution, monkeypatch):
    repo, subject, outcome = execution
    directory = Path(outcome["artifact_path"])
    before = {path.name: path.read_bytes() for path in directory.iterdir()}

    def forbidden(*args, **kwargs):
        pytest.fail("adapter must not launch commands or mutate execution claims")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subject, "execute", forbidden)
    monkeypatch.setattr(subject.ledger, "claim", forbidden)
    assert read_retained_execution(repo, outcome)["status"] == "pass"
    assert {path.name: path.read_bytes() for path in directory.iterdir()} == before


@pytest.mark.parametrize("target", ["patch", "manifest", "output"])
@pytest.mark.parametrize("damage", ["change-bytes", "rewrite-identical-bytes"])
def test_mutation_after_read_is_rechecked_after_parsing(execution, monkeypatch, target, damage):
    repo, _, outcome = execution
    directory = Path(outcome["artifact_path"])
    path = {
        "patch": directory / "proposal.patch",
        "manifest": directory / f"{outcome['attempt_id']}.json",
        "output": Path(outcome["baseline_gate_logs"][0]["output_path"]),
    }[target]
    original = path.read_bytes()
    parse = retained_module._patch_scope

    def mutate_after_read(patch):
        parsed = parse(patch)
        path.write_bytes(b"tampered" if damage == "change-bytes" else original)
        return parsed

    monkeypatch.setattr(retained_module, "_patch_scope", mutate_after_read)
    try:
        # Outputs are read later, so mutate them after the output was first read.
        if target == "output":
            monkeypatch.setattr(retained_module, "_patch_scope", parse)
            read = retained_module._read
            mutated = False

            def mutate_output(root, subject, observed=None):
                nonlocal mutated
                data = read(root, subject, observed)
                if subject == path and not mutated:
                    mutated = True
                    path.write_bytes(b"tampered" if damage == "change-bytes" else original)
                return data

            monkeypatch.setattr(retained_module, "_read", mutate_output)
        result = read_retained_execution(repo, outcome)
        assert result["status"] == "unknown", result
    finally:
        path.write_bytes(original)


def test_local_retained_evidence_does_not_infer_independence_from_labels(execution):
    repo, _, outcome = execution
    payload = validation(repo, outcome)
    payload["observer"] = payload["author"]
    result = assurance.adversarial_validation(payload)
    assert result["status"] == "pass"
    assert not result["authenticated_review"]
    assert "unauthenticated" in result["reason"]


def test_artifact_growth_is_rejected_with_a_bounded_read(tmp_path, monkeypatch):
    path = tmp_path / "artifact"
    path.write_bytes(b"small")
    open_path = Path.open
    reads = []
    observed = {}
    limit = 4 * 1024 * 1024

    @contextmanager
    def grow_before_open(subject, *args, **kwargs):
        if subject == path:
            with open_path(subject, "wb") as handle:
                handle.truncate(limit * 2)
        with open_path(subject, *args, **kwargs) as handle:

            class Reader:
                def read(self, size):
                    reads.append(size)
                    return handle.read(size)

            yield Reader()

    monkeypatch.setattr(Path, "open", grow_before_open)
    with pytest.raises(ValueError, match="exceeds size limit"):
        retained_module._read(tmp_path, path, observed)
    assert reads == [limit + 1]
    assert not observed


def test_patch_hunk_counts_include_header_like_content():
    patch = """diff --git a/doc.md b/doc.md
--- a/doc.md
+++ b/doc.md
@@ -1,2 +1,2 @@
----
-old
+++new
+---
diff --git a/other.md b/other.md
--- a/other.md
+++ b/other.md
@@ -1 +1 @@
-before
+after
"""
    paths, lines = retained_module._patch_scope(patch)
    assert paths == ["doc.md", "other.md"]
    assert lines == 6
    assert IsolatedExecutor._patch_inventory("2\t2\tdoc.md\0" "1\t1\tother.md\0") == (
        sorted(paths),
        lines,
    )


def test_retained_inventory_uses_executor_canonical_path_order(execution, monkeypatch):
    repo, _, outcome = execution
    directory = Path(outcome["artifact_path"])
    identity_path = directory / f"{outcome['attempt_id']}-identity.json"
    inventory_path = directory / "inventory.json"
    originals = {path: path.read_bytes() for path in (identity_path, inventory_path)}
    paths = ["src/z.py", "src/a.py"]
    monkeypatch.setattr(retained_module, "_patch_scope", lambda _: (paths, 4))
    try:
        identity = json.loads(originals[identity_path])
        identity["declared_files"] = paths
        identity_path.write_text(json.dumps(identity))
        inventory = json.loads(originals[inventory_path])
        inventory["files"] = sorted(paths)
        inventory_path.write_text(json.dumps(inventory))
        assert read_retained_execution(repo, outcome)["status"] == "pass"
        inventory["files"] = paths
        inventory_path.write_text(json.dumps(inventory))
        assert read_retained_execution(repo, outcome)["status"] == "unknown"
    finally:
        for path, data in originals.items():
            path.write_bytes(data)
