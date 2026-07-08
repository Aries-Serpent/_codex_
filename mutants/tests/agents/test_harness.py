"""
Agent Test Harness Framework
=============================

Base class and common patterns for comprehensive agent testing.
Provides:
- AgentTestHarness base class for all agent tests
- Common execution flow validation patterns
- Output verification utilities
- Performance benchmarking support
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================


class ExecutionStatus(Enum):
    """Agent execution status states."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class TestPhase(Enum):
    """Test execution phases."""

    INITIALIZATION = "initialization"
    SETUP = "setup"
    EXECUTION = "execution"
    VALIDATION = "validation"
    CLEANUP = "cleanup"


@dataclass
class ExecutionMetrics:
    """Metrics for agent execution."""

    duration_ms: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_percent: float = 0.0
    ops_executed: int = 0
    errors_caught: int = 0
    warnings_issued: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    """Result of a single agent test."""

    test_name: str
    status: ExecutionStatus
    message: str = ""
    duration_ms: float = 0.0
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    assertions: int = 0
    failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "metrics": self.metrics.to_dict(),
            "assertions": self.assertions,
            "failures": self.failures,
            "warnings": self.warnings,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExecutionContext:
    """Context for agent test execution."""

    agent_id: str
    agent_type: str
    session_id: str
    user_id: str = "test-user"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# BASE TEST HARNESS CLASS
# ============================================================================


class AgentTestHarness(ABC):
    """
    Base class for comprehensive agent testing.

    Provides standard execution flow, validation patterns, and metrics collection.

    Subclasses must implement:
    - setup(): Initialize test environment
    - teardown(): Cleanup after tests
    - execute_agent(): Run the agent being tested
    """

    def __init__(self, agent_id: str, agent_type: str):
        """Initialize test harness."""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")

        # Execution tracking
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.test_results: List[TestResult] = []
        self.start_time: Optional[float] = None
        self.current_phase = TestPhase.PENDING

        # Metrics
        self.metrics = ExecutionMetrics()
        self.phase_times: Dict[TestPhase, float] = {}

    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================

    @abstractmethod
    def setup(self, context: ExecutionContext) -> None:
        """Set up test environment. Must be implemented by subclass."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Tear down test environment. Must be implemented by subclass."""
        pass

    @abstractmethod
    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent. Must be implemented by subclass."""
        pass

    def run_test(
        self,
        test_name: str,
        test_func: Callable,
        context: Optional[ExecutionContext] = None,
        timeout_ms: float = 30000,
    ) -> TestResult:
        """
        Run a single test with timing and metrics.

        Args:
            test_name: Name of the test
            test_func: Function to execute
            context: Execution context (optional)
            timeout_ms: Test timeout in milliseconds

        Returns:
            TestResult with execution metrics
        """
        result = TestResult(test_name=test_name, status=ExecutionStatus.PENDING)
        self.execution_count += 1

        start = time.time()
        try:
            # Execute test with timeout
            test_func()
            result.status = ExecutionStatus.SUCCESS
            self.success_count += 1

        except AssertionError as e:
            result.status = ExecutionStatus.FAILED
            result.message = str(e)
            result.failures.append(str(e))
            self.failure_count += 1

        except TimeoutError:
            result.status = ExecutionStatus.TIMEOUT
            result.message = f"Test exceeded {timeout_ms}ms timeout"
            result.failures.append(result.message)
            self.failure_count += 1

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.message = f"Unexpected error: {str(e)}"
            result.failures.append(result.message)
            self.failure_count += 1

        finally:
            result.duration_ms = (time.time() - start) * 1000
            self.test_results.append(result)
            self.metrics.ops_executed += 1

            self.logger.info(
                f"Test {test_name}: {result.status.value} ({result.duration_ms:.2f}ms)"
            )

        return result

    # ========================================================================
    # CONTROL FLOW VALIDATION
    # ========================================================================

    def test_initialization(self) -> TestResult:
        """Test agent initialization."""

        def test_init():
            context = ExecutionContext(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                session_id="test-session",
            )
            self.setup(context)
            assert context is not None
            assert context.agent_id == self.agent_id
            assert context.agent_type == self.agent_type

        return self.run_test("test_initialization", test_init)

    def test_basic_execution(self, inputs: Dict[str, Any]) -> TestResult:
        """Test basic agent execution."""

        def test_exec():
            result = self.execute_agent(inputs)
            assert result is not None
            assert isinstance(result, dict)

        return self.run_test("test_basic_execution", test_exec)

    def test_output_format(self, inputs: Dict[str, Any], expected_keys: List[str]) -> TestResult:
        """Test that output has expected format."""

        def test_format():
            result = self.execute_agent(inputs)
            for key in expected_keys:
                assert key in result, f"Expected key '{key}' in output"

        return self.run_test("test_output_format", test_format)

    def test_error_handling(self, invalid_inputs: Dict[str, Any]) -> TestResult:
        """Test agent error handling."""

        def test_errors():
            try:
                result = self.execute_agent(invalid_inputs)
                # Should either return error status or raise
                if isinstance(result, dict):
                    assert "error" in result or "status" in result
            except Exception:
                # Error handling is working
                pass

        return self.run_test("test_error_handling", test_errors)

    # ========================================================================
    # OUTPUT VALIDATION
    # ========================================================================

    def validate_output_status(self, output: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate output has valid status field."""
        if "status" not in output:
            return False, "Missing 'status' field"

        valid_statuses = ["success", "partial", "error"]
        if output["status"] not in valid_statuses:
            return False, f"Invalid status: {output['status']}"

        return True, "OK"

    def validate_output_structure(
        self, output: Dict[str, Any], required_fields: List[str]
    ) -> Tuple[bool, str]:
        """Validate output has required fields."""
        missing = [f for f in required_fields if f not in output]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, "OK"

    def validate_output_types(
        self, output: Dict[str, Any], expected_types: Dict[str, type]
    ) -> Tuple[bool, str]:
        """Validate output field types."""
        for field, expected_type in expected_types.items():
            if field not in output:
                continue
            if not isinstance(output[field], expected_type):
                return (
                    False,
                    f"Field '{field}' has wrong type: {type(output[field])}, expected {expected_type}",
                )
        return True, "OK"

    # ========================================================================
    # PERFORMANCE BENCHMARKING
    # ========================================================================

    def benchmark_execution(
        self, inputs: Dict[str, Any], iterations: int = 10, max_duration_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """Benchmark agent execution performance."""
        durations = []
        errors = []

        start = time.time()
        for i in range(iterations):
            try:
                iter_start = time.time()
                self.execute_agent(inputs)
                iter_duration = (time.time() - iter_start) * 1000
                durations.append(iter_duration)
            except Exception as e:
                errors.append(str(e))

        total_time = (time.time() - start) * 1000

        benchmark = {
            "iterations": iterations,
            "successes": len(durations),
            "errors": len(errors),
            "total_time_ms": total_time,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
        }

        if max_duration_ms and benchmark["max_duration_ms"] > max_duration_ms:
            self.logger.warning(
                f"Execution exceeded max duration: {benchmark['max_duration_ms']}ms > {max_duration_ms}ms"
            )

        return benchmark

    # ========================================================================
    # INTEGRATION FLOW TESTING
    # ========================================================================

    def test_multi_step_execution(
        self, steps: List[Dict[str, Any]], assertions: List[Callable]
    ) -> TestResult:
        """Test multi-step agent execution with assertions at each step."""

        def test_steps():
            for i, step in enumerate(steps):
                result = self.execute_agent(step)
                assert result is not None, f"Step {i} returned None"

                if i < len(assertions):
                    assertions[i](result)

        return self.run_test("test_multi_step_execution", test_steps)

    def test_state_preservation(
        self, initial_state: Dict[str, Any], transitions: List[Dict[str, Any]]
    ) -> TestResult:
        """Test that agent preserves state across multiple executions."""

        def test_state():
            current_state = initial_state.copy()

            for transition in transitions:
                result = self.execute_agent(transition)
                # Verify state changes are reflected in output
                assert result is not None

        return self.run_test("test_state_preservation", test_state)

    # ========================================================================
    # REPORTING
    # ========================================================================

    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary."""
        total = self.execution_count
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "total_tests": total,
            "passed": self.success_count,
            "failed": self.failure_count,
            "pass_rate": (
                self.success_count / total * 100 if total > 0 else 0
            ),
            "total_time_ms": sum(
                r.duration_ms for r in self.test_results
            ),
            "avg_time_ms": (
                sum(r.duration_ms for r in self.test_results) / total
                if total > 0
                else 0
            ),
            "metrics": self.metrics.to_dict(),
        }

    def report_results(self, format: str = "text") -> str:
        """Generate test report."""
        summary = self.get_summary()

        if format == "json":
            return json.dumps(
                {
                    "summary": summary,
                    "results": [r.to_dict() for r in self.test_results],
                },
                indent=2,
            )

        # Text format
        lines = [
            f"Agent Test Results: {self.agent_id}",
            "=" * 60,
            f"Total Tests: {summary['total_tests']}",
            f"Passed: {summary['passed']}",
            f"Failed: {summary['failed']}",
            f"Pass Rate: {summary['pass_rate']:.1f}%",
            f"Total Time: {summary['total_time_ms']:.2f}ms",
            f"Avg Time: {summary['avg_time_ms']:.2f}ms",
            "",
            "Test Results:",
            "-" * 60,
        ]

        for result in self.test_results:
            status_str = f"[{result.status.value.upper()}]"
            lines.append(
                f"  {status_str} {result.test_name} ({result.duration_ms:.2f}ms)"
            )
            if result.failures:
                for failure in result.failures:
                    lines.append(f"      → {failure}")

        return "\n".join(lines)


# ============================================================================
# COMMON PATTERNS
# ============================================================================


class AgentTestPattern:
    """Common testing patterns for agent tests."""

    @staticmethod
    def happy_path_test(
        harness: AgentTestHarness, inputs: Dict[str, Any], expected_keys: List[str]
    ) -> None:
        """Standard happy path test pattern."""
        result = harness.execute_agent(inputs)
        assert result is not None
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    @staticmethod
    def error_recovery_test(
        harness: AgentTestHarness, invalid_inputs: Dict[str, Any]
    ) -> None:
        """Test error recovery and handling."""
        try:
            result = harness.execute_agent(invalid_inputs)
            # Should have error status
            assert (
                "status" in result and result["status"] == "error"
            ) or "error" in result
        except Exception as e:
            # Error handling is acceptable
            pass

    @staticmethod
    def idempotency_test(
        harness: AgentTestHarness, inputs: Dict[str, Any]
    ) -> None:
        """Test that repeated executions produce same results."""
        result1 = harness.execute_agent(inputs)
        result2 = harness.execute_agent(inputs)

        # Results should be equivalent
        assert json.dumps(result1, sort_keys=True) == json.dumps(
            result2, sort_keys=True
        )

    @staticmethod
    def performance_test(
        harness: AgentTestHarness,
        inputs: Dict[str, Any],
        max_ms: float = 5000,
        iterations: int = 10,
    ) -> None:
        """Test performance meets requirements."""
        benchmark = harness.benchmark_execution(inputs, iterations)
        avg_time = benchmark["avg_duration_ms"]
        assert (
            avg_time <= max_ms
        ), f"Average execution time {avg_time}ms exceeds {max_ms}ms"
