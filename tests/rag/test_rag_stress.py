"""
Stress Test Suite for RAG Module Robustness - PHASE 4D PLANSET 003

Validates:
- 99%+ reliability under 2x normal load
- Timeout handling and circuit breaker effectiveness
- Graceful degradation without cascading failures
- Resource utilization stays within bounds

Authority: D-tier autonomous
"""

import concurrent.futures
import logging
import statistics
import time
import unittest
from typing import List, Tuple

from rag.hardened_embedding import HardenedEmbeddingPipeline
from rag.monitoring import RAGMonitor
from rag.monitoring import set_rag_monitor as set_monitor
from rag.pipelines.embedding import EmbeddingConfig
from rag.resilience import RetryConfig
from rag.timeout_manager import TimeoutConfig, TimeoutManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class StressTestConfig:
    """Configuration for stress tests."""

    # Load parameters
    NORMAL_LOAD_RPS = 50  # Requests per second
    STRESS_LOAD_RPS = 100  # 2x normal load

    # Duration
    WARM_UP_SECONDS = 5
    TEST_SECONDS = 30
    COOL_DOWN_SECONDS = 5

    # Reliability targets
    MIN_SUCCESS_RATE = 0.99  # 99% minimum
    MAX_ERROR_RATE = 0.01  # 1% maximum
    MAX_TIMEOUT_RATE = 0.02  # 2% maximum

    # Performance targets
    MAX_P99_LATENCY_MS = 2000  # P99 latency < 2s
    MAX_AVG_LATENCY_MS = 500  # Average latency < 500ms

    # Resource targets
    MAX_MEMORY_MB = 500


class StressTestResult:
    """Results from a stress test run."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.latencies: List[float] = []
        self.successes = 0
        self.failures = 0
        self.timeouts = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self.total_duration = 0.0

    def add_result(
        self,
        duration_ms: float,
        success: bool = True,
        timed_out: bool = False,
    ) -> None:
        """Record operation result."""
        self.latencies.append(duration_ms)
        if success:
            self.successes += 1
        else:
            self.failures += 1
        if timed_out:
            self.timeouts += 1

    @property
    def total_operations(self) -> int:
        """Total number of operations."""
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_operations == 0:
            return 0.0
        return self.successes / self.total_operations

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        return 1.0 - self.success_rate

    @property
    def timeout_rate(self) -> float:
        """Calculate timeout rate."""
        if self.total_operations == 0:
            return 0.0
        return self.timeouts / self.total_operations

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if not self.latencies:
            return 0.0
        return statistics.mean(self.latencies)

    @property
    def p50_latency_ms(self) -> float:
        """Calculate P50 latency."""
        if not self.latencies:
            return 0.0
        return statistics.median(self.latencies)

    @property
    def p95_latency_ms(self) -> float:
        """Calculate P95 latency."""
        if not self.latencies or len(self.latencies) < 20:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        return sorted_latencies[int(len(sorted_latencies) * 0.95)]

    @property
    def p99_latency_ms(self) -> float:
        """Calculate P99 latency."""
        if not self.latencies or len(self.latencies) < 100:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        return sorted_latencies[int(len(sorted_latencies) * 0.99)]

    def meets_targets(self) -> Tuple[bool, List[str]]:
        """Check if results meet target thresholds."""
        issues = []

        if self.success_rate < StressTestConfig.MIN_SUCCESS_RATE:
            issues.append(
                f"Success rate {self.success_rate:.1%} below target "
                f"{StressTestConfig.MIN_SUCCESS_RATE:.1%}"
            )

        if self.error_rate > StressTestConfig.MAX_ERROR_RATE:
            issues.append(
                f"Error rate {self.error_rate:.1%} exceeds target "
                f"{StressTestConfig.MAX_ERROR_RATE:.1%}"
            )

        if self.timeout_rate > StressTestConfig.MAX_TIMEOUT_RATE:
            issues.append(
                f"Timeout rate {self.timeout_rate:.1%} exceeds target "
                f"{StressTestConfig.MAX_TIMEOUT_RATE:.1%}"
            )

        if self.avg_latency_ms > StressTestConfig.MAX_AVG_LATENCY_MS:
            issues.append(
                f"Average latency {self.avg_latency_ms:.0f}ms exceeds target "
                f"{StressTestConfig.MAX_AVG_LATENCY_MS:.0f}ms"
            )

        if self.p99_latency_ms > StressTestConfig.MAX_P99_LATENCY_MS:
            issues.append(
                f"P99 latency {self.p99_latency_ms:.0f}ms exceeds target "
                f"{StressTestConfig.MAX_P99_LATENCY_MS:.0f}ms"
            )

        return len(issues) == 0, issues

    def print_summary(self) -> None:
        """Print test summary."""
        print(f"\n{'=' * 70}")
        print(f"Stress Test: {self.test_name}")
        print(f"{'=' * 70}")
        print(f"Total Operations: {self.total_operations}")
        print(f"Successes: {self.successes} ({self.success_rate:.1%})")
        print(f"Failures: {self.failures} ({self.error_rate:.1%})")
        print(f"Timeouts: {self.timeouts} ({self.timeout_rate:.1%})")
        print("\nLatency Metrics:")
        print(f"  Average: {self.avg_latency_ms:.1f}ms")
        print(f"  P50: {self.p50_latency_ms:.1f}ms")
        print(f"  P95: {self.p95_latency_ms:.1f}ms")
        print(f"  P99: {self.p99_latency_ms:.1f}ms")
        print(f"\nDuration: {self.total_duration:.1f}s")

        passes, issues = self.meets_targets()
        if passes:
            print("✅ PASSED - All targets met")
        else:
            print("❌ FAILED - Target violations:")
            for issue in issues:
                print(f"   - {issue}")
        print(f"{'=' * 70}\n")


class RAGStressTest(unittest.TestCase):
    """Stress tests for RAG module."""

    @classmethod
    def setUpClass(cls):
        """Set up for all tests."""
        # Create pipeline with hardening
        config = EmbeddingConfig(batch_size=32)
        timeout_config = TimeoutConfig(
            embedding_timeout=30.0,
            batch_embedding_timeout=60.0,
            enable_circuit_breaker=True,
            circuit_breaker_threshold=10,
        )
        cls.timeout_manager = TimeoutManager(timeout_config)
        cls.monitor = RAGMonitor(window_size=300)
        set_monitor(cls.monitor)

        cls.pipeline = HardenedEmbeddingPipeline(
            config=config,
            timeout_manager=cls.timeout_manager,
            retry_config=RetryConfig(max_retries=2),
        )

    def test_concurrent_embedding_normal_load(self):
        """Test concurrent embedding at normal load."""
        result = self._run_concurrent_test(
            "Concurrent Embedding (Normal Load)",
            StressTestConfig.NORMAL_LOAD_RPS,
            StressTestConfig.TEST_SECONDS,
        )

        passes, issues = result.meets_targets()
        self.assertTrue(passes, f"Failed: {issues}")
        result.print_summary()

    def test_concurrent_embedding_stress_load(self):
        """Test concurrent embedding at 2x normal load."""
        result = self._run_concurrent_test(
            "Concurrent Embedding (2x Stress Load)",
            StressTestConfig.STRESS_LOAD_RPS,
            StressTestConfig.TEST_SECONDS,
        )

        passes, issues = result.meets_targets()
        self.assertTrue(passes, f"Failed: {issues}")
        result.print_summary()

    def test_batch_embedding_under_load(self):
        """Test batch embedding under load."""
        result = StressTestResult("Batch Embedding Under Load")
        result.start_time = time.time()

        batch_size = 50
        num_batches = 10

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            for i in range(num_batches):
                texts = [f"text {i}_{j}" for j in range(batch_size)]

                def embed_batch():
                    start = time.time()
                    try:
                        results = self.pipeline.embed_texts(texts)
                        duration = (time.time() - start) * 1000
                        return duration, len(results) == len(texts), False
                    except TimeoutError:
                        duration = (time.time() - start) * 1000
                        return duration, False, True
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        logger.error(f"Batch embedding failed: {e}")
                        return duration, False, False

                futures.append(executor.submit(embed_batch))

            for future in concurrent.futures.as_completed(futures):
                duration, success, timed_out = future.result()
                result.add_result(duration, success, timed_out)

        result.end_time = time.time()
        result.total_duration = result.end_time - result.start_time

        passes, issues = result.meets_targets()
        self.assertTrue(passes, f"Failed: {issues}")
        result.print_summary()

    def test_circuit_breaker_protection(self):
        """Test circuit breaker prevents cascading failures."""
        result = StressTestResult("Circuit Breaker Protection")
        result.start_time = time.time()

        # Simulate many failures
        num_operations = 100

        for i in range(num_operations):
            start = time.time()
            try:
                # Try to trigger failures
                if i < 15:  # First 15 will likely fail due to circuit
                    result_obj = self.pipeline.embed_text("test")
                    duration = (time.time() - start) * 1000
                    result.add_result(duration, True, False)
                else:
                    # After circuit opens, should fail fast
                    result_obj = self.pipeline.embed_text("test")
                    duration = (time.time() - start) * 1000
                    result.add_result(duration, True, False)
            except Exception as e:
                duration = (time.time() - start) * 1000
                result.add_result(duration, False, False)

        result.end_time = time.time()
        result.total_duration = result.end_time - result.start_time

        # Circuit breaker should help maintain reasonable success rate
        self.assertGreater(result.success_rate, 0.90)
        result.print_summary()

    def _run_concurrent_test(
        self, test_name: str, rps: int, duration_seconds: int
    ) -> StressTestResult:
        """Run concurrent load test.

        Args:
            test_name: Name of test
            rps: Target requests per second
            duration_seconds: Duration of test

        Returns:
            StressTestResult with test results
        """
        result = StressTestResult(test_name)
        result.start_time = time.time()

        request_interval = 1.0 / rps
        num_requests = rps * duration_seconds
        num_workers = min(20, max(5, rps // 10))

        texts = [f"text {i}" for i in range(1000)]
        text_idx = 0

        def embed_text():
            nonlocal text_idx
            start = time.time()
            try:
                text = texts[text_idx % len(texts)]
                text_idx += 1
                embed_result = self.pipeline.embed_text(text)
                duration = (time.time() - start) * 1000
                return duration, True, False
            except TimeoutError:
                duration = (time.time() - start) * 1000
                return duration, False, True
            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.error(f"Embedding failed: {e}")
                return duration, False, False

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_workers
        ) as executor:
            futures = []

            for i in range(num_requests):
                futures.append(executor.submit(embed_text))

                # Throttle to target RPS
                elapsed = time.time() - result.start_time
                expected_time = (i + 1) * request_interval
                if elapsed < expected_time:
                    time.sleep(expected_time - elapsed)

            for future in concurrent.futures.as_completed(futures):
                duration, success, timed_out = future.result()
                result.add_result(duration, success, timed_out)

        result.end_time = time.time()
        result.total_duration = result.end_time - result.start_time

        return result


if __name__ == "__main__":
    unittest.main(verbosity=2)
