"""Recovery of actual durable windows, not a missing-API import incident.

Pre-edit reproduction (2026-11-02, disposable local JSONL fixtures):
pending: claim raised "learning pending reconciliation; replay refused";
normal complete_observation still completed/qualified (not recovery proof).
complete-noqual: claim returned False; complete_observation raised
"no pending consumption"; qualifications empty and pattern_enabled False.
The tracker orders claim -> submit_learning -> durable check -> complete ->
qualification; neither an interrupted claim nor a missing receipt proves that
the external learning write happened.
"""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

import pytest

from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.learning_reconciliation import ExternalSnapshot


@contextmanager
def snapshot():
    # Fixtures have no external writer. Production must exclude every writer.
    identity = "external-store:fixture-revision-1"
    yield ExternalSnapshot(identity, lambda: identity)


def trusted(_):
    return True


def fixture_store(tmp_path: Path, window="pending"):
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=trusted)
    store.record_event(
        {
            "event_id": "event",
            "pattern": {"pattern_id": "pattern"},
            "proposal": {"patch_hash": "a" * 64},
        }
    )
    store.record_outcome(
        event_id="event",
        pattern_id="pattern",
        patch_hash="a" * 64,
        merged_sha="b" * 40,
        merged=True,
        outcome="success",
        observation_id="measurement",
        provenance={"source": "fixture", "measured_at": "2026-11-02T00:00:00Z"},
        details={"private": "do-not-export"},
    )
    observation = store.outcome_for("event")
    assert store.claim_observation(observation)
    if window == "complete":
        with store._transaction():
            store._append(
                "consumption",
                {
                    "event_id": "event",
                    "observation_key": store.observation_key(observation),
                    "state": "complete",
                },
            )
    return store, observation


def decide(store, identity, disposition="already_applied", **kwargs):
    return store.reconcile_learning(
        identity,
        disposition,
        snapshot_reader=snapshot,
        policy_verifier=trusted,
        consumption_verifier=trusted,
        dry_run=False,
        **kwargs,
    )


@pytest.mark.parametrize("window", ["pending", "complete"])
def test_inspect_exact_readonly_identity(tmp_path, window):
    store, observation = fixture_store(tmp_path, window)
    store.record(
        "execution",
        "event",
        {"attempt_id": "c" * 32, "patch_hash": "a" * 64, "status": "cancelled"},
    )
    before = store.path.read_bytes()
    files = set(tmp_path.iterdir())
    stats = store.stats()
    (identity,) = store.inspect_learning(snapshot)
    assert identity.state == window
    assert identity.observation_id == observation["observation_id"]
    assert identity.event_id == observation["event_id"]
    assert identity.pattern_id == observation["pattern_id"]
    assert identity.patch_hash == observation["patch_hash"]
    assert identity.merged_sha == observation["merged_sha"]
    assert identity.attempt_id == "c" * 32
    assert identity.journal_sha256 == hashlib.sha256(before).hexdigest()
    assert identity.external_snapshot == "external-store:fixture-revision-1"
    assert "private" not in repr(identity)
    assert store.stats() == stats
    assert store.path.read_bytes() == before
    assert set(tmp_path.iterdir()) == files


@pytest.mark.parametrize("kind", ["execution", "event"])
@pytest.mark.parametrize("patch_hash", [None, "d" * 64, "a" * 64])
def test_attempt_source_requires_explicit_matching_patch(tmp_path, kind, patch_hash):
    store, observation = fixture_store(tmp_path)
    if kind == "execution":
        payload = {"attempt_id": "candidate", "status": "cancelled"}
        if patch_hash is not None:
            payload["patch_hash"] = patch_hash
        store.record(kind, "event", payload)
    else:
        # Exercise correlation directly: a foreign proposal also fails journal loading.
        event = next(record["payload"] for record in store._records if record["kind"] == "event")
        event["attempt_id"] = "candidate"
        event["patch_hash"] = "a" * 64
        event["proposal"] = {} if patch_hash is None else {"patch_hash": patch_hash}
    identity = store._learning_identity(
        store.observation_key(observation), "external-fixture", store._journal_sha256
    )
    expected = "candidate" if patch_hash == observation["patch_hash"] else None
    assert identity.attempt_id == expected
    assert identity.attempt_ids == (() if expected is None else (expected,))


def test_missing_inspection_no_directories_or_locks(tmp_path):
    store = EvidenceStore(tmp_path / "missing" / "evidence.jsonl")
    assert store.inspect_learning(snapshot) == []
    assert not store.path.parent.exists()


@pytest.mark.parametrize("tail", [b'{"broken":', b"not-json\n", b"\xff\n"])
def test_corrupt_inspection_preserves_bytes(tmp_path, tail):
    store, _ = fixture_store(tmp_path)
    before = store.path.read_bytes() + tail
    store.path.write_bytes(before)
    with pytest.raises(EvidenceIntegrityError):
        store.inspect_learning(snapshot)
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("window", ["pending", "complete"])
def test_single_append_resolves_and_restarts(tmp_path, window):
    store, observation = fixture_store(tmp_path, window)
    (identity,) = store.inspect_learning(snapshot)
    assert identity.attempt_id is None
    before = store.path.read_bytes()
    assert decide(store, identity)
    assert store.path.read_bytes().startswith(before)
    assert len(store.path.read_bytes().splitlines()) == len(before.splitlines()) + 1
    reloaded = EvidenceStore(store.path)
    assert reloaded.inspect_learning(snapshot) == []
    assert reloaded.pattern_enabled("pattern")
    assert not reloaded.claim_observation(observation)
    assert not decide(reloaded, identity)
    assert reloaded.breaker("pattern")._consecutive_failures == 0


@pytest.mark.parametrize("window", ["pending", "complete"])
def test_abandon_permanent_unknown_and_later_measurements(tmp_path, window):
    store, observation = fixture_store(tmp_path, window)
    # Execution claims/cancellations are audit evidence, never recovery targets.
    for status in ("claimed", "cancelled"):
        store.record(
            "execution",
            "event",
            {"attempt_id": "c" * 32, "patch_hash": "a" * 64, "status": status},
        )
    executions = [r for r in store.audit_trail() if r["kind"] == "execution"]
    (identity,) = store.inspect_learning(snapshot)
    assert decide(store, identity, "abandoned")
    store = EvidenceStore(store.path, measurement_verifier=trusted)
    assert not store.claim_observation(observation)
    assert not store._qualifications
    assert not store.pattern_enabled("pattern")
    assert "unknown" in store.disable_reason("pattern")
    assert not decide(store, identity, "abandoned")
    with pytest.raises(EvidenceIntegrityError):
        decide(store, identity)
    for index, outcome in enumerate(("regression", "rollback")):
        store.record_outcome(
            **{
                **observation,
                "observation_id": f"later-{index}",
                "outcome": outcome,
            }
        )
        later = store.outcome_for("event")
        assert store.claim_observation(later)
        store.complete_observation(later)
    assert store.breaker("pattern")._consecutive_failures == 2
    assert not store.pattern_enabled("pattern")
    assert executions == [r for r in store.audit_trail() if r["kind"] == "execution"]


def test_denied_default_and_missing_proof(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = store.path.read_bytes()
    lock = store.path.with_suffix(".jsonl.lock")
    lock.unlink()
    for options in (
        {},
        {"policy_verifier": lambda _: False},
        {"policy_verifier": lambda _: 1},
        {"policy_verifier": trusted},
        {"policy_verifier": trusted, "consumption_verifier": lambda _: False},
    ):
        with pytest.raises(EvidenceIntegrityError):
            store.reconcile_learning(
                identity,
                "already_applied",
                snapshot_reader=snapshot,
                dry_run=False,
                **options,
            )
        assert not lock.exists()
        assert store.path.read_bytes() == before


def test_measurement_verifier_still_required(tmp_path):
    store, _ = fixture_store(tmp_path)
    store.measurement_verifier = None
    (identity,) = store.inspect_learning(snapshot)
    with pytest.raises(EvidenceIntegrityError):
        decide(store, identity)


@pytest.mark.parametrize(
    "change",
    [
        {"event_id": "forged"},
        {"patch_hash": "d" * 64},
        {"merged_sha": "d" * 40},
        {"pattern_id": "forged"},
        {"observation_id": "forged"},
        {"attempt_id": "forged"},
        {"attempt_ids": ("forged",)},
        {"observation_hash": "d" * 64},
        {"journal_sha256": "d" * 64},
        {"external_snapshot": "forged"},
        {"state": "complete"},
    ],
)
def test_forged_identity_no_append(tmp_path, change):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = store.path.read_bytes()
    with pytest.raises(EvidenceIntegrityError):
        decide(store, replace(identity, **change))
    assert store.path.read_bytes() == before


def test_stale_journal_and_external_snapshot(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    store.record("confidence", "event", {"note": "intervening append"})
    with pytest.raises(EvidenceIntegrityError):
        decide(store, identity)
    (identity,) = store.inspect_learning(snapshot)

    @contextmanager
    def changed():
        yield ExternalSnapshot("external-store:revision-2", lambda: "external-store:revision-2")

    with pytest.raises(EvidenceIntegrityError):
        store.reconcile_learning(
            identity,
            "abandoned",
            snapshot_reader=changed,
            policy_verifier=trusted,
            dry_run=False,
        )


@pytest.mark.parametrize("disposition", ["abandoned", "already_applied"])
def test_dry_run_no_files_stats_or_sidecars(tmp_path, disposition):
    store, _ = fixture_store(tmp_path)
    store.path.with_suffix(".jsonl.lock").unlink()
    (identity,) = store.inspect_learning(snapshot)
    before = store.path.read_bytes()
    stats = store.stats()
    files = set(tmp_path.iterdir())
    assert store.reconcile_learning(
        identity,
        disposition,
        snapshot_reader=snapshot,
        policy_verifier=trusted,
        consumption_verifier=trusted,
        dry_run=True,
    )
    assert set(tmp_path.iterdir()) == files
    assert store.path.read_bytes() == before
    assert store.stats() == stats


@pytest.mark.parametrize("after_append", [False, True])
@pytest.mark.parametrize("window", ["pending", "complete"])
@pytest.mark.parametrize("disposition", ["already_applied", "abandoned"])
def test_append_crash_boundary(tmp_path, after_append, window, disposition):
    store, _ = fixture_store(tmp_path, window)
    (identity,) = store.inspect_learning(snapshot)
    append = store._append

    def crashing(kind, payload):
        if after_append:
            append(kind, payload)
        raise OSError("fixture process interrupted")

    with patch.object(EvidenceStore, "_append", side_effect=crashing):
        with pytest.raises(OSError):
            decide(store, identity, disposition)
    restarted = EvidenceStore(store.path, measurement_verifier=trusted)
    if after_append:
        assert restarted.inspect_learning(snapshot) == []
        assert not decide(restarted, identity, disposition)
    else:
        assert restarted.inspect_learning(snapshot) == [identity]
        assert decide(restarted, identity, disposition)


def test_partial_resolving_append_preserved_not_repaired(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    assert decide(store, identity)
    before = store.path.read_bytes()[:-12]
    store.path.write_bytes(before)
    with pytest.raises(EvidenceIntegrityError):
        EvidenceStore(store.path)
    assert store.path.read_bytes() == before


def test_concurrent_identical_decisions_only_one_append(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = len(store.path.read_bytes().splitlines())

    def resolve(_):
        return decide(EvidenceStore(store.path, measurement_verifier=trusted), identity)

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(resolve, range(2))) == [False, True]
    assert len(store.path.read_bytes().splitlines()) == before + 1


def test_pending_block_removed_only_by_resolution(tmp_path):
    store, observation = fixture_store(tmp_path)
    later = {**observation, "observation_id": "later", "outcome": "regression"}
    store.record_outcome(**later)
    with pytest.raises(EvidenceIntegrityError, match="unreconciled"):
        store.claim_observation(later)
    (identity,) = store.inspect_learning(snapshot)
    assert decide(store, identity, "abandoned")
    assert store.claim_observation(later)
    assert not store.claim_observation(observation)


@pytest.mark.parametrize(
    "mutation", ["duplicate", "wrong-event", "wrong-attempt", "qual-abandon", "wrong-digest"]
)
def test_restart_rejects_invalid_reconciliation_records(tmp_path, mutation):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    decide(store, identity, "abandoned")
    lines = store.path.read_bytes().splitlines(keepends=True)
    record = json.loads(lines[-1])
    if mutation == "duplicate":
        lines.append(lines[-1])
    else:
        if mutation == "wrong-event":
            record["payload"]["identity"]["event_id"] = "wrong"
        elif mutation == "wrong-attempt":
            record["payload"]["identity"]["attempt_id"] = "wrong"
        elif mutation == "wrong-digest":
            record["payload"]["identity"]["journal_sha256"] = "d" * 64
        else:
            record["payload"]["qualification"] = {"forged": True}
        lines[-1] = (json.dumps(record) + "\n").encode()
    invalid = b"".join(lines)
    store.path.write_bytes(invalid)
    with pytest.raises(EvidenceIntegrityError):
        EvidenceStore(store.path)
    assert store.path.read_bytes() == invalid


def test_unrelated_external_writes_are_not_consumption_proof(tmp_path):
    store, _ = fixture_store(tmp_path)
    external = tmp_path / "brain.json"
    external.write_text('{"times_applied":12,"success_rate":0.95}')
    original = external.read_bytes()

    @contextmanager
    def external_snapshot():
        # No other writer exists in this fixture; rate/count are not receipts.
        def recheck():
            return hashlib.sha256(external.read_bytes()).hexdigest()

        yield ExternalSnapshot(recheck(), recheck)

    (identity,) = store.inspect_learning(external_snapshot)
    with pytest.raises(EvidenceIntegrityError, match="independent consumption"):
        store.reconcile_learning(
            identity,
            "already_applied",
            snapshot_reader=external_snapshot,
            policy_verifier=trusted,
            consumption_verifier=lambda _: False,
            dry_run=False,
        )
    assert external.read_bytes() == original
    assert store.inspect_learning(external_snapshot) == [identity]


def test_applied_failure_repeated_decision_does_not_double_breaker(tmp_path):
    store, first = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    decide(store, identity, "abandoned")
    store.record_outcome(**{**first, "observation_id": "regression", "outcome": "regression"})
    observation = store.outcome_for("event")
    assert store.claim_observation(observation)
    (identity,) = store.inspect_learning(snapshot)
    assert decide(store, identity)
    assert not decide(store, identity)
    assert EvidenceStore(store.path).breaker("pattern")._consecutive_failures == 1


def test_actual_normal_completion_crash_before_qualification(tmp_path):
    store, observation = fixture_store(tmp_path)
    append = store._append

    def interrupt_qualification(kind, payload):
        if kind == "qualification":
            raise OSError("fixture crash after completion append")
        append(kind, payload)

    with patch.object(EvidenceStore, "_append", side_effect=interrupt_qualification):
        with pytest.raises(OSError):
            store.complete_observation(observation)
    store = EvidenceStore(store.path, measurement_verifier=trusted)
    assert not store.claim_observation(observation)
    with pytest.raises(EvidenceIntegrityError, match="no pending consumption"):
        store.complete_observation(observation)
    (identity,) = store.inspect_learning(snapshot)
    assert identity.state == "complete"
    assert not store.pattern_enabled("pattern")
    assert decide(store, identity)
    assert EvidenceStore(store.path).pattern_enabled("pattern")


def test_unsupported_ambiguous_decision_cannot_resolve(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = store.path.read_bytes()
    with pytest.raises(EvidenceIntegrityError, match="invalid reconciliation decision"):
        decide(store, identity, "ambiguous")
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("verifier", ["policy", "consumption", "measurement"])
@pytest.mark.parametrize("truthy", [1, "approved", {"authorized": True}])
def test_all_verifiers_require_exact_true(tmp_path, verifier, truthy):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = store.path.read_bytes()
    options = {
        "snapshot_reader": snapshot,
        "policy_verifier": trusted,
        "consumption_verifier": trusted,
        "measurement_verifier": trusted,
        "dry_run": False,
    }
    options[f"{verifier}_verifier"] = lambda _: truthy
    with pytest.raises(EvidenceIntegrityError):
        store.reconcile_learning(identity, "already_applied", **options)
    assert store.path.read_bytes() == before
    assert not store._qualifications


def test_concurrent_competing_decisions_recheck_under_write_lock(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    before = len(store.path.read_bytes().splitlines())
    barrier = Barrier(2)

    def resolve(disposition):
        calls = 0

        def policy(_):
            nonlocal calls
            calls += 1
            if calls == 1:
                # Both requests have inspected the same pre-resolution journal.
                barrier.wait(timeout=10)
            return True

        other = EvidenceStore(store.path, measurement_verifier=trusted)
        try:
            return other.reconcile_learning(
                identity,
                disposition,
                snapshot_reader=snapshot,
                policy_verifier=policy,
                consumption_verifier=trusted,
                dry_run=False,
            )
        except EvidenceIntegrityError as exc:
            assert "conflicting reconciliation decision" in str(exc)
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(resolve, ("abandoned", "already_applied"))) == [False, True]
    assert len(store.path.read_bytes().splitlines()) == before + 1
    restarted = EvidenceStore(store.path)
    assert restarted.inspect_learning(snapshot) == []
    assert len(restarted._qualifications) <= 1


@pytest.mark.parametrize("source", ["journal", "external"])
def test_recheck_snapshots_inside_write_transaction(tmp_path, source):
    store, _ = fixture_store(tmp_path)
    revision = ["external-v1"]

    @contextmanager
    def live_snapshot():
        yield ExternalSnapshot(revision[0], lambda: revision[0])

    (identity,) = store.inspect_learning(live_snapshot)
    transaction = store._transaction
    intervened = False

    @contextmanager
    def intervening_transaction(self, *, write=True):
        nonlocal intervened
        if self is not store:
            with transaction(write=write):
                yield
            return
        if write and not intervened:
            intervened = True
            if source == "journal":
                other = EvidenceStore(store.path)
                # This append lands after read-only preflight, before write lock.
                with transaction():
                    other._append("confidence", {"event_id": "event", "intervening": True})
        with transaction(write=write):
            if write and source == "external":
                # Simulate a writer violating the external exclusion protocol.
                revision[0] = "external-v2"
            yield

    with patch.object(EvidenceStore, "_transaction", intervening_transaction):
        with pytest.raises(EvidenceIntegrityError):
            store.reconcile_learning(
                identity,
                "already_applied",
                snapshot_reader=live_snapshot,
                policy_verifier=trusted,
                consumption_verifier=trusted,
                dry_run=False,
            )
    restarted = EvidenceStore(store.path)
    assert not restarted._qualifications
    assert not restarted._reconciliations


@pytest.mark.parametrize("condition", ["absent", "disappeared", "unreadable", "changed"])
def test_external_store_unavailable_never_resolves(tmp_path, condition):
    store, _ = fixture_store(tmp_path)
    external = tmp_path / "external.json"
    external.write_bytes(b'{"fixture": 1}')
    blocked = False

    def read_identity():
        if blocked:
            raise PermissionError("fixture external source denied")
        return hashlib.sha256(external.read_bytes()).hexdigest()

    @contextmanager
    def file_snapshot():
        yield ExternalSnapshot(read_identity(), read_identity)

    (identity,) = store.inspect_learning(file_snapshot)
    before = store.path.read_bytes()
    if condition in ("absent", "disappeared"):
        external.unlink()
    elif condition == "unreadable":
        blocked = True
    else:
        external.write_bytes(b'{"fixture": 2}')
    with pytest.raises((EvidenceIntegrityError, OSError)):
        store.reconcile_learning(
            identity,
            "already_applied",
            snapshot_reader=file_snapshot,
            policy_verifier=trusted,
            consumption_verifier=trusted,
            dry_run=False,
        )
    assert store.path.read_bytes() == before
    assert not store._qualifications
    if condition == "absent":
        # An absent source cannot produce an accepted identity or create a store.
        missing = EvidenceStore(tmp_path / "missing" / "journal.jsonl")
        with pytest.raises(OSError):
            missing.inspect_learning(file_snapshot)
        assert not missing.path.parent.exists()
        external.write_bytes(b'{"fixture": 2}')
        with pytest.raises(EvidenceIntegrityError):
            store.reconcile_learning(
                identity,
                "abandoned",
                snapshot_reader=file_snapshot,
                policy_verifier=trusted,
                dry_run=False,
            )


def test_external_disappears_during_trusted_proof_callback(tmp_path):
    store, _ = fixture_store(tmp_path)
    external = tmp_path / "external.json"
    external.write_bytes(b"fixture")

    def recheck():
        return hashlib.sha256(external.read_bytes()).hexdigest()

    @contextmanager
    def file_snapshot():
        yield ExternalSnapshot(recheck(), recheck)

    def consumption(_):
        external.unlink()
        return True

    (identity,) = store.inspect_learning(file_snapshot)
    before = store.path.read_bytes()
    with pytest.raises(EvidenceIntegrityError, match="external snapshot unavailable"):
        store.reconcile_learning(
            identity,
            "already_applied",
            snapshot_reader=file_snapshot,
            policy_verifier=trusted,
            consumption_verifier=consumption,
            dry_run=False,
        )
    assert store.path.read_bytes() == before


def test_resolution_metadata_without_qualification_is_not_eligibility(tmp_path):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    assert decide(store, identity)
    lines = store.path.read_bytes().splitlines(keepends=True)
    resolving = json.loads(lines[-1])
    resolving["payload"]["qualification"] = None
    lines[-1] = (json.dumps(resolving) + "\n").encode()
    corrupted = b"".join(lines)
    store.path.write_bytes(corrupted)
    with pytest.raises(EvidenceIntegrityError):
        EvidenceStore(store.path)
    assert store.path.read_bytes() == corrupted


def test_crash_after_normal_qualification_append_restarts_qualified_once(tmp_path):
    store, observation = fixture_store(tmp_path)
    append = store._append

    def crash_after_append(kind, payload):
        append(kind, payload)
        if kind == "qualification":
            raise OSError("fixture process interrupted after qualification fsync")

    with patch.object(EvidenceStore, "_append", side_effect=crash_after_append):
        with pytest.raises(OSError):
            store.complete_observation(observation)
    restarted = EvidenceStore(store.path)
    assert restarted.inspect_learning(snapshot) == []
    assert not restarted.claim_observation(observation)
    assert len(restarted._qualifications) == 1
    assert restarted.pattern_enabled("pattern")


@pytest.mark.parametrize("disposition", ["already_applied", "abandoned"])
def test_repeated_decision_does_not_create_missing_lock(tmp_path, disposition):
    store, _ = fixture_store(tmp_path)
    (identity,) = store.inspect_learning(snapshot)
    decide(store, identity, disposition)
    store.path.with_suffix(".jsonl.lock").unlink()
    before = store.path.read_bytes()
    stats = store.stats()
    files = set(tmp_path.iterdir())
    assert not decide(store, identity, disposition)
    assert store.path.read_bytes() == before
    assert store.stats() == stats
    assert set(tmp_path.iterdir()) == files
