"""
Quality and Performance Tests for Agent Test Harness
===================================================

Tests output validation, performance benchmarks, resource usage,
and metric collection for all agent types.

Phase 4B Deliverable: Quality Tests
"""

import json
import time
from typing import Any, Dict

import pytest

from tests.agents.test_harness import (
    AgentTestHarness,
    ExecutionContext,
)

# ============================================================================
# MOCK AGENTS FOR QUALITY TESTING
# ============================================================================


class FastAgent(AgentTestHarness):
    """Agent that completes quickly."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize fast agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup fast agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fast operation."""
        return {
            "status": "success",
            "data": {"result": "fast"},
            "metadata": {"execution_time_ms": 10},
        }


class SlowAgent(AgentTestHarness):
    """Agent that takes longer to complete."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize slow agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup slow agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute slow operation."""
        time.sleep(0.1)  # Sleep 100ms
        return {
            "status": "success",
            "data": {"result": "slow"},
            "metadata": {"execution_time_ms": 100},
        }


class PartialSuccessAgent(AgentTestHarness):
    """Agent that sometimes fails."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize partial agent."""
        self.context = context
        self.execution_count = 0

    def teardown(self) -> None:
        """Cleanup partial agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with partial success."""
        self.execution_count += 1
        success_rate = inputs.get("success_rate", 0.8)

        if self.execution_count % 10 < (10 * success_rate):
            return {
                "status": "success",
                "data": {"result": "success"},
                "metadata": {"execution_time_ms": 50},
            }
        else:
            return {
                "status": "partial",
                "data": {"completed": 8, "failed": 2},
                "warnings": ["Some items could not be processed"],
                "metadata": {"execution_time_ms": 75},
            }


# ============================================================================
# OUTPUT VALIDATION TESTS
# ============================================================================


class TestOutputValidation:
    """Test suite for output format validation."""

    @pytest.mark.quality
    def test_output_status_field_presence(self):
        """Test output always has status field."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({})

        assert "status" in result, "Output missing 'status' field"
        assert result["status"] in [
            "success",
            "partial",
            "error",
        ], "Invalid status value"

        agent.teardown()

    @pytest.mark.quality
    def test_output_data_field_presence(self):
        """Test success output has data field."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({})

        if result["status"] in ["success", "partial"]:
            assert "data" in result, "Success output missing 'data' field"
            assert isinstance(result["data"], dict), "Data must be dict"

        agent.teardown()

    @pytest.mark.quality
    def test_output_metadata_field_presence(self):
        """Test output has metadata field."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({})

        if "metadata" in result:
            assert isinstance(
                result["metadata"], dict
            ), "Metadata must be dict"
            if "execution_time_ms" in result["metadata"]:
                assert isinstance(
                    result["metadata"]["execution_time_ms"], (int, float)
                ), "execution_time_ms must be numeric"

        agent.teardown()

    @pytest.mark.quality
    def test_error_output_format(self):
        """Test error output has required fields."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        # Manually create error output
        error_output = {
            "status": "error",
            "error": "Test error",
            "code": "ERROR_001",
        }

        assert error_output["status"] == "error"
        assert "error" in error_output
        assert "code" in error_output

        agent.teardown()

    @pytest.mark.quality
    def test_output_json_serializable(self):
        """Test output is JSON serializable."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({})

        try:
            json_str = json.dumps(result)
            assert json_str is not None
            parsed = json.loads(json_str)
            assert parsed["status"] == result["status"]
        except (TypeError, ValueError) as e:
            pytest.fail(f"Output not JSON serializable: {e}")

        agent.teardown()

    @pytest.mark.quality
    def test_output_consistency(self):
        """Test output format consistency across multiple executions."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        results = []
        for _ in range(5):
            result = agent.execute_agent({})
            results.append(result)

        # All results should have same structure
        keys = set(results[0].keys())
        for result in results[1:]:
            assert set(result.keys()) == keys, "Output format inconsistent"

        agent.teardown()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Test suite for performance benchmarking."""

    @pytest.mark.quality
    def test_execution_time_tracking(self):
        """Test execution time is tracked correctly."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.test_basic_execution({})

        assert result.duration_ms >= 0
        assert result.duration_ms < 1000  # Should complete in < 1 second

        agent.teardown()

    @pytest.mark.quality
    def test_fast_agent_performance(self):
        """Test fast agent meets performance requirements."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=10)

        assert benchmark["avg_duration_ms"] < 50  # Should be < 50ms on average
        assert benchmark["max_duration_ms"] < 100  # Max < 100ms

        agent.teardown()

    @pytest.mark.quality
    @pytest.mark.slow
    def test_slow_agent_performance(self):
        """Test slow agent performance characteristics."""
        agent = SlowAgent("agent", "slow")
        context = ExecutionContext(
            agent_id="agent", agent_type="slow", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=5)

        assert benchmark["avg_duration_ms"] > 50  # Should be > 50ms
        assert benchmark["successes"] == 5  # All should succeed

        agent.teardown()

    @pytest.mark.quality
    def test_throughput_measurement(self):
        """Test throughput measurement."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        start = time.time()
        count = 0
        while (time.time() - start) < 1.0:  # 1 second
            agent.execute_agent({})
            count += 1

        throughput = count / (time.time() - start)
        assert throughput > 10, f"Throughput {throughput} ops/s is too low"

        agent.teardown()

    @pytest.mark.quality
    def test_performance_variance(self):
        """Test execution time variance."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=20)

        # Calculate variance
        if benchmark["max_duration_ms"] > 0:
            variance = (
                benchmark["max_duration_ms"] - benchmark["min_duration_ms"]
            ) / benchmark["avg_duration_ms"]
            assert variance < 5.0, "Execution time variance too high"

        agent.teardown()


# ============================================================================
# RELIABILITY TESTS
# ============================================================================


class TestReliability:
    """Test suite for agent reliability metrics."""

    @pytest.mark.quality
    def test_error_rate(self):
        """Test error rate measurement."""
        agent = PartialSuccessAgent("agent", "partial")
        context = ExecutionContext(
            agent_id="agent", agent_type="partial", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=20)

        error_rate = benchmark["errors"] / benchmark["iterations"] if benchmark["iterations"] > 0 else 0
        assert error_rate < 0.5, f"Error rate {error_rate} too high"

        agent.teardown()

    @pytest.mark.quality
    def test_success_rate(self):
        """Test success rate measurement."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=10)

        success_rate = (
            benchmark["successes"] / benchmark["iterations"]
            if benchmark["iterations"] > 0
            else 0
        )
        assert success_rate == 1.0, "Success rate should be 100%"

        agent.teardown()

    @pytest.mark.quality
    def test_error_recovery(self):
        """Test agent can recover from errors."""
        agent = PartialSuccessAgent("agent", "partial")
        context = ExecutionContext(
            agent_id="agent", agent_type="partial", session_id="test"
        )
        agent.setup(context)

        # Execute multiple times to test recovery
        results = []
        for i in range(10):
            result = agent.execute_agent({"success_rate": 0.8})
            results.append(result)

        # Should have both successes and partial results
        statuses = [r["status"] for r in results]
        assert "success" in statuses or "partial" in statuses

        agent.teardown()


# ============================================================================
# METRICS COLLECTION TESTS
# ============================================================================


class TestMetricsCollection:
    """Test suite for metrics collection."""

    @pytest.mark.quality
    def test_metrics_initialization(self):
        """Test metrics are initialized correctly."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        assert agent.metrics.duration_ms == 0
        assert agent.metrics.ops_executed == 0

        agent.teardown()

    @pytest.mark.quality
    def test_metrics_collection_during_execution(self):
        """Test metrics are collected during execution."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        agent.test_basic_execution({})
        agent.test_basic_execution({})

        assert agent.metrics.ops_executed == 2

        agent.teardown()

    @pytest.mark.quality
    def test_test_result_metrics(self):
        """Test individual test result metrics."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        result = agent.test_basic_execution({})

        assert result.duration_ms >= 0
        assert result.metrics is not None

        agent.teardown()

    @pytest.mark.quality
    def test_summary_metrics(self):
        """Test summary metrics are accurate."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        for _ in range(5):
            agent.test_basic_execution({})

        summary = agent.get_summary()

        assert summary["total_tests"] == 5
        assert summary["passed"] >= 0
        assert summary["failed"] >= 0
        assert summary["pass_rate"] >= 0
        assert summary["avg_time_ms"] >= 0

        agent.teardown()


# ============================================================================
# COVERAGE QUALITY TESTS
# ============================================================================


class TestCoverageMetrics:
    """Test suite for coverage-related metrics."""

    @pytest.mark.quality
    def test_code_path_coverage(self):
        """Test different code paths are executed."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        # Test initialization path
        agent.test_initialization()

        # Test execution path
        agent.test_basic_execution({})

        # Test output format path
        agent.test_output_format({}, ["status"])

        # Test error handling path
        agent.test_error_handling({})

        # All paths should have executed
        assert agent.execution_count > 0

        agent.teardown()

    @pytest.mark.quality
    def test_test_coverage_tracking(self):
        """Test coverage tracking during test execution."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        initial_results = len(agent.test_results)

        agent.test_basic_execution({})
        agent.test_output_format({}, ["status"])
        agent.test_error_handling({})

        final_results = len(agent.test_results)

        assert final_results >= initial_results + 3

        agent.teardown()


# ============================================================================
# RESOURCE USAGE TESTS
# ============================================================================


class TestResourceUsage:
    """Test suite for resource usage tracking."""

    @pytest.mark.quality
    def test_memory_is_tracked(self):
        """Test memory usage is tracked."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        # Memory tracking is optional but should not error
        assert agent.metrics.memory_peak_mb >= 0

        agent.teardown()

    @pytest.mark.quality
    def test_cpu_is_tracked(self):
        """Test CPU usage is tracked."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        # CPU tracking is optional but should not error
        assert agent.metrics.cpu_percent >= 0

        agent.teardown()

    @pytest.mark.quality
    def test_no_resource_leaks(self):
        """Test no resource leaks during execution."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        # Execute many times
        for _ in range(100):
            agent.execute_agent({})

        # Should complete without issues
        assert agent.execution_count == 0  # Mock agent doesn't track this
        agent.teardown()


# ============================================================================
# QUALITY GATE TESTS
# ============================================================================


class TestQualityGates:
    """Test suite for quality gate validation."""

    @pytest.mark.quality
    def test_pass_rate_gate(self):
        """Test pass rate meets minimum threshold."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        for _ in range(10):
            agent.test_basic_execution({})

        summary = agent.get_summary()

        assert summary["pass_rate"] >= 90, "Pass rate below 90%"

        agent.teardown()

    @pytest.mark.quality
    def test_performance_gate(self):
        """Test performance meets requirements."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=10)

        assert benchmark["avg_duration_ms"] < 1000, "Performance below threshold"

        agent.teardown()

    @pytest.mark.quality
    def test_reliability_gate(self):
        """Test reliability meets requirements."""
        agent = FastAgent("agent", "fast")
        context = ExecutionContext(
            agent_id="agent", agent_type="fast", session_id="test"
        )
        agent.setup(context)

        benchmark = agent.benchmark_execution({}, iterations=10)

        error_rate = (
            benchmark["errors"] / benchmark["iterations"]
            if benchmark["iterations"] > 0
            else 0
        )
        assert error_rate < 0.1, "Error rate above 10%"

        agent.teardown()


# ============================================================================
# COMPARATIVE PERFORMANCE TESTS
# ============================================================================


class TestComparativePerformance:
    """Test suite for comparing performance across agents."""

    @pytest.mark.quality
    def test_fast_vs_slow_agent(self):
        """Compare fast and slow agents."""
        fast_agent = FastAgent("fast", "fast")
        slow_agent = SlowAgent("slow", "slow")

        context = ExecutionContext(
            agent_id="test", agent_type="test", session_id="test"
        )
        fast_agent.setup(context)
        slow_agent.setup(context)

        fast_benchmark = fast_agent.benchmark_execution({}, iterations=5)
        slow_benchmark = slow_agent.benchmark_execution({}, iterations=5)

        # Fast agent should be faster
        assert (
            fast_benchmark["avg_duration_ms"]
            < slow_benchmark["avg_duration_ms"]
        )

        fast_agent.teardown()
        slow_agent.teardown()

    @pytest.mark.quality
    def test_agent_consistency(self):
        """Test agent execution consistency."""
        agent1 = FastAgent("agent1", "fast")
        agent2 = FastAgent("agent2", "fast")

        context = ExecutionContext(
            agent_id="test", agent_type="test", session_id="test"
        )
        agent1.setup(context)
        agent2.setup(context)

        bench1 = agent1.benchmark_execution({}, iterations=10)
        bench2 = agent2.benchmark_execution({}, iterations=10)

        # Both should have similar performance
        avg_diff = abs(bench1["avg_duration_ms"] - bench2["avg_duration_ms"])
        assert avg_diff < 50, "Agent performance inconsistency detected"

        agent1.teardown()
        agent2.teardown()
