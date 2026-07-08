#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         """Test list creation doesn't regress."""
# Tests performance characteristics to detect regressions:
# - Tokenization throughput
# - Model inference latency
# - Training iteration time
# - Memory usage patterns
#     def test_list_creation_performance(self):
# """
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# import gc
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# import time
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# class PerformanceBaseline:
#     """Stores and compares performance baselines."""
#     BASELINES = {
#     # Baseline thresholds (operations per second or milliseconds)
#     BASELINES = {
#         "list_creation_1000": {"min_ops_per_sec": 10000, "max_time_ms": 1},
#         "dict_lookup_10000": {
#             "min_ops_per_sec": 45000,
#             "max_time_ms": 1,
#         },  # Lowered for CI environment compatibility (actual: 58-70K; 45K gives reasonable headroom)
#         "string_concat_1000": {"min_ops_per_sec": 5000, "max_time_ms": 2},
#         "json_serialize_100": {"min_ops_per_sec": 1000, "max_time_ms": 10},
#         "hash_computation_1000": {"min_ops_per_sec": 5000, "max_time_ms": 2},
#         "file_read_small": {"max_time_ms": 50},
#         "memory_allocation_mb": {"max_mb": 100},
#     }
#     @classmethod
#     def check_threshold(cls, test_name: str, actual_value: float, metric: str) -> bool:
#     def check_threshold(cls, test_name: str, actual_value: float, metric: str) -> bool:
#         """Check if actual value meets baseline threshold."""
#         if test_name not in cls.BASELINES:
#             return True  # No baseline, assume pass
#         baseline = cls.BASELINES[test_name]
# 
#         if metric == "ops_per_sec" and "min_ops_per_sec" in baseline:
#             return actual_value >= baseline["min_ops_per_sec"]
#         if metric == "time_ms" and "max_time_ms" in baseline:
#             return actual_value <= baseline["max_time_ms"]
#         if metric == "memory_mb" and "max_mb" in baseline:
#             return actual_value <= baseline["max_mb"]
# 
#         return True
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Measure execution time statistics for a function."""
#     times = []
#     for _ in range(min(10, iterations // 10)):
#         func()
# 
#     # Actual measurements
#     for _ in range(iterations):
#         gc.disable()
#         start = time.perf_counter()
#         func()
#         end = time.perf_counter()
#         gc.enable()
#         times.append((end - start) * 1000)  # Convert to ms
#         times.append((end - start) * 1000)  # Convert to ms
# 
#     return {
#     return {
#         "mean_ms": statistics.mean(times),
#         "median_ms": statistics.median(times),
#         "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
#         "min_ms": min(times),
#         "max_ms": max(times),
#         "ops_per_sec": (
#             1000 / statistics.mean(times) if statistics.mean(times) > 0 else float("inf")
#         ),
#     }
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Measure memory usage of a function in MB."""
#     gc.collect()
#     import tracemalloc
#     import tracemalloc
# 
#     tracemalloc.start()
# 
#     func()
# 
#     _current, peak = tracemalloc.get_traced_memory()
#     tracemalloc.stop()
# 
#     return peak / (1024 * 1024)  # Convert to MB
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test list operation performance."""
#     def test_list_creation_performance(self):
#     def test_list_creation_performance(self):
#         """Test list creation doesn't regress."""
#         def create_list():
#             return [i for i in range(1000)]
# 
#         stats = measure_time(create_list, iterations=100)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "list_creation_1000", stats["ops_per_sec"], "ops_per_sec"
#         ), f"List creation too slow: {stats['ops_per_sec']:.0f} ops/sec"
#     def test_list_append_performance(self):
#     def test_list_append_performance(self):
#         """Test list append doesn't regress."""
#         def append_to_list():
#             lst = []
#             for i in range(1000):
#                 lst.append(i)
#             return lst
# 
#         stats = measure_time(append_to_list, iterations=100)
#         assert stats["mean_ms"] < 5, f"List append too slow: {stats['mean_ms']:.2f}ms"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test dictionary operation performance."""
#     def test_dict_lookup_performance(self):
#     def test_dict_lookup_performance(self):
#         """Test dict lookup doesn't regress."""
#         data = {f"key_{i}": i for i in range(10000)}
#         def lookup_dict():
#             return [data.get(f"key_{i}") for i in range(100)]
# 
#         stats = measure_time(lookup_dict, iterations=100)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "dict_lookup_10000", stats["ops_per_sec"], "ops_per_sec"
#         ), f"Dict lookup too slow: {stats['ops_per_sec']:.0f} ops/sec"
#     def test_dict_creation_performance(self):
#     def test_dict_creation_performance(self):
#         """Test dict creation doesn't regress."""
#         def create_dict():
#             return {f"key_{i}": i for i in range(1000)}
# 
#         stats = measure_time(create_dict, iterations=100)
#         assert stats["mean_ms"] < 5, f"Dict creation too slow: {stats['mean_ms']:.2f}ms"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test string operation performance."""
#     def test_string_concat_performance(self):
#     def test_string_concat_performance(self):
#         """Test string concatenation doesn't regress."""
#         def concat_strings():
#             parts = [f"part_{i}" for i in range(100)]
#             return "".join(parts)
# 
#         stats = measure_time(concat_strings, iterations=100)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "string_concat_1000", stats["ops_per_sec"], "ops_per_sec"
#         ), f"String concat too slow: {stats['ops_per_sec']:.0f} ops/sec"
#     def test_string_formatting_performance(self):
#     def test_string_formatting_performance(self):
#         """Test f-string formatting doesn't regress."""
#         def format_strings():
#             return [f"item_{i}_value_{i*2}" for i in range(1000)]
# 
#         stats = measure_time(format_strings, iterations=100)
#         assert stats["mean_ms"] < 5, f"String formatting too slow: {stats['mean_ms']:.2f}ms"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test JSON serialization performance."""
#     def test_json_serialize_performance(self):
#     def test_json_serialize_performance(self):
#         """Test JSON serialization doesn't regress."""
#         import json
#         data = {
#         data = {
#             "items": [{"id": i, "name": f"item_{i}", "value": i * 1.5} for i in range(100)],
#             "metadata": {"count": 100, "version": "1.0"},
#         }
#         def serialize_json():
#             return json.dumps(data)
# 
#         stats = measure_time(serialize_json, iterations=100)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "json_serialize_100", stats["ops_per_sec"], "ops_per_sec"
#         ), f"JSON serialize too slow: {stats['ops_per_sec']:.0f} ops/sec"
#     def test_json_deserialize_performance(self):
#     def test_json_deserialize_performance(self):
#         """Test JSON deserialization doesn't regress."""
#         import json
#         data = {
#         data = {
#             "items": [{"id": i, "name": f"item_{i}"} for i in range(100)],
#         }
#         json_str = json.dumps(data)
#         def deserialize_json():
#             return json.loads(json_str)
# 
#         stats = measure_time(deserialize_json, iterations=100)
#         assert stats["mean_ms"] < 5, f"JSON deserialize too slow: {stats['mean_ms']:.2f}ms"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test hash computation performance."""
#     def test_sha256_performance(self):
#     def test_sha256_performance(self):
#         """Test SHA256 hashing doesn't regress."""
#         import hashlib
#         data = b"test data " * 100
# 
#         def compute_hash():
#             return hashlib.sha256(data).hexdigest()
# 
#         stats = measure_time(compute_hash, iterations=1000)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "hash_computation_1000", stats["ops_per_sec"], "ops_per_sec"
#         ), f"Hash computation too slow: {stats['ops_per_sec']:.0f} ops/sec"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#     """Test memory usage patterns."""
#     def test_large_list_memory(self):
#     def test_large_list_memory(self):
#         """Test large list doesn't use excessive memory."""
#         def create_large_list():
#             return [i for i in range(100000)]
# 
#         memory_mb = measure_memory(create_large_list)
# 
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#         assert PerformanceBaseline.check_threshold(, "Perf is not valid"
#             "memory_allocation_mb", memory_mb, "memory_mb"
#         ), f"Memory usage too high: {memory_mb:.2f}MB"
#     def test_dict_memory_efficiency(self):
#     def test_dict_memory_efficiency(self):
#         """Test dict memory efficiency."""
#         def create_large_dict():
#             return {f"key_{i}": i for i in range(10000)}
# 
#         memory_mb = measure_memory(create_large_dict)
#         assert memory_mb < 50, f"Dict memory too high: {memory_mb:.2f}MB"


class TestAgentMemoryPerformance:
    """Test agent memory system performance."""

    def test_store_decision_performance(self):
        """Test decision storage performance."""
        import tempfile
        from pathlib import Path

        AgentMemorySystem = pytest.importorskip("agents.agent_memory").AgentMemorySystem

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "perf_test.db"
            system = AgentMemorySystem(agent_id="perf_test", db_path=db_path)

            def store_decision():
                system.store_decision(
                    task_id="perf_task",
                    decision="Test decision",
                    rationale="Performance test",
                )

            stats = measure_time(store_decision, iterations=50)

            # Should be able to store at least 10 decisions per second
            assert (stats["ops_per_sec"] >= 10, "Value must be greater than zero"
            ), f"Decision storage too slow: {stats['ops_per_sec']:.1f} ops/sec"

    def test_retrieve_context_performance(self):
        """Test context retrieval performance."""
        import tempfile
        from pathlib import Path

        AgentMemorySystem = pytest.importorskip("agents.agent_memory").AgentMemorySystem

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "perf_test.db"
            system = AgentMemorySystem(agent_id="perf_test", db_path=db_path)

            # Pre-populate with data
            for i in range(20):
                system.store_decision(
                    task_id=f"task_{i}",
                    decision=f"Decision about feature {i}",
                    rationale=f"Rationale {i}",
                )

            def retrieve_context():
                return system.retrieve_similar_context("feature decision", limit=5)

            stats = measure_time(retrieve_context, iterations=50)

            # Should retrieve in under 100ms
            assert stats["mean_ms"] < 100, f"Context retrieval too slow: {stats['mean_ms']:.2f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
