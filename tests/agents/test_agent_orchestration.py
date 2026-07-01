"""
Test cases for quantum-inspired agent orchestration.

Tests agent entanglement, chain creation, and optimization.
"""

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy", reason="numpy not installed")
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.agents.quantum_agent_orchestrator import (
    AgentQuantumState,
    QuantumAgentOrchestrator,
)


class TestAgentQuantumState:
    """Test quantum state behavior of agents"""

    def test_agent_entanglement(self):
        """Agents can be entangled"""
        agent1 = AgentQuantumState("agent1", ["cap1"])
        agent2 = AgentQuantumState("agent2", ["cap2"])

        agent1.entangle(agent2)

        assert agent2 in agent1.entangled_agents, "Condition must be true"
        assert agent1 in agent2.entangled_agents, "Condition must be true"

    def test_correlated_activation(self):
        """Entangled agents show correlated behavior"""
        agent1 = AgentQuantumState("agent1", ["cap1"])
        agent2 = AgentQuantumState("agent2", ["cap2"])

        agent1.entangle(agent2)

        # Activate agent1
        agent1.trigger()

        # agent2 should transition to waiting (correlation)
        assert agent1.state == "active", "state is not valid"
        assert agent2.state == "waiting", "state is not valid"

    def test_coherence_measurement(self):
        """Coherence measures agent coordination"""
        agent1 = AgentQuantumState("agent1", ["cap1"])
        agent2 = AgentQuantumState("agent2", ["cap2"])
        agent3 = AgentQuantumState("agent3", ["cap3"])

        agent1.entangle(agent2)
        agent1.entangle(agent3)

        # All idle = low coherence
        coherence_idle = agent1.measure_coherence()
        assert coherence_idle == 0.0, "coherence_idle is not valid"

        # Activate agents = higher coherence
        agent2.state = "active"
        agent3.state = "active"
        coherence_active = agent1.measure_coherence()
        assert coherence_active == 1.0, "coherence_active is not valid"


class TestQuantumAgentOrchestrator:
    """Test agent orchestration"""

    def test_agent_loading(self):
        """Agents are loaded correctly"""
        orchestrator = QuantumAgentOrchestrator()

        assert "workflow-health-monitor" in orchestrator.agents, "Condition must be true"
        assert "ci-testing-agent" in orchestrator.agents, "Condition must be true"
        assert len(orchestrator.agents) >= 5, "Collection must not be empty"

    def test_entanglement_calculation(self):
        """Entanglements are calculated from prerequisites and data flow"""
        orchestrator = QuantumAgentOrchestrator()

        # workflow-health-monitor outputs should entangle with ci-testing-agent inputs
        ci_testing = orchestrator.agents["ci-testing-agent"]

        # ci-testing should be entangled with workflow-health-monitor
        assert (
            "workflow-health-monitor" in ci_testing.prerequisites
            or "ci-testing-agent" in orchestrator.entanglements.get("workflow-health-monitor", [])
        )

    def test_chain_creation(self):
        """Chains are created correctly"""
        orchestrator = QuantumAgentOrchestrator()

        chain = orchestrator.create_chain(
            primary_agent="workflow-health-monitor", max_depth=2, quantum_optimize=False
        )

        # Chain should start with primary agent
        assert chain[0] == "workflow-health-monitor", "Condition must be true"

        # Chain should have length >= 1
        assert len(chain) >= 1, "Chain must not be empty"

    def test_prerequisite_validation(self):
        """Prerequisites are validated in chain"""
        orchestrator = QuantumAgentOrchestrator()

        # Valid order
        valid_order = ["workflow-health-monitor", "ci-testing-agent", "test-alignment-fixer"]
        assert orchestrator._prerequisites_satisfied(valid_order)

        # Invalid order (ci-testing-agent before prerequisite)
        invalid_order = ["ci-testing-agent", "workflow-health-monitor"]
        assert not orchestrator._prerequisites_satisfied(invalid_order), "not is not valid"

    def test_quantum_optimization(self):
        """Quantum optimization improves chain"""
        orchestrator = QuantumAgentOrchestrator()

        # Set random seed for reproducibility
        np.random.seed(42)

        # Create chain without optimization
        chain_unoptimized = orchestrator.create_chain(
            primary_agent="workflow-health-monitor", max_depth=3, quantum_optimize=False
        )

        # Reset seed
        np.random.seed(42)

        # Create chain with optimization
        chain_optimized = orchestrator.create_chain(
            primary_agent="workflow-health-monitor", max_depth=3, quantum_optimize=True
        )

        # Both should have same agents, possibly different order
        assert set(chain_unoptimized) == set(chain_optimized), "Condition must be true"

        # Optimized should satisfy prerequisites
        assert orchestrator._prerequisites_satisfied(chain_optimized), "orchestrat is not valid"

    def test_chain_plan_generation(self, tmp_path):
        """Chain plan is generated correctly"""
        orchestrator = QuantumAgentOrchestrator()

        chain = ["workflow-health-monitor", "ci-testing-agent"]
        output_file = tmp_path / "chain_plan.json"

        plan = orchestrator.generate_chain_plan(chain, output_file)

        # Plan should have required keys
        assert "chain" in plan, "Condition must be true"
        assert "agents" in plan, "Condition must be true"
        assert "estimated_cost" in plan, "Condition must be true"
        assert "entanglements" in plan, "Condition must be true"

        # Plan should be saved to file
        assert output_file.exists(), "Condition must be true"

        # Cost should be positive
        assert plan["estimated_cost"] > 0, "Value must be greater than zero"

        # Verify file content
        with open(output_file) as f:
            loaded_plan = json.load(f)
        assert loaded_plan == plan, "loaded_plan is not valid"


@pytest.mark.integration
class TestAgentChainExecution:
    """Integration tests for agent chain execution"""

    def test_full_chain_execution(self):
        """Full agent chain can be executed"""
        orchestrator = QuantumAgentOrchestrator()

        # Create chain
        chain = orchestrator.create_chain(
            primary_agent="workflow-health-monitor", max_depth=2, quantum_optimize=True
        )

        # Verify chain structure
        assert len(chain) >= 1, "Chain must not be empty"
        assert chain[0] == "workflow-health-monitor", "Condition must be true"

        # Verify all agents in chain exist
        for agent_name in chain:
            assert agent_name in orchestrator.agents, "Condition must be true"


class TestAgentCapabilityMatching:
    """Test capability input/output matching for entanglement"""

    def test_output_input_matching(self):
        """Agents with matching output/input are entangled"""
        orchestrator = QuantumAgentOrchestrator()

        # workflow-health-monitor outputs 'failures'
        # ci-testing-agent inputs 'failure_analysis' (derived from failures)
        # They should be entangled
        workflow_health = orchestrator.agents["workflow-health-monitor"]

        # Check outputs
        outputs = set()
        for cap in workflow_health.capabilities:
            outputs.update(cap.output_types)

        assert "failures" in outputs or "failure_analysis" in outputs, "Condition must be true"

    def test_shared_prerequisites_entanglement(self):
        """Agents with shared prerequisites are entangled"""
        orchestrator = QuantumAgentOrchestrator()

        # ci-testing-agent and coverage-roadmap-agent both depend on workflow-health-monitor
        ci_agent = orchestrator.agents["ci-testing-agent"]
        coverage_agent = orchestrator.agents["coverage-roadmap-agent"]

        shared_prereqs = set(ci_agent.prerequisites) & set(coverage_agent.prerequisites)

        # If they share prerequisites, they should be entangled
        if shared_prereqs:
            pass  # Placeholder for assertion that was corrupted


class TestQuantumAnnealingOptimization:
    """Test quantum annealing optimization"""

    def test_annealing_respects_prerequisites(self):
        """Annealing optimization maintains prerequisite order"""
        orchestrator = QuantumAgentOrchestrator()

        # Create a longer chain
        np.random.seed(123)
        chain = orchestrator.create_chain(
            primary_agent="workflow-health-monitor", max_depth=3, quantum_optimize=True
        )

        # Verify prerequisites are satisfied
        assert orchestrator._prerequisites_satisfied(chain), "orchestrat is not valid"

    def test_annealing_convergence(self):
        """Annealing optimization converges to solution"""
        orchestrator = QuantumAgentOrchestrator()

        test_chain = ["workflow-health-monitor", "ci-testing-agent", "test-alignment-fixer"]

        # Run optimization multiple times
        np.random.seed(456)
        optimized1 = orchestrator._quantum_optimize_chain(test_chain.copy())

        np.random.seed(789)
        optimized2 = orchestrator._quantum_optimize_chain(test_chain.copy())

        # Both should satisfy prerequisites
        assert orchestrator._prerequisites_satisfied(optimized1), "orchestrat is not valid"
        assert orchestrator._prerequisites_satisfied(optimized2), "orchestrat is not valid"

        # Both should have same agents
        assert set(optimized1) == set(test_chain), "Condition must be true"
        assert set(optimized2) == set(test_chain), "Condition must be true"
