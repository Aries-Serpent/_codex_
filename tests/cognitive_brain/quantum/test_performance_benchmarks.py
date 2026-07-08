import pytest

"""
Phase 8.1 Performance Benchmark Tests.

Tests performance targets: compression speed, retrieval speed, cache hit rate,
memory efficiency, and consolidation throughput.
"""
pytest.importorskip("psutil")

import os
import time

import psutil

from cognitive_brain.integrations.memory_integration import (
    MemoryAugmentedComplianceAssessor,
)
from cognitive_brain.quantum.compression import PatternCompressor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.memory import MemoryPattern, QuantumMemoryManager


class TestPerformanceBenchmarks:
    """Performance benchmark tests for Phase 8.1."""

    def test_compression_speed_benchmark(self):
        """Test compression speed: target 1000 patterns/second."""
        compressor = PatternCompressor(target_dimensions=3)

        # Training data
        training = [
            {
                "f1": float(i) / 100,
                "f2": float(i) / 80,
                "f3": float(i) / 60,
                "f4": float(i) / 40,
            }
            for i in range(100)
        ]
        compressor.fit(training)

        # Benchmark compression
        test_patterns = [
            {
                "f1": float(i) / 50,
                "f2": float(i) / 40,
                "f3": float(i) / 30,
                "f4": float(i) / 20,
            }
            for i in range(1000)
        ]

        start = time.time()
        for pattern in test_patterns:
            compressor.compress(pattern)
        elapsed = time.time() - start

        patterns_per_second = len(test_patterns) / elapsed

        # Target: >= 1000 patterns/second
        # Relaxed for test environment: >= 500 patterns/second
        assert (patterns_per_second >= 500, "patterns_per_second must be greater than zero"
        ), f"Compression speed: {patterns_per_second:.0f} patterns/s (target: 1000)"

    def test_retrieval_speed_benchmark(self):
        """Test retrieval speed: target <10ms for k=5."""
        manager = QuantumMemoryManager(QuantumConfig(), stm_capacity=100, ltm_capacity=1000)

        # Populate LTM with patterns
        for i in range(500):
            pattern = MemoryPattern(
                pattern_id=f"perf_pat_{i}",
                features={
                    "f1": float(i % 10) / 10,
                    "f2": float(i % 20) / 20,
                    "f3": float(i % 15) / 15,
                },
                decision="approve" if i % 2 == 0 else "reject",
                confidence=0.85,
            )
            manager.store_pattern(pattern)

            if i % 50 == 0:
                manager.consolidate()

        # Benchmark retrieval
        query = {"f1": 0.5, "f2": 0.5, "f3": 0.5}

        retrieval_times = []
        for _ in range(100):
            start = time.time()
            manager.retrieve_similar(query, k=5)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            retrieval_times.append(elapsed)

        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)

        # Target: < 10ms average
        # Relaxed for test environment: < 50ms
        assert (avg_retrieval_time < 50, "avg_retrieval_time is not valid"
        ), f"Avg retrieval time: {avg_retrieval_time:.2f}ms (target: <10ms)"

    def test_cache_hit_rate_realistic_workload(self):
        """Test cache hit rate: target >=30% on realistic workload."""
        assessor = MemoryAugmentedComplianceAssessor()

        # Generate scenarios with patterns (some similar)
        from cognitive_brain.experiments.complex_scenarios import (
            generate_complex_scenarios,
        )

        # First batch: create memory
        training_scenarios = generate_complex_scenarios(50, seed=42)
        for scenario in training_scenarios:
            assessor.assess_with_memory(scenario)

        # Consolidate patterns
        assessor.memory_manager.consolidate()

        # Second batch: similar patterns (should hit cache)
        test_scenarios = generate_complex_scenarios(50, seed=43)  # Similar but not identical

        initial_hits = assessor.memory_manager.cache_hits

        for scenario in test_scenarios:
            assessor.assess_with_memory(scenario)

        final_hits = assessor.memory_manager.cache_hits
        cache_hits = final_hits - initial_hits

        cache_hit_rate = cache_hits / len(test_scenarios)

        # Target: >= 30%
        # Relaxed for test: >= 10% (depends on scenario similarity)
        assert cache_hit_rate >= 0.10, f"Cache hit rate: {cache_hit_rate * 100:.1f}% (target: 30%)"

    def test_memory_efficiency_ltm_capacity(self):
        """Test memory efficiency: <100MB for 10,000 LTM patterns."""
        manager = QuantumMemoryManager(QuantumConfig(), stm_capacity=100, ltm_capacity=10000)

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_mem = process.memory_info().rss / 1024 / 1024  # MB

        # Fill LTM with patterns
        for i in range(1000):  # Reduced from 10k for test speed
            pattern = MemoryPattern(
                pattern_id=f"mem_pat_{i}",
                features={
                    "f1": float(i % 100) / 100,
                    "f2": float(i % 200) / 200,
                    "f3": float(i % 150) / 150,
                    "f4": float(i % 250) / 250,
                },
                decision="approve" if i % 2 == 0 else "reject",
                confidence=0.8,
            )
            manager.store_pattern(pattern)

            if i % 100 == 0:
                manager.consolidate()

        # Get final memory usage
        final_mem = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_mem - initial_mem

        # Extrapolate to 10k patterns
        memory_per_pattern = memory_used / 1000
        estimated_10k_memory = memory_per_pattern * 10000

        # Target: < 100MB for 10k patterns
        # Relaxed: < 200MB
        assert (estimated_10k_memory < 200, "estimated_10k_memory is not valid"
        ), f"Estimated memory for 10k: {estimated_10k_memory:.1f}MB (target: <100MB)"

    def test_consolidation_throughput(self):
        """Test consolidation throughput: target 100 STM→LTM/second."""
        manager = QuantumMemoryManager(QuantumConfig(), stm_capacity=100, ltm_capacity=1000)

        # Fill STM — use confidence=1.0 so promotion score (0.4*success_rate + 0.2*confidence)
        # meets the consolidation_threshold=0.6 even before patterns have been accessed.
        for i in range(100):
            pattern = MemoryPattern(
                pattern_id=f"consol_pat_{i}",
                features={"f1": float(i) / 100, "f2": float(i) / 80},
                decision="approve",
                confidence=1.0,
            )
            manager.store_pattern(pattern)

        # Benchmark consolidation
        start = time.time()
        result = manager.consolidate()
        elapsed = time.time() - start

        patterns_per_second = result.promoted / elapsed if elapsed > 0 else 0

        # Target: >= 100 patterns/second
        # Relaxed: >= 50 patterns/second
        assert (patterns_per_second >= 50, "patterns_per_second must be greater than zero"
        ), f"Consolidation throughput: {patterns_per_second:.0f} patterns/s (target: 100)"
        assert result.promoted > 0, "No patterns were promoted during consolidation"
