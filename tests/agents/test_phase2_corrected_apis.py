"""
Phase 2: Corrected Deep Coverage Tests with Actual APIs

This test file uses the ACTUAL module exports discovered from inspection:
- MentalMappingModel (not MentalMapping)
- StrategyState (not StrategySpace)
- No ActionType in quantum_game_theory
- DecisionState, ForceVector, ActionPath actual signatures

Physics Reference Tables Applied:
- Table 4, Eq #1: Initialization tests
- Table 4, Eq #2: Enum validations
- Table 4, Eq #3: Property tests
- Table 4, Eq #6: Operator wiring tests
- Table 1, Eq #49: J = Coverage/Runtime optimization
"""

import pytest

pytest.importorskip("numpy")

from agents.mental_mapping import (
    EdgeType,
    MentalMappingModel,
    MentalNode,
    NodeType,
    ReasoningStep,
)
from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    DiffusionFlowModel,
    EnergyLandscape,
    ForceVector,
    PhysicsInspiredOrchestrator,
    SwarmIntelligence,
)
from agents.quantum_game_theory import (
    NUMPY_AVAILABLE,
    BlueRedTeamSimulator,
    ClassicalGameEngine,
    PayoffOperator,
    QuantumGameState,
    QuantumInspiredGameEngine,
    StrategyState,
    TeamType,
)

# =============================================================================
# MENTAL MAPPING TESTS (Corrected API: MentalMappingModel)
# =============================================================================


class TestPhase2_MentalMappingModel_Corrected:
    """Tests using actual MentalMappingModel class - Table 4, Eq #1"""

    def test_mental_mapping_model_initialization(self):
        """Table 4, Eq #1: Initialization test"""
        model = MentalMappingModel()
        assert model is not None, "model must be initialized"
        assert hasattr(model, "nodes")
        assert hasattr(model, "edges")

    def test_create_node_in_model(self):
        """Table 4, Eq #1: Basic operation coverage"""
        model = MentalMappingModel()
        node = model.create_node(node_type=NodeType.PROBLEM, content="Test problem")
        assert node is not None, "node must be initialized"
        assert node.node_type == NodeType.PROBLEM, "node_type is not valid"

    def test_connect_nodes_in_model(self):
        """Table 4, Eq #1: Graph operations"""
        model = MentalMappingModel()
        node1 = model.create_node(NodeType.PROBLEM, "Problem 1")
        node2 = model.create_node(NodeType.HYPOTHESIS, "Hypothesis 1")

        edge = model.connect_nodes(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type=EdgeType.LEADS_TO,
        )
        assert edge is not None, "edge must be initialized"

    def test_mental_node_creation(self):
        """Table 4, Eq #1: Direct node creation"""
        node = MentalNode(
            node_id="test-1",
            node_type=NodeType.DECISION,
            content="Test decision",
            timestamp="2024-01-01T00:00:00",
        )
        assert node.node_id == "test-1", "node_id is not valid"
        assert node.node_type == NodeType.DECISION, "node_type is not valid"

    def test_reasoning_step_creation(self):
        """Table 4, Eq #1: Reasoning chain elements"""
        step = ReasoningStep(
            step_id="step-1",
            timestamp="2024-01-01T00:00:00",
            thought="Test thought",
            reasoning_type="deductive",
            confidence=0.8,
        )
        assert step.confidence == 0.8, "confidence is not valid"
        assert step.reasoning_type == "deductive", "reasoning_type is not valid"


class TestPhase2_MentalMapping_EnumValidations:
    """Enum validation tests - Table 4, Eq #2"""

    def test_node_type_enum_all_values(self):
        """Table 4, Eq #2: Complete enum coverage"""
        assert NodeType.PROBLEM.value == "problem", "Value must be initialized"
        assert NodeType.HYPOTHESIS.value == "hypothesis", "Value must be initialized"
        assert NodeType.EVIDENCE.value == "evidence", "Value must be initialized"
        assert NodeType.DECISION.value == "decision", "Value must be initialized"
        assert NodeType.ACTION.value == "action", "Value must be initialized"
        assert NodeType.OUTCOME.value == "outcome", "Value must be initialized"
        assert NodeType.REFLECTION.value == "reflection", "Value must be initialized"
        assert NodeType.LEARNING.value == "learning", "Value must be initialized"

    def test_edge_type_enum_all_values(self):
        """Table 4, Eq #2: Edge type enum coverage"""
        assert EdgeType.CAUSES.value == "causes", "Value must be initialized"
        assert EdgeType.SUPPORTS.value == "supports", "Value must be initialized"
        assert EdgeType.CONTRADICTS.value == "contradicts", "Value must be initialized"
        assert EdgeType.LEADS_TO.value == "leads_to", "Value must be initialized"
        assert EdgeType.SIMILAR_TO.value == "similar_to", "Value must be initialized"
        assert EdgeType.DEPENDS_ON.value == "depends_on", "Value must be initialized"
        assert EdgeType.REFINES.value == "refines", "Value must be initialized"
        assert EdgeType.VALIDATES.value == "validates", "Value must be initialized"


# =============================================================================
# PHYSICS ORCHESTRATOR TESTS (Corrected Signatures)
# =============================================================================


class TestPhase2_PhysicsOrchestrator_Corrected:
    """Tests using actual PhysicsInspiredOrchestrator API - Table 4, Eq #1"""

    def test_orchestrator_initialization(self):
        """Table 4, Eq #1: Initialization test"""
        orch = PhysicsInspiredOrchestrator()
        assert orch is not None, "orch must be initialized"

    def test_decision_state_initialization(self):
        """Table 4, Eq #1: DecisionState with actual signature"""
        state = DecisionState(
            current_position="start",
            goal_position="end",
            available_resources=100.0,
            time_available=60.0,
            current_velocity=5.0,
            context={},
        )
        assert state.current_position == "start", "current_position is not valid"
        assert state.goal_position == "end", "goal_position is not valid"
        assert state.available_resources == 100.0, "available_resources is not valid"

    def test_force_vector_creation(self):
        """Table 4, Eq #1: ForceVector with actual signature"""
        force = ForceVector(
            name="test_force",
            magnitude=0.8,
            direction=1.57,
            priority=1.0,  # ~90 degrees
        )
        assert force.name == "test_force", "name is not valid"
        assert force.magnitude == 0.8, "magnitude is not valid"

    def test_force_vector_components(self):
        """Table 4, Eq #6: Operator wiring - vector decomposition"""
        force = ForceVector(
            name="diagonal",
            magnitude=1.0,
            direction=0.785,
            priority=1.0,  # 45 degrees
        )
        x, y = force.get_components()
        assert x > 0, "x must be greater than zero"
        assert y > 0, "y must be greater than zero"

    def test_action_path_creation(self):
        """Table 4, Eq #1: ActionPath with actual signature"""
        path = ActionPath(
            action_type=ActionType.TEST,
            description="Run tests",
            potential_energy=50.0,
            kinetic_energy=20.0,
            friction=2.0,
            momentum=3.0,
        )
        assert path.action_type == ActionType.TEST, "action_type is not valid"
        assert path.description == "Run tests", "description is not valid"

    def test_action_path_energy_calculation(self):
        """Table 4, Eq #20: Euler integration - energy calculation"""
        path = ActionPath(
            action_type=ActionType.REFACTOR,
            description="Refactor code",
            potential_energy=40.0,
            kinetic_energy=15.0,
            friction=1.5,
            momentum=2.0,
        )
        total = path.calculate_total_energy()
        assert isinstance(total, float)
        assert total > 0, "total must be greater than zero"

    def test_action_path_optimization_score(self):
        """Table 4, Eq #49: J = Coverage/Runtime optimization"""
        path = ActionPath(
            action_type=ActionType.OPTIMIZE,
            description="Optimize performance",
            potential_energy=30.0,
            confidence=0.8,
            impact=0.9,
            risk=0.2,
        )
        path.calculate_total_energy()
        score = path.calculate_optimization_score()
        assert isinstance(score, float)


class TestPhase2_PhysicsOrchestrator_EnumValidations:
    """ActionType enum validation - Table 4, Eq #2"""

    def test_action_type_enum_all_values(self):
        """Table 4, Eq #2: Complete ActionType enum coverage"""
        assert ActionType.AUDIT.value == "audit", "Value must be initialized"
        assert ActionType.REFACTOR.value == "refactor", "Value must be initialized"
        assert ActionType.TEST.value == "test", "Value must be initialized"
        assert ActionType.DOCUMENT.value == "document", "Value must be initialized"
        assert ActionType.DEPLOY.value == "deploy", "Value must be initialized"
        assert ActionType.OPTIMIZE.value == "optimize", "Value must be initialized"
        assert ActionType.DEBUG.value == "debug", "Value must be initialized"
        assert ActionType.RESEARCH.value == "research", "Value must be initialized"

    def test_action_type_enum_access(self):
        """Table 4, Eq #2: Enum member access"""
        assert hasattr(ActionType, "AUDIT")
        assert hasattr(ActionType, "REFACTOR")
        assert hasattr(ActionType, "TEST")


class TestPhase2_PhysicsOrchestrator_AdvancedClasses:
    """Advanced physics calculator classes - Table 4, Eq #11"""

    def test_diffusion_flow_model_init(self):
        """Table 4, Eq #11: Advanced pattern initialization"""
        model = DiffusionFlowModel()
        assert model is not None, "model must be initialized"

    def test_energy_landscape_init(self):
        """Table 4, Eq #11: Energy landscape pattern"""
        landscape = EnergyLandscape()
        assert landscape is not None, "landscape must be initialized"

    def test_swarm_intelligence_init(self):
        """Table 4, Eq #11: Swarm intelligence pattern"""
        swarm = SwarmIntelligence()
        assert swarm is not None, "swarm must be initialized"


# =============================================================================
# QUANTUM GAME THEORY TESTS (Corrected API)
# =============================================================================


class TestPhase2_QuantumGameTheory_Corrected:
    """Tests using actual quantum_game_theory API - Table 4, Eq #1"""

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_quantum_game_engine_initialization(self):
        """Table 4, Eq #1: Initialization test"""
        import numpy as np

        blue_strats = ["defend_perimeter", "active_monitoring"]
        red_strats = ["brute_force", "social_engineer"]
        payoff_blue = np.array([[0.8, 0.3], [0.6, 0.9]])
        payoff_red = np.array([[0.2, 0.7], [0.4, 0.1]])

        engine = QuantumInspiredGameEngine(
            blue_strategies=blue_strats,
            red_strategies=red_strats,
            payoff_blue=payoff_blue,
            payoff_red=payoff_red,
        )
        assert engine is not None, "engine must be initialized"

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_classical_game_engine_initialization(self):
        """Table 4, Eq #1: Classical variant"""
        import numpy as np

        blue_strats = ["strategy1"]
        red_strats = ["strategy2"]
        payoff_blue = np.array([[0.5]])
        payoff_red = np.array([[0.5]])

        engine = ClassicalGameEngine(
            blue_strategies=blue_strats,
            red_strategies=red_strats,
            payoff_blue=payoff_blue,
            payoff_red=payoff_red,
        )
        assert engine is not None, "engine must be initialized"

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_blue_red_team_simulator_initialization(self):
        """Table 4, Eq #1: Blue-Red team simulation"""
        import numpy as np

        blue_strats = ["def1"]
        red_strats = ["att1"]
        payoff_blue = np.array([[0.7]])
        payoff_red = np.array([[0.3]])

        sim = BlueRedTeamSimulator(
            blue_strategies=blue_strats,
            red_strategies=red_strats,
            payoff_blue=payoff_blue,
            payoff_red=payoff_red,
        )
        assert sim is not None, "sim must be initialized"

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_quantum_game_state_creation(self):
        """Table 4, Eq #1: Game state initialization"""
        blue_strategy_state = StrategyState(team=TeamType.BLUE, strategies=["defend", "monitor"])
        red_strategy_state = StrategyState(team=TeamType.RED, strategies=["attack", "probe"])

        state = QuantumGameState(blue_state=blue_strategy_state, red_state=red_strategy_state)
        assert state is not None, "state must be initialized"
        assert state.dimension == 4, "dimension is not valid"

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_strategy_state_creation(self):
        """Table 4, Eq #1: Strategy state (not StrategySpace)"""

        strategies = ["s1", "s2"]

        strategy = StrategyState(team=TeamType.BLUE, strategies=strategies)
        assert strategy is not None, "strategy must be initialized"

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy required")
    def test_payoff_operator_creation(self):
        """Table 4, Eq #6: Operator wiring - payoff calculation"""
        import numpy as np

        payoff_matrix = np.array([[0.5, 0.5], [0.5, 0.5]])

        operator = PayoffOperator(payoff_matrix=payoff_matrix, team=TeamType.BLUE)
        assert operator is not None, "operator must be initialized"


class TestPhase2_QuantumGameTheory_EnumValidations:
    """Enum validation tests - Table 4, Eq #2"""

    def test_team_type_enum_values(self):
        """Table 4, Eq #2: TeamType enum coverage"""
        assert hasattr(TeamType, "BLUE")
        assert hasattr(TeamType, "RED")


# =============================================================================
# CROSS-MODULE INTEGRATION TESTS - Table 1, Eq #4 (Conservation)
# =============================================================================


class TestPhase2_CrossModule_Integration:
    """Integration tests across modules - Table 1, Eq #4"""

    def test_mental_mapping_with_physics_orchestrator(self):
        """Table 1, Eq #4: Conservation across modules"""
        # Mental mapping for decision tracking
        model = MentalMappingModel()
        decision_node = model.create_node(NodeType.DECISION, "Choose action path")

        # Physics orchestrator for decision making
        orch = PhysicsInspiredOrchestrator()

        assert decision_node is not None, "decision_node must be initialized"
        assert orch is not None, "orch must be initialized"

    def test_physics_orchestrator_with_mental_mapping(self):
        """Table 1, Eq #4: Decision tracking integration"""
        # Create physics-based decision
        path = ActionPath(
            action_type=ActionType.OPTIMIZE,
            description="Optimize code",
            potential_energy=20.0,
        )

        # Track in mental map
        model = MentalMappingModel()
        action_node = model.create_node(NodeType.ACTION, f"Execute {path.description}")

        assert path is not None, "path must be initialized"
        assert action_node is not None, "action_node must be initialized"


# =============================================================================
# PROPERTY AND GETTER TESTS - Table 4, Eq #3
# =============================================================================


class TestPhase2_Properties_And_Getters:
    """Property and getter coverage tests - Table 4, Eq #3"""

    def test_mental_node_properties(self):
        """Table 4, Eq #3: MentalNode property access"""
        node = MentalNode(
            node_id="prop-test",
            node_type=NodeType.EVIDENCE,
            content="Evidence data",
            timestamp="2024-01-01T00:00:00",
        )

        assert node.confidence == 0.5, "confidence is not valid"
        assert node.importance == 0.5, "importance is not valid"
        assert node.quality_score == 0.0, "quality_score is not valid"
        assert node.needs_review is False, "needs_review is not valid"
        assert node.review_count == 0, "Count must be greater than zero"

    def test_force_vector_properties(self):
        """Table 4, Eq #3: ForceVector properties"""
        force = ForceVector(name="test", magnitude=0.7, direction=1.0, priority=0.9)

        assert force.name == "test", "name is not valid"
        assert force.magnitude == 0.7, "magnitude is not valid"
        assert force.direction == 1.0, "direction is not valid"
        assert force.priority == 0.9, "priority is not valid"

    def test_action_path_calculated_properties(self):
        """Table 4, Eq #3: ActionPath calculated fields"""
        path = ActionPath(
            action_type=ActionType.AUDIT,
            description="Audit code",
            potential_energy=25.0,
        )

        # Check default calculated fields
        assert hasattr(path, "total_energy")
        assert hasattr(path, "optimization_score")


# =============================================================================
# EDGE CASE TESTS - Table 1, Eq #56 (Invariants)
# =============================================================================


class TestPhase2_EdgeCases_Invariants:
    """Edge case tests maintaining invariants - Table 1, Eq #56"""

    def test_force_vector_zero_magnitude(self):
        """Table 1, Eq #56: Zero magnitude invariant"""
        force = ForceVector(name="zero", magnitude=0.0, direction=0.0)
        x, y = force.get_components()
        assert x == 0.0, "x is not valid"
        assert y == 0.0, "y is not valid"

    def test_action_path_minimal_energy(self):
        """Table 1, Eq #56: Minimal energy path"""
        path = ActionPath(
            action_type=ActionType.TEST,
            description="Simple test",
            potential_energy=0.1,
            kinetic_energy=0.1,
            friction=0.0,
            momentum=0.0,
        )
        total = path.calculate_total_energy()
        assert total >= 0, "total must be greater than zero"

    def test_mental_node_confidence_bounds(self):
        """Table 1, Eq #56: Confidence stays in [0, 1]"""
        node = MentalNode(
            node_id="conf-test",
            node_type=NodeType.DECISION,
            content="Test",
            timestamp="2024-01-01T00:00:00",
            confidence=0.9,
        )
        assert 0.0 <= node.confidence <= 1.0, "0 is not valid"

    def test_empty_mental_mapping_model(self):
        """Table 1, Eq #56: Empty model invariants"""
        model = MentalMappingModel()
        # Should not crash with no nodes/edges
        assert model is not None, "model must be initialized"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
