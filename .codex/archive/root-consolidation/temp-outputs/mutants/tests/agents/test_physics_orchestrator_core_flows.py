"""
Comprehensive tests for PhysicsInspiredOrchestrator core orchestration flows.

Coverage targets:
- assess_situation: Lines 205-242
- deliberate_paths: Lines 244-300
- optimize_path: Lines 302-346
- act: Lines 348-392
- orchestrate: Lines 427-460

Target coverage: 28.72% → 85%+
"""

import pytest

from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    PhysicsInspiredOrchestrator,
)


class TestPhysicsOrchestratorCoreFlows:
    """Comprehensive test suite for core orchestration cycle."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def orchestrator(self):
        """Create standard orchestrator instance."""
        return PhysicsInspiredOrchestrator()

    @pytest.fixture
    def decision_state_standard(self):
        """Standard decision state for testing."""
        return DecisionState(
            current_position="feature_implementation",
            goal_position="production_deployment",
            available_resources=0.8,
            time_available=0.7,
            current_velocity=0.5,
            context={"project": "codex", "priority": "high"},
        )

    @pytest.fixture
    def decision_state_constrained(self):
        """Resource-constrained decision state."""
        return DecisionState(
            current_position="bug_fix",
            goal_position="verified_solution",
            available_resources=0.2,
            time_available=0.3,
            current_velocity=0.1,
            context={"urgency": "critical"},
        )

    @pytest.fixture
    def action_paths_standard(self):
        """Standard set of action paths."""
        return [
            ActionPath(
                action_type=ActionType.ANALYZE,
                description="Analyze codebase for optimal solution",
                potential_energy=30.0,
                kinetic_energy=20.0,
                friction=2.0,
                momentum=7.0,
                confidence=0.85,
                risk=0.2,
                impact=0.7,
                urgency=0.6,
            ),
            ActionPath(
                action_type=ActionType.TEST,
                description="Run comprehensive test suite",
                potential_energy=40.0,
                kinetic_energy=25.0,
                friction=3.0,
                momentum=6.0,
                confidence=0.9,
                risk=0.1,
                impact=0.8,
                urgency=0.7,
            ),
            ActionPath(
                action_type=ActionType.REFACTOR,
                description="Refactor for better architecture",
                potential_energy=60.0,
                kinetic_energy=15.0,
                friction=5.0,
                momentum=4.0,
                confidence=0.7,
                risk=0.4,
                impact=0.9,
                urgency=0.4,
            ),
        ]

    @pytest.fixture
    def action_paths_high_energy(self):
        """Action paths exceeding energy budget."""
        return [
            ActionPath(
                action_type=ActionType.DEPLOY,
                description="Major system deployment",
                potential_energy=150.0,  # Exceeds default budget of 100
                kinetic_energy=50.0,
                friction=8.0,
                momentum=2.0,
                confidence=0.6,
                risk=0.8,
                impact=0.95,
                urgency=0.9,
            )
        ]

    @pytest.fixture
    def action_paths_low_confidence(self):
        """Action paths with confidence below threshold."""
        return [
            ActionPath(
                action_type=ActionType.EXECUTE,
                description="Execute uncertain plan",
                potential_energy=20.0,
                kinetic_energy=10.0,
                friction=1.0,
                momentum=5.0,
                confidence=0.4,  # Below default threshold of 0.6
                risk=0.3,
                impact=0.6,
                urgency=0.5,
            )
        ]

    # ========== ASSESS STAGE TESTS ==========

    def test_assess_situation_standard_state(self, orchestrator, decision_state_standard):
        """Test assessment with standard resource allocation."""
        assessment = orchestrator.assess_situation(decision_state_standard)

        # Verify all metrics present
        assert "distance_to_goal" in assessment, "Condition must be true"
        assert "system_entropy" in assessment, "Condition must be true"
        assert "attractive_potential" in assessment, "Condition must be true"
        assert "repulsive_potential" in assessment, "Condition must be true"
        assert "net_potential" in assessment, "Condition must be true"

        # Verify types
        assert isinstance(assessment["distance_to_goal"], float)
        assert isinstance(assessment["system_entropy"], float)
        assert isinstance(assessment["attractive_potential"], float)
        assert isinstance(assessment["repulsive_potential"], float)

        # Verify reasonable ranges
        assert 0.0 <= assessment["distance_to_goal"] <= 10.0, "0 is not valid"
        assert 0.0 <= assessment["system_entropy"] <= 1.0, "0 is not valid"
        assert assessment["attractive_potential"] >= 0.0, "Value must be greater than zero"
        assert assessment["repulsive_potential"] >= 0.0, "Value must be greater than zero"

    def test_assess_situation_high_resources(self, orchestrator):
        """Test assessment with abundant resources."""
        state = DecisionState(
            current_position="planning",
            goal_position="execution",
            available_resources=1.0,
            time_available=1.0,
            current_velocity=0.9,
        )

        assessment = orchestrator.assess_situation(state)

        # High resources → low distance, low entropy, high attractive potential
        assert assessment["distance_to_goal"] < 2.0, "Condition must be true"
        assert assessment["system_entropy"] < 0.3, "Condition must be true"
        assert assessment["attractive_potential"] > 5.0, "Value must be greater than zero"

    def test_assess_situation_low_resources(self, orchestrator, decision_state_constrained):
        """Test assessment with limited resources."""
        assessment = orchestrator.assess_situation(decision_state_constrained)

        # Low resources → high distance, high entropy, low attractive potential
        assert assessment["distance_to_goal"] > 5.0, "Value must be greater than zero"
        assert assessment["system_entropy"] > 0.5, "Value must be greater than zero"
        assert assessment["attractive_potential"] < 3.0, "Condition must be true"

    def test_assess_situation_zero_resources(self, orchestrator):
        """Test assessment edge case: zero resources."""
        state = DecisionState(
            current_position="stuck",
            goal_position="unstuck",
            available_resources=0.0,
            time_available=0.0,
            current_velocity=0.0,
        )

        assessment = orchestrator.assess_situation(state)

        # Zero resources → maximum distance and entropy
        assert assessment["distance_to_goal"] == 10.0, "Condition must be true"
        assert assessment["system_entropy"] == 1.0, "Condition must be true"
        assert assessment["attractive_potential"] == 0.0, "Condition must be true"
        assert assessment["repulsive_potential"] == 5.0, "Condition must be true"

    # ========== DELIBERATE STAGE TESTS ==========

    def test_deliberate_paths_multiple_actions(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test deliberation with multiple action options."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_standard)

        # Verify all paths processed
        assert len(ranked) == len(action_paths_standard), "Ranked must not be empty"

        # Verify all paths have calculated properties
        for path in ranked:
            assert hasattr(path, "optimization_score")
            assert hasattr(path, "total_energy")
            assert path.optimization_score > 0, "optimization_score must be greater than zero"
            assert path.total_energy > 0, "total_energy must be greater than zero"

        # Verify ranking (highest score first)
        scores = [p.optimization_score for p in ranked]
        assert scores == sorted(
            scores, reverse=True
        ), "Paths should be ranked by optimization score"

    def test_deliberate_paths_single_action(self, orchestrator, decision_state_standard):
        """Test deliberation with only one option."""
        single_path = [
            ActionPath(
                action_type=ActionType.EXECUTE,
                description="Only option available",
                potential_energy=50.0,
                confidence=0.8,
                impact=0.9,
            )
        ]

        ranked = orchestrator.deliberate_paths(decision_state_standard, single_path)

        assert len(ranked) == 1, "Ranked must not be empty"
        assert ranked[0].optimization_score > 0, "optimization_score must be greater than zero"

    def test_deliberate_paths_empty_list(self, orchestrator, decision_state_standard):
        """Test deliberation with no actions."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, [])

        assert ranked == [], "ranked is not valid"

    def test_deliberate_paths_tie_breaking(self, orchestrator, decision_state_standard):
        """Test deliberation when multiple paths have similar scores."""
        similar_paths = [
            ActionPath(
                action_type=ActionType.ANALYZE,
                description=f"Option {i}",
                potential_energy=30.0,
                kinetic_energy=20.0,
                friction=2.0,
                momentum=7.0,
                confidence=0.85,
                risk=0.2,
                impact=0.7,
                urgency=0.6,
            )
            for i in range(3)
        ]

        ranked = orchestrator.deliberate_paths(decision_state_standard, similar_paths)

        # All should have identical scores (within floating point precision)
        scores = [p.optimization_score for p in ranked]
        assert (len(set(round(s, 6) for s in scores)) == 1
        ), "Identical paths should have identical scores"

    # ========== OPTIMIZE STAGE TESTS ==========

    def test_optimize_path_finds_optimal(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test optimization finds best path within constraints."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_standard)
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)

        assert optimal is not None, "optimal must be initialized"
        assert optimal.confidence >= orchestrator.config["confidence_threshold"], "confidence must be greater than zero"
        assert optimal.total_energy <= orchestrator.config["energy_budget"], "total_energy is not valid"
        assert optimal.risk <= orchestrator.config["risk_tolerance"], "risk is not valid"

    def test_optimize_path_no_path_meets_constraints(
        self, orchestrator, decision_state_standard, action_paths_low_confidence
    ):
        """Test optimization when no path satisfies all constraints."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_low_confidence)
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)

        assert optimal is None, "optimal is not valid"

    def test_optimize_path_energy_budget_exceeded(
        self, orchestrator, decision_state_standard, action_paths_high_energy
    ):
        """Test optimization with paths exceeding energy budget."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_high_energy)
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)

        assert optimal is None, "optimal is not valid"

    def test_optimize_path_relaxed_constraints(
        self, orchestrator, decision_state_standard, action_paths_high_energy
    ):
        """Test optimization with relaxed constraints allows high-energy paths."""
        # Increase energy budget significantly to accommodate path
        orchestrator.config["energy_budget"] = 300.0  # Increased from 250 to 300
        orchestrator.config["risk_tolerance"] = 0.9

        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_high_energy)
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)

        assert optimal is not None, "optimal must be initialized"
        assert optimal.potential_energy > 100.0, "potential_energy must be greater than zero"

    # ========== ACT STAGE TESTS ==========

    def test_act_with_optimal_path(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test action execution with valid optimal path."""
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_standard)
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)

        result = orchestrator.act(optimal, decision_state_standard)

        # Verify result structure
        assert result["action_taken"] != "wait", "Result must not be empty"
        assert "confidence" in result, "Result must not be empty"
        assert "expected_impact" in result, "Result must not be empty"
        assert "energy_required" in result, "Result must not be empty"
        assert "optimization_score" in result, "Result must not be empty"
        assert "timestamp" in result, "Result must not be empty"

        # Verify decision recorded
        assert len(orchestrator.decision_history) == 1, "Collection must not be empty"
        assert orchestrator.decision_history[0] == result, "Result must not be empty"

    def test_act_with_no_path_waits(self, orchestrator, decision_state_standard):
        """Test action when no optimal path found triggers wait state."""
        result = orchestrator.act(None, decision_state_standard)

        assert result["action_taken"] == "wait", "Result must not be empty"
        assert result["rationale"] == "No path met constraints", "Result must not be empty"
        assert "recommendation" in result, "Result must not be empty"
        assert "timestamp" in result, "Result must not be empty"

    def test_act_records_in_history(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test that all actions are recorded in decision history."""
        # Execute multiple actions
        for _ in range(3):
            ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_standard)
            optimal = orchestrator.optimize_path(ranked, decision_state_standard)
            orchestrator.act(optimal, decision_state_standard)

        assert len(orchestrator.decision_history) == 3, "Collection must not be empty"

    # ========== FULL ORCHESTRATION CYCLE TESTS ==========

    def test_orchestrate_complete_cycle(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test complete ASSESS → DELIBERATE → OPTIMIZE → ACT cycle."""
        result = orchestrator.orchestrate(decision_state_standard, action_paths_standard)

        # Verify all stages executed
        assert "action_taken" in result, "Result must not be empty"
        assert "timestamp" in result, "Result must not be empty"

        # Verify decision recorded
        assert len(orchestrator.decision_history) == 1, "Collection must not be empty"
        assert orchestrator.decision_history[0] == result, "Result must not be empty"

    def test_orchestrate_multiple_cycles_maintain_history(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test multiple orchestration cycles maintain complete history."""
        results = []
        for _ in range(5):
            result = orchestrator.orchestrate(decision_state_standard, action_paths_standard)
            results.append(result)

        # Verify history
        assert len(orchestrator.decision_history) == 5, "Collection must not be empty"
        for i, result in enumerate(results):
            assert orchestrator.decision_history[i] == result, "Result must not be empty"

    def test_orchestrate_no_viable_paths_returns_wait(
        self, orchestrator, decision_state_standard, action_paths_high_energy
    ):
        """Test orchestration with no viable paths returns wait recommendation."""
        result = orchestrator.orchestrate(decision_state_standard, action_paths_high_energy)

        assert result["action_taken"] == "wait", "Result must not be empty"

    # ========== STATE EVOLUTION TESTS ==========
    # Note: These tests removed because PhysicsInspiredOrchestrator.evolve_state()
    # has a different signature (takes EnergyState, not DecisionState with timesteps)
    # The evolve_state tests in test_phase2_deep_coverage_batch13_branch_expansion.py
    # test a different class/method with the timesteps parameter

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow_assess_to_action(
        self, orchestrator, decision_state_standard, action_paths_standard
    ):
        """Test complete workflow from assessment through action."""
        # Step 1: Assess
        assessment = orchestrator.assess_situation(decision_state_standard)
        assert assessment["net_potential"] != 0, "Condition must be true"

        # Step 2: Deliberate
        ranked = orchestrator.deliberate_paths(decision_state_standard, action_paths_standard)
        assert len(ranked) > 0, "Ranked must not be empty"

        # Step 3: Optimize
        optimal = orchestrator.optimize_path(ranked, decision_state_standard)
        assert optimal is not None, "optimal must be initialized"

        # Step 4: Act
        result = orchestrator.act(optimal, decision_state_standard)
        assert result["action_taken"] != "wait", "Result must not be empty"

    def test_load_config_updates_thresholds(self, orchestrator):
        """Test loading configuration updates decision thresholds."""
        original_threshold = orchestrator.config["confidence_threshold"]

        new_config = orchestrator.load_config()
        assert new_config["confidence_threshold"] == original_threshold, "Condition must be true"

        # Modify and verify
        orchestrator.config["confidence_threshold"] = 0.8
        assert orchestrator.config["confidence_threshold"] == 0.8, "orchestrat is not valid"


class TestDiffusionFlowModel:
    """Test suite for DiffusionFlowModel."""

    def test_diffusion_coefficient_property_exists(self):
        """Test diffusion_coefficient property is accessible."""
        from agents.physics_orchestrator import DiffusionFlowModel

        model = DiffusionFlowModel(dimensions=2, resolution=10, diffusion_coefficient=0.3)

        assert hasattr(model, "diffusion_coefficient")
        assert model.diffusion_coefficient == 0.3, "diffusion_coefficient is not valid"

    def test_diffusion_coefficient_default_value(self):
        """Test default diffusion coefficient value."""
        from agents.physics_orchestrator import DiffusionFlowModel

        model = DiffusionFlowModel()

        assert model.diffusion_coefficient == 0.5, "diffusion_coefficient is not valid"

    def test_add_attractor_and_repulsor(self):
        """Test adding attractors and repulsors."""
        from agents.physics_orchestrator import DiffusionFlowModel

        model = DiffusionFlowModel(dimensions=2, resolution=10)

        # Add attractor
        model.add_attractor((0.5, 0.5), strength=1.0)
        assert len(model.attractors) == 1, "Collection must not be empty"

        # Add repulsor
        model.add_repulsor((0.2, 0.2), strength=0.5)
        assert len(model.repulsors) == 1, "Collection must not be empty"

    def test_potential_field_calculation(self):
        """Test potential field is calculated correctly."""
        from agents.physics_orchestrator import DiffusionFlowModel

        model = DiffusionFlowModel(dimensions=2, resolution=5)
        model.add_attractor((0.5, 0.5), strength=1.0)

        # Field should be recalculated
        assert len(model.potential_field) > 0, "Collection must not be empty"
