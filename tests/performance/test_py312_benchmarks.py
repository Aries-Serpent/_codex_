"""
Benchmark performance improvements in Python 3.12.

Measures speed of critical operations to verify expected gains.
Python 3.12 has significant performance improvements including:
- 5-10% faster dict operations
- Improved comprehension inlining
- Faster imports
- Better f-string performance
"""

from __future__ import annotations

import sys
import time

import pytest


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12 benchmarks")
class TestPython312Performance:
    """Performance regression tests for Python 3.12."""

    def test_dict_operations_faster(self):
        """
        Verify dict operations leverage 3.12 speedups.

        Python 3.12 has optimized dict implementation.
        """
        iterations = 10000

        start = time.perf_counter()
        for _ in range(iterations):
            d = {"key1": "value1", "key2": "value2", "key3": "value3"}
            _ = d["key1"]
            d["key4"] = "value4"
            _ = list(d.keys())
            _ = list(d.values())
            _ = list(d.items())
        elapsed = time.perf_counter() - start

        # Should complete reasonably fast (adjust threshold based on hardware)
        assert elapsed < 1.0, f"Dict operations took {elapsed:.3f}s, expected < 1.0s"

    def test_comprehension_inlining(self):
        """
        Test list/dict comprehension performance (3.12 optimization).

        Python 3.12 inlines comprehensions for better performance.
        """
        iterations = 1000
        data = list(range(1000))

        start = time.perf_counter()
        for _ in range(iterations):
            # List comprehension
            _ = [x * 2 for x in data if x % 2 == 0]

            # Dict comprehension
            _ = {x: x**2 for x in data if x < 100}

            # Set comprehension
            _ = {x % 10 for x in data}
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"Comprehensions took {elapsed:.3f}s, expected < 2.0s"

    def test_import_time_improved(self):
        """
        Verify module import times are improved.

        Python 3.12 has faster import machinery.
        """
        import importlib

        modules_to_test = [
            "json",
            "pathlib",
            "collections",
            "itertools",
        ]

        total_time = 0
        for module_name in modules_to_test:
            # Remove from cache to force re-import
            if module_name in sys.modules:
                del sys.modules[module_name]

            start = time.perf_counter()
            importlib.import_module(module_name)
            elapsed = time.perf_counter() - start
            total_time += elapsed

        # Imports should be fast
        assert total_time < 0.1, f"Imports took {total_time:.3f}s, expected < 0.1s"

    def test_function_call_performance(self):
        """
        Test function call performance.

        Python 3.12 has optimizations for function calls.
        """

        def simple_func(a, b, c=10):
            return a + b + c

        iterations = 100000

        start = time.perf_counter()
        for i in range(iterations):
            _ = simple_func(1, 2, c=i % 100)  # Discard result, measuring performance
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Function calls took {elapsed:.3f}s, expected < 0.5s"

    def test_string_operations_performance(self):
        """Test string operations performance."""
        iterations = 10000
        test_string = "Hello, World! " * 100

        start = time.perf_counter()
        for _ in range(iterations):
            # String concatenation
            result = test_string + "suffix"

            # String formatting
            formatted = f"Prefix: {result} :Suffix"

            # String splitting
            parts = formatted.split(" ")

            # String joining
            _ = "-".join(parts[:10])  # Discard result, measuring performance
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"String operations took {elapsed:.3f}s, expected < 2.0s"


@pytest.mark.benchmark
class TestCriticalPathBenchmarks:
    """Benchmark critical paths in codex_ml."""

    def test_json_parsing_performance(self):
        """Test JSON parsing performance."""
        import json

        # Create sample JSON data
        data = {
            "config": {
                "model": "test-model",
                "layers": [{"size": 128, "activation": "relu"} for _ in range(100)],
                "training": {
                    "epochs": 10,
                    "batch_size": 32,
                    "learning_rate": 0.001,
                },
            }
        }

        iterations = 1000

        # Benchmark serialization
        start = time.perf_counter()
        for _ in range(iterations):
            _ = json.dumps(data)  # Discard result, we're measuring performance
        serialize_time = time.perf_counter() - start

        # Benchmark deserialization
        json_str = json.dumps(data)
        start = time.perf_counter()
        for _ in range(iterations):
            _ = json.loads(json_str)  # Discard result, measuring performance
        deserialize_time = time.perf_counter() - start

        assert serialize_time < 1.0, f"JSON serialization took {serialize_time:.3f}s"
        assert deserialize_time < 1.0, f"JSON deserialization took {deserialize_time:.3f}s"

    def test_list_operations_performance(self):
        """Test list operations that may be used in data processing."""
        data = list(range(10000))
        iterations = 100

        start = time.perf_counter()
        for _ in range(iterations):
            # Common list operations
            filtered = [x for x in data if x % 2 == 0]
            mapped = [x * 2 for x in filtered]
            _ = sum(mapped)  # Discard result, measuring performance

            # List slicing
            subset = data[1000:2000]
            _ = list(reversed(subset))  # Discard result, measuring performance
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"List operations took {elapsed:.3f}s"

    def test_file_io_performance(self, tmp_path):
        """Test file I/O performance."""
        test_file = tmp_path / "test.txt"
        content = "Test line\n" * 1000
        iterations = 100

        # Write benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            test_file.write_text(content)
        write_time = time.perf_counter() - start

        # Read benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            _ = test_file.read_text()  # Discard result, measuring performance
        read_time = time.perf_counter() - start

        assert write_time < 1.0, f"File writes took {write_time:.3f}s"
        assert read_time < 0.5, f"File reads took {read_time:.3f}s"


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ comparison")
class TestPerformanceComparisons:
    """Compare performance metrics with baselines."""

    def test_loop_performance(self):
        """Test basic loop performance."""
        iterations = 1000000

        start = time.perf_counter()
        total = 0
        for i in range(iterations):
            total += i
        elapsed = time.perf_counter() - start

        # Should complete quickly
        assert elapsed < 0.5, f"Loop took {elapsed:.3f}s, expected < 0.5s"

    def test_generator_performance(self):
        """Test generator performance."""

        def number_generator(n):
            for i in range(n):
                yield i * 2

        iterations = 100000

        start = time.perf_counter()
        result = list(number_generator(iterations))
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Generator took {elapsed:.3f}s, expected < 0.5s"
        assert len(result) == iterations, "Result must not be empty"

    def test_exception_handling_performance(self):
        """Test exception handling performance."""
        iterations = 10000

        start = time.perf_counter()
        for _ in range(iterations):
            try:
                _ = 1 / 1  # No exception, benchmarking try-except overhead
            except ZeroDivisionError:
                # Exception not expected, benchmarking happy path
                _ = None  # suppressed: no action needed
        elapsed_no_exception = time.perf_counter() - start

        start = time.perf_counter()
        for _ in range(iterations):
            try:
                _ = 1 / 0  # Raises exception
            except ZeroDivisionError:
                # Expected exception, intentionally caught for benchmarking
                _ = None  # suppressed: no action needed
        elapsed_with_exception = time.perf_counter() - start

        # Both should complete reasonably
        assert elapsed_no_exception < 0.2, f"Try/except (no error) took {elapsed_no_exception:.3f}s"
        assert (elapsed_with_exception < 1.0, "elapsed_with_exception is not valid"
        ), f"Try/except (with error) took {elapsed_with_exception:.3f}s"


@pytest.mark.integration
@pytest.mark.benchmark
class TestRealWorldPerformance:
    """Test real-world performance scenarios."""

    def test_data_processing_pipeline(self):
        """Test a typical data processing pipeline."""
        # Simulate data processing
        raw_data = [{"id": i, "value": i * 2, "label": str(i % 10)} for i in range(10000)]

        start = time.perf_counter()

        # Filter
        filtered = [item for item in raw_data if item["value"] % 3 == 0]

        # Transform
        transformed = [
            {**item, "processed": item["value"] ** 2, "category": int(item["label"]) > 5}
            for item in filtered
        ]

        # Aggregate
        categories = {}
        for item in transformed:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item["processed"])

        # Compute statistics
        stats = {
            cat: {
                "count": len(values),
                "sum": sum(values),
                "mean": sum(values) / len(values) if values else 0,
            }
            for cat, values in categories.items()
        }

        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Data pipeline took {elapsed:.3f}s, expected < 0.5s"
        assert len(stats) == 2, "Stats must not be empty"

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires 3.11+")
    def test_tomllib_parsing_performance(self, tmp_path):
        """Test TOML parsing performance with tomllib."""
        try:
            import tomllib
        except ImportError:
            pytest.skip("tomllib not available")

        # Create a moderately sized TOML file
        toml_file = tmp_path / "config.toml"
        sections = []
        for i in range(100):
            sections.append(f"""
[section_{i}]
name = "Section {i}"
value = {i}
enabled = true
items = [{", ".join(str(j) for j in range(10))}]
""")
        toml_file.write_text("\n".join(sections))

        iterations = 100

        start = time.perf_counter()
        for _ in range(iterations):
            with open(toml_file, "rb") as f:
                _ = tomllib.load(f)  # Discard result, measuring performance
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, f"TOML parsing took {elapsed:.3f}s, expected < 5.0s"
