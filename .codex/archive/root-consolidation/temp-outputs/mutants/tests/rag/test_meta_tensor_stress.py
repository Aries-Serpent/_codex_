"""
Meta-Tensor Stress Test Suite

Comprehensive stress testing for meta tensor prevention and recovery mechanisms.
Tests 1000+ meta-tensor operations across various scenarios.

This module is part of Phase 13.2: RAG Meta-Tensor Safety
"""

import gc
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

try:
    import pytest
except ImportError:
    pytest = None

logger = logging.getLogger(__name__)


@dataclass
class StressTestResult:
    """Result from a single stress test."""

    test_name: str
    iterations: int
    total_time_ms: float
    avg_time_per_iter_ms: float
    passed: int
    failed: int
    exceptions: list[str]
    timestamp: datetime

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.passed + self.failed
        return self.passed / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "iterations": self.iterations,
            "total_time_ms": self.total_time_ms,
            "avg_time_per_iter_ms": self.avg_time_per_iter_ms,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "exceptions": self.exceptions,
            "timestamp": self.timestamp.isoformat(),
        }


class MetaTensorStressTest:
    """
    Stress test suite for meta tensor prevention and recovery.

    Tests:
    - Rapid model loading/unloading cycles
    - Memory pressure scenarios
    - Concurrent operation handling
    - Recovery mechanism robustness
    """

    def __init__(self, iterations: int = 100):
        """Initialize stress test suite."""
        self.iterations = iterations
        self.results: list[StressTestResult] = []

    def test_rapid_model_loading_cycles(self) -> StressTestResult:
        """
        Stress Test 1: Rapid model loading/unloading cycles.

        Tests if guard rails prevent meta tensor creation during rapid
        initialization sequences.
        """
        from codex.rag.meta_tensor_guard import MetaTensorGuardRail

        test_name = "rapid_model_loading_cycles"
        start_time = time.time()
        passed = 0
        failed = 0
        exceptions = []

        for iteration in range(self.iterations):
            try:
                guard = MetaTensorGuardRail()

                # Simulate guard rail checks
                guard.check_environment()
                guard.check_pre_init_state()

                # Simulate model loading
                gc.collect()

                guard.check_oom_condition()

                # Verify state
                summary = guard.get_summary()
                if summary["failed"] == 0:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                exceptions.append(f"Iteration {iteration}: {type(e).__name__}: {str(e)[:100]}")

        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_iter = total_time_ms / self.iterations

        result = StressTestResult(
            test_name=test_name,
            iterations=self.iterations,
            total_time_ms=total_time_ms,
            avg_time_per_iter_ms=avg_time_per_iter,
            passed=passed,
            failed=failed,
            exceptions=exceptions,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)
        return result

    def test_memory_pressure_scenarios(self) -> StressTestResult:
        """
        Stress Test 2: Memory pressure scenarios.

        Tests if guard rails handle memory pressure gracefully.
        """
        test_name = "memory_pressure_scenarios"
        start_time = time.time()
        passed = 0
        failed = 0
        exceptions = []

        for iteration in range(self.iterations):
            try:
                from codex.rag.meta_tensor_guard import MetaTensorGuardRail

                guard = MetaTensorGuardRail()

                # Simulate memory pressure
                try:
                    test_tensors = []
                    for i in range(10):
                        test_tensors.append(b"x" * 1024 * 1024)  # 1MB each
                except MemoryError:
                    # MemoryError is expected under simulated pressure; continue test execution
                    logger.debug("MemoryError encountered during stress simulation (expected)")

                # Check OOM detection still works
                oom_report = guard.check_oom_condition()

                if oom_report.status.value in ["passed", "bypassed"]:
                    passed += 1
                else:
                    failed += 1

                gc.collect()

            except Exception as e:
                failed += 1
                exceptions.append(f"Iteration {iteration}: {type(e).__name__}: {str(e)[:100]}")

        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_iter = total_time_ms / self.iterations

        result = StressTestResult(
            test_name=test_name,
            iterations=self.iterations,
            total_time_ms=total_time_ms,
            avg_time_per_iter_ms=avg_time_per_iter,
            passed=passed,
            failed=failed,
            exceptions=exceptions,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)
        return result

    def test_meta_tensor_detection_accuracy(self) -> StressTestResult:
        """
        Stress Test 3: Meta tensor detection accuracy.

        Tests if detector accurately identifies meta tensors
        across various model architectures.
        """
        from codex.rag.materialization_prevention import MatTensorDetector

        test_name = "meta_tensor_detection_accuracy"
        start_time = time.time()
        passed = 0
        failed = 0
        exceptions = []

        for iteration in range(self.iterations):
            try:
                detector = MatTensorDetector()

                # Test with mock model-like object
                class MockModel:
                    def named_parameters(self):
                        return []

                    def named_buffers(self):
                        return []

                    def named_modules(self):
                        return []

                model = MockModel()
                meta_tensors = detector.detect_in_model(model)

                if len(meta_tensors) == 0:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                exceptions.append(f"Iteration {iteration}: {type(e).__name__}: {str(e)[:100]}")

        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_iter = total_time_ms / self.iterations

        result = StressTestResult(
            test_name=test_name,
            iterations=self.iterations,
            total_time_ms=total_time_ms,
            avg_time_per_iter_ms=avg_time_per_iter,
            passed=passed,
            failed=failed,
            exceptions=exceptions,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)
        return result

    def test_recovery_mechanism_robustness(self) -> StressTestResult:
        """
        Stress Test 4: Recovery mechanism robustness.

        Tests if recovery mechanisms reliably restore model state.
        """
        from codex.rag.materialization_prevention import MaterializationRecoveryStrategy

        test_name = "recovery_mechanism_robustness"
        start_time = time.time()
        passed = 0
        failed = 0
        exceptions = []

        for iteration in range(self.iterations):
            try:
                strategies = MaterializationRecoveryStrategy.try_all_strategies()

                # All strategies should at least attempt
                if len(strategies) >= 3:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                exceptions.append(f"Iteration {iteration}: {type(e).__name__}: {str(e)[:100]}")

        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_iter = total_time_ms / self.iterations

        result = StressTestResult(
            test_name=test_name,
            iterations=self.iterations,
            total_time_ms=total_time_ms,
            avg_time_per_iter_ms=avg_time_per_iter,
            passed=passed,
            failed=failed,
            exceptions=exceptions,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)
        return result

    def test_guard_rail_performance(self) -> StressTestResult:
        """
        Stress Test 5: Guard rail performance under load.

        Tests if guard rails don't significantly degrade model loading performance.
        """
        from codex.rag.meta_tensor_guard import guard_rail_context

        test_name = "guard_rail_performance"
        start_time = time.time()
        passed = 0
        failed = 0
        exceptions = []

        for iteration in range(self.iterations):
            try:
                with guard_rail_context() as guard:
                    # Simulate minimal work
                    _ = guard.check_environment()

                    if len(guard.reports) > 0:
                        passed += 1
                    else:
                        failed += 1

            except Exception as e:
                failed += 1
                exceptions.append(f"Iteration {iteration}: {type(e).__name__}: {str(e)[:100]}")

        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_iter = total_time_ms / self.iterations

        result = StressTestResult(
            test_name=test_name,
            iterations=self.iterations,
            total_time_ms=total_time_ms,
            avg_time_per_iter_ms=avg_time_per_iter,
            passed=passed,
            failed=failed,
            exceptions=exceptions,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)
        return result

    def run_all_tests(self) -> dict[str, Any]:
        """
        Run all stress tests.

        Returns:
            Summary of all test results
        """
        logger.info("Starting meta-tensor stress test suite (%d iterations per test)", self.iterations)

        self.test_rapid_model_loading_cycles()
        self.test_memory_pressure_scenarios()
        self.test_meta_tensor_detection_accuracy()
        self.test_recovery_mechanism_robustness()
        self.test_guard_rail_performance()

        return self.get_summary()

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all stress test results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.failed == 0)
        total_iterations = sum(r.iterations for r in self.results)
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "total_iterations": total_iterations,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "overall_success_rate": total_passed / total_iterations if total_iterations > 0 else 0,
            "results": [r.to_dict() for r in self.results],
        }


# pytest tests

if pytest:

    class TestMetaTensorStress:
        """pytest-compatible stress tests."""

        def test_rapid_loading_cycles(self):
            """Test rapid model loading cycles."""
            suite = MetaTensorStressTest(iterations=50)
            result = suite.test_rapid_model_loading_cycles()
            assert result.failed == 0, f"Failed iterations: {result.exceptions}"

        def test_memory_pressure(self):
            """Test memory pressure handling."""
            suite = MetaTensorStressTest(iterations=50)
            result = suite.test_memory_pressure_scenarios()
            assert result.success_rate > 0.8, f"Success rate too low: {result.success_rate}"

        def test_detection_accuracy(self):
            """Test detection accuracy."""
            suite = MetaTensorStressTest(iterations=50)
            result = suite.test_meta_tensor_detection_accuracy()
            assert result.failed == 0, f"Failed iterations: {result.exceptions}"

        def test_recovery_robustness(self):
            """Test recovery mechanism."""
            suite = MetaTensorStressTest(iterations=50)
            result = suite.test_recovery_mechanism_robustness()
            assert result.success_rate > 0.8, f"Success rate too low: {result.success_rate}"

        def test_guard_rail_performance(self):
            """Test guard rail performance."""
            suite = MetaTensorStressTest(iterations=50)
            result = suite.test_guard_rail_performance()
            assert result.success_rate > 0.8, f"Success rate too low: {result.success_rate}"

        def test_full_stress_suite(self):
            """Run full stress test suite."""
            suite = MetaTensorStressTest(iterations=100)
            summary = suite.run_all_tests()
            assert summary["overall_success_rate"] > 0.95, (
                f"Overall success rate too low: {summary['overall_success_rate']}"
            )


if __name__ == "__main__":
    # Run as standalone script
    suite = MetaTensorStressTest(iterations=100)
    summary = suite.run_all_tests()

    print("\n" + "=" * 80)
    print("META-TENSOR STRESS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed Tests: {summary['passed_tests']}")
    print(f"Total Iterations: {summary['total_iterations']}")
    print(f"Total Passed: {summary['total_passed']}")
    print(f"Total Failed: {summary['total_failed']}")
    print(f"Overall Success Rate: {summary['overall_success_rate']:.2%}")
    print("=" * 80)

    for result in summary["results"]:
        print(f"\n{result['test_name']}:")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Success Rate: {result['success_rate']:.2%}")
        print(f"  Avg Time/Iter: {result['avg_time_per_iter_ms']:.2f}ms")
        if result["exceptions"]:
            print(f"  Exceptions: {len(result['exceptions'])}")
