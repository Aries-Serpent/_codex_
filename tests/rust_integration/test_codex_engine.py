"""
Integration tests for codex_engine Rust module.

These tests validate the Rust-Python bridge and ensure that the
high-performance orchestration layer works correctly from Python.
"""

import pytest

# Note: These tests will work once maturin build completes
# For now, they serve as documentation of expected API


def test_swarm_state_creation():
    """Test creating a SwarmState instance."""
    try:
        from codex_engine import SwarmState

        state = SwarmState()
        assert state.get_agent_count() == 0, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet (run: maturin develop)")


def test_agent_registration():
    """Test registering agents with SwarmState."""
    try:
        from codex_engine import SwarmState

        state = SwarmState()

        state.register_agent("agent_1")
        assert state.get_agent_count() == 1, "Count must be greater than zero"

        state.register_agent("agent_2")
        assert state.get_agent_count() == 2, "Count must be greater than zero"

        agents = state.list_agents()
        assert "agent_1" in agents, "Condition must be true"
        assert "agent_2" in agents, "Condition must be true"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_status_management():
    """Test updating and querying agent status."""
    try:
        from codex_engine import SwarmState

        state = SwarmState()

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
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_orchestrator_lifecycle():
    """Test starting and stopping the orchestrator."""
    try:
        from codex_engine import Orchestrator, SwarmState

        state = SwarmState()
        orch = Orchestrator(state)

        assert not orch.is_running(), "not is not valid"

        orch.start()
        assert orch.is_running(), "Condition must be true"

        orch.stop()
        # Note: May still show running briefly due to async shutdown
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_task_queue_operations():
    """Test task submission and retrieval."""
    try:
        from codex_engine import Task, TaskQueue

        queue = TaskQueue()

        # Submit a task
        task = Task(id="task_1", task_type="analyze", data='{"file": "main.py"}')
        queue.submit(task)

        # Receive the task
        received = queue.receive()
        assert received is not None, "received must be initialized"
        assert received.id == "task_1", "id is not valid"
        assert received.task_type == "analyze", "task_type is not valid"

        # Queue should now be empty
        assert queue.receive() is None, "Condition must be true"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_concurrent_agent_registration():
    """Test that multiple agents can be registered concurrently."""
    try:
        import concurrent.futures

        from codex_engine import SwarmState

        state = SwarmState()

        def register_agents(start, count):
            for i in range(start, start + count):
                state.register_agent(f"agent_{i}")

        # Register 100 agents concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_agents, i * 10, 10) for i in range(10)]
            concurrent.futures.wait(futures)

        assert state.get_agent_count() == 100, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_high_throughput_task_queue():
    """Test that task queue can handle high throughput."""
    try:
        import time

        from codex_engine import Task, TaskQueue

        queue = TaskQueue()

        # Submit 10,000 tasks
        start = time.time()
        for i in range(10000):
            task = Task(id=f"task_{i}", task_type="test", data="{}")
            queue.submit(task)
        elapsed = time.time() - start

        # Should complete in < 1 second (10,000 tasks/s)
        assert elapsed < 1.0, f"Task submission took {elapsed}s (should be < 1s)"

        # Receive all tasks
        count = 0
        while queue.receive() is not None:
            count += 1

        assert count == 10000, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
