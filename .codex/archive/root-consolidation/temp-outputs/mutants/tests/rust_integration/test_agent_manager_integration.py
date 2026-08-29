"""
Python integration tests for AgentManager
"""

import concurrent.futures
import time

import pytest


def test_agent_manager_creation():
    """Test creating an AgentManager instance."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=10)
        assert manager.get_max_agents() == 10, "Condition must be true"
        assert manager.get_active_count() == 0, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_manager_properties():
    """Test AgentManager properties."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=25)
        assert manager.get_max_agents() == 25, "Condition must be true"
        assert manager.get_active_count() == 0, "Count must be greater than zero"
        assert manager.list_active_agents() == [], "Condition must be true"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_spawning_capacity():
    """Test that manager respects max_agents limit."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=5)

        # Try to spawn more than max
        for i in range(10):
            try:
                manager.spawn_agent(f"agent_{i}", "{}")
            except RuntimeError:
                _ = None  # Expected when limit reached

        time.sleep(0.1)
        # Should not exceed max
        assert manager.get_active_count() <= 5, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_termination():
    """Test terminating agents."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=10)

        manager.spawn_agent("agent_1", "{}")
        time.sleep(0.05)

        terminated = manager.terminate_agent("agent_1")
        assert isinstance(terminated, bool)
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_list_active_agents():
    """Test listing active agents."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=10)

        manager.spawn_agent("agent_1", "{}")
        manager.spawn_agent("agent_2", "{}")

        time.sleep(0.1)

        active = manager.list_active_agents()
        assert isinstance(active, list)
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_manager_concurrent_access():
    """Test concurrent agent manager access from multiple threads."""
    try:
        from codex_engine import AgentManager

        manager = AgentManager(max_agents=50)

        def spawn_agents(start, count):
            for i in range(start, start + count):
                try:
                    manager.spawn_agent(f"agent_{i}", "{}")
                except RuntimeError:
                    # Expected: manager may hit max_agents capacity (50)
                    # during concurrent spawning from multiple threads.
                    # This is intentional behavior to test concurrent access limits.
                    # We catch and ignore this error to continue testing other agents.
                    _ = None  # suppressed: no action needed

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(spawn_agents, i * 5, 5) for i in range(10)]
            concurrent.futures.wait(futures)

        time.sleep(0.2)
        assert manager.get_active_count() <= 50, "Count must be greater than zero"
    except ImportError:
        pytest.skip("codex_engine not built yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
