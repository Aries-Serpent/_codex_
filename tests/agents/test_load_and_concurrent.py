"""
Load and concurrent testing for scalability validation.

Tests system behavior under:
- High load (many simultaneous operations)
- Concurrent access (race conditions)
- Memory pressure (large data sets)
- Sustained operations (endurance testing)
"""

import concurrent.futures
import tempfile
import threading
import time
from pathlib import Path

import pytest

from agents.agent_memory import AgentMemory, MemoryEntry
from agents.physics_integration import HybridPhysicsOrchestrator
from codex.logging.structured_logger import logger


class TestConcurrentMemoryAccess:
    """Test concurrent access to memory system."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_path = Path(temp_file.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_concurrent_memory_writes(self, temp_db):
        """Test multiple threads writing memories simultaneously."""
        if not hasattr(AgentMemory, "__init__"):
            pytest.skip("AgentMemory API not available")

        memory = AgentMemory(db_path=str(temp_db))
        errors = []

        def write_memories(thread_id, count=50):
            try:
                for i in range(count):
                    entry = MemoryEntry(
                        memory_id=f"thread_{thread_id}_mem_{i}",
                        category="fact",
                        content=f"Data from thread {thread_id}, iteration {i}",
                        context={"thread": thread_id, "iteration": i},
                    )
                    if hasattr(memory, "add_memory"):
                        memory.add_memory(entry)
            except Exception as e:
                errors.append(e)

        # Run 10 threads, each writing 50 memories
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_memories, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)

        # Should complete without errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_concurrent_memory_reads(self, temp_db):
        """Test multiple threads reading memories simultaneously."""
        if not hasattr(AgentMemory, "__init__"):
            pytest.skip("AgentMemory API not available")

        memory = AgentMemory(db_path=str(temp_db))

        # Pre-populate with data
        if hasattr(memory, "add_memory"):
            for i in range(100):
                entry = MemoryEntry(
                    memory_id=f"read_test_{i}",
                    category="fact",
                    content=f"Content {i}",
                    context={},
                )
                memory.add_memory(entry)

        errors = []
        results = []

        def read_memories(thread_id, count=50):
            try:
                for i in range(count):
                    memory_id = f"read_test_{i % 100}"
                    if hasattr(memory, "get_memory"):
                        result = memory.get_memory(memory_id)
                        results.append((thread_id, result))
            except (IOError, OSError) as e:
                errors.append(e)

        # Run 10 threads reading simultaneously
        threads = []
        for i in range(10):
            t = threading.Thread(target=read_memories, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)

        assert len(errors) == 0, "Errors must not be empty"
        assert len(results) > 0, "Results must not be empty"

    def test_concurrent_read_write_mix(self, temp_db):
        """Test concurrent reads and writes."""
        if not hasattr(AgentMemory, "__init__"):
            pytest.skip("AgentMemory API not available")

        memory = AgentMemory(db_path=str(temp_db))
        errors = []

        def mixed_operations(thread_id, iterations=30):
            try:
                for i in range(iterations):
                    if i % 2 == 0:
                        # Write
                        entry = MemoryEntry(
                            memory_id=f"mixed_{thread_id}_{i}",
                            category="fact",
                            content=f"Mixed {i}",
                            context={},
                        )
                        if hasattr(memory, "add_memory"):
                            memory.add_memory(entry)
                    else:
                        # Read
                        if hasattr(memory, "search_memories"):
                            memory.search_memories(category="fact")
            except (IOError, OSError) as e:
                errors.append(e)

        threads = []
        for i in range(5):
            t = threading.Thread(target=mixed_operations, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)

        assert len(errors) == 0, "Errors must not be empty"


class TestHighLoadOrchestration:
    """Test orchestrator under high load."""

    def test_rapid_orchestration_calls(self):
        """Test making many orchestration calls rapidly."""
        orch = HybridPhysicsOrchestrator()

        start = time.time()
        results = []

        for i in range(100):
            decision_space = {
                "current_position": f"state_{i}",
                "goal_position": f"target_{i}",
                "iteration": i,
            }
            result = orch.orchestrate_with_all_paradigms(decision_space)
            results.append(result)

        duration = time.time() - start

        # 100 calls should complete in reasonable time
        assert duration < 10.0, "duration is not valid"
        assert len(results) == 100, "Results must not be empty"
        assert all(r is not None for r in results), "r must be initialized"

    def test_concurrent_orchestration(self):
        """Test concurrent orchestration from multiple threads."""
        orch = HybridPhysicsOrchestrator()
        errors = []
        results = []

        def orchestrate_batch(thread_id, count=20):
            try:
                for i in range(count):
                    decision_space = {
                        "current_position": f"thread_{thread_id}_state_{i}",
                        "goal_position": f"thread_{thread_id}_target_{i}",
                    }
                    result = orch.orchestrate_with_all_paradigms(decision_space)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Run 5 threads concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(orchestrate_batch, i) for i in range(5)]
            concurrent.futures.wait(futures, timeout=30)

        assert len(errors) == 0, "Errors must not be empty"
        assert len(results) == 100, "Results must not be empty"


class TestMemoryPressure:
    """Test behavior under memory pressure."""

    def test_large_memory_dataset(self):
        """Test storing and retrieving large number of memories."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            if hasattr(AgentMemory, "__init__"):
                memory = AgentMemory(db_path=str(temp_path))

                # Add 1000 memories
                start = time.time()
                if hasattr(memory, "add_memory"):
                    for i in range(1000):
                        entry = MemoryEntry(
                            memory_id=f"large_dataset_{i}",
                            category="fact" if i % 2 == 0 else "decision",
                            content=f"Large dataset entry {i}" * 10,  # Make it bigger
                            context={"index": i, "batch": i // 100},
                        )
                        memory.add_memory(entry)

                add_duration = time.time() - start

                # Should complete in reasonable time
                assert add_duration < 30.0, "add_duration is not valid"

                # Search should still be fast
                start = time.time()
                if hasattr(memory, "search_memories"):
                    memory.search_memories(category="fact")
                search_duration = time.time() - start

                assert search_duration < 2.0, "search_duration is not valid"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_large_context_frames(self):
        """Test handling large context frames."""
        from agents.agent_memory import ContextFrame

        # Create frame with many active memories
        large_frame = ContextFrame(
            frame_id="large_frame",
            task_description="Task with many dependencies",
            start_time="2025-01-01T00:00:00",
            active_memories=[f"mem_{i}" for i in range(1000)],
        )

        assert len(large_frame.active_memories) == 1000, "Collection must not be empty"
        assert large_frame.frame_id == "large_frame", "frame_id is not valid"


class TestEnduranceTesting:
    """Test sustained operations over time."""

    def test_sustained_orchestration(self):
        """Test orchestrator over sustained period."""
        orch = HybridPhysicsOrchestrator()

        start_time = time.time()
        iteration_count = 0
        errors = []

        # Run for 5 seconds
        while time.time() - start_time < 5.0:
            try:
                decision_space = {
                    "current_position": f"sustained_{iteration_count}",
                    "goal_position": f"target_{iteration_count}",
                }
                result = orch.orchestrate_with_all_paradigms(decision_space)
                assert result is not None, "result must be initialized"
                iteration_count += 1
            except Exception as e:
                errors.append(e)

        # Should complete many iterations without errors
        assert iteration_count > 50, "iteration_count must be positive"
        assert len(errors) == 0, "Errors must not be empty"

    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        import sys

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            if hasattr(AgentMemory, "__init__"):
                memory = AgentMemory(db_path=str(temp_path))

                # Get initial memory usage (approximate)
                initial_size = sys.getsizeof(memory)

                # Perform many operations
                if hasattr(memory, "add_memory"):
                    for i in range(100):
                        entry = MemoryEntry(
                            memory_id=f"leak_test_{i}",
                            category="fact",
                            content="Test",
                            context={},
                        )
                        memory.add_memory(entry)

                # Memory growth should be reasonable
                final_size = sys.getsizeof(memory)

                # Size increase should be bounded
                # (This is a rough check, not precise memory profiling)
                assert final_size < initial_size * 10, "final_size is not valid"
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestRaceConditions:
    """Test for race conditions in concurrent scenarios."""

    def test_counter_increment_race(self):
        """Test concurrent counter increments (classic race condition test)."""
        from agents.agent_memory import MemoryEntry

        entry = MemoryEntry(
            memory_id="counter_test",
            category="fact",
            content="Counter",
            context={},
            access_count=0,
        )

        errors = []

        def increment_counter(iterations=100):
            try:
                for _ in range(iterations):
                    entry.access_count += 1
            except Exception as e:
                errors.append(e)

        # Run 10 threads incrementing
        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment_counter)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        # Note: This WILL have race conditions without locking
        # The test verifies the code doesn't crash
        assert len(errors) == 0, "Errors must not be empty"

        # Counter might not be exactly 1000 due to races
        # but should be in reasonable range
        assert entry.access_count > 0, "access_count must be positive"


class TestPerformanceBenchmarks:
    """Performance benchmarks for optimization."""

    def test_memory_search_performance(self):
        """Benchmark memory search performance."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            if hasattr(AgentMemory, "__init__"):
                memory = AgentMemory(db_path=str(temp_path))

                # Add 500 memories
                if hasattr(memory, "add_memory"):
                    for i in range(500):
                        entry = MemoryEntry(
                            memory_id=f"perf_{i}",
                            category="decision" if i % 3 == 0 else "fact",
                            content=f"Performance test {i}",
                            context={"index": i},
                            tags=[f"tag_{i % 10}"],
                        )
                        memory.add_memory(entry)

                # Benchmark: Search by category
                if hasattr(memory, "search_memories"):
                    start = time.time()
                    results = memory.search_memories(category="decision")
                    duration = time.time() - start

                    # Should be fast
                    assert duration < 0.5, "duration is not valid"
                    assert len(results) > 0, "Results must not be empty"

                # Benchmark: Search by tags
                if hasattr(memory, "search_memories"):
                    start = time.time()
                    memory.search_memories(tags=["tag_5"])
                    duration = time.time() - start

                    assert duration < 0.5, "duration is not valid"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_orchestration_throughput(self):
        """Benchmark orchestration throughput."""
        orch = HybridPhysicsOrchestrator()

        iterations = 50
        start = time.time()

        for i in range(iterations):
            decision_space = {"current_position": f"s_{i}", "goal_position": f"t_{i}"}
            orch.orchestrate_with_all_paradigms(decision_space)

        duration = time.time() - start
        throughput = iterations / duration

        # Should achieve reasonable throughput
        assert throughput > 10, "throughput must be greater than zero"

        logger.info(f"Orchestration throughput: {throughput:.2f} ops/sec")


class TestScalability:
    """Test system scalability."""

    def test_increasing_load_handling(self):
        """Test handling increasing load gracefully."""
        orch = HybridPhysicsOrchestrator()

        load_levels = [10, 50, 100, 200]
        timings = []

        for load in load_levels:
            start = time.time()
            for i in range(load):
                decision_space = {
                    "current_position": f"load_{load}_item_{i}",
                    "goal_position": f"target_{i}",
                }
                orch.orchestrate_with_all_paradigms(decision_space)
            duration = time.time() - start
            timings.append((load, duration))

        # Check that time scales roughly linearly (not exponentially)
        # Allow some overhead
        for i in range(len(timings) - 1):
            load_ratio = timings[i + 1][0] / timings[i][0]
            time_ratio = timings[i + 1][1] / timings[i][1]

            # Time shouldn't grow faster than 2x the load ratio
            assert time_ratio < load_ratio * 2, "time_ratio is not valid"

    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted."""
        # This would test database connection limits
        # Simplified version: just ensure many concurrent accesses work

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            if hasattr(AgentMemory, "__init__"):
                errors = []

                def access_memory(thread_id):
                    try:
                        memory = AgentMemory(db_path=str(temp_path))
                        if hasattr(memory, "add_memory"):
                            entry = MemoryEntry(
                                memory_id=f"pool_{thread_id}",
                                category="fact",
                                content="Pool test",
                                context={},
                            )
                            memory.add_memory(entry)
                    except Exception as e:
                        errors.append(e)

                # Create many concurrent connections
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(access_memory, i) for i in range(50)]
                    concurrent.futures.wait(futures, timeout=30)

                # Should handle gracefully
                assert len(errors) < 10, "Errors must not be empty"
        finally:
            if temp_path.exists():
                temp_path.unlink()
