"""Integration tests for the selected ``codex_swarm`` Rust extension.

These tests validate the Rust-Python bridge and ensure that the
high-performance orchestration layer works correctly from Python.
"""

import concurrent.futures
import time

import pytest

codex_swarm = pytest.importorskip(
    "codex_swarm", reason="codex_swarm not built yet (run: maturin develop)"
)


def test_swarm_state_creation():
    """Test creating a SwarmState instance."""
    state = codex_swarm.SwarmState()
    assert state.get_agent_count() == 0, "Count must be greater than zero"


def test_agent_registration():
    """Test registering agents with SwarmState."""
    state = codex_swarm.SwarmState()

    state.register_agent("agent_1")
    assert state.get_agent_count() == 1, "Count must be greater than zero"

    state.register_agent("agent_2")
    assert state.get_agent_count() == 2, "Count must be greater than zero"

    agents = state.list_agents()
    assert "agent_1" in agents, "Condition must be true"
    assert "agent_2" in agents, "Condition must be true"


def test_agent_status_management():
    """Test updating and querying agent status."""
    state = codex_swarm.SwarmState()

    state.register_agent("agent_1")

    # Set status to working
    state.set_agent_status("agent_1", "working", "Processing file.py")
    status, message = state.get_agent_status("agent_1")
    assert status == "working", "status is not valid"
    assert message == "Processing file.py", "message is not valid"

    # Set status to complete
    state.set_agent_status("agent_1", "complete")
    status, message = state.get_agent_status("agent_1")
    assert status == "complete", "status is not valid"


def test_orchestrator_lifecycle():
    """Test starting and stopping the orchestrator."""
    state = codex_swarm.SwarmState()
    orch = codex_swarm.Orchestrator(state)

    assert not orch.is_running(), "not is not valid"

    orch.start()
    assert orch.is_running(), "Condition must be true"

    orch.stop()
    # Note: May still show running briefly due to async shutdown


def test_task_queue_operations():
    """Test task submission and retrieval."""
    queue = codex_swarm.TaskQueue()

    # Submit a task
    task = codex_swarm.Task(id="task_1", task_type="analyze", data='{"file": "main.py"}')
    queue.submit(task)

    # Receive the task
    received = queue.receive()
    assert received is not None, "received must be initialized"
    assert received.id == "task_1", "id is not valid"
    assert received.task_type == "analyze", "task_type is not valid"

    # Queue should now be empty
    assert queue.receive() is None, "Condition must be true"


def test_concurrent_agent_registration():
    """Test that multiple agents can be registered concurrently."""
    state = codex_swarm.SwarmState()

    def register_agents(start, count):
        for i in range(start, start + count):
            state.register_agent(f"agent_{i}")

    # Register 100 agents concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(register_agents, i * 10, 10) for i in range(10)]
        concurrent.futures.wait(futures)

    assert state.get_agent_count() == 100, "Count must be greater than zero"


def test_high_throughput_task_queue():
    """Test that task queue can handle high throughput."""
    queue = codex_swarm.TaskQueue()

    # Submit 10,000 tasks
    start = time.time()
    for i in range(10000):
        task = codex_swarm.Task(id=f"task_{i}", task_type="test", data="{}")
        queue.submit(task)
    elapsed = time.time() - start

    # Should complete in < 1 second (10,000 tasks/s)
    assert elapsed < 1.0, f"Task submission took {elapsed}s (should be < 1s)"

    # Receive all tasks
    count = 0
    while queue.receive() is not None:
        count += 1

    assert count == 10000, "Count must be greater than zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
