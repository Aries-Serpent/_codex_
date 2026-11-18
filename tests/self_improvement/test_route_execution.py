"""Tests for idempotent and resumable Cognitive Brain route execution."""

from __future__ import annotations

from pathlib import Path

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
    second = store.execute(
        request(),
        lambda: (_ for _ in ()).throw(AssertionError("duplicate execution")),
    )

    calls += 1
    assert calls == 1
    assert first.replayed is False
    assert second.replayed is True
    assert second.result == first.result


def test_changed_request_with_same_idempotency_key_conflicts(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    store.execute(request(), lambda: {"status": 201})
    changed = {**request(), "arguments": {"content": "different"}}

    with pytest.raises(RouteExecutionConflict, match="different request"):
        store.execute(changed, lambda: {"status": 201})


def test_incomplete_record_blocks_automatic_replay(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")
    prepared = store.prepare(request())

    with pytest.raises(RouteExecutionConflict, match="incomplete"):
        store.execute(request(), lambda: {"status": 201})

    assert prepared.operation_id


def test_execution_failure_is_recorded_and_reconciled(tmp_path: Path) -> None:
    store = RouteExecutionStore(tmp_path / "routes.db")

    with pytest.raises(RouteExecutionConflict, match="execution failed"):
        store.execute(request(), lambda: (_ for _ in ()).throw(RuntimeError("denied")))

    with pytest.raises(RouteExecutionConflict, match="failed"):
        store.execute(request(), lambda: {"status": 201})
