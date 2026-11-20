"""Tests for idempotent and resumable Cognitive Brain route execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event, Lock
from typing import Any

import pytest

from codex.cognitive_brain.route_execution import (
    RouteExecutionConflict,
    RouteExecutionStore,
)


def request() -> dict[str, object]:
    return {
        "capability": "github.write",
        "action": "create_dangling_blob",
        "target": "Aries-Serpent/_codex_",
        "arguments": {"content": "probe"},
        "idempotency_key": "task-probe-1",
    }


def test_replay_returns_completed_result_without_second_execution(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    calls = 0

    first = store.execute(request(), lambda: {"status": 201, "sha": "abc"})
    replay_claim = store.prepare(request())
    second = store.execute(
        request(),
        lambda: (_ for _ in ()).throw(AssertionError("duplicate execution")),
    )

    calls += 1
    assert calls == 1
    assert replay_claim.state == "replayed"
    assert replay_claim.result == first.result
    assert first.replayed is False
    assert second.replayed is True
    assert second.result == first.result


def test_changed_request_with_same_idempotency_key_conflicts(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    store.execute(request(), lambda: {"status": 201})
    changed = {**request(), "arguments": {"content": "different"}}

    with pytest.raises(RouteExecutionConflict, match="different request"):
        store.execute(changed, lambda: {"status": 201})


def test_concurrent_execution_claims_operation_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    original_prepare = store.prepare
    first_prepare_started = Event()
    release_first_prepare = Event()
    prepare_lock = Lock()
    first_prepare = True
    operation_calls = 0
    operation_lock = Lock()

    def interleaved_prepare(route_request: dict[str, object]):
        nonlocal first_prepare
        with prepare_lock:
            should_pause = first_prepare
            first_prepare = False
        if should_pause:
            first_prepare_started.set()
            assert release_first_prepare.wait(timeout=5)
        return original_prepare(route_request)

    def operation() -> dict[str, Any]:
        nonlocal operation_calls
        with operation_lock:
            operation_calls += 1
            call_number = operation_calls
        return {"status": 201, "call": call_number}

    monkeypatch.setattr(store, "prepare", interleaved_prepare)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(store.execute, request(), operation)
        assert first_prepare_started.wait(timeout=5)
        second = executor.submit(store.execute, request(), operation)
        try:
            second_result = second.result(timeout=5)
        finally:
            release_first_prepare.set()
        first_result = first.result(timeout=5)

    assert operation_calls == 1
    assert first_result.result == second_result.result
    assert sorted((first_result.replayed, second_result.replayed)) == [False, True]


def test_incomplete_record_blocks_automatic_replay(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    prepared = store.prepare(request())

    with pytest.raises(RouteExecutionConflict, match="incomplete"):
        store.execute(request(), lambda: {"status": 201})

    assert prepared.state == "claimed"
    assert prepared.operation_id


def test_execution_failure_is_recorded_and_reconciled(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")

    with pytest.raises(RouteExecutionConflict, match="execution failed"):
        store.execute(request(), lambda: (_ for _ in ()).throw(RuntimeError("denied")))

    with pytest.raises(RouteExecutionConflict, match="failed"):
        store.execute(request(), lambda: {"status": 201})


def test_live_execution_is_not_reconcilable_or_reported_incomplete(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    claim = store.prepare(request())

    assert store.incomplete_operations() == []
    with pytest.raises(RouteExecutionConflict, match="live executor"):
        store.reconcile(claim.operation_id, result={"status": 201})


def test_abandoned_operation_reconciliation_enables_verified_replay(tmp_path: Path) -> None:
    database = tmp_path / "routes.db"
    crashed_store = RouteExecutionStore(database)
    recovery_store = RouteExecutionStore(database)
    claim = crashed_store.prepare(request())

    with crashed_store._connect() as connection:
        connection.execute(
            "UPDATE route_operations SET owner_pid = ?, owner_start = ? WHERE operation_id = ?",
            (999999999, "dead-process", claim.operation_id),
        )

    incomplete = recovery_store.incomplete_operations()
    recovery_store.reconcile(claim.operation_id, result={"status": 201, "verified": True})

    assert incomplete == [
        {
            "operation_id": claim.operation_id,
            "idempotency_key": "task-probe-1",
            "request_digest": claim.request_digest,
            "state": "executing",
            "created_at": incomplete[0]["created_at"],
            "updated_at": incomplete[0]["updated_at"],
        }
    ]
    assert recovery_store.prepare(request()).state == "replayed"


def test_reconciliation_rejects_missing_outcome_and_terminal_operation(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    claim = store.prepare(request())

    with pytest.raises(RouteExecutionConflict, match="requires a result or error"):
        store.reconcile(claim.operation_id)

    with store._connect() as connection:
        connection.execute(
            "UPDATE route_operations SET owner_pid = ?, owner_start = ? WHERE operation_id = ?",
            (999999999, "dead-process", claim.operation_id),
        )
    store.reconcile(claim.operation_id, error="external operation was not applied")
    with pytest.raises(RouteExecutionConflict, match="not awaiting reconciliation"):
        store.reconcile(claim.operation_id, result={"status": 201})


def test_finish_detects_lost_execution_ownership(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    claim = store.prepare(request())

    with store._connect() as connection:
        connection.execute(
            "UPDATE route_operations SET owner_id = ? WHERE operation_id = ?",
            ("replacement-owner", claim.operation_id),
        )

    with pytest.raises(RouteExecutionConflict, match="lost ownership"):
        store._finish(claim, result={"status": 201})
