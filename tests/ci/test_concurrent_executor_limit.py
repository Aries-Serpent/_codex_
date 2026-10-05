from __future__ import annotations

import asyncio
import importlib
import sys
import threading
import time
import types
from unittest.mock import patch

import pytest


@pytest.mark.parametrize("worker_limit", [1, 2])
def test_executor_honors_worker_limit_and_runs_tasks_in_bounded_batches(
    monkeypatch, worker_limit: int
) -> None:
    monkeypatch.setenv("COPILOT_AGENT_WORKERS", str(worker_limit))
    active = 0
    maximum_active = 0
    lock = threading.Lock()

    def dispatch(_subtask):
        nonlocal active, maximum_active
        with lock:
            active += 1
            maximum_active = max(maximum_active, active)
        time.sleep(0.02)
        with lock:
            active -= 1
        return {"ok": True}

    with patch.dict(sys.modules, {"networkx": types.ModuleType("networkx")}):
        executor_module = importlib.import_module("scripts.ci.phase_9_3_concurrent_executor")
    executor = executor_module.ConcurrentExecutor(
        max_concurrent_agents=5,
        agent_dispatcher_fn=dispatch,
    )
    subtasks = {}
    for index in range(4):
        subtask = executor_module.SubTask(
            id=f"task-{index}",
            parent_task_id="root",
            name="task",
            timeout_s=2,
        )
        subtasks[subtask.id] = subtask

    results = asyncio.run(executor._execute_layer(list(subtasks), subtasks, timeout_s=2))

    assert executor.max_concurrent_agents == worker_limit
    assert maximum_active == worker_limit
    assert set(results) == set(subtasks)


def test_executor_fails_closed_on_invalid_worker_limit(monkeypatch) -> None:
    monkeypatch.setenv("COPILOT_AGENT_WORKERS", "unbounded")

    with patch.dict(sys.modules, {"networkx": types.ModuleType("networkx")}):
        importlib.invalidate_caches()
        executor_module = importlib.reload(
            importlib.import_module("scripts.ci.phase_9_3_concurrent_executor")
        )
    executor = executor_module.ConcurrentExecutor(max_concurrent_agents=5)

    assert executor.max_concurrent_agents == 1
