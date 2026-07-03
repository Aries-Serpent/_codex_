"""
Load Test Scripts: 100-Concurrent PR Simulation

This module provides load testing capabilities with:
- Concurrent PR request simulation
- Latency and throughput measurement
- Request generation and validation
- Ramp-up/ramp-down procedures
- JSON report generation

Author: AI Agent Process Phase 9.3
Version: 1.0.0-baseline
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# ============================================================================
# Load Test Configuration
# ============================================================================


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    # Test parameters
    test_name: str = "load_test"
    duration_sec: int = 600  # 10 minutes
    max_concurrent_requests: int = 100
    requests_per_second: Optional[int] = None  # If None, saturate with max_concurrent

    # Ramp configuration
    ramp_up_sec: int = 60
    ramp_down_sec: int = 30

    # Request configuration
    request_timeout_sec: int = 30
    connection_timeout_sec: int = 10

    # Success criteria
    target_success_rate: float = 0.95  # 95% success rate
    target_p99_latency_ms: float = 5000.0  # 5 second max p99

    # Request type distribution
    request_types: dict[str, float] = field(
        default_factory=lambda: {
            "simple": 0.5,
            "complex": 0.3,
            "heavy": 0.2,
        }
    )


@dataclass
class LoadTestRequest:
    """Simulated PR request."""

    request_id: str
    request_type: str
    created_at: float
    timeout_at: float
    pr_number: int
    file_count: int
    status: str = "pending"  # pending, in_progress, success, failed, timeout


@dataclass
class LoadTestMetrics:
    """Metrics from load test run."""

    start_time: float
    end_time: Optional[float] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    latencies: list[float] = field(default_factory=list)
    request_timeline: list[dict[str, Any]] = field(default_factory=list)

    def add_request(
        self, request_id: str, latency_ms: float, status: str
    ) -> None:
        """Record a completed request."""
        self.total_requests += 1
        self.latencies.append(latency_ms)

        if status == "success":
            self.successful_requests += 1
        elif status == "timeout":
            self.timeout_requests += 1
        else:
            self.failed_requests += 1

        self.request_timeline.append(
            {
                "request_id": request_id,
                "timestamp": time.time(),
                "latency_ms": latency_ms,
                "status": status,
            }
        )

    def get_summary(self) -> dict[str, Any]:
        """Get test summary."""
        if not self.latencies:
            return {
                "status": "no_requests",
                "total_requests": 0,
            }

        sorted_latencies = sorted(self.latencies)
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0
        )
        duration = (self.end_time or time.time()) - self.start_time

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "timeout_requests": self.timeout_requests,
            "success_rate": success_rate,
            "throughput_req_sec": self.total_requests / duration if duration > 0 else 0,
            "avg_latency_ms": sum(self.latencies) / len(self.latencies),
            "p50_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.50)],
            "p95_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.95)],
            "p99_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.99)],
            "max_latency_ms": max(self.latencies),
            "duration_sec": duration,
        }


# ============================================================================
# Load Test Runner
# ============================================================================


class LoadTestRunner:
    """Executes load tests with concurrent PR simulation."""

    def __init__(self, config: LoadTestConfig) -> None:
        """Initialize load test runner."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = LoadTestMetrics(start_time=time.time())
        self.active_requests: dict[str, LoadTestRequest] = {}
        self.request_counter = 0
        self.failed = False

    def _generate_request(self) -> LoadTestRequest:
        """Generate a new PR request."""
        self.request_counter += 1
        request_type = random.choices(
            list(self.config.request_types.keys()),
            weights=list(self.config.request_types.values()),
        )[0]

        # Simulate different request sizes
        file_counts = {
            "simple": (5, 10),
            "complex": (10, 50),
            "heavy": (50, 200),
        }
        min_files, max_files = file_counts[request_type]
        file_count = random.randint(min_files, max_files)

        now = time.time()
        return LoadTestRequest(
            request_id=f"pr_{self.request_counter}",
            request_type=request_type,
            created_at=now,
            timeout_at=now + self.config.request_timeout_sec,
            pr_number=1000 + self.request_counter,
            file_count=file_count,
        )

    async def _process_request(self, request: LoadTestRequest) -> None:
        """Process a single request."""
        try:
            request.status = "in_progress"
            start_time = time.time()

            # Simulate request processing with latency based on type
            latency_base = {
                "simple": (0.05, 0.2),
                "complex": (0.2, 1.0),
                "heavy": (1.0, 5.0),
            }
            min_latency, max_latency = latency_base[request.request_type]
            simulated_latency = random.uniform(min_latency, max_latency)

            # Randomly inject failures (5% failure rate)
            if random.random() < 0.05:
                request.status = "failed"
                self.metrics.add_request(request.request_id, 0, "failed")
                self.logger.debug(f"Request {request.request_id} failed")
                return

            # Simulate processing
            await asyncio.sleep(simulated_latency)

            # Check for timeout
            if time.time() > request.timeout_at:
                request.status = "timeout"
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.add_request(request.request_id, latency_ms, "timeout")
                self.logger.debug(f"Request {request.request_id} timed out")
                return

            # Success
            request.status = "success"
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.add_request(request.request_id, latency_ms, "success")
            self.logger.debug(
                f"Request {request.request_id} succeeded in {latency_ms:.2f}ms"
            )

        except Exception as e:
            request.status = "failed"
            self.logger.error(f"Request {request.request_id} error: {e}")
            self.metrics.add_request(request.request_id, 0, "failed")
        finally:
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]

    async def _ramp_up(self) -> None:
        """Ramp up to target concurrency."""
        self.logger.info(
            f"Ramping up to {self.config.max_concurrent_requests} concurrent requests"
        )
        step_duration = (
            self.config.ramp_up_sec / self.config.max_concurrent_requests
        )
        current_concurrent = 0

        start_time = time.time()
        while current_concurrent < self.config.max_concurrent_requests:
            if time.time() - start_time > self.config.ramp_up_sec:
                current_concurrent = self.config.max_concurrent_requests
                break

            # Add new request
            request = self._generate_request()
            self.active_requests[request.request_id] = request
            asyncio.create_task(self._process_request(request))
            current_concurrent += 1

            await asyncio.sleep(step_duration)

        self.logger.info("Ramp-up complete")

    async def _sustained_load(self) -> None:
        """Maintain sustained load."""
        self.logger.info("Entering sustained load phase")
        start_time = time.time()

        while time.time() - start_time < self.config.duration_sec:
            # Calculate how many new requests to create
            target_concurrent = self.config.max_concurrent_requests
            current_concurrent = len(self.active_requests)
            new_requests = max(0, target_concurrent - current_concurrent)

            # Create new requests
            for _ in range(new_requests):
                request = self._generate_request()
                self.active_requests[request.request_id] = request
                asyncio.create_task(self._process_request(request))

            # Log periodic statistics
            if int(time.time() - start_time) % 60 == 0:
                summary = self.metrics.get_summary()
                self.logger.info(
                    f"Active requests: {current_concurrent}, "
                    f"Total: {summary['total_requests']}, "
                    f"Success rate: {summary['success_rate']:.2%}"
                )

            await asyncio.sleep(1.0)

    async def _ramp_down(self) -> None:
        """Ramp down from target concurrency."""
        self.logger.info("Ramping down")
        start_time = time.time()

        while len(self.active_requests) > 0:
            if time.time() - start_time > self.config.ramp_down_sec:
                break

            await asyncio.sleep(0.5)

        # Wait for remaining requests
        if self.active_requests:
            self.logger.info(
                f"Waiting for {len(self.active_requests)} remaining requests"
            )
            await asyncio.gather(
                *[
                    self._process_request(r)
                    for r in list(self.active_requests.values())
                ],
                return_exceptions=True,
            )

        self.logger.info("Ramp-down complete")

    async def run(self) -> LoadTestMetrics:
        """Execute full load test."""
        try:
            # Phase 1: Ramp up
            await self._ramp_up()

            # Phase 2: Sustained load
            await self._sustained_load()

            # Phase 3: Ramp down
            await self._ramp_down()

        except Exception as e:
            self.logger.error(f"Load test failed: {e}")
            self.failed = True
        finally:
            self.metrics.end_time = time.time()

        return self.metrics


# ============================================================================
# Load Test Entry Points
# ============================================================================


async def run_baseline_load_test(duration_sec: int = 300) -> LoadTestMetrics:
    """Run baseline load test (5 minutes)."""
    config = LoadTestConfig(
        test_name="baseline_load",
        duration_sec=duration_sec,
        max_concurrent_requests=10,  # Start small for baseline
        ramp_up_sec=30,
    )

    logging.basicConfig(level=logging.INFO)
    runner = LoadTestRunner(config)
    metrics = await runner.run()
    return metrics


async def run_100_concurrent_load_test(
    duration_sec: int = 600,
) -> LoadTestMetrics:
    """Run 100-concurrent load test (10 minutes)."""
    config = LoadTestConfig(
        test_name="100_concurrent_load",
        duration_sec=duration_sec,
        max_concurrent_requests=100,
        ramp_up_sec=60,
    )

    logging.basicConfig(level=logging.INFO)
    runner = LoadTestRunner(config)
    metrics = await runner.run()
    return metrics


async def run_sustained_load_test(
    duration_sec: int = 1800, concurrent: int = 50
) -> LoadTestMetrics:
    """Run sustained load test (30 minutes)."""
    config = LoadTestConfig(
        test_name="sustained_load",
        duration_sec=duration_sec,
        max_concurrent_requests=concurrent,
        ramp_up_sec=120,
    )

    logging.basicConfig(level=logging.INFO)
    runner = LoadTestRunner(config)
    metrics = await runner.run()
    return metrics


async def generate_load_test_report(
    metrics: LoadTestMetrics,
    output_file: Optional[str] = None,
) -> dict[str, Any]:
    """Generate load test report."""
    summary = metrics.get_summary()

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "requirements": {
            "target_success_rate": 0.95,
            "target_p99_latency_ms": 5000.0,
        },
        "pass_criteria": {
            "success_rate_passed": summary.get("success_rate", 0)
            >= 0.95,
            "p99_latency_passed": summary.get("p99_latency_ms", float("inf"))
            <= 5000.0,
        },
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

    return report


# ============================================================================
# CLI Interface
# ============================================================================


if __name__ == "__main__":
    import sys

    # Run baseline test
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

    logger.info("Starting baseline load test (5 minutes)...")
    metrics = asyncio.run(run_baseline_load_test(duration_sec=300))

    summary = metrics.get_summary()
    logger.info(json.dumps(summary, indent=2))

    # Generate report
    report = asyncio.run(
        generate_load_test_report(metrics, "load_test_report.json")
    )
    logger.info("Report generated: load_test_report.json")

    sys.exit(0 if not asyncio.run(run_baseline_load_test()) else 1)
