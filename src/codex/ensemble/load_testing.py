"""Load testing framework for ensemble prediction API."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

import numpy as np

from src.codex.ensemble.ensemble_predictor import EnsemblePredictor, EnsembleConfig

logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load testing."""

    target_rps: int = 1000  # Requests per second
    duration_seconds: int = 300  # 5 minutes steady state
    ramp_up_seconds: int = 60  # Ramp-up time
    warmup_seconds: int = 30  # Warmup time
    max_workers: int = 100
    timeout_seconds: int = 10
    p99_latency_threshold_ms: float = 200.0
    p95_latency_threshold_ms: float = 100.0
    error_rate_threshold: float = 0.05  # 5% max error rate


@dataclass
class LoadTestResult:
    """Results from load test execution."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    total_duration_seconds: float
    actual_rps: float
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    p99_meets_sla: bool
    p95_meets_sla: bool
    error_rate_acceptable: bool


class LoadTester:
    """Load testing framework for prediction API."""

    def __init__(self, predictor: EnsemblePredictor, config: LoadTestConfig):
        """Initialize load tester.

        Args:
            predictor: EnsemblePredictor instance
            config: LoadTestConfig instance
        """
        self.predictor = predictor
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)

    def generate_test_features(self) -> Dict[str, Any]:
        """Generate random test features.

        Returns:
            Feature dictionary for prediction
        """
        return {
            "confidence": np.random.uniform(0.2, 0.95),
            "frequency": np.random.randint(10, 100),
            "days_old": np.random.randint(0, 90),
            "priority": np.random.randint(1, 10),
            "category": np.random.choice(["critical", "urgent", "high", "general", "low"]),
        }

    def make_prediction(self) -> Tuple[bool, float]:
        """Make a single prediction and measure latency.

        Returns:
            Tuple of (success: bool, latency_ms: float)
        """
        start_time = time.time()
        try:
            features = self.generate_test_features()
            self.predictor.predict(features)
            latency_ms = (time.time() - start_time) * 1000
            return True, latency_ms
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(f"Prediction failed: {e}")
            return False, latency_ms

    def warmup(self) -> None:
        """Warmup: prepare the models and system."""
        logger.info(f"Starting warmup for {self.config.warmup_seconds} seconds...")
        start_time = time.time()
        warmup_count = 0

        while time.time() - start_time < self.config.warmup_seconds:
            success, _ = self.make_prediction()
            if success:
                warmup_count += 1

        logger.info(f"Warmup complete: {warmup_count} successful predictions")

    def ramp_up(self) -> None:
        """Ramp up: gradually increase request rate."""
        logger.info(f"Starting ramp-up for {self.config.ramp_up_seconds} seconds...")
        start_time = time.time()
        ramp_count = 0

        while time.time() - start_time < self.config.ramp_up_seconds:
            # Gradually increase parallelism
            elapsed = time.time() - start_time
            progress = elapsed / self.config.ramp_up_seconds
            current_parallelism = max(1, int(self.config.max_workers * progress))

            futures = [self.executor.submit(self.make_prediction) for _ in range(current_parallelism)]
            for future in as_completed(futures):
                try:
                    success, _ = future.result(timeout=self.config.timeout_seconds)
                    if success:
                        ramp_count += 1
                except Exception as e:
                    logger.warning(f"Ramp-up request failed: {e}")

        logger.info(f"Ramp-up complete: {ramp_count} successful predictions")

    def steady_state(self) -> List[Tuple[bool, float]]:
        """Execute steady state: maintain constant RPS.

        Returns:
            List of (success, latency_ms) tuples
        """
        logger.info(
            f"Starting steady state for {self.config.duration_seconds}s "
            f"at {self.config.target_rps} RPS..."
        )

        results = []
        start_time = time.time()
        request_count = 0
        batch_start = time.time()

        while time.time() - start_time < self.config.duration_seconds:
            # Calculate how many requests to submit in this batch
            elapsed = time.time() - batch_start
            target_batch_count = int((elapsed + 0.001) * (self.config.target_rps / 1000.0))
            to_submit = max(0, target_batch_count - request_count)

            if to_submit > 0:
                futures = [self.executor.submit(self.make_prediction) for _ in range(to_submit)]
                request_count += to_submit

                # Collect results as they complete
                for future in as_completed(futures, timeout=self.config.timeout_seconds):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Request failed: {e}")
                        results.append((False, self.config.timeout_seconds * 1000))

            # Small sleep to prevent busy-waiting
            time.sleep(0.001)

        logger.info(f"Steady state complete: {len(results)} total requests")
        return results

    def run_load_test(self) -> LoadTestResult:
        """Run complete load test sequence.

        Returns:
            LoadTestResult with all metrics
        """
        overall_start = time.time()

        try:
            # Phase 1: Warmup
            self.warmup()

            # Phase 2: Ramp-up
            self.ramp_up()

            # Phase 3: Steady state
            steady_state_results = self.steady_state()

            # Collect all latencies
            latencies = [latency for _, latency in steady_state_results]
            successes = sum(1 for success, _ in steady_state_results if success)
            failures = len(steady_state_results) - successes

            overall_duration = time.time() - overall_start

            # Calculate metrics
            if latencies:
                latencies_array = np.array(latencies)
                p99_latency = float(np.percentile(latencies_array, 99))
                p95_latency = float(np.percentile(latencies_array, 95))
            else:
                p99_latency = float("inf")
                p95_latency = float("inf")

            error_rate = failures / len(steady_state_results) if steady_state_results else 0.0
            actual_rps = len(steady_state_results) / (overall_duration - self.config.warmup_seconds - self.config.ramp_up_seconds)

            result = LoadTestResult(
                total_requests=len(steady_state_results),
                successful_requests=successes,
                failed_requests=failures,
                error_rate=error_rate,
                total_duration_seconds=overall_duration,
                actual_rps=actual_rps,
                min_latency_ms=float(np.min(latencies_array)) if latencies else 0.0,
                max_latency_ms=float(np.max(latencies_array)) if latencies else 0.0,
                mean_latency_ms=float(np.mean(latencies_array)) if latencies else 0.0,
                median_latency_ms=float(np.median(latencies_array)) if latencies else 0.0,
                p50_latency_ms=float(np.percentile(latencies_array, 50)) if latencies else 0.0,
                p95_latency_ms=p95_latency,
                p99_latency_ms=p99_latency,
                throughput_rps=len(steady_state_results) / self.config.duration_seconds,
                p99_meets_sla=p99_latency < self.config.p99_latency_threshold_ms,
                p95_meets_sla=p95_latency < self.config.p95_latency_threshold_ms,
                error_rate_acceptable=error_rate < self.config.error_rate_threshold,
            )

            return result

        finally:
            self.executor.shutdown(wait=True)

    def print_results(self, result: LoadTestResult) -> None:
        """Print load test results.

        Args:
            result: LoadTestResult object
        """
        print("\n" + "=" * 70)
        print("LOAD TEST RESULTS")
        print("=" * 70)
        print(f"\nRequest Summary:")
        print(f"  Total Requests:       {result.total_requests:,}")
        print(f"  Successful:           {result.successful_requests:,}")
        print(f"  Failed:               {result.failed_requests:,}")
        print(f"  Error Rate:           {result.error_rate:.2%}")
        print(f"\nTiming Metrics:")
        print(f"  Total Duration:       {result.total_duration_seconds:.2f}s")
        print(f"  Actual RPS:           {result.actual_rps:.1f} req/s")
        print(f"  Throughput:           {result.throughput_rps:.1f} req/s")
        print(f"\nLatency Percentiles (ms):")
        print(f"  Min:                  {result.min_latency_ms:.2f}ms")
        print(f"  P50 (Median):         {result.p50_latency_ms:.2f}ms")
        print(f"  P95:                  {result.p95_latency_ms:.2f}ms (SLA: {result.p95_meets_sla})")
        print(f"  P99:                  {result.p99_latency_ms:.2f}ms (SLA: {result.p99_meets_sla})")
        print(f"  Max:                  {result.max_latency_ms:.2f}ms")
        print(f"  Mean:                 {result.mean_latency_ms:.2f}ms")
        print(f"\nSLA Compliance:")
        print(f"  P99 Latency <200ms:   {'✓ PASS' if result.p99_meets_sla else '✗ FAIL'}")
        print(f"  P95 Latency <100ms:   {'✓ PASS' if result.p95_meets_sla else '✗ FAIL'}")
        print(f"  Error Rate <5%:       {'✓ PASS' if result.error_rate_acceptable else '✗ FAIL'}")
        print(f"\nOverall:               {'✓ PASS' if result.passes_sla() else '✗ FAIL'}")
        print("=" * 70 + "\n")

    def export_results(self, result: LoadTestResult) -> Dict[str, Any]:
        """Export results as dictionary.

        Args:
            result: LoadTestResult object

        Returns:
            Dictionary with all metrics
        """
        return {
            "total_requests": result.total_requests,
            "successful_requests": result.successful_requests,
            "failed_requests": result.failed_requests,
            "error_rate": result.error_rate,
            "total_duration_seconds": result.total_duration_seconds,
            "actual_rps": result.actual_rps,
            "latency": {
                "min_ms": result.min_latency_ms,
                "max_ms": result.max_latency_ms,
                "mean_ms": result.mean_latency_ms,
                "median_ms": result.median_latency_ms,
                "p50_ms": result.p50_latency_ms,
                "p95_ms": result.p95_latency_ms,
                "p99_ms": result.p99_latency_ms,
            },
            "throughput_rps": result.throughput_rps,
            "sla_compliance": {
                "p99_meets_sla": result.p99_meets_sla,
                "p95_meets_sla": result.p95_meets_sla,
                "error_rate_acceptable": result.error_rate_acceptable,
            },
        }


# Extend LoadTestResult with helper method
def passes_sla(self) -> bool:
    """Check if all SLA criteria are met."""
    return self.p99_meets_sla and self.p95_meets_sla and self.error_rate_acceptable


LoadTestResult.passes_sla = passes_sla
