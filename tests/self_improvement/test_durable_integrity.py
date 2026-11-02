"""Bounded integrity regressions: durable replay, identity and honest proof."""

from __future__ import annotations

import fcntl
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Event
from typing import Any

import pytest

from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.improvement_evaluator import COMPLETE, UNVERIFIED, evaluate_event
from codex.cognitive_brain.outcome_tracking import OutcomeTracker, store_outcome_source
from tests.self_improvement.test_improvement_evaluator import _full_store
from tests.self_improvement.test_outcome_hook import _brain


def _outcome(store: EvidenceStore, outcome: str = "success", **kwargs: object) -> None:
    store.record_outcome(
        event_id="e1",
        pattern_id="RP-019",
        patch_hash="p",
        merged=True,
        outcome=outcome,
        synthetic=True,
        **kwargs,
    )


def test_breaker_reconstructs_failures_after_each_restart(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    for index in range(3):
        store = EvidenceStore(path, allow_synthetic=True)
        store.record_outcome(
            event_id=f"e{index}",
            pattern_id="RP-019",
            merged=True,
            outcome="rollback",
            synthetic=True,
        )
    recovered = EvidenceStore(path, allow_synthetic=True)
    assert not recovered.pattern_enabled("RP-019")
    assert "3 consecutive" in recovered.disable_reason("RP-019")
    assert len(recovered.audit_trail()) == 3


@pytest.mark.parametrize(
    "bad",
    [
        "{",
        "[]",
        "null",
        '{"schema_version":"1.0.0","kind":"outcome","recorded_at":null,"payload":{}}',
    ],
)
def test_corrupt_store_is_explicit_and_preserved(tmp_path: Path, bad: str) -> None:
    path = tmp_path / "evidence.jsonl"
    path.write_text(bad)
    with pytest.raises(EvidenceIntegrityError):
        EvidenceStore(path)
    assert path.read_text() == bad


def test_corruption_after_open_cannot_be_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path)
    store.record_event({"event_id": "e1"})
    path.write_text(path.read_text() + "{")
    original = path.read_bytes()
    with pytest.raises(EvidenceIntegrityError):
        store.record_event({"event_id": "e2"})
    assert path.read_bytes() == original


@pytest.mark.parametrize("kind", ["event", "outcome", "consumption", "qualification", "execution"])
def test_auxiliary_cannot_override_identity(tmp_path: Path, kind: str) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    with pytest.raises(EvidenceIntegrityError):
        store.record(kind, "e1", {"event_id": "other"})
    assert store.audit_trail() == []


def test_event_id_cannot_be_reused_for_different_payload(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event({"event_id": "e1", "sha": "one"})
    with pytest.raises(EvidenceIntegrityError):
        store.record_event({"event_id": "e1", "sha": "two"})
    assert len(store.audit_trail()) == 1


def test_audit_views_cannot_mutate_store(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    _outcome(store)
    store.audit_trail()[0]["payload"]["outcome"] = "rollback"
    record = store.outcome_for("e1")
    assert record is not None
    record["outcome"] = "regression"
    assert store.outcome_for("e1")["outcome"] == "success"


@pytest.mark.parametrize("identity", ["event_id", "pattern_id", "patch_hash"])
def test_wrong_outcome_identity_cannot_learn(tmp_path: Path, identity: str) -> None:
    brain = _brain(tmp_path)
    record = {
        "event_id": "e1",
        "pattern_id": "RP-019",
        "patch_hash": "p",
        "merged": True,
        "outcome": "success",
        "synthetic": True,
    }
    record[identity] = "wrong"
    tracker = OutcomeTracker(brain, lambda _: record, allow_synthetic=True)
    with pytest.raises(EvidenceIntegrityError, match="mismatch"):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert brain.get_pattern("RP-019").success_rate == 0.9


def test_outcome_cannot_disagree_with_original_event(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_event(
        {
            "event_id": "e1",
            "pattern": {"pattern_id": "other"},
            "proposal": {"patch_hash": "p"},
        }
    )
    with pytest.raises(EvidenceIntegrityError, match="pattern_id"):
        _outcome(store)
    assert store.outcome_for("e1") is None


def test_completed_consumption_survives_tracker_and_store_restart(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, allow_synthetic=True)
    _outcome(store)
    tracker = OutcomeTracker(_brain(tmp_path), store_outcome_source(store), allow_synthetic=True)
    first = tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert first is not None and first.new_rate > first.previous_rate
    restarted = OutcomeTracker(
        type(tracker.brain)(agent_id="test-agent", repo_root=tmp_path, auto_register=False),
        store_outcome_source(EvidenceStore(path, allow_synthetic=True)),
        allow_synthetic=True,
    )
    assert restarted.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p") is None
    assert restarted.brain.get_pattern("RP-019").success_rate == first.new_rate
    assert restarted.brain.get_pattern("RP-019").times_applied == 4


def test_later_regression_and_rollback_are_distinct_observations(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", allow_synthetic=True)
    tracker = OutcomeTracker(_brain(tmp_path), store_outcome_source(store), allow_synthetic=True)
    updates = []
    for index, outcome in enumerate(("success", "regression", "rollback", "regression")):
        _outcome(store, outcome, observation_id=f"measurement-{index}")
        updates.append(tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p"))
    assert all(update is not None for update in updates)
    assert updates[0].new_rate > 0.9
    assert updates[1].new_rate < updates[0].new_rate
    assert updates[2].new_rate < updates[1].new_rate
    assert updates[3].new_rate < updates[2].new_rate
    assert not EvidenceStore(store.path, allow_synthetic=True).pattern_enabled("RP-019")
    assert tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p") is None


def test_observation_id_cannot_be_rebound(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    _outcome(store, observation_id="measurement")
    with pytest.raises(EvidenceIntegrityError, match="observation identity"):
        _outcome(store, "rollback", observation_id="measurement")


def test_crash_window_remains_pending_and_never_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", allow_synthetic=True)
    _outcome(store)
    brain = _brain(tmp_path)
    tracker = OutcomeTracker(brain, store_outcome_source(store), allow_synthetic=True)

    def crash(self: EvidenceStore, _: object, **kwargs: object) -> None:
        raise OSError("simulated crash after brain persistence")

    monkeypatch.setattr(EvidenceStore, "complete_observation", crash)
    with pytest.raises(OSError):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    rate = brain.get_pattern("RP-019").success_rate
    recovered = OutcomeTracker(
        brain,
        store_outcome_source(EvidenceStore(store.path, allow_synthetic=True)),
        allow_synthetic=True,
    )
    with pytest.raises(EvidenceIntegrityError, match="pending reconciliation"):
        recovered.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert brain.get_pattern("RP-019").success_rate == rate


def test_swallowed_brain_write_failure_does_not_claim_completion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", allow_synthetic=True)
    _outcome(store)
    brain = _brain(tmp_path)
    monkeypatch.setattr(brain, "_save_patterns", lambda: None)
    tracker = OutcomeTracker(brain, store_outcome_source(store), allow_synthetic=True)
    with pytest.raises(EvidenceIntegrityError, match="persistence unconfirmed"):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert store.audit_trail()[-1]["payload"]["state"] == "pending"


def test_merged_boolean_is_not_production_proof(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.record_outcome(
        event_id="e1",
        pattern_id="RP-019",
        patch_hash="b" * 64,
        merged=True,
        outcome="success",
        observation_id="m1",
        merged_sha="a" * 40,
        provenance={"source": "github", "measured_at": "2026-10-31T00:00:00Z"},
    )
    brain = _brain(tmp_path)
    tracker = OutcomeTracker(brain, store_outcome_source(store))
    assert tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="b" * 64) is None
    assert brain.get_pattern("RP-019").success_rate == 0.9
    verified = OutcomeTracker(
        brain,
        store_outcome_source(store),
        measurement_verifier=lambda record: record["merged_sha"] == "a" * 40,
    )
    assert (
        verified.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="b" * 64)
        is not None
    )


@pytest.mark.parametrize(
    "gates",
    [
        [],
        [{"name": "tests", "returncode": 1}],
        [{"name": "tests"}],
        [{"name": "tests", "returncode": None}],
        [{"name": "tests", "returncode": False}],
        [{"name": "tests", "returncode": 0, "status": "unknown"}],
        [None],
    ],
)
def test_failed_empty_unknown_gates_never_complete(tmp_path: Path, gates: list) -> None:
    store = _full_store(tmp_path)
    store.record("execution", "e1", {"status": "verified", "patch_hash": "p", "gate_logs": gates})
    report = evaluate_event(store, "e1")
    assert report.verdict != COMPLETE
    assert not report.links["gates"]


@pytest.mark.parametrize("field", ["patch_hash", "merged_sha", "source_sha", "pattern_id"])
def test_evaluator_rejects_mismatched_available_identities(tmp_path: Path, field: str) -> None:
    store = _full_store(tmp_path)
    store.record("confidence", "e1", {field: "wrong"})
    assert evaluate_event(store, "e1").verdict == UNVERIFIED


@pytest.mark.parametrize("bad", [None, [], {"kind": "confidence", "payload": []}])
def test_evaluator_malformed_records_are_unverified(bad: object) -> None:
    class BadStore:
        def audit_trail(self, _: str) -> list:
            return [bad]

    assert evaluate_event(BadStore(), "e1").verdict == UNVERIFIED


def test_evaluator_production_claim_without_verifier_is_unknown(tmp_path: Path) -> None:
    store = _full_store(tmp_path)
    path = store.path
    records = [json.loads(line) for line in path.read_text().splitlines()]
    records = [record for record in records if record["kind"] != "qualification"]
    for record in records:
        if record["kind"] == "outcome":
            record["payload"]["synthetic"] = False
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    report = evaluate_event(EvidenceStore(path), "e1")
    assert report.verdict != COMPLETE
    assert report.proof_scope == "unknown"


def test_evaluation_of_empty_store_creates_no_lock_or_records(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    assert list(tmp_path.iterdir()) == []
    assert evaluate_event(store, "e1").verdict == UNVERIFIED
    assert list(tmp_path.iterdir()) == []


def test_direct_source_replay_never_substitutes_newer_observation(tmp_path: Path) -> None:
    brain = _brain(tmp_path)
    record = {
        "event_id": "e1",
        "pattern_id": "RP-019",
        "patch_hash": "p",
        "merged": True,
        "outcome": "success",
        "synthetic": True,
        "observation_id": "first",
    }
    tracker = OutcomeTracker(brain, lambda _: record, allow_synthetic=True)
    assert tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p") is not None
    _outcome(tracker.evidence_store, "rollback", observation_id="second")
    rate = brain.get_pattern("RP-019").success_rate
    assert tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p") is None
    assert brain.get_pattern("RP-019").success_rate == rate
    second = tracker.evidence_store.outcome_for("e1")
    assert second["outcome"] == "rollback"
    assert tracker.evidence_store.claim_observation(second)


def test_synthetic_learning_default_denies_before_pattern_write_or_lock(tmp_path: Path) -> None:
    brain = _brain(tmp_path)
    original = brain.pattern_store_path.read_bytes()
    record = {
        "event_id": "e1",
        "pattern_id": "RP-019",
        "patch_hash": "p",
        "merged": True,
        "outcome": "success",
        "synthetic": True,
    }
    tracker = OutcomeTracker(brain, lambda _: record, measurement_verifier=lambda _: True)
    with pytest.raises(EvidenceIntegrityError, match="fixture-only opt-in"):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert brain.pattern_store_path.read_bytes() == original
    assert brain.get_pattern("RP-019").success_rate == 0.9
    assert not brain.pattern_store_path.with_name(
        brain.pattern_store_path.name + ".outcome.lock"
    ).exists()
    assert tracker.evidence_store.audit_trail() == []


def test_synthetic_evaluation_requires_explicit_opt_in(tmp_path: Path) -> None:
    store = _full_store(tmp_path)
    assert evaluate_event(store, "e1").verdict != COMPLETE
    report = evaluate_event(store, "e1", allow_synthetic=True)
    assert report.verdict == COMPLETE and report.proof_scope == "synthetic"


class _SnapshotStore:
    def __init__(self, records: list[dict]) -> None:
        self.records = records

    def audit_trail(self, _: str) -> list[dict]:
        return self.records


@pytest.mark.parametrize(
    "defect",
    [
        "compile_only",
        "arbitrary_gate",
        "implicit_status",
        "missing_required",
        "duplicate_required",
        "duplicate_result",
        "missing_declaration",
    ],
)
def test_required_behavioral_gates_are_explicit_and_complete(tmp_path: Path, defect: str) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    event = records[0]["payload"]
    execution = next(r["payload"] for r in records if r["kind"] == "execution")
    if defect == "compile_only":
        event["proposal"]["required_gates"] = ["compile"]
        execution["required_gates"] = ["compile"]
        execution["gate_logs"] = execution["gate_logs"][:1]
    elif defect == "arbitrary_gate":
        event["proposal"]["required_gates"] = ["arbitrary"]
        execution["required_gates"] = ["arbitrary"]
        execution["gate_logs"][0]["name"] = "arbitrary"
    elif defect == "implicit_status":
        del execution["gate_logs"][1]["status"]
    elif defect == "missing_required":
        execution["gate_logs"] = execution["gate_logs"][:1]
    elif defect == "duplicate_required":
        execution["required_gates"] = ["compile", "tests", "tests"]
    elif defect == "duplicate_result":
        execution["gate_logs"].append(dict(execution["gate_logs"][1]))
    else:
        del event["proposal"]["required_gates"]
        del execution["required_gates"]
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict != COMPLETE
    assert not report.links["gates"]


@pytest.mark.parametrize("kind", ["execution", "pr", "outcome", "confidence"])
@pytest.mark.parametrize("identity", ["attempt_id", "base_sha", "patch_hash"])
def test_complete_chain_requires_matching_attempt_base_patch(
    tmp_path: Path,
    kind: str,
    identity: str,
) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    payload = next(r["payload"] for r in records if r["kind"] == kind)
    if kind == "outcome" and identity in ("attempt_id", "base_sha"):
        payload["details"][identity] = "wrong"
    else:
        payload[identity] = "wrong"
    assert evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True).verdict != COMPLETE


@pytest.mark.parametrize(
    "defect",
    [
        "pr_before_execution",
        "confidence_before_measurement",
        "measurement_before_merge",
        "merge_before_execution",
        "future_measurement",
        "reversed_envelope",
    ],
)
def test_complete_chain_requires_chronological_observations(tmp_path: Path, defect: str) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    pr = next(r for r in records if r["kind"] == "pr")
    outcome = next(r for r in records if r["kind"] == "outcome")
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    if defect == "pr_before_execution":
        records[1], records[2] = records[2], records[1]
    elif defect == "confidence_before_measurement":
        records[3], records[-1] = records[-1], records[3]
    elif defect == "measurement_before_merge":
        outcome["payload"]["provenance"]["measured_at"] = past
    elif defect == "merge_before_execution":
        pr["payload"]["merged_at"] = past
    elif defect == "future_measurement":
        outcome["payload"]["provenance"]["measured_at"] = future
    else:
        pr["recorded_at"] = past
    assert evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True).verdict == UNVERIFIED


@pytest.mark.parametrize("location", ["event_sha", "proposal_hash", "merge_sha"])
def test_short_sha_and_patch_identities_cannot_complete(tmp_path: Path, location: str) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    if location == "event_sha":
        records[0]["payload"]["sha"] = "abc"
    elif location == "proposal_hash":
        records[0]["payload"]["proposal"]["patch_hash"] = "p"
    else:
        for record in records:
            if "merged_sha" in record["payload"]:
                record["payload"]["merged_sha"] = "abc"
    assert evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True).verdict != COMPLETE


@pytest.mark.parametrize("identity", ["event_id", "patch_hash", "base_sha", "attempt_id"])
def test_available_gate_identities_must_match_attempt(tmp_path: Path, identity: str) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    execution = next(r["payload"] for r in records if r["kind"] == "execution")
    execution["gate_logs"][1][identity] = "wrong"
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict != COMPLETE and not report.links["gates"]


def test_gate_timestamps_cannot_precede_event(tmp_path: Path) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    execution = next(r["payload"] for r in records if r["kind"] == "execution")
    execution["gate_logs"][1]["started_at"] = "2020-01-01T00:00:00Z"
    execution["gate_logs"][1]["finished_at"] = "2020-01-01T00:01:00Z"
    assert evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True).verdict == UNVERIFIED


@pytest.mark.parametrize(
    "defect",
    [
        "denied",
        "absent",
        "truthy_string",
        "reasons",
        "wrong_event",
        "wrong_base",
    ],
)
def test_authority_is_affirmative_and_identity_bound(tmp_path: Path, defect: str) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    execution = next(r["payload"] for r in records if r["kind"] == "execution")
    if defect == "denied":
        execution["authority"]["authorized"] = False
    elif defect == "absent":
        del execution["authority"]
    elif defect == "truthy_string":
        execution["authority"]["authorized"] = "true"
    elif defect == "reasons":
        execution["authority"]["reasons"] = ["human approval absent"]
    elif defect == "wrong_event":
        execution["authority"]["idempotency_key"] = "another-event"
    else:
        execution["authority"]["base_sha"] = "f" * 40
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict != COMPLETE and not report.links["gates"]


@pytest.mark.parametrize(
    "defect",
    [
        "passing_baseline",
        "compile_failure_only",
        "absent",
        "timeout",
        "launch_error",
        "wrong_command",
        "wrong_base",
        "wrong_attempt",
        "duplicate_baseline",
    ],
)
def test_baseline_demonstrates_corresponding_behavioral_failure(
    tmp_path: Path,
    defect: str,
) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    execution = next(r["payload"] for r in records if r["kind"] == "execution")
    baselines = execution["baseline_gate_logs"]
    behavior = next(gate for gate in baselines if gate["name"] == "tests")
    if defect in ("passing_baseline", "compile_failure_only"):
        behavior["status"], behavior["returncode"] = "passed", 0
        if defect == "compile_failure_only":
            compile_gate = dict(execution["gate_logs"][0])
            compile_gate["status"], compile_gate["returncode"] = "failed", 1
            baselines.append(compile_gate)
    elif defect == "absent":
        del execution["baseline_gate_logs"]
    elif defect in ("timeout", "launch_error"):
        behavior["status"] = defect
    elif defect == "wrong_command":
        behavior["command"] = ["python", "-m", "different_tests"]
    elif defect == "wrong_base":
        behavior["base_sha"] = "f" * 40
    elif defect == "wrong_attempt":
        behavior["attempt_id"] = "another-attempt"
    else:
        baselines.append(dict(behavior))
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict != COMPLETE and not report.links["gates"]


def _test_measurement_verifier(record: dict) -> bool:
    """Offline verifier stub, not a claim of authenticated hosted execution."""
    return record.get("provenance", {}).get("source") == "trusted-verifier-fixture"


def _qualified_outcome(
    store: EvidenceStore,
    event_id: str,
    outcome: str,
    *,
    consume: bool = True,
) -> None:
    store.record_outcome(
        event_id=event_id,
        pattern_id="RP-019",
        patch_hash="b" * 64,
        merged=True,
        outcome=outcome,
        observation_id=event_id + "-measurement",
        merged_sha="c" * 40,
        provenance={
            "source": "trusted-verifier-fixture",
            "measured_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    if consume:
        record = store.outcome_for(event_id)
        assert record is not None
        assert store.claim_observation(record)
        store.complete_observation(record)


def test_synthetic_and_raw_success_cannot_reset_production_failure_streak(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    _qualified_outcome(store, "real1", "regression")
    store.record_outcome(
        event_id="synthetic", merged=True, outcome="success", pattern_id="RP-019", synthetic=True
    )
    _qualified_outcome(store, "real2", "regression")
    store.record_outcome(event_id="raw", merged=True, outcome="success", pattern_id="RP-019")
    _qualified_outcome(store, "real3", "rollback")
    assert not store.pattern_enabled("RP-019")
    recovered = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    assert not recovered.pattern_enabled("RP-019")
    assert "3 consecutive" in recovered.disable_reason("RP-019")
    assert len(recovered.audit_trail()) == 14
    assert sum(r["kind"] == "outcome" for r in recovered.audit_trail()) == 5


@pytest.mark.parametrize("synthetic", [False, True])
def test_unqualified_failures_cannot_disable_production_breaker(
    tmp_path: Path,
    synthetic: bool,
) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    for index in range(3):
        store.record_outcome(
            event_id=f"unqualified{index}",
            merged=True,
            outcome="rollback",
            pattern_id="RP-019",
            synthetic=synthetic,
        )
    assert not store.breaker("RP-019").disabled
    assert store.pattern_enabled("RP-019") is synthetic
    assert EvidenceStore(path).pattern_enabled("RP-019") is synthetic
    if synthetic:
        assert not EvidenceStore(path, allow_synthetic=True).pattern_enabled("RP-019")


def test_complete_shaped_proof_rejected_by_verifier_does_not_affect_breaker(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: False)
    for index in range(3):
        _qualified_outcome(store, f"rejected{index}", "rollback", consume=False)
    assert not store.breaker("RP-019").disabled
    assert not store.pattern_enabled("RP-019")
    assert "unknown eligibility" in store.disable_reason("RP-019")
    assert len(store.audit_trail()) == 3


def test_qualified_success_resets_production_streak(tmp_path: Path) -> None:
    store = EvidenceStore(
        tmp_path / "evidence.jsonl", measurement_verifier=_test_measurement_verifier
    )
    for index, outcome in enumerate(
        ("regression", "regression", "success", "rollback", "rollback")
    ):
        _qualified_outcome(store, f"trusted{index}", outcome)
    assert store.pattern_enabled("RP-019")
    _qualified_outcome(store, "trusted5", "regression")
    assert not store.pattern_enabled("RP-019")


def test_fixture_breaker_history_is_isolated_from_production_success(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(
        path, allow_synthetic=True, measurement_verifier=_test_measurement_verifier
    )
    for index in range(3):
        store.record_outcome(
            event_id=f"fixture{index}",
            merged=True,
            outcome="regression",
            pattern_id="RP-019",
            synthetic=True,
        )
        if index == 1:
            _qualified_outcome(store, "production-success", "success", consume=False)
    assert not store.pattern_enabled("RP-019")
    production = EvidenceStore(path)
    assert not production.breaker("RP-019").disabled
    assert not production.pattern_enabled("RP-019")
    assert "unknown eligibility" in production.disable_reason("RP-019")


def test_read_only_initialization_never_creates_missing_store_directories(tmp_path: Path) -> None:
    path = tmp_path / ".codex" / "improvement" / "evidence.jsonl"
    store = EvidenceStore(path)
    assert store.audit_trail() == []
    assert store.outcome_for("unknown") is None
    assert store.pattern_enabled("RP-019")
    assert evaluate_event(store, "unknown").verdict == UNVERIFIED
    assert not path.parent.exists()


def test_qualified_production_breaker_restarts_without_verifier_credentials(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    for index in range(3):
        _qualified_outcome(store, f"production{index}", "regression")
    recovered = EvidenceStore(path)
    assert recovered.measurement_verifier is None
    assert not recovered.pattern_enabled("RP-019")
    assert recovered.breaker("RP-019").disabled
    assert "3 consecutive" in recovered.disable_reason("RP-019")
    assert sum(r["kind"] == "qualification" for r in recovered.audit_trail()) == 3
    store.record_outcome(
        event_id="fixture-success",
        merged=True,
        outcome="success",
        pattern_id="RP-019",
        synthetic=True,
    )
    assert not EvidenceStore(path).pattern_enabled("RP-019")


def test_raw_merged_history_is_unknown_not_healthy_on_default_restart(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path)
    for index in range(3):
        _qualified_outcome(store, f"raw{index}", "regression", consume=False)
    recovered = EvidenceStore(path)
    assert not recovered.breaker("RP-019").disabled
    assert not recovered.pattern_enabled("RP-019")
    assert "unknown eligibility" in recovered.disable_reason("RP-019")
    assert recovered.stats()["unknown_patterns"] == ["RP-019"]


def test_caller_boolean_cannot_write_a_qualification_receipt(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    _qualified_outcome(store, "untrusted", "success", consume=False)
    original = store.path.read_bytes()
    record = store.outcome_for("untrusted")
    with pytest.raises(EvidenceIntegrityError, match="unqualified"):
        store.claim_observation(record)
    with pytest.raises(EvidenceIntegrityError, match="dedicated"):
        store.record("qualification", "untrusted", {"qualified": True, "mode": "production"})
    assert store.path.read_bytes() == original


def test_persisted_qualification_binds_entire_original_observation(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    _qualified_outcome(store, "real", "regression")
    records = store.audit_trail()
    next(r for r in records if r["kind"] == "outcome")["payload"]["provenance"][
        "source"
    ] = "changed"
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    original = path.read_bytes()
    with pytest.raises(EvidenceIntegrityError, match="qualification"):
        EvidenceStore(path)
    assert path.read_bytes() == original


def test_qualification_write_crash_does_not_replay_completed_learning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    _qualified_outcome(store, "e1", "success", consume=False)
    brain = _brain(tmp_path)
    tracker = OutcomeTracker(
        brain, store_outcome_source(store), measurement_verifier=_test_measurement_verifier
    )
    original_append = EvidenceStore._append

    def interrupted(self: EvidenceStore, kind: str, payload: dict) -> None:
        if kind == "qualification":
            raise OSError("simulated interruption before qualification receipt")
        original_append(self, kind, payload)

    monkeypatch.setattr(EvidenceStore, "_append", interrupted)
    with pytest.raises(OSError):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="b" * 64)
    rate = brain.get_pattern("RP-019").success_rate
    assert rate > 0.9
    restarted = EvidenceStore(store.path)
    assert not restarted.pattern_enabled("RP-019")
    assert "unknown eligibility" in restarted.disable_reason("RP-019")
    replay = OutcomeTracker(
        brain, store_outcome_source(restarted), measurement_verifier=_test_measurement_verifier
    )
    assert replay.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="b" * 64) is None
    assert brain.get_pattern("RP-019").success_rate == rate


def test_delayed_consumption_does_not_reorder_measured_breaker_history(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path, measurement_verifier=_test_measurement_verifier)
    _qualified_outcome(store, "success-first", "success", consume=False)
    for index in range(3):
        _qualified_outcome(store, f"failure{index}", "regression", consume=False)
    for event_id in ("failure0", "failure1", "success-first", "failure2"):
        record = store.outcome_for(event_id)
        assert store.claim_observation(record)
        store.complete_observation(record)
    assert not EvidenceStore(path).pattern_enabled("RP-019")
    assert EvidenceStore(path).breaker("RP-019").disabled


def test_missing_qualification_receipt_cannot_complete_evaluation(tmp_path: Path) -> None:
    records = [
        record
        for record in _full_store(tmp_path).audit_trail("e1")
        if record["kind"] != "qualification"
    ]
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict != COMPLETE
    assert not report.links["confidence_update"]


def test_default_candidate_compile_behavior_needs_only_behavior_baseline(tmp_path: Path) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    event = records[0]["payload"]
    execution = next(record["payload"] for record in records if record["kind"] == "execution")
    event["proposal"]["required_gates"] = ["compile", "behavior"]
    execution["required_gates"] = ["compile", "behavior"]
    for gate in execution["gate_logs"] + execution["baseline_gate_logs"]:
        if gate["name"] == "tests":
            gate["name"] = "behavior"
            gate["command"] = ["python", "-m", "unittest", "discover"]
    assert [gate["name"] for gate in execution["baseline_gate_logs"]] == ["behavior"]
    assert execution["candidate_tree_hash"] != event["sha"]
    report = evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True)
    assert report.verdict == COMPLETE and all(report.links.values())


def test_available_candidate_tree_identity_must_match_not_commit_identity(tmp_path: Path) -> None:
    records = _full_store(tmp_path).audit_trail("e1")
    confidence = next(record["payload"] for record in records if record["kind"] == "confidence")
    confidence["candidate_tree_hash"] = records[0]["payload"]["sha"]
    assert evaluate_event(_SnapshotStore(records), "e1", allow_synthetic=True).verdict == UNVERIFIED


@pytest.mark.parametrize(
    "tail", ["valid_unterminated", "corrupt_unterminated", "corrupt_terminated"]
)
def test_unterminated_or_corrupt_tail_is_never_extended_or_repaired(
    tmp_path: Path,
    tail: str,
) -> None:
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path)
    store.record_event({"event_id": "e1"})
    original = path.read_bytes()
    if tail == "valid_unterminated":
        damaged = original[:-1]
    else:
        damaged = original + b'{"kind":' + (b"\n" if tail == "corrupt_terminated" else b"")
    path.write_bytes(damaged)
    with pytest.raises(EvidenceIntegrityError):
        EvidenceStore(path)
    assert path.read_bytes() == damaged
    with pytest.raises(EvidenceIntegrityError):
        store.record_event({"event_id": "e2"})
    assert path.read_bytes() == damaged


def test_constructor_waits_for_exclusive_data_write_before_reading_tail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "evidence.jsonl"
    EvidenceStore(path).record_event({"event_id": "e1"})
    original_flock = fcntl.flock
    read_started = Event()

    def watched_flock(handle: Any, operation: int) -> None:
        if operation == fcntl.LOCK_SH and Path(handle.name) == path:
            read_started.set()
        original_flock(handle, operation)

    monkeypatch.setattr(fcntl, "flock", watched_flock)
    second = {
        "schema_version": "1.0.0",
        "kind": "event",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "payload": {"event_id": "e2"},
    }
    with ThreadPoolExecutor(max_workers=1) as executor:
        with path.open("ab") as writer:
            original_flock(writer, fcntl.LOCK_EX)
            try:
                writer.write(json.dumps(second).encode("utf-8"))
                writer.flush()
                recovered = executor.submit(EvidenceStore, path)
                assert read_started.wait(timeout=5)
                assert not recovered.done()
                writer.write(b"\n")
                writer.flush()
            finally:
                original_flock(writer, fcntl.LOCK_UN)
        store = recovered.result(timeout=5)
    assert store.seen("e1") and store.seen("e2")


def test_append_takes_exclusive_data_lock_and_monitoring_creates_no_lockfile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "evidence.jsonl"
    original_flock = fcntl.flock
    exclusive_data = Event()

    def watched_flock(handle: Any, operation: int) -> None:
        if operation == fcntl.LOCK_EX and Path(handle.name) == path:
            exclusive_data.set()
        original_flock(handle, operation)

    monkeypatch.setattr(fcntl, "flock", watched_flock)
    EvidenceStore(path).record_event({"event_id": "e1"})
    assert exclusive_data.is_set()
    path.with_name(path.name + ".lock").unlink()
    original = path.read_bytes()
    assert EvidenceStore(path).audit_trail()[0]["payload"]["event_id"] == "e1"
    assert not path.with_name(path.name + ".lock").exists()
    assert path.read_bytes() == original
