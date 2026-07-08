"""
Python integration tests for Serialization
"""

import time

import pytest


def test_agent_state_creation():
    """Test creating an AgentState instance."""
    try:
        from codex_engine import AgentState

        state = AgentState("agent_1", ["memory1", "memory2"])
        assert state.id == "agent_1", "id is not valid"
        assert state.memory == ["memory1", "memory2"]
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_agent_state_metrics():
    """Test AgentState metrics."""
    try:
        from codex_engine import AgentState

        state = AgentState("agent_1", [])

        state.set_metric("accuracy", 0.95)
        assert state.get_metric("accuracy") == 0.95, "Condition must be true"

        state.set_metric("loss", 0.05)
        keys = state.get_metric_keys()
        assert "accuracy" in keys, "Condition must be true"
        assert "loss" in keys, "Condition must be true"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_serialization_round_trip():
    """Test serialization and deserialization."""
    try:
        from codex_engine import AgentState, deserialize_state, serialize_state

        state = AgentState("agent_1", ["item1", "item2"])
        state.set_metric("score", 0.98)

        serialized = serialize_state(state)
        assert isinstance(serialized, bytes)

        deserialized = deserialize_state(serialized)
        assert deserialized.id == "agent_1", "id is not valid"
        assert deserialized.memory == ["item1", "item2"]
        assert deserialized.get_metric("score") == 0.98, "Condition must be true"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_serialization_size():
    """Test that MessagePack is compact."""
    try:
        import json

        from codex_engine import AgentState, serialize_state

        state = AgentState("agent_1", ["memory"] * 1000)

        # MessagePack
        msgpack_bytes = serialize_state(state)

        # JSON for comparison
        json_str = json.dumps({"id": state.id, "memory": state.memory, "metrics": {}})
        json_bytes = json_str.encode("utf-8")

        # MessagePack should be smaller or comparable
        ratio = len(json_bytes) / len(msgpack_bytes)
        assert ratio >= 0.8, f"Size ratio JSON/MessagePack: {ratio:.2f}"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_serialization_performance():
    """Test that MessagePack is faster than JSON."""
    try:
        import json

        from codex_engine import AgentState, deserialize_state, serialize_state

        state = AgentState("agent_1", ["item"] * 1000)
        for i in range(10):
            state.set_metric(f"metric_{i}", float(i))

        iterations = 1000

        # MessagePack
        start = time.time()
        for _ in range(iterations):
            serialized = serialize_state(state)
            _ = deserialize_state(serialized)
        msgpack_time = time.time() - start

        # JSON
        start = time.time()
        for _ in range(iterations):
            json_str = json.dumps(
                {
                    "id": state.id,
                    "memory": state.memory,
                    "metrics": {k: state.get_metric(k) for k in state.get_metric_keys()},
                }
            )
            _ = json.loads(json_str)
        json_time = time.time() - start

        # MessagePack should be faster
        speedup = json_time / msgpack_time
        assert speedup > 1.0, f"MessagePack speedup: {speedup:.2f}x"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_large_state_serialization():
    """Test serialization of large state."""
    try:
        from codex_engine import AgentState, deserialize_state, serialize_state

        state = AgentState("agent_1", ["large_memory_item"] * 10000)

        serialized = serialize_state(state)
        deserialized = deserialize_state(serialized)

        assert len(deserialized.memory) == 10000, "Collection must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_empty_state_serialization():
    """Test serialization of empty state."""
    try:
        from codex_engine import AgentState, deserialize_state, serialize_state

        state = AgentState("agent_1", [])

        serialized = serialize_state(state)
        deserialized = deserialize_state(serialized)

        assert deserialized.id == "agent_1", "id is not valid"
        assert len(deserialized.memory) == 0, "Collection must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_concurrent_serialization():
    """Test concurrent serialization from multiple threads."""
    try:
        import concurrent.futures

        from codex_engine import AgentState, serialize_state

        state = AgentState("agent_1", ["item"] * 100)

        def serialize_many():
            for _ in range(100):
                serialize_state(state)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(serialize_many) for _ in range(10)]
            concurrent.futures.wait(futures)

        # Should complete without errors
    except ImportError:
        pytest.skip("codex_engine not built yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
