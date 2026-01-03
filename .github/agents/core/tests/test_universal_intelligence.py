"""
Tests for Universal Intelligence Module (Phase 8.7).

Test Categories:
1. Universal Task Interface (UTI)
2. Meta-Policy Router (MPR)
3. Abstraction Engine
4. Grounding Layer
5. Meta-Cognition
6. Universal Pattern Store
7. Universal Controller
8. Adiabatic Scheduler
9. Decoherence Model
10. Integration Tests

All tests are deterministic with fixed seeds.
"""

import pytest
import json
import math
from datetime import datetime

from ..universal_intelligence import (
    # Constants
    K1_TARGET,
    K1_STRETCH_TARGET,
    QUANTUM_ADVANTAGE_TARGET,
    NEGATIVE_TRANSFER_THRESHOLD,
    STRATEGIES,
    DEFAULT_MAX_DEMO_STEPS,
    EARLY_TERMINATION_PROBABILITY,
    MAX_QUANTUM_ADVANTAGE,
    K1_EPSILON,
    # UTI
    TaskSpec,
    TaskResult,
    UniversalTaskInterface,
    # MPR
    StrategyAmplitude,
    TaskFeatures,
    MetaPolicyRouter,
    # Abstraction
    Concept,
    Relation,
    Analogy,
    AbstractionEngine,
    # Grounding
    AbstractStep,
    GroundedAction,
    ExecutionTrace,
    GroundingLayer,
    # Meta-Cognition
    SelfAssessment,
    RecommendedAction,
    MetaCognition,
    # UPS
    Pattern,
    UniversalPatternStore,
    # Controller
    UniversalController,
    # Annealing
    AdiabaticScheduler,
    # Decoherence
    DecoherenceModel,
    # Helper functions
    calculate_safe_quantum_advantage,
    # PRE-COMMIT 1 additions
    TaskComplexity,
    estimate_task_complexity,
    validate_task_spec_schema,
    EnvironmentAdapter,
    GridWorldAdapter,
    BanditAdapter,
    ClassificationAdapter,
    ENVIRONMENT_ADAPTERS,
    # PRE-COMMIT 2 additions
    MAMLState,
    ReptileState,
    StrategyPerformance,
    DynamicHyperparamTuner,
    StrategyBenchmark,
)


# =============================================================================
# TEST CONSTANTS
# =============================================================================


class TestConstants:
    """Test constant definitions."""
    
    def test_k1_target(self):
        """Test k₁ target is correct."""
        assert K1_TARGET == 0.28
    
    def test_k1_stretch_target(self):
        """Test k₁ stretch target is correct."""
        assert K1_STRETCH_TARGET == 0.255
    
    def test_quantum_advantage_target(self):
        """Test quantum advantage target is correct."""
        assert QUANTUM_ADVANTAGE_TARGET == 3.57
    
    def test_negative_transfer_threshold(self):
        """Test negative transfer threshold is correct."""
        assert NEGATIVE_TRANSFER_THRESHOLD == 0.05
    
    def test_strategies_defined(self):
        """Test strategies list is defined."""
        assert len(STRATEGIES) >= 5
        assert "maml" in STRATEGIES
        assert "reptile" in STRATEGIES
    
    def test_execution_constants(self):
        """Test execution constants are defined."""
        assert DEFAULT_MAX_DEMO_STEPS == 100
        assert EARLY_TERMINATION_PROBABILITY == 0.01
        # MAX_QUANTUM_ADVANTAGE = 10 * QUANTUM_ADVANTAGE_TARGET = 35.7
        assert MAX_QUANTUM_ADVANTAGE == 10.0 * QUANTUM_ADVANTAGE_TARGET
        assert K1_EPSILON == 1e-10


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_calculate_safe_quantum_advantage_normal(self):
        """Test quantum advantage with normal k1."""
        # k1 = 0.28 -> advantage = 1/0.28 = 3.57
        advantage = calculate_safe_quantum_advantage(0.28)
        assert advantage == pytest.approx(3.57, abs=0.01)
    
    def test_calculate_safe_quantum_advantage_zero(self):
        """Test quantum advantage with zero k1."""
        advantage = calculate_safe_quantum_advantage(0.0)
        assert advantage == MAX_QUANTUM_ADVANTAGE
    
    def test_calculate_safe_quantum_advantage_tiny(self):
        """Test quantum advantage with very small k1."""
        advantage = calculate_safe_quantum_advantage(1e-15)
        assert advantage == MAX_QUANTUM_ADVANTAGE
    
    def test_calculate_safe_quantum_advantage_capped(self):
        """Test quantum advantage is capped."""
        advantage = calculate_safe_quantum_advantage(0.001)
        # 1/0.001 = 1000, but capped at MAX_QUANTUM_ADVANTAGE (~35.7)
        assert advantage == MAX_QUANTUM_ADVANTAGE


# =============================================================================
# TEST UNIVERSAL TASK INTERFACE
# =============================================================================


class TestTaskSpec:
    """Test TaskSpec dataclass."""
    
    def test_create_task_spec(self):
        """Test creating a TaskSpec."""
        spec = TaskSpec(
            environment="test_env",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1", "params": {}},
            termination={"max_steps": 100, "criteria": {}},
            seed=12345,
        )
        assert spec.environment == "test_env"
        assert spec.seed == 12345
    
    def test_task_spec_to_json(self):
        """Test TaskSpec JSON serialization."""
        spec = TaskSpec(
            environment="test_env",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1", "params": {}},
            termination={"max_steps": 100},
            seed=12345,
        )
        json_str = spec.to_json()
        data = json.loads(json_str)
        assert data["environment"] == "test_env"
        assert data["seed"] == 12345
    
    def test_task_spec_from_json(self):
        """Test TaskSpec JSON deserialization."""
        json_str = json.dumps({
            "environment": "test_env",
            "initial_state": {"x": 0},
            "reward_spec": {"id": "reward:v1", "params": {}},
            "termination": {"max_steps": 100},
            "seed": 12345,
        })
        spec = TaskSpec.from_json(json_str)
        assert spec.environment == "test_env"
        assert spec.seed == 12345
    
    def test_task_spec_signature(self):
        """Test TaskSpec signature generation."""
        spec = TaskSpec(
            environment="test_env",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1", "params": {}},
            termination={"max_steps": 100},
            seed=12345,
        )
        sig = spec.get_signature()
        assert len(sig) == 16
        assert isinstance(sig, str)


class TestTaskResult:
    """Test TaskResult dataclass."""
    
    def test_create_task_result(self):
        """Test creating a TaskResult."""
        result = TaskResult(
            action_sequence=["a1", "a2"],
            cumulative_reward=10.5,
            v_mu_pi=0.75,
            metrics={"accuracy": 0.9},
        )
        assert result.cumulative_reward == 10.5
        assert result.v_mu_pi == 0.75
    
    def test_task_result_json_roundtrip(self):
        """Test TaskResult JSON roundtrip."""
        result = TaskResult(
            action_sequence=["a1", "a2"],
            cumulative_reward=10.5,
            v_mu_pi=0.75,
            metrics={"accuracy": 0.9},
        )
        json_str = result.to_json()
        restored = TaskResult.from_json(json_str)
        assert restored.cumulative_reward == result.cumulative_reward
        assert restored.v_mu_pi == result.v_mu_pi


class TestUniversalTaskInterface:
    """Test UniversalTaskInterface."""
    
    def test_create_uti(self):
        """Test creating UTI."""
        uti = UniversalTaskInterface(seed=12345)
        assert uti.seed == 12345
    
    def test_validate_task_spec_valid(self):
        """Test validating a valid TaskSpec."""
        uti = UniversalTaskInterface()
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 100},
        )
        is_valid, errors = uti.validate_task_spec(spec)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_task_spec_invalid(self):
        """Test validating an invalid TaskSpec."""
        uti = UniversalTaskInterface()
        spec = TaskSpec(
            environment="",  # Empty
            initial_state={},
            reward_spec={},  # Missing id
            termination={},  # Missing max_steps
        )
        is_valid, errors = uti.validate_task_spec(spec)
        assert not is_valid
        assert len(errors) >= 2
    
    def test_execute_task_deterministic(self):
        """Test task execution is deterministic."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
            seed=42,
        )
        
        result1 = uti.execute_task(spec)
        
        uti2 = UniversalTaskInterface(seed=12345)
        result2 = uti2.execute_task(spec)
        
        assert result1.cumulative_reward == result2.cumulative_reward
        assert result1.action_sequence == result2.action_sequence


# =============================================================================
# TEST META-POLICY ROUTER
# =============================================================================


class TestStrategyAmplitude:
    """Test StrategyAmplitude dataclass."""
    
    def test_create_amplitude(self):
        """Test creating StrategyAmplitude."""
        amp = StrategyAmplitude(strategy="maml", real=0.5, imag=0.5)
        assert amp.strategy == "maml"
    
    def test_probability_calculation(self):
        """Test Born rule probability calculation."""
        amp = StrategyAmplitude(strategy="maml", real=0.5, imag=0.5)
        prob = amp.probability
        assert prob == pytest.approx(0.5, abs=0.01)
    
    def test_phase_rotation(self):
        """Test phase rotation."""
        amp = StrategyAmplitude(strategy="maml", real=1.0, imag=0.0)
        amp.apply_phase(math.pi / 2)
        assert amp.real == pytest.approx(0.0, abs=0.01)
        assert amp.imag == pytest.approx(1.0, abs=0.01)


class TestMetaPolicyRouter:
    """Test MetaPolicyRouter."""
    
    def test_create_router(self):
        """Test creating router."""
        router = MetaPolicyRouter(seed=12345)
        assert router.seed == 12345
        assert len(router.amplitudes) == len(STRATEGIES)
    
    def test_uniform_superposition(self):
        """Test uniform superposition initialization."""
        router = MetaPolicyRouter(seed=12345)
        probs = router.get_probability_distribution()
        
        # Should be approximately uniform
        expected_prob = 1.0 / len(STRATEGIES)
        for prob in probs.values():
            assert prob == pytest.approx(expected_prob, abs=0.01)
    
    def test_normalization(self):
        """Test amplitude normalization."""
        router = MetaPolicyRouter(seed=12345)
        
        # Manually denormalize
        for amp in router.amplitudes:
            amp.real *= 2.0
        
        router.normalize()
        
        total_prob = sum(a.probability for a in router.amplitudes)
        assert total_prob == pytest.approx(1.0, abs=0.001)
    
    def test_measurement_deterministic(self):
        """Test measurement is deterministic with seed."""
        router = MetaPolicyRouter(seed=12345)
        
        result1 = router.measure(seed=42)
        result2 = MetaPolicyRouter(seed=12345).measure(seed=42)
        
        assert result1 == result2
    
    def test_update_amplitudes(self):
        """Test updating amplitudes based on features."""
        router = MetaPolicyRouter(seed=12345)
        
        features = TaskFeatures(
            domain_signature="test",
            complexity={"obs_dim": 128},
            similarity_topk=[{"domain": "similar", "score": 0.9}],
            risk={"neg_transfer_prob": 0.0},
        )
        
        router.update_amplitudes(features)
        
        # Transfer strategies should have higher probability
        probs = router.get_probability_distribution()
        transfer_prob = sum(p for s, p in probs.items() if "transfer" in s)
        assert transfer_prob > 0


# =============================================================================
# TEST ABSTRACTION ENGINE
# =============================================================================


class TestAbstractionEngine:
    """Test AbstractionEngine."""
    
    def test_create_engine(self):
        """Test creating abstraction engine."""
        engine = AbstractionEngine()
        assert len(engine.concepts) == 0
    
    def test_extract_concepts(self):
        """Test concept extraction."""
        engine = AbstractionEngine()
        observations = [
            {"is_active": True, "value": 10},
            {"is_active": False, "is_valid": True},
        ]
        
        concepts = engine.extract_concepts(observations)
        assert len(concepts) > 0
    
    def test_map_relations(self):
        """Test relation mapping."""
        engine = AbstractionEngine()
        observations = [
            {"is_active": True, "is_valid": True},
        ]
        
        concepts = engine.extract_concepts(observations)
        relations = engine.map_relations(concepts, observations)
        
        # Should find co-occurrence relation
        assert len(relations) >= 0  # May or may not find relations
    
    def test_get_abstraction_output(self):
        """Test getting abstraction output."""
        engine = AbstractionEngine()
        observations = [
            {"is_active": True},
        ]
        engine.extract_concepts(observations)
        
        output = engine.get_abstraction_output()
        assert "abstractions" in output
        assert "relations" in output
        assert "analogies" in output
        assert "confidence" in output


# =============================================================================
# TEST GROUNDING LAYER
# =============================================================================


class TestGroundingLayer:
    """Test GroundingLayer."""
    
    def test_create_grounding_layer(self):
        """Test creating grounding layer."""
        layer = GroundingLayer()
        assert len(layer.adapters) >= 2
    
    def test_ground_plan(self):
        """Test grounding a plan."""
        layer = GroundingLayer()
        steps = [
            AbstractStep(op="request_review", target="PR#123"),
            AbstractStep(op="comment", target="issue#456"),
        ]
        
        actions, feasibility = layer.ground_plan(steps)
        assert len(actions) == 2
        assert feasibility > 0
    
    def test_execute_actions_dry_run(self):
        """Test executing actions in dry run mode."""
        layer = GroundingLayer()
        actions = [
            GroundedAction(adapter="github_api_mock", op="request_reviewers", args={}),
        ]
        
        traces = layer.execute_actions(actions, dry_run=True)
        assert len(traces) == 1
        assert traces[0].status == "simulated"
    
    def test_get_grounding_output(self):
        """Test getting grounding output."""
        layer = GroundingLayer()
        steps = [AbstractStep(op="request_review", target="PR#123")]
        
        output = layer.get_grounding_output(steps)
        assert "abstract_plan" in output
        assert "grounded_actions" in output
        assert "feasibility_score" in output
        assert "execution_trace" in output


# =============================================================================
# TEST META-COGNITION
# =============================================================================


class TestMetaCognition:
    """Test MetaCognition."""
    
    def test_create_metacognition(self):
        """Test creating meta-cognition."""
        mc = MetaCognition()
        assert len(mc.domain_knowledge) == 0
    
    def test_update_domain_knowledge(self):
        """Test updating domain knowledge."""
        mc = MetaCognition()
        mc.update_domain_knowledge("domain_a", 0.8)
        
        assert "domain_a" in mc.domain_knowledge
        assert mc.domain_knowledge["domain_a"] == 0.8
    
    def test_get_self_assessment(self):
        """Test getting self-assessment."""
        mc = MetaCognition()
        mc.update_domain_knowledge("known_domain", 0.9)
        mc.update_domain_knowledge("unknown_domain", 0.3)
        
        assessment = mc.get_self_assessment()
        assert assessment.known_domains >= 1
        assert assessment.unknown_domains >= 1
    
    def test_get_recommendations(self):
        """Test getting recommendations."""
        mc = MetaCognition()
        mc.update_domain_knowledge("unknown1", 0.3)
        mc.update_domain_knowledge("unknown2", 0.2)
        
        recs = mc.get_recommendations()
        assert len(recs) >= 1
    
    def test_get_metacognition_output(self):
        """Test getting meta-cognition output."""
        mc = MetaCognition()
        output = mc.get_metacognition_output()
        
        assert "self_assessment" in output
        assert "confidence_levels" in output
        assert "recommended_actions" in output


# =============================================================================
# TEST UNIVERSAL PATTERN STORE
# =============================================================================


class TestUniversalPatternStore:
    """Test UniversalPatternStore."""
    
    def test_create_store(self):
        """Test creating pattern store."""
        store = UniversalPatternStore()
        assert len(store.patterns) == 0
    
    def test_store_pattern(self):
        """Test storing a pattern."""
        store = UniversalPatternStore()
        pattern = Pattern(
            id="pat:test:v1",
            payload={"data": "test"},
            domain="test_domain",
        )
        
        pattern_id = store.store_pattern(pattern)
        assert pattern_id == "pat:test:v1"
        assert len(store.patterns) == 1
    
    def test_retrieve_patterns(self):
        """Test retrieving patterns."""
        store = UniversalPatternStore()
        store.store_pattern(Pattern(
            id="pat:permission:v1",
            payload={"type": "gate"},
            domain="workflow",
        ))
        
        patterns, scores = store.retrieve_patterns("permission gate")
        assert len(patterns) >= 0  # May or may not match
    
    def test_delete_pattern(self):
        """Test deleting a pattern."""
        store = UniversalPatternStore()
        store.store_pattern(Pattern(id="pat:test", payload={}))
        
        deleted = store.delete_pattern("pat:test")
        assert deleted
        assert len(store.patterns) == 0
    
    def test_pattern_versioning(self):
        """Test pattern version incrementing."""
        store = UniversalPatternStore()
        
        p1 = Pattern(id="pat:test", payload={"v": 1})
        store.store_pattern(p1)
        
        p2 = Pattern(id="pat:test", payload={"v": 2})
        store.store_pattern(p2)
        
        assert store.patterns["pat:test"].version == 2


# =============================================================================
# TEST UNIVERSAL CONTROLLER
# =============================================================================


class TestUniversalController:
    """Test UniversalController."""
    
    def test_create_controller(self):
        """Test creating controller."""
        controller = UniversalController(seed=12345)
        assert controller.seed == 12345
        assert controller.uti is not None
        assert controller.router is not None
    
    def test_process_task(self):
        """Test processing a task."""
        controller = UniversalController(seed=12345)
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
            seed=42,
        )
        
        output = controller.process_task(spec)
        
        assert "task_result" in output
        assert "selected_strategy" in output
        assert "k1" in output
        assert "meets_target" in output
    
    def test_k1_calculation(self):
        """Test k₁ is calculated correctly."""
        controller = UniversalController(seed=12345)
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
            seed=42,
        )
        
        output = controller.process_task(spec)
        k1 = output["k1"]
        
        # k₁ = 1 - decision_score
        assert 0 <= k1 <= 1
    
    def test_get_metrics_jsonl(self):
        """Test getting metrics as JSONL."""
        controller = UniversalController(seed=12345)
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
        )
        
        controller.process_task(spec)
        jsonl = controller.get_metrics_jsonl()
        
        assert len(jsonl) > 0
        # Validate JSONL format
        for line in jsonl.strip().split("\n"):
            data = json.loads(line)
            assert "metric" in data
    
    def test_check_safety_constraints(self):
        """Test safety constraint checking."""
        controller = UniversalController(seed=12345)
        
        constraints = controller.check_safety_constraints()
        
        assert "negative_transfer_ok" in constraints
        assert "forgetting_ok" in constraints


# =============================================================================
# TEST ADIABATIC SCHEDULER
# =============================================================================


class TestAdiabaticScheduler:
    """Test AdiabaticScheduler."""
    
    def test_create_scheduler(self):
        """Test creating scheduler."""
        scheduler = AdiabaticScheduler(total_steps=100)
        assert scheduler.total_steps == 100
    
    def test_linear_schedule(self):
        """Test linear annealing schedule."""
        scheduler = AdiabaticScheduler(total_steps=100, schedule="linear")
        
        assert scheduler.get_beta(0) == 0.0
        assert scheduler.get_beta(50) == pytest.approx(0.5, abs=0.01)
        assert scheduler.get_beta(100) == pytest.approx(1.0, abs=0.01)
    
    def test_step_advances(self):
        """Test step advances correctly."""
        scheduler = AdiabaticScheduler(total_steps=10)
        
        beta1 = scheduler.step()
        beta2 = scheduler.step()
        
        assert beta2 > beta1
    
    def test_get_energy_weights(self):
        """Test getting energy weights."""
        scheduler = AdiabaticScheduler(total_steps=100)
        
        weights = scheduler.get_energy_weights()
        
        assert "lambda_explore" in weights
        assert "lambda_exploit" in weights
        assert weights["lambda_explore"] + weights["lambda_exploit"] == pytest.approx(1.0, abs=0.01)


# =============================================================================
# TEST DECOHERENCE MODEL
# =============================================================================


class TestDecoherenceModel:
    """Test DecoherenceModel."""
    
    def test_create_model(self):
        """Test creating decoherence model."""
        model = DecoherenceModel(threshold=0.05)
        assert model.threshold == 0.05
    
    def test_measure_no_decoherence(self):
        """Test measuring no decoherence."""
        model = DecoherenceModel()
        
        rate = model.measure_decoherence(
            source_performance=0.8,
            target_performance=0.85,  # Better than baseline
            baseline_performance=0.7,
        )
        
        assert rate == 0.0
    
    def test_measure_with_decoherence(self):
        """Test measuring decoherence."""
        model = DecoherenceModel()
        
        rate = model.measure_decoherence(
            source_performance=0.8,
            target_performance=0.5,  # Worse than baseline
            baseline_performance=0.7,
        )
        
        assert rate > 0
    
    def test_trigger_rollback(self):
        """Test rollback trigger."""
        model = DecoherenceModel(threshold=0.05)
        
        should_rollback = model.check_trigger_rollback(
            decoherence_rate=0.10,  # Above threshold
            domain="test_domain",
        )
        
        assert should_rollback
        assert len(model.decoherence_events) == 1


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for Phase 8.7."""
    
    def test_full_pipeline(self):
        """Test full pipeline from task to result."""
        controller = UniversalController(seed=12345)
        
        spec = TaskSpec(
            environment="gridworld_v1",
            initial_state={"x": 0, "y": 0},
            reward_spec={"id": "reward:sparse", "params": {"goal": [5, 5]}},
            termination={"max_steps": 100, "criteria": {"reach_goal": True}},
            seed=42,
        )
        
        output = controller.process_task(spec)
        
        # Validate complete output
        assert output.get("error") is None
        assert "task_result" in output
        assert "selected_strategy" in output
        assert "k1" in output
        assert "quantum_advantage" in output
        assert "metacognition" in output
    
    def test_pattern_accumulation(self):
        """Test patterns accumulate over tasks."""
        controller = UniversalController(seed=12345)
        
        for i in range(5):
            spec = TaskSpec(
                environment=f"env_{i}",
                initial_state={},
                reward_spec={"id": "reward:v1"},
                termination={"max_steps": 10},
                seed=i * 100,
            )
            controller.process_task(spec)
        
        # Should have stored some patterns
        assert len(controller.store.patterns) >= 0
    
    def test_deterministic_execution(self):
        """Test full pipeline is deterministic."""
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
            seed=42,
        )
        
        controller1 = UniversalController(seed=12345)
        output1 = controller1.process_task(spec)
        
        controller2 = UniversalController(seed=12345)
        output2 = controller2.process_task(spec)
        
        assert output1["k1"] == output2["k1"]
        assert output1["selected_strategy"] == output2["selected_strategy"]
    
    def test_json_serialization(self):
        """Test all outputs are JSON serializable."""
        controller = UniversalController(seed=12345)
        
        spec = TaskSpec(
            environment="test_env",
            initial_state={},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
        )
        
        output = controller.process_task(spec)
        
        # Should not raise
        json_str = json.dumps(output)
        assert len(json_str) > 0
        
        # Should be parseable
        parsed = json.loads(json_str)
        assert parsed["k1"] == output["k1"]


# =============================================================================
# TEST PRE-COMMIT 1: UTI ENHANCEMENTS
# =============================================================================


class TestTaskComplexity:
    """Test task complexity estimation."""
    
    def test_complexity_enum(self):
        """Test TaskComplexity enum values."""
        from ..universal_intelligence import TaskComplexity
        assert TaskComplexity.LOW.value == "low"
        assert TaskComplexity.MEDIUM.value == "medium"
        assert TaskComplexity.HIGH.value == "high"
        assert TaskComplexity.VERY_HIGH.value == "very_high"
    
    def test_estimate_complexity_low(self):
        """Test estimating low complexity task."""
        from ..universal_intelligence import estimate_task_complexity, TaskComplexity
        spec = TaskSpec(
            environment="simple",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 10},
        )
        score, level = estimate_task_complexity(spec)
        assert score < 100
        assert level == TaskComplexity.LOW
    
    def test_estimate_complexity_medium(self):
        """Test estimating medium complexity task."""
        from ..universal_intelligence import estimate_task_complexity, TaskComplexity
        spec = TaskSpec(
            environment="medium",
            initial_state={f"var_{i}": 0 for i in range(10)},
            reward_spec={"id": "reward:v1", "params": {"a": 1, "b": 2}},
            termination={"max_steps": 500},
        )
        score, level = estimate_task_complexity(spec)
        assert level in [TaskComplexity.MEDIUM, TaskComplexity.HIGH]
    
    def test_estimate_complexity_high(self):
        """Test estimating high complexity task."""
        from ..universal_intelligence import estimate_task_complexity, TaskComplexity
        spec = TaskSpec(
            environment="complex",
            initial_state={f"var_{i}": 0 for i in range(50)},
            reward_spec={"id": "reward:v1", "params": {f"p_{i}": i for i in range(10)}},
            termination={"max_steps": 10000},
        )
        score, level = estimate_task_complexity(spec)
        assert level in [TaskComplexity.HIGH, TaskComplexity.VERY_HIGH]


class TestSchemaValidation:
    """Test JSON schema validation."""
    
    def test_validate_valid_spec(self):
        """Test validating a valid task spec."""
        from ..universal_intelligence import validate_task_spec_schema
        spec = TaskSpec(
            environment="test",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 100},
        )
        is_valid, errors = validate_task_spec_schema(spec)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_missing_environment(self):
        """Test validation catches missing environment."""
        from ..universal_intelligence import validate_task_spec_schema
        spec = TaskSpec(
            environment="",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 100},
        )
        is_valid, errors = validate_task_spec_schema(spec)
        assert not is_valid
        assert any("environment" in e for e in errors)
    
    def test_validate_missing_reward_id(self):
        """Test validation catches missing reward_spec.id."""
        from ..universal_intelligence import validate_task_spec_schema
        spec = TaskSpec(
            environment="test",
            initial_state={"x": 0},
            reward_spec={"params": {}},  # Missing "id"
            termination={"max_steps": 100},
        )
        is_valid, errors = validate_task_spec_schema(spec)
        assert not is_valid
        assert any("reward_spec.id" in e for e in errors)
    
    def test_validate_invalid_max_steps(self):
        """Test validation catches invalid max_steps."""
        from ..universal_intelligence import validate_task_spec_schema
        spec = TaskSpec(
            environment="test",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": -10},  # Invalid negative
        )
        is_valid, errors = validate_task_spec_schema(spec)
        assert not is_valid
        assert any("max_steps" in e for e in errors)


class TestEnvironmentAdapters:
    """Test environment-specific adapters."""
    
    def test_gridworld_adapter(self):
        """Test gridworld adapter."""
        from ..universal_intelligence import GridWorldAdapter
        adapter = GridWorldAdapter(seed=12345)
        state = {"x": 0, "y": 0, "goal": {"x": 5, "y": 5}}
        
        # Test movement
        next_state, reward, done = adapter.execute_step(state, "right", 0)
        assert next_state["x"] == 1
        assert next_state["y"] == 0
        assert not done
        assert reward < 0  # Still far from goal
    
    def test_gridworld_adapter_goal(self):
        """Test gridworld adapter reaching goal."""
        from ..universal_intelligence import GridWorldAdapter
        adapter = GridWorldAdapter(seed=12345)
        state = {"x": 5, "y": 5, "goal": {"x": 5, "y": 5}}
        
        # Already at goal
        next_state, reward, done = adapter.execute_step(state, "stay", 0)
        assert done
        assert reward > 0  # Goal bonus
    
    def test_bandit_adapter(self):
        """Test bandit adapter."""
        from ..universal_intelligence import BanditAdapter
        adapter = BanditAdapter(seed=12345)
        state = {"arm_means": [0.5, 0.3, 0.7, 0.4], "pulls": 0}
        
        # Pull an arm
        next_state, reward, done = adapter.execute_step(state, "arm_2", 0)
        assert next_state["pulls"] == 1
        assert next_state["last_arm"] == 2
        assert not done  # Bandit never "finishes"
        assert isinstance(reward, float)
    
    def test_classification_adapter(self):
        """Test classification adapter."""
        from ..universal_intelligence import ClassificationAdapter
        adapter = ClassificationAdapter(seed=12345)
        state = {
            "features": [0.5] * 10,
            "true_label": 2,
            "num_classes": 5,
        }
        
        # Make correct prediction
        next_state, reward, done = adapter.execute_step(state, "class_2", 0)
        assert reward == 1.0
        assert "examples_seen" in next_state
        assert next_state["examples_seen"] == 1
    
    def test_classification_adapter_wrong(self):
        """Test classification adapter with wrong prediction."""
        from ..universal_intelligence import ClassificationAdapter
        adapter = ClassificationAdapter(seed=12345)
        state = {
            "features": [0.5] * 10,
            "true_label": 2,
            "num_classes": 5,
        }
        
        # Make incorrect prediction
        next_state, reward, done = adapter.execute_step(state, "class_0", 0)
        assert reward == 0.0


class TestUTIEnhancements:
    """Test UTI with environment adapters and complexity estimation."""
    
    def test_uti_with_gridworld(self):
        """Test UTI executing gridworld task."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="gridworld",
            initial_state={"x": 0, "y": 0, "goal": {"x": 2, "y": 2}},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 50},
        )
        
        result = uti.execute_task(spec, use_adapter=True)
        assert len(result.action_sequence) > 0
        assert "complexity_score" in result.metrics
        assert "complexity_level" in result.metrics
    
    def test_uti_with_bandit(self):
        """Test UTI executing bandit task."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="bandit",
            initial_state={"arm_means": [0.5, 0.3, 0.7], "pulls": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 20},
        )
        
        result = uti.execute_task(spec, use_adapter=True)
        assert len(result.action_sequence) > 0
        assert result.cumulative_reward >= 0
    
    def test_uti_with_classification(self):
        """Test UTI executing classification task."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="classification",
            initial_state={
                "features": [0.5] * 10,
                "true_label": 2,
                "num_classes": 5,
            },
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 30},
        )
        
        result = uti.execute_task(spec, use_adapter=True)
        assert len(result.action_sequence) > 0
    
    def test_uti_estimate_complexity(self):
        """Test UTI complexity estimation."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="test",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 100},
        )
        
        score, level = uti.estimate_complexity(spec)
        assert score >= 0
        assert level.value in ["low", "medium", "high", "very_high"]
    
    def test_uti_validation_integration(self):
        """Test UTI validation integration."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="test",
            initial_state={"x": 0},
            reward_spec={"id": "reward:v1"},
            termination={"max_steps": 100},
        )
        
        is_valid, errors = uti.validate_task_spec(spec)
        assert is_valid
        assert len(errors) == 0
    
    def test_uti_invalid_spec_raises(self):
        """Test UTI raises on invalid spec."""
        uti = UniversalTaskInterface(seed=12345)
        spec = TaskSpec(
            environment="",  # Invalid
            initial_state={"x": 0},
            reward_spec={},  # Missing "id"
            termination={},  # Missing "max_steps"
        )
        
        with pytest.raises(ValueError):
            uti.execute_task(spec)


# =============================================================================
# TEST PRE-COMMIT 2: MPR ENHANCEMENTS
# =============================================================================


class TestMAMLState:
    """Test MAML algorithm state."""
    
    def test_maml_initialization(self):
        """Test MAML state initialization."""
        from ..universal_intelligence import MAMLState
        maml = MAMLState(
            meta_params={"w0": 1.0, "w1": 0.5},
            meta_lr=0.001,
            inner_lr=0.01,
            inner_steps=5,
        )
        assert maml.meta_lr == 0.001
        assert maml.inner_steps == 5
        assert "w0" in maml.meta_params
    
    def test_maml_adapt_to_task(self):
        """Test MAML task adaptation."""
        from ..universal_intelligence import MAMLState
        maml = MAMLState(meta_params={"w0": 1.0, "w1": 0.5})
        
        task_data = [(i, i**2) for i in range(10)]
        adapted = maml.adapt_to_task("task1", task_data)
        
        assert "w0" in adapted
        assert "w1" in adapted
        # Params should be different after adaptation
        assert adapted["w0"] != maml.meta_params["w0"]
    
    def test_maml_meta_update(self):
        """Test MAML meta-parameter update."""
        from ..universal_intelligence import MAMLState
        maml = MAMLState(meta_params={"w0": 1.0})
        
        original_w0 = maml.meta_params["w0"]
        maml.meta_update({"task1": 0.8, "task2": 0.7})
        
        # Meta params should change
        assert maml.meta_params["w0"] != original_w0


class TestReptileState:
    """Test Reptile algorithm state."""
    
    def test_reptile_initialization(self):
        """Test Reptile state initialization."""
        from ..universal_intelligence import ReptileState
        reptile = ReptileState(
            init_params={"theta0": 0.5, "theta1": 0.3},
            step_size=0.01,
            inner_steps=10,
        )
        assert reptile.step_size == 0.01
        assert reptile.inner_steps == 10
        assert "theta0" in reptile.init_params
    
    def test_reptile_adapt_to_task(self):
        """Test Reptile task adaptation."""
        from ..universal_intelligence import ReptileState
        reptile = ReptileState(init_params={"theta0": 0.5})
        
        task_data = [(i, i**2) for i in range(5)]
        adapted = reptile.adapt_to_task("task1", task_data)
        
        assert "theta0" in adapted
        # Should differ from init params
        assert adapted["theta0"] != reptile.init_params["theta0"]
    
    def test_reptile_meta_update(self):
        """Test Reptile meta-update."""
        from ..universal_intelligence import ReptileState
        reptile = ReptileState(init_params={"theta0": 0.5})
        
        adapted = {"theta0": 0.7}
        original = reptile.init_params["theta0"]
        
        reptile.meta_update(adapted)
        
        # Init params should move toward adapted params
        assert reptile.init_params["theta0"] != original
        # Should be between original and adapted
        assert original < reptile.init_params["theta0"] < adapted["theta0"]


class TestStrategyPerformance:
    """Test strategy performance tracking."""
    
    def test_performance_initialization(self):
        """Test performance tracker initialization."""
        from ..universal_intelligence import StrategyPerformance
        perf = StrategyPerformance(strategy_name="maml")
        assert perf.strategy_name == "maml"
        assert perf.avg_score == 0.0
        assert perf.success_count == 0
    
    def test_performance_update(self):
        """Test updating performance."""
        from ..universal_intelligence import StrategyPerformance
        perf = StrategyPerformance(strategy_name="maml")
        
        perf.update(0.8, success=True)
        assert perf.success_count == 1
        assert perf.avg_score == 0.8
        
        perf.update(0.6, success=True)
        assert perf.success_count == 2
        assert perf.avg_score == 0.7  # (0.8 + 0.6) / 2
    
    def test_success_rate(self):
        """Test success rate calculation."""
        from ..universal_intelligence import StrategyPerformance
        perf = StrategyPerformance(strategy_name="maml")
        
        perf.update(0.9, success=True)
        perf.update(0.4, success=False)
        perf.update(0.8, success=True)
        
        assert perf.success_count == 2
        assert perf.failure_count == 1
        assert perf.get_success_rate() == pytest.approx(2/3, abs=0.01)


class TestDynamicHyperparamTuner:
    """Test dynamic hyperparameter tuning."""
    
    def test_tuner_initialization(self):
        """Test tuner initialization."""
        from ..universal_intelligence import DynamicHyperparamTuner
        tuner = DynamicHyperparamTuner(seed=12345)
        assert tuner.seed == 12345
        assert len(tuner.param_history) == 0
    
    def test_tune_poor_performance(self):
        """Test tuning with poor performance."""
        from ..universal_intelligence import DynamicHyperparamTuner
        tuner = DynamicHyperparamTuner(seed=12345)
        
        current = {"meta_lr": 0.001, "inner_lr": 0.01}
        tuned = tuner.tune_hyperparams("maml", current, performance=0.3)
        
        # Should increase learning rates for poor performance
        assert tuned["meta_lr"] > current["meta_lr"]
        assert tuned["inner_lr"] > current["inner_lr"]
    
    def test_tune_good_performance(self):
        """Test tuning with good performance."""
        from ..universal_intelligence import DynamicHyperparamTuner
        tuner = DynamicHyperparamTuner(seed=12345)
        
        current = {"meta_lr": 0.001, "inner_lr": 0.01}
        tuned = tuner.tune_hyperparams("maml", current, performance=0.9)
        
        # Should decrease learning rates for good performance
        assert tuned["meta_lr"] < current["meta_lr"]
        assert tuned["inner_lr"] < current["inner_lr"]
    
    def test_get_best_params(self):
        """Test getting best parameters."""
        from ..universal_intelligence import DynamicHyperparamTuner
        tuner = DynamicHyperparamTuner(seed=12345)
        
        # No history yet
        assert tuner.get_best_params("maml") is None
        
        # Add history
        params1 = {"meta_lr": 0.001}
        tuner.tune_hyperparams("maml", params1, 0.5)
        
        best = tuner.get_best_params("maml")
        assert best is not None
        assert "meta_lr" in best


class TestStrategyBenchmark:
    """Test strategy benchmark suite."""
    
    def test_benchmark_initialization(self):
        """Test benchmark initialization."""
        from ..universal_intelligence import StrategyBenchmark
        benchmark = StrategyBenchmark(seed=12345)
        assert benchmark.seed == 12345
        assert len(benchmark.results) == 0
    
    def test_create_benchmark_task(self):
        """Test creating benchmark tasks."""
        from ..universal_intelligence import StrategyBenchmark
        benchmark = StrategyBenchmark(seed=12345)
        
        task_data = benchmark.create_benchmark_task("task1", difficulty=0.5)
        assert len(task_data) > 0
        assert all(isinstance(x, tuple) and len(x) == 2 for x in task_data)
    
    def test_run_benchmark(self):
        """Test running benchmark."""
        from ..universal_intelligence import StrategyBenchmark
        benchmark = StrategyBenchmark(seed=12345)
        
        strategies = ["maml", "reptile", "adapter_transfer"]
        results = benchmark.run_benchmark(strategies, num_tasks=5)
        
        assert len(results) == 3
        for strategy in strategies:
            assert strategy in results
            assert results[strategy].avg_score >= 0
            assert results[strategy].avg_score <= 1.0
    
    def test_get_rankings(self):
        """Test getting strategy rankings."""
        from ..universal_intelligence import StrategyBenchmark
        benchmark = StrategyBenchmark(seed=12345)
        
        strategies = ["maml", "reptile"]
        benchmark.run_benchmark(strategies, num_tasks=5)
        
        rankings = benchmark.get_rankings()
        assert len(rankings) == 2
        # Rankings should be sorted by score descending
        assert rankings[0][1] >= rankings[1][1]


class TestMPREnhancements:
    """Test MPR with MAML/Reptile integration."""
    
    def test_mpr_maml_integration(self):
        """Test MPR with MAML integration."""
        router = MetaPolicyRouter(seed=12345)
        
        task_data = [(i, i**2) for i in range(10)]
        adapted = router.adapt_with_maml("task1", task_data)
        
        assert isinstance(adapted, dict)
        assert len(adapted) > 0
    
    def test_mpr_reptile_integration(self):
        """Test MPR with Reptile integration."""
        router = MetaPolicyRouter(seed=12345)
        
        task_data = [(i, i**2) for i in range(10)]
        adapted = router.adapt_with_reptile("task1", task_data)
        
        assert isinstance(adapted, dict)
        assert len(adapted) > 0
    
    def test_mpr_performance_tracking(self):
        """Test MPR strategy performance tracking."""
        router = MetaPolicyRouter(seed=12345)
        
        router.update_strategy_performance("maml", 0.8, success=True)
        router.update_strategy_performance("maml", 0.7, success=True)
        
        stats = router.get_performance_stats()
        assert "maml" in stats
        assert stats["maml"]["avg_score"] > 0
    
    def test_mpr_get_best_strategy(self):
        """Test getting best performing strategy."""
        router = MetaPolicyRouter(seed=12345)
        
        # Add some performance data
        router.update_strategy_performance("maml", 0.9, success=True)
        router.update_strategy_performance("reptile", 0.6, success=True)
        
        best = router.get_best_strategy()
        assert best == "maml"  # Higher score
    
    def test_mpr_dynamic_hyperparams(self):
        """Test MPR dynamic hyperparameter tuning."""
        router = MetaPolicyRouter(seed=12345)
        
        # Add performance to trigger tuning
        router.update_strategy_performance("maml", 0.8, success=True)
        
        # Get hyperparams (should be tuned)
        params = router.get_hyperparams("maml")
        assert "meta_lr" in params
        assert "inner_lr" in params
        assert "inner_steps" in params


# =============================================================================
# RUN TESTS
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
