"""Disposable integration coverage for the maintained writer recovery boundary."""

from __future__ import annotations

import builtins
import copy
import json
import multiprocessing
import os
import stat
from contextlib import contextmanager
from dataclasses import replace
from multiprocessing.context import SpawnContext
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import aries_serpent_core.cognitive.brain_interface as brain_module
from aries_serpent_core.cognitive.brain_interface import (
    AgentBrainInterface,
    LearningFeedback,
    PatternPersistenceError,
)
from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.learning_reconciliation import pattern_store_lock
from codex.cognitive_brain.outcome_tracking import OutcomeTracker
from codex.cognitive_brain.writer_recovery import MaintainedWriterRecovery


@pytest.fixture
def spawn_context(monkeypatch: pytest.MonkeyPatch) -> SpawnContext:
    # Spawn imports targets afresh; importlib mode alone does not make the local
    # tests package precede an unrelated site-packages/tests package in children.
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return multiprocessing.get_context("spawn")


def _brain(root: Path) -> AgentBrainInterface:
    directory = root / ".codex" / "cognitive_brain"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "pattern_learning_store.json"
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "extension": {"keep": True},
                    "patterns": {
                        "pattern": {
                            "id": "RP-1",
                            "times_applied": 3,
                            "success_rate": 0.9,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
    return AgentBrainInterface("fixture", repo_root=root, auto_register=False)


def _pending(root: Path, window: str = "pending") -> EvidenceStore:
    store = EvidenceStore(root / "evidence.jsonl", measurement_verifier=lambda _: True)
    store.record_event(
        {
            "event_id": "event",
            "pattern": {"pattern_id": "RP-1"},
            "proposal": {"patch_hash": "a" * 64},
        }
    )
    store.record(
        "execution",
        "event",
        {"attempt_id": "cancelled-attempt", "patch_hash": "a" * 64, "status": "cancelled"},
    )
    store.record_outcome(
        event_id="event",
        pattern_id="RP-1",
        patch_hash="a" * 64,
        merged_sha="b" * 40,
        merged=True,
        outcome="success",
        observation_id="measurement",
        provenance={"source": "fixture", "measured_at": "2026-11-02T00:00:00Z"},
    )
    observation = store.outcome_for("event")
    assert observation is not None
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
    return store


def _files(root: Path) -> dict[str, bytes | None]:
    return {
        str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
        for path in root.rglob("*")
    }


def _writer(
    root: str,
    operation: str,
    ready: Any,
    start: Any,
    paused: Any,
    resume: Any,
    done: Any,
    connection: Any,
    pause: str | None,
) -> None:
    try:
        brain = AgentBrainInterface("child", repo_root=root, auto_register=False)
        original = brain_module.os.replace

        def replacement(source: Any, destination: Any) -> None:
            if pause == "before":
                paused.set()
                if not resume.wait(10):
                    raise TimeoutError("writer resume")
            original(source, destination)
            if pause == "after":
                paused.set()
                if not resume.wait(10):
                    raise TimeoutError("writer resume")

        brain_module.os.replace = replacement
        ready.set()
        if not start.wait(10):
            raise TimeoutError("writer start")
        if operation == "learning":
            assert brain.submit_learning("RP-1", "success")
        else:
            assert brain.submit_pattern(operation, "testing", ["symptom"], ["solution"])
        connection.send(None)
    except BaseException as exc:
        connection.send(repr(exc))
    finally:
        done.set()
        connection.close()


def _reader(
    path: str, started: Any, done: Any, connection: Any, journal: str | None = None
) -> None:
    try:
        recovery = MaintainedWriterRecovery(Path(path), participating_writers_only=True)
        started.set()
        if journal is not None:
            recovery.inspect(EvidenceStore(Path(journal)))
        else:
            with recovery.snapshot() as snapshot:
                assert snapshot.recheck() == snapshot.identity
        connection.send(None)
    except BaseException as exc:
        connection.send(repr(exc))
    finally:
        done.set()
        connection.close()


def _tracker_writer(root: str, paused: Any, resume: Any, connection: Any, phase: str) -> None:
    try:
        brain = AgentBrainInterface("tracker", repo_root=root, auto_register=False)
        store = EvidenceStore(Path(root) / "evidence.jsonl")
        original = brain_module.os.replace

        def wait() -> None:
            paused.set()
            if not resume.wait(10):
                raise TimeoutError("tracker resume")

        def replacement(source: Any, destination: Any) -> None:
            if phase == "replace":
                wait()
            original(source, destination)

        brain_module.os.replace = replacement
        claim = EvidenceStore.claim_observation
        complete = EvidenceStore.complete_observation

        def claim_and_pause(subject: EvidenceStore, *args: Any, **kwargs: Any) -> bool:
            claimed = claim(subject, *args, **kwargs)
            if claimed:
                wait()
            return claimed

        def pause_and_complete(subject: EvidenceStore, *args: Any, **kwargs: Any) -> None:
            wait()
            complete(subject, *args, **kwargs)

        if phase == "claimed":
            EvidenceStore.claim_observation = claim_and_pause
        elif phase == "completion":
            EvidenceStore.complete_observation = pause_and_complete
        observation = {
            "event_id": "tracker-event",
            "pattern_id": "RP-1",
            "patch_hash": "c" * 64,
            "merged_sha": "d" * 40,
            "merged": True,
            "outcome": "success",
            "observation_id": "tracker-measurement",
            "provenance": {"source": "fixture", "measured_at": "2026-11-02T00:00:00Z"},
        }
        tracker = OutcomeTracker(
            brain,
            lambda _: observation,
            evidence_store=store,
            measurement_verifier=lambda _: True,
        )
        assert tracker.process_outcome(
            event_id="tracker-event", pattern_id="RP-1", patch_hash="c" * 64
        )
        connection.send(None)
    except BaseException as exc:
        connection.send(repr(exc))
    finally:
        connection.close()


@pytest.mark.parametrize("pause", ["before", "after"])
@pytest.mark.parametrize("operation", ["learning", "patterns"])
def test_process_writers_and_snapshot_exclude_replace_without_lost_updates(
    tmp_path: Path, pause: str, operation: str, spawn_context: SpawnContext
) -> None:
    brain = _brain(tmp_path)
    ctx = spawn_context
    first_ready, second_ready = ctx.Event(), ctx.Event()
    first_start, second_start = ctx.Event(), ctx.Event()
    paused, resume = ctx.Event(), ctx.Event()
    first_done, second_done = ctx.Event(), ctx.Event()
    reader_started, reader_done = ctx.Event(), ctx.Event()
    processes = []
    connections = []
    for index, ready, start, done in (
        (1, first_ready, first_start, first_done),
        (2, second_ready, second_start, second_done),
    ):
        receiver, sender = ctx.Pipe(duplex=False)
        writer_operation = "learning" if operation == "learning" else f"NEW-{index}"
        process = ctx.Process(
            target=_writer,
            args=(
                str(tmp_path),
                writer_operation,
                ready,
                start,
                paused,
                resume,
                done,
                sender,
                pause if index == 1 else None,
            ),
        )
        processes.append(process)
        connections.append(receiver)
        process.start()
        sender.close()
    try:
        assert first_ready.wait(10) and second_ready.wait(10)
        first_start.set()
        assert paused.wait(10)
        receiver, sender = ctx.Pipe(duplex=False)
        reader = ctx.Process(
            target=_reader,
            args=(str(brain.pattern_store_path), reader_started, reader_done, sender),
        )
        processes.append(reader)
        connections.append(receiver)
        reader.start()
        sender.close()
        assert reader_started.wait(10)
        second_start.set()
        assert not reader_done.wait(0.15)
        assert not second_done.wait(0.15)
        resume.set()
        for process, connection in zip(processes, connections, strict=True):
            process.join(10)
            assert not process.is_alive()
            assert process.exitcode == 0
            assert connection.poll(1)
            assert connection.recv() is None
    finally:
        resume.set()
        first_start.set()
        second_start.set()
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(5)
        for connection in connections:
            connection.close()
    saved = json.loads(brain.pattern_store_path.read_bytes())
    assert saved["extension"] == {"keep": True}
    if operation == "learning":
        assert saved["patterns"]["pattern"]["times_applied"] == 5
        assert saved["patterns"]["pattern"]["success_rate"] == pytest.approx(0.951)
    else:
        assert {p["id"] for p in saved["patterns"].values()} == {"RP-1", "NEW-1", "NEW-2"}
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


@pytest.mark.parametrize("window", ["pending", "complete"])
def test_explicit_callbacks_bind_exact_observation_and_do_not_replay(
    tmp_path: Path, window: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    store = _pending(tmp_path, window)
    calls = []

    def policy(request: Any) -> bool:
        calls.append("policy")
        return request["identity"]["attempt_id"] == "cancelled-attempt"

    def consumption(request: Any) -> bool:
        calls.append("consumption")
        identity = request["identity"]
        return (
            identity["observation_id"] == "measurement"
            and identity["event_id"] == "event"
            and identity["pattern_id"] == "RP-1"
            and identity["patch_hash"] == "a" * 64
            and identity["merged_sha"] == "b" * 40
        )

    def measurement(observation: Any) -> bool:
        calls.append("measurement")
        return observation["observation_id"] == "measurement"

    def forbid_learning(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("recovery must not replay learning")

    monkeypatch.setattr(brain, "submit_learning", forbid_learning)
    recovery = MaintainedWriterRecovery(
        brain.pattern_store_path,
        participating_writers_only=True,
        policy_verifier=policy,
        consumption_verifier=consumption,
        measurement_verifier=measurement,
    )
    before = _files(tmp_path)
    (identity,) = recovery.inspect(store)
    assert recovery.reconcile(store, identity, "already_applied", dry_run=True)
    assert _files(tmp_path) == before
    assert recovery.reconcile(store, identity, "already_applied", dry_run=False)
    assert not recovery.reconcile(store, identity, "already_applied", dry_run=False)
    assert {"policy", "consumption", "measurement"} <= set(calls)
    assert (
        brain.pattern_store_path.read_bytes()
        == before[str(brain.pattern_store_path.relative_to(tmp_path))]
    )
    assert len(store._qualifications) == 1
    execution = next(record for record in store.audit_trail() if record["kind"] == "execution")
    assert execution["payload"]["status"] == "cancelled"


@pytest.mark.parametrize("missing", ["policy", "consumption", "measurement", "coverage"])
@pytest.mark.parametrize("dry_run", [True, False])
def test_missing_injected_proof_denies_without_mutation(
    tmp_path: Path, missing: str, dry_run: bool
) -> None:
    brain = _brain(tmp_path)
    store = _pending(tmp_path)
    recovery = MaintainedWriterRecovery(brain.pattern_store_path, participating_writers_only=True)
    (identity,) = recovery.inspect(store)
    recovery.policy_verifier = None if missing == "policy" else lambda _: True
    recovery.consumption_verifier = None if missing == "consumption" else lambda _: True
    recovery.measurement_verifier = None if missing == "measurement" else lambda _: True
    recovery.participating_writers_only = missing != "coverage"
    before = _files(tmp_path)
    with pytest.raises((EvidenceIntegrityError, ValueError)):
        recovery.reconcile(store, identity, "already_applied", dry_run=dry_run)
    assert _files(tmp_path) == before
    assert not store._qualifications


def test_missing_paths_and_missing_journal_inspection_create_nothing(tmp_path: Path) -> None:
    missing = tmp_path / "not-created" / "patterns.json"
    recovery = MaintainedWriterRecovery(missing, participating_writers_only=True)
    store = EvidenceStore(tmp_path / "also-not-created" / "journal.jsonl")
    with pytest.raises(FileNotFoundError):
        recovery.inspect(store)
    assert _files(tmp_path) == {}
    brain = _brain(tmp_path)
    recovery = MaintainedWriterRecovery(brain.pattern_store_path, participating_writers_only=True)
    before = _files(tmp_path)
    assert recovery.inspect(store) == []
    assert _files(tmp_path) == before


@pytest.mark.parametrize("state", ["missing", "malformed", "unreadable", "stale"])
def test_external_state_changes_fail_closed_and_release_lock(
    tmp_path: Path, state: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    store = _pending(tmp_path)
    recovery = MaintainedWriterRecovery(
        brain.pattern_store_path,
        participating_writers_only=True,
        policy_verifier=lambda _: True,
        consumption_verifier=lambda _: True,
        measurement_verifier=lambda _: True,
    )
    (identity,) = recovery.inspect(store)
    original = brain.pattern_store_path.read_bytes()
    if state == "missing":
        brain.pattern_store_path.unlink()
    elif state == "malformed":
        brain.pattern_store_path.write_bytes(b"not-json")
    elif state == "stale":
        brain.submit_learning("RP-1", "success")
    else:
        read_bytes = Path.read_bytes

        def denied(path: Path) -> bytes:
            if path == brain.pattern_store_path:
                raise PermissionError("fixture read denied")
            return read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", denied)
    journal = store.path.read_bytes()
    with pytest.raises((EvidenceIntegrityError, OSError, ValueError)):
        recovery.reconcile(store, identity, "already_applied", dry_run=False)
    assert store.path.read_bytes() == journal
    monkeypatch.undo()
    brain.pattern_store_path.write_bytes(original)
    with recovery.snapshot() as snapshot:
        assert snapshot.recheck() == snapshot.identity
    assert brain.submit_learning("RP-1", "success")


@pytest.mark.parametrize("phase", ["file_sync", "replace", "directory_sync"])
def test_failed_persistence_never_confirms_and_releases_exclusion(
    tmp_path: Path, phase: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    original = brain.pattern_store_path.read_bytes()
    fsync, replacement = os.fsync, os.replace

    def sync(fd: int) -> None:
        directory = stat.S_ISDIR(os.fstat(fd).st_mode)
        if (phase == "file_sync" and not directory) or (phase == "directory_sync" and directory):
            raise OSError("injected sync failure")
        fsync(fd)

    def replace_file(source: Any, destination: Any) -> None:
        if phase == "replace":
            raise OSError("injected replacement failure")
        replacement(source, destination)

    monkeypatch.setattr(brain_module.os, "fsync", sync)
    monkeypatch.setattr(brain_module.os, "replace", replace_file)
    with pytest.raises(PatternPersistenceError) as error:
        brain.submit_learning("RP-1", "success")
    assert error.value.replaced is (phase == "directory_sync")
    if phase != "directory_sync":
        assert brain.pattern_store_path.read_bytes() == original
    monkeypatch.undo()
    assert brain.submit_learning("RP-1", "success")
    applied = json.loads(brain.pattern_store_path.read_bytes())["patterns"]["pattern"][
        "times_applied"
    ]
    assert applied == (5 if phase == "directory_sync" else 4)
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


def test_direct_save_rejects_stale_cache_instead_of_losing_updates(tmp_path: Path) -> None:
    first = _brain(tmp_path)
    second = _brain(tmp_path)
    first.submit_pattern("NEW", "testing", [], [])
    before = first.pattern_store_path.read_bytes()
    second._patterns["pattern"]["times_applied"] = 999
    with pytest.raises(ValueError, match="stale"):
        second._save_patterns()
    assert first.pattern_store_path.read_bytes() == before
    assert second.submit_learning("RP-1", "success")
    assert "new" in second._patterns


@pytest.mark.parametrize("state", ["missing", "malformed"])
@pytest.mark.parametrize("operation", ["learning", "submit_pattern", "direct_save"])
def test_learning_does_not_restore_cached_missing_or_invalid_store(
    tmp_path: Path, state: str, operation: str
) -> None:
    brain = _brain(tmp_path)
    previous = copy.deepcopy(brain._patterns)
    if state == "missing":
        brain.pattern_store_path.unlink()
    else:
        brain.pattern_store_path.write_bytes(b"[]")
    before = _files(tmp_path)
    with pytest.raises((OSError, ValueError)):
        if operation == "learning":
            brain.submit_learning("RP-1", "success")
        elif operation == "submit_pattern":
            brain.submit_pattern("NEW", "testing", [], [])
        else:
            brain._save_patterns()
    assert _files(tmp_path) == before
    assert brain._patterns == previous


def test_callback_exception_and_abandonment_leave_ambiguity_semantics_intact(
    tmp_path: Path,
) -> None:
    brain = _brain(tmp_path)
    store = _pending(tmp_path)
    recovery = MaintainedWriterRecovery(brain.pattern_store_path, participating_writers_only=True)
    (identity,) = recovery.inspect(store)

    def interrupt(_: Any) -> bool:
        raise KeyboardInterrupt("fixture cancellation")

    recovery.policy_verifier = interrupt
    before = _files(tmp_path)
    with pytest.raises(KeyboardInterrupt):
        recovery.reconcile(store, identity, "already_applied", dry_run=False)
    assert _files(tmp_path) == before
    recovery.policy_verifier = lambda _: True
    assert recovery.reconcile(store, identity, "abandoned", dry_run=False)
    assert not store._qualifications
    with pytest.raises(EvidenceIntegrityError, match="conflicting"):
        recovery.reconcile(store, identity, "already_applied", dry_run=False)
    with pytest.raises(EvidenceIntegrityError):
        recovery.reconcile(
            store, replace(identity, observation_id="wrong"), "abandoned", dry_run=False
        )
    assert brain.submit_learning("RP-1", "success")


def test_lock_exception_releases_process_and_thread_ownership(
    tmp_path: Path, spawn_context: SpawnContext
) -> None:
    brain = _brain(tmp_path)
    with pytest.raises(RuntimeError):
        with pattern_store_lock(brain.pattern_store_path):
            with pattern_store_lock(brain.pattern_store_path):
                raise RuntimeError("fixture")
    ctx = spawn_context
    started, done = ctx.Event(), ctx.Event()
    receiver, sender = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_reader, args=(str(brain.pattern_store_path), started, done, sender)
    )
    process.start()
    sender.close()
    try:
        assert done.wait(10)
        process.join(10)
        assert process.exitcode == 0
        assert receiver.recv() is None
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
        receiver.close()


def test_external_exclusion_precedes_every_journal_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import codex.cognitive_brain.writer_recovery as recovery_module

    brain = _brain(tmp_path)
    store = _pending(tmp_path)
    recovery = MaintainedWriterRecovery(
        brain.pattern_store_path,
        participating_writers_only=True,
        policy_verifier=lambda _: True,
    )
    external_held = False
    lock = recovery_module.pattern_store_lock
    transaction = store._transaction
    transactions = []

    @contextmanager
    def external(path: Path):
        nonlocal external_held
        with lock(path):
            external_held = True
            try:
                yield
            finally:
                external_held = False

    @contextmanager
    def journal(_store: EvidenceStore, *args: Any, **kwargs: Any):
        assert external_held
        transactions.append(kwargs.get("write", True))
        with transaction(*args, **kwargs):
            yield

    monkeypatch.setattr(recovery_module, "pattern_store_lock", external)
    monkeypatch.setattr(EvidenceStore, "_transaction", journal)
    (identity,) = recovery.inspect(store)
    assert recovery.reconcile(store, identity, "abandoned", dry_run=False)
    assert transactions == [False, False, True]


def test_callback_cannot_qualify_changed_external_snapshot(tmp_path: Path) -> None:
    brain = _brain(tmp_path)
    store = _pending(tmp_path)
    recovery = MaintainedWriterRecovery(
        brain.pattern_store_path,
        participating_writers_only=True,
        policy_verifier=lambda _: True,
        measurement_verifier=lambda _: True,
    )
    (identity,) = recovery.inspect(store)
    original = brain.pattern_store_path.read_bytes()

    def nonparticipating_change(_: Any) -> bool:
        # Advisory locking cannot prevent this; the fresh recheck must detect it.
        brain.pattern_store_path.write_bytes(original + b"\n")
        return True

    recovery.consumption_verifier = nonparticipating_change
    journal = store.path.read_bytes()
    with pytest.raises(EvidenceIntegrityError, match="external snapshot changed"):
        recovery.reconcile(store, identity, "already_applied", dry_run=False)
    assert store.path.read_bytes() == journal
    assert not store._qualifications


@pytest.mark.parametrize(
    ("outcome", "expected"), [("success", 0.93), ("failure", 0.63), ("partial", 0.78)]
)
def test_pathless_nonpersistent_ema_consumer_remains_compatible(
    outcome: str, expected: float
) -> None:
    brain = object.__new__(AgentBrainInterface)
    brain._patterns = {"fixture": {"id": "RP-1", "success_rate": 0.9}}
    brain._save_patterns = lambda: None  # type: ignore[method-assign]
    feedback = LearningFeedback(agent_id="fixture", pattern_id="RP-1", outcome=outcome)
    assert brain._update_pattern_stats(feedback)
    assert brain._patterns["fixture"]["success_rate"] == pytest.approx(expected)


@pytest.mark.parametrize("failure", [None, "file_sync", "replace"])
def test_windows_persistence_mock_contract_remains_compatible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str | None
) -> None:
    brain = _brain(tmp_path)
    original = brain.pattern_store_path.read_bytes()
    operations = []

    def sync(fd: int) -> None:
        assert stat.S_ISREG(os.fstat(fd).st_mode)
        operations.append("file_sync")
        if failure == "file_sync":
            raise OSError("fixture file sync")
        os.fsync(fd)

    def replacement(source: Any, destination: Any) -> None:
        operations.append("replace")
        if failure == "replace":
            raise OSError("fixture replace")
        os.replace(source, destination)

    monkeypatch.setattr(
        brain_module,
        "os",
        SimpleNamespace(name="nt", fsync=sync, replace=replacement),
    )
    if failure is None:
        assert brain.submit_learning("RP-1", "success")
        assert operations == ["file_sync", "replace"]
    else:
        with pytest.raises(PatternPersistenceError) as error:
            brain.submit_learning("RP-1", "success")
        assert error.value.replaced is False
        assert brain.pattern_store_path.read_bytes() == original
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


def test_platform_without_fcntl_fails_closed_without_filesystem_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    recovery = MaintainedWriterRecovery(brain.pattern_store_path, participating_writers_only=True)
    before = _files(tmp_path)
    original_import = builtins.__import__

    def unavailable(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "fcntl":
            raise ModuleNotFoundError("fixture unsupported platform")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", unavailable)
    with pytest.raises(OSError, match="requires POSIX"):
        with recovery.snapshot():
            pytest.fail("unsupported snapshot was accepted")
    with pytest.raises(OSError, match="requires POSIX"):
        brain.submit_learning("RP-1", "success")
    assert _files(tmp_path) == before


@pytest.mark.parametrize("phase", ["claimed", "replace", "completion"])
def test_tracker_sidecar_and_recovery_directory_journal_order_do_not_invert(
    tmp_path: Path, spawn_context: SpawnContext, phase: str
) -> None:
    brain = _brain(tmp_path)
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    ctx = spawn_context
    paused, resume, started, done = (ctx.Event() for _ in range(4))
    writer_receiver, writer_sender = ctx.Pipe(duplex=False)
    reader_receiver, reader_sender = ctx.Pipe(duplex=False)
    writer = ctx.Process(
        target=_tracker_writer, args=(str(tmp_path), paused, resume, writer_sender, phase)
    )
    reader = ctx.Process(
        target=_reader,
        args=(
            str(brain.pattern_store_path),
            started,
            done,
            reader_sender,
            str(store.path),
        ),
    )
    writer.start()
    writer_sender.close()
    try:
        assert paused.wait(10), (
            writer_receiver.recv() if writer_receiver.poll() else "tracker did not pause"
        )
        reader.start()
        reader_sender.close()
        assert started.wait(10)
        assert not done.wait(0.15)
        resume.set()
        writer.join(10)
        reader.join(10)
        assert not writer.is_alive() and not reader.is_alive()
        assert writer.exitcode == reader.exitcode == 0
        assert writer_receiver.poll(1) and writer_receiver.recv() is None
        assert reader_receiver.poll(1) and reader_receiver.recv() is None
        assert len(EvidenceStore(store.path)._qualifications) == 1
    finally:
        resume.set()
        for process in (writer, reader):
            if process.pid is not None and process.is_alive():
                process.terminate()
                process.join(5)
        writer_receiver.close()
        reader_receiver.close()
        reader_sender.close()
