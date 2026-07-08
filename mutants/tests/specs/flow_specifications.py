"""
Pre-defined flow specifications for all core orchestration flows.

These specifications drive the automated test generation.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tests.framework.test_generator import OrchestrationFlowSpec

# ========== PHYSICS ORCHESTRATOR SPECS ==========

physics_orchestration_spec = OrchestrationFlowSpec(
    module_path="agents.physics_orchestrator",
    class_name="PhysicsInspiredOrchestrator",
    method_name="orchestrate",
    stages=["ASSESS", "DELIBERATE", "OPTIMIZE", "ACT"],
    decision_points=[
        "no_paths_meet_constraints",
        "multiple_optimal_paths",
        "energy_budget_exceeded",
    ],
    inputs={"state": "DecisionState", "possible_actions": "List[ActionPath]"},
    outputs={
        "action_taken": "str",
        "confidence": "float",
        "expected_impact": "float",
        "optimization_score": "float",
    },
    line_range=(427, 460),
    branch_paths=["optimal_path_found", "no_path_found_wait", "fallback_to_best_available"],
    edge_cases=[
        "empty_action_list",
        "all_actions_exceed_budget",
        "ties_in_optimization_score",
        "negative_energy_values",
    ],
    fixtures_needed=["decision_state", "action_paths", "orchestrator"],
    mocks_needed=[],
)


diffusion_flow_spec = OrchestrationFlowSpec(
    module_path="agents.physics_orchestrator",
    class_name="DiffusionFlowModel",
    method_name="simulate_flow",
    stages=["INITIALIZE", "CALCULATE_GRADIENT", "STEP", "CHECK_CONVERGENCE"],
    decision_points=["convergence_reached", "max_steps_exceeded"],
    inputs={"start_position": "Tuple[float, float]", "steps": "int", "dt": "float"},
    outputs={"trajectory": "List[Tuple[float, float]]"},
    line_range=(1066, 1098),
    branch_paths=["converged", "max_steps"],
    edge_cases=["zero_steps", "single_step", "start_at_attractor", "no_attractors"],
    fixtures_needed=["diffusion_model"],
    mocks_needed=[],
)


# ========== QUANTUM GAME THEORY SPECS ==========

quantum_game_spec = OrchestrationFlowSpec(
    module_path="agents.quantum_game_theory",
    class_name="BlueRedTeamSimulator",
    method_name="run_simulation",
    stages=["INITIALIZE", "UPDATE_STRATEGIES", "MEASURE", "RECORD"],
    decision_points=["quantum_vs_classical_mode", "apply_decoherence", "convergence_check"],
    inputs={"num_rounds": "int", "learning_rate": "float"},
    outputs={
        "mode": "str",
        "num_rounds": "int",
        "rounds": "List[Dict]",
        "final_blue_payoff": "float",
        "final_red_payoff": "float",
    },
    line_range=(1026, 1077),
    branch_paths=["quantum_mode_path", "classical_mode_path", "with_noise", "without_noise"],
    edge_cases=["zero_rounds", "single_round", "very_high_learning_rate", "negative_learning_rate"],
    fixtures_needed=["simulator", "payoff_matrices"],
    mocks_needed=[],
)


# ========== MENTAL MAPPING SPECS ==========

mental_mapping_spec = OrchestrationFlowSpec(
    module_path="agents.mental_mapping",
    class_name="MentalMappingModel",
    method_name="think_through_problem",
    stages=["CREATE_PROBLEM_NODE", "DECOMPOSE", "GENERATE_HYPOTHESIS", "GATHER_EVIDENCE"],
    decision_points=["low_confidence_mark_review", "create_connections"],
    inputs={"problem": "str", "context": "Dict"},
    outputs={"problem_node": "MentalNode", "reasoning_steps": "List[ReasoningStep]"},
    line_range=(443, 546),
    branch_paths=["simple_problem", "complex_problem"],
    edge_cases=["empty_problem_string", "very_long_problem", "null_context"],
    fixtures_needed=["mental_map"],
    mocks_needed=["get_timestamp"],
)
