from __future__ import annotations

import asyncio
import importlib
import sys
import threading
import time
import types
from unittest.mock import patch

import pytest


def _install_networkx_test_stub(executor_module) -> None:
    """Install the small directed-graph API this module uses in tests."""

    class NetworkXError(Exception):
        pass

    class DiGraph:
        def __init__(self):
            self.nodes = []
            self.edges = {}

        def add_node(self, node):
            if node not in self.nodes:
                self.nodes.append(node)
            self.edges.setdefault(node, [])

        def add_edge(self, source, target, **_attributes):
            self.add_node(source)
            self.add_node(target)
            self.edges[source].append(target)

        def predecessors(self, node):
            return [source for source, targets in self.edges.items() if node in targets]

    def topological_generations(graph):
        remaining = set(graph.nodes)
        while remaining:
            ready = [
                node
                for node in graph.nodes
                if node in remaining
                and not (set(graph.predecessors(node)) & remaining)
            ]
            if not ready:
                raise NetworkXError("Dependency graph contains a cycle")
            yield ready
            remaining.difference_update(ready)

    def is_directed_acyclic_graph(graph):
        try:
            list(topological_generations(graph))
        except NetworkXError:
            return False
        return True

    executor_module.nx = types.SimpleNamespace(
        DiGraph=DiGraph,
        NetworkXError=NetworkXError,
        algorithms=types.SimpleNamespace(
            dag=types.SimpleNamespace(topological_generations=topological_generations)
        ),
        is_directed_acyclic_graph=is_directed_acyclic_graph,
        simple_cycles=lambda _graph: [],
    )


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


def test_execute_runs_independent_subtasks_concurrently_and_waits_for_dependencies(
    monkeypatch,
) -> None:
    monkeypatch.setenv("COPILOT_AGENT_WORKERS", "2")
    active = 0
    maximum_active = 0
    started = set()
    completed = set()
    dependency_checks = []
    lock = threading.Lock()
    overlap = threading.Event()
    task_id = "dependency-test"
    independent_ids = {
        f"{task_id}-diagnose",
        f"{task_id}-logs",
        f"{task_id}-tests",
    }
    aggregate_id = f"{task_id}-aggregate"

    def dispatch(subtask):
        nonlocal active, maximum_active
        with lock:
            started.add(subtask.id)
            if subtask.id == aggregate_id:
                dependency_checks.append(independent_ids.issubset(completed))
            active += 1
            maximum_active = max(maximum_active, active)
            if active >= 2:
                overlap.set()

        if subtask.id != aggregate_id:
            # Hold the first independent task until a second one has started,
            # making accidental serialization observable without timing guesses.
            overlap.wait(timeout=1)
        time.sleep(0.02)

        with lock:
            completed.add(subtask.id)
            active -= 1
        return {"ok": True}

    with patch.dict(sys.modules, {"networkx": types.ModuleType("networkx")}):
        executor_module = importlib.import_module("scripts.ci.phase_9_3_concurrent_executor")
    _install_networkx_test_stub(executor_module)
    executor = executor_module.ConcurrentExecutor(
        max_concurrent_agents=5,
        agent_dispatcher_fn=dispatch,
    )
    task = executor_module.TaskMetadata(
        id=task_id,
        name="dependency execution",
        task_type="ci_failure_analysis",
        category="ci_cd",
        timeout_s=3,
        max_parallel_agents=2,
    )

    result = asyncio.run(executor.execute(task, {}))

    assert result.status == executor_module.TaskStatus.COMPLETED
    assert maximum_active == 2
    assert independent_ids.issubset(started)
    assert dependency_checks == [True]
    assert completed == independent_ids | {aggregate_id}


def test_executor_fails_closed_on_invalid_worker_limit(monkeypatch) -> None:
    monkeypatch.setenv("COPILOT_AGENT_WORKERS", "unbounded")

    with patch.dict(sys.modules, {"networkx": types.ModuleType("networkx")}):
        importlib.invalidate_caches()
        executor_module = importlib.reload(
            importlib.import_module("scripts.ci.phase_9_3_concurrent_executor")
        )
    executor = executor_module.ConcurrentExecutor(max_concurrent_agents=5)

    assert executor.max_concurrent_agents == 1
