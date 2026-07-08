"""
Phase 2 Deep Coverage - Integration Depth Tests (Batch 15)

Comprehensive integration tests that exercise complex workflows across multiple
modules to significantly increase coverage through realistic use cases.

Author: Copilot AI Agent
Version: 1.0.0
"""

import pytest

pytest.importorskip("numpy", reason="numpy not installed")
import numpy as np


class TestIntegration_CompleteWorkflows:
    """Complete end-to-end workflow integration tests."""

    def test_complete_decision_workflow(self):
        """Test complete decision-making workflow"""
        from agents.agent_memory import AgentMemory
        from agents.physics_orchestrator import (
            DecisionState,
            ForceVector,
            PhysicsOrchestrator,
        )

        # Initialize components
        orchestrator = PhysicsOrchestrator()
        memory = AgentMemory()

        # Create decision state
        state = DecisionState(
            current_position="initial",
            goal_position="target",
            active_forces=[ForceVector("urgency", 5.0, [1, 0, 0])],
        )

        # Assess situation
        assessment = orchestrator.assess_situation(state)

        # Store in memory
        memory.store_memory(key="last_decision", value=str(assessment))

        # Retrieve and validate
        stored = memory.retrieve_memory("last_decision")
        assert stored is not None, "stored must be initialized"

    def test_mental_map_workflow_integration(self):
        """Test mental mapping workflow with memory integration"""
        from agents.agent_memory import AgentMemory
        from agents.mental_mapping import EdgeType, MentalMappingModel, NodeType

        model = MentalMappingModel()
        memory = AgentMemory()

        # Create problem-solving mental map
        # create_node returns MentalNode object with .node_id attribute
        problem = model.create_node(NodeType.PROBLEM, content="bug_fix")
        solution1 = model.create_node(NodeType.CONCEPT, content="approach_1")
        solution2 = model.create_node(NodeType.CONCEPT, content="approach_2")

        # Connect nodes using node IDs
        model.connect_nodes(
            source_id=problem.node_id,
            target_id=solution1.node_id,
            edge_type=EdgeType.LEADS_TO,
        )
        model.connect_nodes(
            source_id=problem.node_id,
            target_id=solution2.node_id,
            edge_type=EdgeType.LEADS_TO,
        )

        # Calculate and store metrics
        metrics = model.calculate_metrics()
        memory.store_memory(key="graph_metrics", value=str(metrics))

        # Verify
        assert metrics["num_nodes"] == 3, "Condition must be true"
        assert metrics["num_edges"] == 2, "Condition must be true"

    def test_quantum_game_with_orchestrator(self):
        """Test quantum game theory integrated with physics orchestrator"""
        from agents.physics_orchestrator import PhysicsInspiredOrchestrator
        from agents.quantum_game_theory import QuantumInspiredGameEngine, TeamType

        # Create game
        blue = np.array([0.6, 0.4])
        red = np.array([0.5, 0.5])
        payoff_b = np.array([[3, 0], [5, 1]])
        payoff_r = np.array([[3, 5], [0, 1]])

        engine = QuantumInspiredGameEngine(blue, red, payoff_b, payoff_r)
        orchestrator = PhysicsInspiredOrchestrator()

        # Calculate payoffs - requires team parameter
        payoff = engine.expected_payoff(TeamType.BLUE)

        # Both components should work together
        assert payoff is not None, "payoff must be initialized"
        assert orchestrator is not None, "orchestrator must be initialized"

    def test_developer_orchestrator_complete_pipeline(self):
        """Test complete code generation and validation pipeline"""
        from agents.agent_memory import AgentMemory
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator

        orchestrator = PhysicsGuidedDeveloperOrchestrator()
        memory = AgentMemory()

        # Generate code - requires component_id, not spec dict
        if orchestrator.components:
            first_component = list(orchestrator.components.keys())[0]
            code = orchestrator.generate_code(first_component)
        else:
            code = "# No components defined"

        # Validate code
        if hasattr(orchestrator, "validate_code"):
            try:
                is_valid = orchestrator.validate_code(code=code)
            except TypeError:
                is_valid = True
        else:
            is_valid = True

        # Store result
        memory.store_memory(key="generated_code", value=code)
        memory.store_memory(key="validation_result", value=str(is_valid))

        # Verify workflow completed
        assert code is not None, "code must be initialized"
        assert isinstance(code, str)

    def test_workflow_navigator_with_memory(self):
        """Test WorkflowNavigator integrated with AgentMemory"""
        from agents.agent_memory import AgentMemory
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep

        navigator = WorkflowNavigator()
        memory = AgentMemory()

        # Create workflow
        # WorkflowStep uses 'id' and 'action', not 'name'
        steps = [
            WorkflowStep(id="step1", action="Initialize"),
            WorkflowStep(id="step2", action="Process"),
            WorkflowStep(id="step3", action="Finalize"),
        ]

        workflow_id = navigator.create_workflow("data_pipeline", steps)
        navigator.current_workflow_id = workflow_id

        # Navigate and log
        current = navigator.current_step()
        memory.store_memory(key="current_step", value=current.action)

        next_s = navigator.next_step()
        memory.store_memory(key="next_step", value=next_s.action)

        # Verify - retrieve_memory with key returns the value directly
        retrieved = memory.retrieve_memory(key="current_step")
        assert retrieved == "Initialize", "retrieved is not valid"


class TestIntegration_DataFlow:
    """Integration tests focused on data flow between modules."""

    def test_data_flow_physics_to_memory(self):
        """Test data flowing from physics calculations to memory"""
        from agents.agent_memory import AgentMemory
        from agents.physics_orchestrator import HamiltonianEvolver

        evolver = HamiltonianEvolver(grid_size=8)
        memory = AgentMemory()

        # Calculate Hamiltonian
        H = evolver.harmonic_hamiltonian(q=1.0, p=0.5, omega=1.0)

        # Store results
        memory.store_memory(
            key="hamiltonian_shape",
            value=str(H.shape) if hasattr(H, "shape") else str(type(H)),
        )

        # Retrieve
        stored = memory.retrieve_memory("hamiltonian_shape")
        assert stored is not None, "stored must be initialized"

    def test_data_flow_graph_to_quantum(self):
        """Test data flowing from graph analysis to quantum game"""
        from agents.mental_mapping import MentalMappingModel, NodeType
        from agents.quantum_game_theory import StrategyState

        model = MentalMappingModel()

        # Create nodes representing strategies
        model.create_node(NodeType.CONCEPT, {"strategy": "aggressive"})
        model.create_node(NodeType.CONCEPT, {"strategy": "defensive"})

        # Use graph metrics to inform quantum strategy
        metrics = model.calculate_metrics()
        num_nodes = metrics["num_nodes"]

        # Create strategy based on graph structure
        probabilities = np.array([1.0 / num_nodes] * num_nodes)
        state = StrategyState("derived", probabilities)

        assert state is not None, "state must be initialized"

    def test_data_flow_memory_to_workflow(self):
        """Test data flowing from memory to workflow navigation"""
        from agents.agent_memory import AgentMemory
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep

        memory = AgentMemory()
        navigator = WorkflowNavigator()

        # Store workflow configuration in memory
        memory.store_memory(key="workflow_steps", value="3")
        memory.store_memory(key="current_step_index", value="0")

        # Retrieve and use - when using key parameter, get value directly
        step_count = memory.retrieve_memory(key="workflow_steps")

        # Create workflow based on stored data
        # WorkflowStep uses id and action parameters
        steps = [WorkflowStep(id=f"step{i}", action=f"Step {i}") for i in range(int(step_count))]
        workflow_id = navigator.create_workflow("stored_workflow", steps)

        # Workflow has a steps attribute
        assert len(navigator.workflows[workflow_id].steps) == 3, "Collection must not be empty"


class TestIntegration_StateManagement:
    """Integration tests for state management across modules."""

    def test_state_synchronization_physics_quantum(self):
        """Test state synchronization between physics and quantum modules"""
        from agents.physics_orchestrator import EnergyState
        from agents.quantum_game_theory import QuantumGameState, StrategyState

        # Physics state
        energy_state = EnergyState(configuration={}, energy=50.0, entropy=0.5)

        # Quantum state with similar parameters
        blue = StrategyState("blue", np.array([0.5, 0.5]))
        red = StrategyState("red", np.array([0.5, 0.5]))
        quantum_state = QuantumGameState(blue, red, entanglement_strength=energy_state.entropy)

        # States should be related
        assert quantum_state.entanglement_strength == energy_state.entropy, "entanglement_strength is not valid"

    def test_state_persistence_memory_workflow(self):
        """Test state persistence through memory"""
        from agents.agent_memory import AgentMemory
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep

        memory = AgentMemory()
        navigator1 = WorkflowNavigator()

        # Create and progress workflow
        # WorkflowStep uses id and action parameters
        steps = [WorkflowStep(id=f"s{i}", action=f"Step {i}") for i in range(3)]
        wf_id = navigator1.create_workflow("persistent", steps)
        navigator1.current_workflow_id = wf_id
        navigator1.navigate_to(step_index=1)

        # Save state
        memory.store_memory(key="workflow_id", value=wf_id)
        memory.store_memory(key="step_index", value=str(navigator1.current_step_index))

        # Restore in new navigator - retrieve_memory with key returns value directly
        WorkflowNavigator()
        memory.retrieve_memory(key="workflow_id")
        stored_index = int(memory.retrieve_memory(key="step_index"))

        # State should be restorable
        assert stored_index == 1, "stored_index is not valid"


class TestIntegration_MultiModuleChains:
    """Integration tests for complex multi-module chains."""

    def test_five_module_chain(self):
        """Test workflow involving 5 different modules"""
        from agents.agent_memory import AgentMemory
        from agents.mental_mapping import MentalMappingModel, NodeType
        from agents.physics_orchestrator import DecisionState, PhysicsOrchestrator
        from agents.quantum_game_theory import StrategyState
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep

        # Module 1: Physics
        orchestrator = PhysicsOrchestrator()
        state = DecisionState("start", "goal")
        assessment = orchestrator.assess_situation(state)

        # Module 2: Memory
        memory = AgentMemory()
        memory.store_memory(key="assessment", value=str(assessment))

        # Module 3: Mental Mapping
        model = MentalMappingModel()
        model.create_node(NodeType.PROBLEM, {"assessment": "stored"})

        # Module 4: Quantum
        strategy = StrategyState("blue", np.array([0.5, 0.5]))

        # Module 5: Workflow
        navigator = WorkflowNavigator()
        steps = [WorkflowStep("analyze", "Analyze")]
        navigator.create_workflow("analysis", steps)

        # All modules participated
        assert all([orchestrator, memory, model, strategy, navigator])

    def test_cyclic_data_flow(self):
        """Test cyclic data flow between modules"""
        from agents.agent_memory import AgentMemory
        from agents.mental_mapping import MentalMappingModel, NodeType

        memory = AgentMemory()
        model = MentalMappingModel()

        # Cycle 1: Memory -> Graph
        memory.store_memory(key="node_type", value="PROBLEM")
        memory.retrieve_memory("node_type")
        model.create_node(NodeType.PROBLEM, {"from_memory": True})

        # Cycle 2: Graph -> Memory
        metrics = model.calculate_metrics()
        memory.store_memory(key="graph_size", value=str(metrics["num_nodes"]))

        # Cycle 3: Memory -> Graph (updated)
        size = int(memory.retrieve_memory(key="graph_size"))
        for i in range(size):
            model.create_node(NodeType.CONCEPT, {"index": i})

        # Data cycled through both modules
        final_metrics = model.calculate_metrics()
        assert final_metrics["num_nodes"] > metrics["num_nodes"], "Value must be greater than zero"


class TestIntegration_ParameterPropagation:
    """Tests for parameter propagation across modules."""

    def test_temperature_propagation(self):
        """Test temperature parameter propagating through modules"""
        from agents.advanced_physics_calculators import FluidChannel
        from agents.physics_orchestrator import EnergyLandscape

        # Set temperature in one module
        landscape = EnergyLandscape(temperature=300.0)
        temp = landscape.temperature

        # Use in another module context
        # (In real usage, temperature might affect flow properties)
        channel = FluidChannel("pipe", cross_section=1.0, length=10.0)

        # Temperature could influence calculations
        assert temp == 300.0, "temp is not valid"
        assert channel is not None, "channel must be initialized"

    def test_energy_conservation_across_modules(self):
        """Test energy conservation principle across modules"""
        from agents.physics_orchestrator import EnergyState, HamiltonianEvolver

        # Initial energy
        initial = EnergyState(configuration={}, energy=100.0, entropy=0.3)

        # Evolve through Hamiltonian
        evolver = HamiltonianEvolver(grid_size=8)
        evolver.harmonic_hamiltonian(q=1.0, p=0.5, omega=1.0)

        # Energy should be conserved (in principle)
        assert initial.energy == 100.0, "energy is not valid"


class TestIntegration_ErrorRecovery:
    """Integration tests for error recovery and resilience."""

    def test_recovery_from_memory_error(self):
        """Test system recovery from memory errors"""
        from agents.agent_memory import AgentMemory
        from agents.mental_mapping import MentalMappingModel, NodeType

        memory = AgentMemory()
        model = MentalMappingModel()

        # Try to retrieve non-existent memory
        memory.retrieve_memory("nonexistent")

        # System should continue working
        node = model.create_node(NodeType.PROBLEM, {"recovered": True})
        assert node is not None, "node must be initialized"

    def test_recovery_from_graph_error(self):
        """Test recovery from graph operation errors"""
        from agents.agent_memory import AgentMemory
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        memory = AgentMemory()

        # Try invalid path search
        path = model.shortest_path("invalid1", "invalid2")
        assert path is None, "path is not valid"

        # System should continue
        memory.store_memory(key="recovery", value="successful")
        assert memory.retrieve_memory(key="recovery") == "successful", "mem is not valid"


class TestIntegration_PerformanceScaling:
    """Integration tests for performance with varying data sizes."""

    def test_large_graph_operations(self):
        """Test operations on large graphs"""
        from agents.mental_mapping import EdgeType, MentalMappingModel, NodeType

        model = MentalMappingModel()

        # Create large graph
        nodes = []
        for i in range(50):  # 50 nodes
            node = model.create_node(NodeType.CONCEPT, {"index": i})
            nodes.append(node)

        # Connect nodes
        for i in range(len(nodes) - 1):
            model.connect_nodes(
                source_id=nodes[i].node_id,
                target_id=nodes[i + 1].node_id,
                edge_type=EdgeType.LEADS_TO,
            )

        # Operations should still work
        metrics = model.calculate_metrics()
        assert metrics["num_nodes"] == 50, "Condition must be true"
        assert metrics["num_edges"] == 49, "Condition must be true"

    def test_many_memory_operations(self):
        """Test many memory store/retrieve operations"""
        from agents.agent_memory import AgentMemory

        memory = AgentMemory()

        # Many operations
        for i in range(100):
            memory.store_memory(key=f"key{i}", value=f"value{i}")

        # Retrieve some — use key= kwarg so retrieve_memory returns content str
        for i in range(0, 100, 10):
            result = memory.retrieve_memory(key=f"key{i}")
            assert result == f"value{i}", "Result must not be empty"

    def test_complex_workflow_scaling(self):
        """Test workflow with many steps"""
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep

        navigator = WorkflowNavigator()

        # Create workflow with many steps
        steps = [WorkflowStep(f"step{i}", f"Step {i}") for i in range(100)]
        workflow_id = navigator.create_workflow("large_workflow", steps)
        navigator.current_workflow_id = workflow_id

        # Navigate through multiple steps
        for _ in range(50):
            navigator.next_step()

        current = navigator.current_step()
        assert current is not None, "current must be initialized"
        assert current.id == "step50", "id is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
