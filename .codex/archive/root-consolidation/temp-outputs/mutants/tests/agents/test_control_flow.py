"""
Control Flow Tests for Agent Test Harness
==========================================

Tests initialization, execution, output format, and error handling
for all agent types. Covers basic control flow execution paths.

Phase 4B Deliverable: Control Flow Tests
"""

import json
from typing import Any, Dict

import pytest

from tests.agents.test_harness import (
    AgentTestHarness,
    AgentTestPattern,
    ExecutionContext,
    ExecutionStatus,
)

# ============================================================================
# MOCK AGENT IMPLEMENTATIONS FOR TESTING
# ============================================================================


class MockBasicAgent(AgentTestHarness):
    """Mock agent for testing control flow."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize mock agent."""
        self.context = context
        self.is_initialized = True
        self.execution_log = []

    def teardown(self) -> None:
        """Cleanup mock agent."""
        self.is_initialized = False
        self.execution_log = []

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock agent."""
        self.execution_log.append({"input": inputs, "status": "executed"})
        return {
            "status": "success",
            "data": {"result": "test result", "input_echo": inputs.get("input")},
            "metadata": {"execution_time_ms": 100},
        }


class MockErrorAgent(AgentTestHarness):
    """Mock agent that can simulate errors."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize error agent."""
        self.context = context
        self.should_error = False

    def teardown(self) -> None:
        """Cleanup error agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with optional error."""
        if inputs.get("trigger_error"):
            return {
                "status": "error",
                "error": "Simulated error",
                "code": "MOCK_ERROR_001",
            }
        return {"status": "success", "data": {}}


class MockComplexAgent(AgentTestHarness):
    """Mock agent with stateful execution."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize complex agent."""
        self.context = context
        self.state = {"counter": 0, "results": []}

    def teardown(self) -> None:
        """Cleanup complex agent."""
        self.state = {"counter": 0, "results": []}

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with state management."""
        self.state["counter"] += 1
        self.state["results"].append(inputs)

        return {
            "status": "success",
            "data": {
                "execution_count": self.state["counter"],
                "results": self.state["results"],
            },
            "metadata": {
                "state_preserved": True,
                "execution_time_ms": 50 * self.state["counter"],
            },
        }


# ============================================================================
# CONTROL FLOW TEST SUITE
# ============================================================================


class TestAgentInitialization:
    """Test suite for agent initialization control flow."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_basic_agent_initialization(self):
        """Test basic agent initialization."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )

        agent.setup(context)

        assert agent.is_initialized is True
        assert agent.context is not None
        assert agent.context.agent_id == "test-agent"

        agent.teardown()
        assert agent.is_initialized is False

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_agent_context_preservation(self):
        """Test that agent context is preserved across setup/teardown."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent",
            agent_type="basic",
            session_id="test-session",
            metadata={"custom_field": "custom_value"},
        )

        agent.setup(context)
        original_context = agent.context

        # Execute some operations
        agent.execute_agent({"input": "test"})

        # Context should be preserved
        assert agent.context == original_context
        assert agent.context.metadata["custom_field"] == "custom_value"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_multiple_agent_initialization(self):
        """Test multiple agent instances can be initialized independently."""
        agent1 = MockBasicAgent("agent1", "basic")
        agent2 = MockBasicAgent("agent2", "basic")

        ctx1 = ExecutionContext(
            agent_id="agent1", agent_type="basic", session_id="session1"
        )
        ctx2 = ExecutionContext(
            agent_id="agent2", agent_type="basic", session_id="session2"
        )

        agent1.setup(ctx1)
        agent2.setup(ctx2)

        assert agent1.agent_id == "agent1"
        assert agent2.agent_id == "agent2"
        assert agent1.context.session_id == "session1"
        assert agent2.context.session_id == "session2"

        agent1.teardown()
        agent2.teardown()


class TestAgentExecution:
    """Test suite for agent execution control flow."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_basic_agent_execution(self):
        """Test basic agent execution."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test input"})

        assert result is not None
        assert result["status"] == "success"
        assert "data" in result
        assert "metadata" in result

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_agent_execution_with_test_harness(self):
        """Test agent execution using test harness methods."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        # Use harness test methods
        result = agent.test_basic_execution({"input": "test"})

        assert result.status == ExecutionStatus.SUCCESS
        assert result.test_name == "test_basic_execution"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_agent_execution_logging(self):
        """Test that agent execution is logged."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        agent.execute_agent({"input": "test1"})
        agent.execute_agent({"input": "test2"})
        agent.execute_agent({"input": "test3"})

        assert len(agent.execution_log) == 3
        assert agent.execution_log[0]["input"]["input"] == "test1"
        assert agent.execution_log[2]["input"]["input"] == "test3"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_agent_execution_metrics(self):
        """Test that execution metrics are collected."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.test_basic_execution({"input": "test"})

        assert result.duration_ms > 0
        assert result.assertions >= 0

        agent.teardown()


class TestOutputFormat:
    """Test suite for agent output format validation."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_output_has_status_field(self):
        """Test that output always has status field."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test"})

        is_valid, msg = agent.validate_output_status(result)
        assert is_valid is True
        assert msg == "OK"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_output_status_values(self):
        """Test that status field has valid values."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        # Test success
        result = agent.execute_agent({"input": "test"})
        assert result["status"] in ["success", "partial", "error"]

        # Test error output
        agent2 = MockErrorAgent("error-agent", "error")
        agent2.setup(context)
        error_result = agent2.execute_agent({"trigger_error": True})
        assert error_result["status"] == "error"

        agent.teardown()
        agent2.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_output_required_fields(self):
        """Test output has required fields."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test"})

        # Success output should have data
        is_valid, msg = agent.validate_output_structure(
            result, ["status", "data", "metadata"]
        )
        assert is_valid is True

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_output_type_validation(self):
        """Test output field type validation."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test"})

        is_valid, msg = agent.validate_output_types(
            result, {"status": str, "data": dict, "metadata": dict}
        )
        assert is_valid is True

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_output_json_serializable(self):
        """Test that output is JSON serializable."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test"})

        # Should be JSON serializable
        try:
            json_str = json.dumps(result)
            assert json_str is not None
            # Should be deserializable
            parsed = json.loads(json_str)
            assert parsed["status"] == "success"
        except (TypeError, ValueError) as e:
            pytest.fail(f"Output not JSON serializable: {e}")

        agent.teardown()


class TestErrorHandling:
    """Test suite for error handling in agent execution."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_error_output_format(self):
        """Test error output format."""
        agent = MockErrorAgent("error-agent", "error")
        context = ExecutionContext(
            agent_id="error-agent", agent_type="error", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"trigger_error": True})

        assert result["status"] == "error"
        assert "error" in result
        assert result["error"] == "Simulated error"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_error_recovery(self):
        """Test agent can recover from errors."""
        agent = MockErrorAgent("error-agent", "error")
        context = ExecutionContext(
            agent_id="error-agent", agent_type="error", session_id="test-session"
        )
        agent.setup(context)

        # First call with error
        result1 = agent.execute_agent({"trigger_error": True})
        assert result1["status"] == "error"

        # Second call without error - should succeed
        result2 = agent.execute_agent({"trigger_error": False})
        assert result2["status"] == "success"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.test_error_handling({})
        # Should complete without crashing
        assert result.status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_exception_handling(self):
        """Test exception handling in test execution."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        def failing_test():
            raise ValueError("Test error")

        result = agent.run_test("test_exception", failing_test)

        assert result.status == ExecutionStatus.FAILED
        assert "Test error" in result.message

        agent.teardown()


class TestStateManagement:
    """Test suite for state management during execution."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_state_initialization(self):
        """Test agent state is properly initialized."""
        agent = MockComplexAgent("complex-agent", "complex")
        context = ExecutionContext(
            agent_id="complex-agent", agent_type="complex", session_id="test-session"
        )
        agent.setup(context)

        assert agent.state["counter"] == 0
        assert agent.state["results"] == []

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_state_updates_during_execution(self):
        """Test state updates during agent execution."""
        agent = MockComplexAgent("complex-agent", "complex")
        context = ExecutionContext(
            agent_id="complex-agent", agent_type="complex", session_id="test-session"
        )
        agent.setup(context)

        agent.execute_agent({"input": "first"})
        assert agent.state["counter"] == 1

        agent.execute_agent({"input": "second"})
        assert agent.state["counter"] == 2

        agent.execute_agent({"input": "third"})
        assert agent.state["counter"] == 3

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_state_cleanup(self):
        """Test state is cleaned up on teardown."""
        agent = MockComplexAgent("complex-agent", "complex")
        context = ExecutionContext(
            agent_id="complex-agent", agent_type="complex", session_id="test-session"
        )
        agent.setup(context)

        agent.execute_agent({"input": "test"})
        assert agent.state["counter"] > 0

        agent.teardown()

        # State should be reset
        assert agent.state["counter"] == 0
        assert agent.state["results"] == []


class TestExecutionMetrics:
    """Test suite for execution metrics collection."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_execution_duration_tracking(self):
        """Test execution duration is tracked."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.test_basic_execution({"input": "test"})

        assert result.duration_ms >= 0
        assert result.duration_ms < 5000  # Should complete in < 5 seconds

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_execution_count_tracking(self):
        """Test execution count is tracked."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        initial_count = agent.execution_count

        agent.test_basic_execution({"input": "test1"})
        agent.test_basic_execution({"input": "test2"})
        agent.test_basic_execution({"input": "test3"})

        assert agent.execution_count == initial_count + 3

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_test_result_tracking(self):
        """Test test results are tracked."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        initial_results = len(agent.test_results)

        agent.test_basic_execution({"input": "test"})

        assert len(agent.test_results) == initial_results + 1

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_metrics_summary(self):
        """Test metrics summary is accurate."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        agent.test_basic_execution({"input": "test"})
        summary = agent.get_summary()

        assert "total_tests" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "pass_rate" in summary
        assert summary["agent_id"] == "test-agent"

        agent.teardown()


class TestCommonPatterns:
    """Test suite for common test patterns."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_happy_path_pattern(self):
        """Test happy path test pattern."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        # Should not raise
        AgentTestPattern.happy_path_test(
            agent, {"input": "test"}, ["status", "data", "metadata"]
        )

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_error_recovery_pattern(self):
        """Test error recovery test pattern."""
        agent = MockErrorAgent("error-agent", "error")
        context = ExecutionContext(
            agent_id="error-agent", agent_type="error", session_id="test-session"
        )
        agent.setup(context)

        # Should not raise
        AgentTestPattern.error_recovery_test(agent, {"trigger_error": True})

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_idempotency_pattern(self):
        """Test idempotency test pattern."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        # Should not raise
        AgentTestPattern.idempotency_test(agent, {"input": "test"})

        agent.teardown()


# ============================================================================
# INTEGRATION WITH FIXTURE-BASED TESTING
# ============================================================================


class TestControlFlowWithFixtures:
    """Test control flow using pytest fixtures."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_with_context_builder(self, agent_context_builder):
        """Test using context builder fixture."""
        context = (
            agent_context_builder.with_agent_id("test-agent")
            .with_agent_type("basic")
            .with_input("data", "test data")
            .build()
        )

        assert context["agent_id"] == "test-agent"
        assert context["inputs"]["data"] == "test data"

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_with_sample_inputs(self, sample_test_inputs):
        """Test with sample input data."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent(sample_test_inputs["simple"])
        assert result["status"] == "success"

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_with_assert_helpers(self, assert_valid_agent_output):
        """Test output validation helper."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        result = agent.execute_agent({"input": "test"})
        assert_valid_agent_output(result)  # Should not raise

        agent.teardown()


# ============================================================================
# REPORTING
# ============================================================================


class TestReporting:
    """Test suite for test reporting functionality."""

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_text_report_generation(self):
        """Test text report generation."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        agent.test_basic_execution({"input": "test"})

        report = agent.report_results(format="text")
        assert "test-agent" in report
        assert "Test Results" in report

        agent.teardown()

    @pytest.mark.agent
    @pytest.mark.control_flow
    def test_json_report_generation(self):
        """Test JSON report generation."""
        agent = MockBasicAgent("test-agent", "basic")
        context = ExecutionContext(
            agent_id="test-agent", agent_type="basic", session_id="test-session"
        )
        agent.setup(context)

        agent.test_basic_execution({"input": "test"})

        report = agent.report_results(format="json")
        parsed = json.loads(report)

        assert "summary" in parsed
        assert "results" in parsed
        assert parsed["summary"]["agent_id"] == "test-agent"

        agent.teardown()
