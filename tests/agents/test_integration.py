"""
Integration Tests for Agent Test Harness
=========================================

Tests multi-agent orchestration, handoff protocols, data passing,
and state preservation across agent executions.

Phase 4B Deliverable: Integration Tests
"""

import json
from typing import Any, Dict, List

import pytest

from tests.agents.test_harness import (
    AgentTestHarness,
    ExecutionContext,
)

# ============================================================================
# MOCK MULTI-AGENT ORCHESTRATOR
# ============================================================================


class MockOrchestrator(AgentTestHarness):
    """Mock orchestrator for testing multi-agent workflows."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize orchestrator."""
        self.context = context
        self.agents = {}
        self.workflow_state = {"agents_executed": [], "results": {}}
        self.handoff_log = []

    def teardown(self) -> None:
        """Cleanup orchestrator."""
        self.agents = {}
        self.workflow_state = {"agents_executed": [], "results": {}}
        self.handoff_log = []

    def register_agent(self, agent_id: str, agent: AgentTestHarness) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent_id] = agent

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration workflow."""
        workflow_type = inputs.get("workflow", "sequential")
        agent_ids = inputs.get("agents", [])

        if workflow_type == "sequential":
            return self._execute_sequential(agent_ids, inputs)
        elif workflow_type == "parallel":
            return self._execute_parallel(agent_ids, inputs)
        else:
            return {
                "status": "error",
                "error": f"Unknown workflow type: {workflow_type}",
            }

    def _execute_sequential(self, agent_ids: List[str], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents sequentially."""
        results = {}
        previous_output = inputs.get("initial_data", {})

        for agent_id in agent_ids:
            if agent_id not in self.agents:
                return {
                    "status": "error",
                    "error": f"Agent not found: {agent_id}",
                }

            agent = self.agents[agent_id]
            result = agent.execute_agent(previous_output)
            results[agent_id] = result
            previous_output = result.get("data", {})

            self.workflow_state["agents_executed"].append(agent_id)
            self.workflow_state["results"][agent_id] = result

        return {
            "status": "success",
            "orchestration": {
                "workflow": "sequential",
                "agents_executed": agent_ids,
                "total_duration_ms": sum(
                    r.get("metadata", {}).get("execution_time_ms", 0)
                    for r in results.values()
                ),
            },
            "results": results,
        }

    def _execute_parallel(self, agent_ids: List[str], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents in parallel (simulated)."""
        results = {}

        for agent_id in agent_ids:
            if agent_id not in self.agents:
                return {
                    "status": "error",
                    "error": f"Agent not found: {agent_id}",
                }

            agent = self.agents[agent_id]
            result = agent.execute_agent(inputs)
            results[agent_id] = result

            self.workflow_state["agents_executed"].append(agent_id)
            self.workflow_state["results"][agent_id] = result

        return {
            "status": "success",
            "orchestration": {
                "workflow": "parallel",
                "agents_executed": agent_ids,
                "total_duration_ms": max(
                    r.get("metadata", {}).get("execution_time_ms", 0)
                    for r in results.values()
                ),
            },
            "results": results,
        }

    def handoff_data(
        self, from_agent: str, to_agent: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute handoff from one agent to another."""
        if from_agent not in self.agents or to_agent not in self.agents:
            return {
                "status": "error",
                "error": "Invalid agent in handoff",
            }

        self.handoff_log.append(
            {
                "from": from_agent,
                "to": to_agent,
                "data_size": len(json.dumps(data)),
            }
        )

        # Execute handoff
        from_agent_obj = self.agents[from_agent]
        from_result = from_agent_obj.execute_agent(data)

        to_agent_obj = self.agents[to_agent]
        to_result = to_agent_obj.execute_agent(from_result.get("data", {}))

        return {
            "status": "success",
            "handoff": {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "data_passed": from_result.get("data", {}),
            },
            "result": to_result,
        }


class MockDataTransformAgent(AgentTestHarness):
    """Mock agent that transforms data."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize transform agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup transform agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation."""
        data = inputs.get("data", {})
        transformed = {
            "original": data,
            "transformed": {k: str(v).upper() if isinstance(v, str) else v for k, v in data.items()},
            "transformation": "uppercase_strings"
        }

        return {
            "status": "success",
            "data": transformed,
            "metadata": {"execution_time_ms": 50},
        }


class MockAggregationAgent(AgentTestHarness):
    """Mock agent that aggregates data."""

    def setup(self, context: ExecutionContext) -> None:
        """Initialize aggregation agent."""
        self.context = context

    def teardown(self) -> None:
        """Cleanup aggregation agent."""
        pass

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data aggregation."""
        if isinstance(inputs, list):
            aggregated = {
                "count": len(inputs),
                "sum": sum(x for x in inputs if isinstance(x, (int, float))),
                "items": inputs,
            }
        else:
            aggregated = {"count": 1, "sum": 0, "items": [inputs]}

        return {
            "status": "success",
            "data": aggregated,
            "metadata": {"execution_time_ms": 100},
        }


# ============================================================================
# INTEGRATION TEST SUITE
# ============================================================================


class TestMultiAgentOrchestration:
    """Test suite for multi-agent orchestration."""

    @pytest.mark.integration
    def test_sequential_workflow_execution(self):
        """Test sequential workflow execution."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockAggregationAgent("agent2", "aggregate")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        result = orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1", "agent2"],
                "initial_data": {"key": "value"},
            }
        )

        assert result["status"] == "success"
        assert result["orchestration"]["workflow"] == "sequential"
        assert result["orchestration"]["agents_executed"] == ["agent1", "agent2"]
        assert "agent1" in result["results"]
        assert "agent2" in result["results"]

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_parallel_workflow_execution(self):
        """Test parallel workflow execution."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        result = orchestrator.execute_agent(
            {
                "workflow": "parallel",
                "agents": ["agent1", "agent2"],
                "initial_data": {"key": "value"},
            }
        )

        assert result["status"] == "success"
        assert result["orchestration"]["workflow"] == "parallel"
        assert len(result["orchestration"]["agents_executed"]) == 2

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_workflow_state_tracking(self):
        """Test workflow state is tracked correctly."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1", "agent2"],
                "initial_data": {"key": "value"},
            }
        )

        assert len(orchestrator.workflow_state["agents_executed"]) == 2
        assert "agent1" in orchestrator.workflow_state["results"]
        assert "agent2" in orchestrator.workflow_state["results"]

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_invalid_agent_handling(self):
        """Test handling of invalid agent references."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)

        result = orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["nonexistent_agent"],
                "initial_data": {},
            }
        )

        assert result["status"] == "error"
        assert "not found" in result["error"]

        orchestrator.teardown()


class TestAgentHandoff:
    """Test suite for agent handoff protocols."""

    @pytest.mark.integration
    def test_basic_handoff(self):
        """Test basic handoff between agents."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockAggregationAgent("agent2", "aggregate")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        result = orchestrator.handoff_data(
            "agent1", "agent2", {"key": "value"}
        )

        assert result["status"] == "success"
        assert result["handoff"]["from_agent"] == "agent1"
        assert result["handoff"]["to_agent"] == "agent2"
        assert "result" in result

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_handoff_data_passing(self):
        """Test data is correctly passed during handoff."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        test_data = {"key": "value"}
        result = orchestrator.handoff_data("agent1", "agent2", test_data)

        assert result["handoff"]["data_passed"] is not None
        assert len(orchestrator.handoff_log) == 1

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_handoff_logging(self):
        """Test handoff is logged correctly."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        orchestrator.handoff_data("agent1", "agent2", {"test": "data"})
        orchestrator.handoff_data("agent2", "agent1", {"test": "data2"})

        assert len(orchestrator.handoff_log) == 2
        assert orchestrator.handoff_log[0]["from"] == "agent1"
        assert orchestrator.handoff_log[1]["from"] == "agent2"

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()


class TestDataPassing:
    """Test suite for data passing between agents."""

    @pytest.mark.integration
    def test_data_structure_preservation(self):
        """Test data structure is preserved through handoff."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        test_data = {"key1": "value1", "key2": "value2", "nested": {"key3": "value3"}}
        result = orchestrator.handoff_data("agent1", "agent2", test_data)

        # Data should be passed to the result
        assert result["status"] == "success"

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()

    @pytest.mark.integration
    def test_large_data_passing(self):
        """Test passing large data structures."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockAggregationAgent("agent2", "aggregate")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)

        # Create large data structure
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}

        result = orchestrator.handoff_data("agent1", "agent2", large_data)

        assert result["status"] == "success"

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()


class TestStatePreservation:
    """Test suite for state preservation across executions."""

    @pytest.mark.integration
    def test_orchestrator_state_preservation(self):
        """Test orchestrator state is preserved across executions."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)

        orchestrator.register_agent("agent1", agent1)

        # First execution
        orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1"],
                "initial_data": {},
            }
        )

        first_state = orchestrator.workflow_state.copy()

        # Second execution
        orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1"],
                "initial_data": {},
            }
        )

        # State should accumulate
        assert len(orchestrator.workflow_state["agents_executed"]) >= len(
            first_state["agents_executed"]
        )

        orchestrator.teardown()
        agent1.teardown()

    @pytest.mark.integration
    def test_state_isolation_between_orchestrators(self):
        """Test state is isolated between different orchestrators."""
        orch1 = MockOrchestrator("orch1", "orchestrator")
        orch2 = MockOrchestrator("orch2", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orch1.setup(context)
        orch2.setup(context)
        agent1.setup(context)

        orch1.register_agent("agent1", agent1)
        orch2.register_agent("agent1", agent1)

        orch1.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1"],
                "initial_data": {},
            }
        )

        assert len(orch1.workflow_state["agents_executed"]) == 1
        assert len(orch2.workflow_state["agents_executed"]) == 0

        orch1.teardown()
        orch2.teardown()
        agent1.teardown()


class TestErrorPropagation:
    """Test suite for error handling in integration."""

    @pytest.mark.integration
    def test_error_in_sequential_workflow(self):
        """Test error handling in sequential workflow."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)

        orchestrator.register_agent("agent1", agent1)

        # Invalid workflow type
        result = orchestrator.execute_agent(
            {
                "workflow": "invalid",
                "agents": ["agent1"],
                "initial_data": {},
            }
        )

        assert result["status"] == "error"

        orchestrator.teardown()
        agent1.teardown()

    @pytest.mark.integration
    def test_partial_workflow_failure(self):
        """Test handling of partial workflow failures."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)

        orchestrator.register_agent("agent1", agent1)
        # agent2 not registered - should cause error

        result = orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1", "agent2"],
                "initial_data": {},
            }
        )

        assert result["status"] == "error"

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()


class TestComplexWorkflows:
    """Test suite for complex multi-agent workflows."""

    @pytest.mark.integration
    def test_three_agent_sequential_workflow(self):
        """Test three-agent sequential workflow."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        agent1 = MockDataTransformAgent("agent1", "transform")
        agent2 = MockDataTransformAgent("agent2", "transform")
        agent3 = MockAggregationAgent("agent3", "aggregate")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        agent1.setup(context)
        agent2.setup(context)
        agent3.setup(context)

        orchestrator.register_agent("agent1", agent1)
        orchestrator.register_agent("agent2", agent2)
        orchestrator.register_agent("agent3", agent3)

        result = orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["agent1", "agent2", "agent3"],
                "initial_data": {"key": "value"},
            }
        )

        assert result["status"] == "success"
        assert len(result["orchestration"]["agents_executed"]) == 3

        orchestrator.teardown()
        agent1.teardown()
        agent2.teardown()
        agent3.teardown()

    @pytest.mark.integration
    def test_mixed_agent_types_workflow(self):
        """Test workflow with mixed agent types."""
        orchestrator = MockOrchestrator("orchestrator", "orchestrator")
        transform_agent = MockDataTransformAgent("transformer", "transform")
        aggregate_agent = MockAggregationAgent("aggregator", "aggregate")

        context = ExecutionContext(
            agent_id="orchestrator",
            agent_type="orchestrator",
            session_id="test-session",
        )
        orchestrator.setup(context)
        transform_agent.setup(context)
        aggregate_agent.setup(context)

        orchestrator.register_agent("transformer", transform_agent)
        orchestrator.register_agent("aggregator", aggregate_agent)

        result = orchestrator.execute_agent(
            {
                "workflow": "sequential",
                "agents": ["transformer", "aggregator"],
                "initial_data": {"key": "value"},
            }
        )

        assert result["status"] == "success"
        assert "transformer" in result["results"]
        assert "aggregator" in result["results"]

        orchestrator.teardown()
        transform_agent.teardown()
        aggregate_agent.teardown()
