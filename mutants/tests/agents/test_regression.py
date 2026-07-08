"""
Regression Tests for Agent Test Harness
========================================

Tests for previously reported bugs, known edge cases, boundary conditions,
and historical failure patterns.

Phase 4B Deliverable: Regression Tests
"""

import json
from typing import Any, Dict

import pytest

from tests.agents.test_harness import (
    AgentTestHarness,
    ExecutionContext,
)

# ============================================================================
# REGRESSION TEST AGENTS
# ============================================================================


class BoundaryAgent(AgentTestHarness):
    """Agent that tests boundary conditions."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize boundary agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup boundary agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with boundary handling."""
        value = inputs.get("value", 0)

        # Handle boundary conditions
        if value is None:
            return {
                "status": "error",
                "error": "Value cannot be None",
                "code": "NULL_VALUE",
            }
        elif value < 0:
            return {
                "status": "error",
                "error": "Value must be non-negative",
                "code": "NEGATIVE_VALUE",
            }
        elif value == 0:
            return {"status": "success", "data": {"result": "zero"}}
        elif value > 1000000:
            return {
                "status": "error",
                "error": "Value exceeds maximum",
                "code": "OVERFLOW",
            }
        else:
            return {"status": "success", "data": {"result": value * 2}}


class EdgeCaseAgent(AgentTestHarness):
    """Agent that handles edge cases."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize edge case agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup edge case agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with edge case handling."""
        data = inputs.get("data", {})

        # Handle various edge cases
        if isinstance(data, dict):
            if len(data) == 0:
                return {"status": "success", "data": {"processed": 0}}
            else:
                return {
                    "status": "success",
                    "data": {"processed": len(data)},
                }
        elif isinstance(data, list):
            if len(data) == 0:
                return {"status": "success", "data": {"items": 0}}
            else:
                return {"status": "success", "data": {"items": len(data)}}
        elif isinstance(data, str):
            if data == "":
                return {"status": "success", "data": {"length": 0}}
            else:
                return {"status": "success", "data": {"length": len(data)}}
        else:
            return {
                "status": "error",
                "error": f"Unsupported type: {type(data)}",
            }


class LegacyCompatibilityAgent(AgentTestHarness):
    """Agent that maintains backward compatibility."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize legacy agent."""
        self.context = context
        self.version = "2.0.0"

    def teardown(self) -> None:
        """Cleanup legacy agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with legacy support."""
        version = inputs.get("api_version", "1.0")

        if version == "1.0":
            # Legacy response format
            return {
                "status": "success",
                "result": inputs.get("data"),
                "timestamp": "2024-01-01T00:00:00Z",
            }
        elif version == "2.0":
            # New response format
            return {
                "status": "success",
                "data": inputs.get("data"),
                "metadata": {"version": self.version},
            }
        else:
            return {
                "status": "error",
                "error": f"Unsupported API version: {version}",
            }


class StateRegressionAgent(AgentTestHarness):
    """Agent that tests state-related regressions."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize state agent."""
        self.context = context
        self.state = {"counter": 0, "history": []}

    def teardown(self) -> None:
        """Cleanup state agent."""
        self.state = {"counter": 0, "history": []}

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with state management."""
        action = inputs.get("action", "increment")

        if action == "increment":
            self.state["counter"] += 1
        elif action == "decrement":
            self.state["counter"] -= 1
        elif action == "reset":
            self.state["counter"] = 0
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
            }

        self.state["history"].append(action)

        return {
            "status": "success",
            "data": {
                "counter": self.state["counter"],
                "history_length": len(self.state["history"]),
            },
        }


# ============================================================================
# KNOWN ISSUE REGRESSION TESTS
# ============================================================================


class TestZeroBoundary:
    """Regression tests for zero/boundary handling."""

    @pytest.mark.regression
    def test_zero_value_handling(self):
        """Test handling of zero values (previously broken)."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": 0})

        assert result["status"] == "success"
        assert result["data"]["result"] == "zero"

        agent.teardown()

    @pytest.mark.regression
    def test_small_positive_values(self):
        """Test small positive value handling."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": 1})

        assert result["status"] == "success"
        assert result["data"]["result"] == 2

        agent.teardown()

    @pytest.mark.regression
    def test_large_value_boundary(self):
        """Test large value boundary detection."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": 1000001})

        assert result["status"] == "error"
        assert result["code"] == "OVERFLOW"

        agent.teardown()

    @pytest.mark.regression
    def test_negative_value_rejection(self):
        """Test negative value rejection."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": -1})

        assert result["status"] == "error"
        assert result["code"] == "NEGATIVE_VALUE"

        agent.teardown()


class TestEmptyCollections:
    """Regression tests for empty collection handling."""

    @pytest.mark.regression
    def test_empty_dict_handling(self):
        """Test empty dictionary handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"data": {}})

        assert result["status"] == "success"
        assert result["data"]["processed"] == 0

        agent.teardown()

    @pytest.mark.regression
    def test_empty_list_handling(self):
        """Test empty list handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"data": []})

        assert result["status"] == "success"
        assert result["data"]["items"] == 0

        agent.teardown()

    @pytest.mark.regression
    def test_empty_string_handling(self):
        """Test empty string handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"data": ""})

        assert result["status"] == "success"
        assert result["data"]["length"] == 0

        agent.teardown()


class TestNullValues:
    """Regression tests for null/None value handling."""

    @pytest.mark.regression
    def test_none_value_rejection(self):
        """Test None value rejection."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": None})

        assert result["status"] == "error"
        assert result["code"] == "NULL_VALUE"

        agent.teardown()

    @pytest.mark.regression
    def test_missing_optional_field(self):
        """Test missing optional field handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        # Not providing 'data' field
        result = agent.execute_agent({})

        assert result["status"] == "success"
        assert "data" in result

        agent.teardown()


class TestTypeHandling:
    """Regression tests for type handling."""

    @pytest.mark.regression
    def test_unsupported_type_error(self):
        """Test unsupported type error handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"data": 12345})

        assert result["status"] == "error"

        agent.teardown()

    @pytest.mark.regression
    def test_dict_with_nested_structures(self):
        """Test nested dictionary handling."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent(
            {"data": {"a": {"b": {"c": "value"}}}}
        )

        assert result["status"] == "success"

        agent.teardown()

    @pytest.mark.regression
    def test_list_with_mixed_types(self):
        """Test list with mixed types."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent(
            {"data": [1, "string", {"key": "value"}, [1, 2, 3]]}
        )

        assert result["status"] == "success"

        agent.teardown()


class TestBackwardCompatibility:
    """Regression tests for backward compatibility."""

    @pytest.mark.regression
    def test_legacy_api_v1_support(self):
        """Test legacy API v1.0 support."""
        agent = LegacyCompatibilityAgent("legacy", "legacy")
        context = ExecutionContext(
            agent_id="legacy", agent_type="legacy", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent(
            {"api_version": "1.0", "data": "legacy_data"}
        )

        assert result["status"] == "success"
        assert "result" in result
        assert result["result"] == "legacy_data"

        agent.teardown()

    @pytest.mark.regression
    def test_new_api_v2_support(self):
        """Test new API v2.0 support."""
        agent = LegacyCompatibilityAgent("legacy", "legacy")
        context = ExecutionContext(
            agent_id="legacy", agent_type="legacy", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent(
            {"api_version": "2.0", "data": "new_data"}
        )

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"] == "new_data"

        agent.teardown()

    @pytest.mark.regression
    def test_unsupported_api_version_error(self):
        """Test unsupported API version error."""
        agent = LegacyCompatibilityAgent("legacy", "legacy")
        context = ExecutionContext(
            agent_id="legacy", agent_type="legacy", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"api_version": "3.0"})

        assert result["status"] == "error"

        agent.teardown()


class TestStateManagementRegressions:
    """Regression tests for state management issues."""

    @pytest.mark.regression
    def test_state_counter_increment(self):
        """Test state counter increments correctly."""
        agent = StateRegressionAgent("state", "state")
        context = ExecutionContext(
            agent_id="state", agent_type="state", session_id="test"
        )
        agent.setup(context)

        agent.execute_agent({"action": "increment"})
        result = agent.execute_agent({"action": "increment"})

        assert result["data"]["counter"] == 2

        agent.teardown()

    @pytest.mark.regression
    def test_state_counter_decrement(self):
        """Test state counter decrements correctly."""
        agent = StateRegressionAgent("state", "state")
        context = ExecutionContext(
            agent_id="state", agent_type="state", session_id="test"
        )
        agent.setup(context)

        agent.execute_agent({"action": "increment"})
        agent.execute_agent({"action": "increment"})
        result = agent.execute_agent({"action": "decrement"})

        assert result["data"]["counter"] == 1

        agent.teardown()

    @pytest.mark.regression
    def test_state_reset(self):
        """Test state reset functionality."""
        agent = StateRegressionAgent("state", "state")
        context = ExecutionContext(
            agent_id="state", agent_type="state", session_id="test"
        )
        agent.setup(context)

        agent.execute_agent({"action": "increment"})
        agent.execute_agent({"action": "increment"})
        result = agent.execute_agent({"action": "reset"})

        assert result["data"]["counter"] == 0

        agent.teardown()

    @pytest.mark.regression
    def test_state_history_tracking(self):
        """Test state history is tracked."""
        agent = StateRegressionAgent("state", "state")
        context = ExecutionContext(
            agent_id="state", agent_type="state", session_id="test"
        )
        agent.setup(context)

        agent.execute_agent({"action": "increment"})
        agent.execute_agent({"action": "increment"})
        agent.execute_agent({"action": "decrement"})
        result = agent.execute_agent({"action": "reset"})

        assert result["data"]["history_length"] == 4

        agent.teardown()

    @pytest.mark.regression
    def test_invalid_state_action(self):
        """Test invalid state action handling."""
        agent = StateRegressionAgent("state", "state")
        context = ExecutionContext(
            agent_id="state", agent_type="state", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"action": "invalid_action"})

        assert result["status"] == "error"

        agent.teardown()


class TestOutputFormatRegressions:
    """Regression tests for output format issues."""

    @pytest.mark.regression
    def test_output_json_compatibility(self):
        """Test output is JSON compatible."""
        agent = EdgeCaseAgent("edge", "edge")
        context = ExecutionContext(
            agent_id="edge", agent_type="edge", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"data": {"key": "value"}})

        # Should be JSON serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        assert parsed["status"] == "success"

        agent.teardown()

    @pytest.mark.regression
    def test_output_contains_required_fields(self):
        """Test output contains required fields."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": 10})

        assert "status" in result
        assert result["status"] in ["success", "partial", "error"]

        agent.teardown()

    @pytest.mark.regression
    def test_error_output_format_consistency(self):
        """Test error output format is consistent."""
        agent = BoundaryAgent("boundary", "boundary")
        context = ExecutionContext(
            agent_id="boundary", agent_type="boundary", session_id="test"
        )
        agent.setup(context)

        result = agent.execute_agent({"value": -1})

        assert result["status"] == "error"
        assert "error" in result
        assert isinstance(result["error"], str)

        agent.teardown()


class TestConcurrencyRegressions:
    """Regression tests for concurrency issues."""

    @pytest.mark.regression
    def test_independent_agent_instances(self):
        """Test independent agent instances don't interfere."""
        agent1 = StateRegressionAgent("agent1", "state")
        agent2 = StateRegressionAgent("agent2", "state")

        context = ExecutionContext(
            agent_id="test", agent_type="state", session_id="test"
        )
        agent1.setup(context)
        agent2.setup(context)

        agent1.execute_agent({"action": "increment"})
        agent1.execute_agent({"action": "increment"})

        result2 = agent2.execute_agent({"action": "increment"})

        # agent2 should have counter=1, not affected by agent1
        assert result2["data"]["counter"] == 1

        agent1.teardown()
        agent2.teardown()

    @pytest.mark.regression
    def test_state_isolation(self):
        """Test state is properly isolated."""
        agent = StateRegressionAgent("agent", "state")
        context = ExecutionContext(
            agent_id="agent", agent_type="state", session_id="test"
        )
        agent.setup(context)

        # Modify state
        agent.state["counter"] = 10

        # Execute and verify state was used
        agent.execute_agent({"action": "increment"})

        # State should be maintained
        assert agent.state["counter"] == 11

        agent.teardown()
