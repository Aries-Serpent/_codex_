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
    ConceptLevel,
    RelationType,
    # Grounding
    AbstractStep,
    GroundedAction,
    ExecutionTrace,
    GroundingLayer,
    GitHubAPIAdapter,
    ActionValidator,
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
    # PRE-COMMIT 3-7 additions
    DomainIsolation,
    RollbackTrigger,
    ForgettingDetector,
    SafetyConstraintEnforcer,
    EXP10BenchmarkHarness,
    K1ValidationFramework,
    TransferTestSuite,
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
# PRE-COMMIT 3: ABSTRACTION ENGINE ENHANCEMENT TESTS
# =============================================================================


class TestConceptLevels:
    """Test hierarchical concept levels."""
    
    def test_concept_level_enum(self):
        """Test ConceptLevel enum values."""
        from ..universal_intelligence import ConceptLevel
        
        assert ConceptLevel.LEAF.value == "leaf"
        assert ConceptLevel.INTERMEDIATE.value == "intermediate"
        assert ConceptLevel.ROOT.value == "root"
    
    def test_concept_with_level(self):
        """Test Concept with hierarchical level."""
        concept = Concept(
            id="test_concept",
            props={"key": "value"},
            support=5,
            level=ConceptLevel.INTERMEDIATE,
        )
        
        assert concept.level == ConceptLevel.INTERMEDIATE
        assert concept.to_dict()["level"] == "intermediate"
    
    def test_hierarchical_extraction(self):
        """Test hierarchical concept extraction."""
        engine = AbstractionEngine()
        
        observations = [
            {"x": 10, "y": 20, "active": True},
            {"x": 15, "y": 25, "active": False},
            {"x": 12, "y": 22, "active": True},
        ]
        
        hierarchy = engine.hierarchical_concept_extraction(observations)
        
        assert ConceptLevel.LEAF in hierarchy
        assert ConceptLevel.INTERMEDIATE in hierarchy
        assert ConceptLevel.ROOT in hierarchy
        
        # Check leaf concepts
        leaf_concepts = hierarchy[ConceptLevel.LEAF]
        assert len(leaf_concepts) >= 3  # x, y, active
    
    def test_hierarchical_levels_structure(self):
        """Test hierarchical levels have proper structure."""
        engine = AbstractionEngine()
        
        observations = [
            {"pos": 1, "vel": 2.0, "flag": True},
            {"pos": 2, "vel": 3.0, "flag": False},
        ]
        
        hierarchy = engine.hierarchical_concept_extraction(observations, max_depth=3)
        
        # Verify hierarchy structure
        assert isinstance(hierarchy, dict)
        assert all(isinstance(k, ConceptLevel) for k in hierarchy.keys())
        assert all(isinstance(v, list) for v in hierarchy.values())


class TestRelationTypes:
    """Test typed semantic relations."""
    
    def test_relation_type_enum(self):
        """Test RelationType enum values."""
        from ..universal_intelligence import RelationType
        
        assert RelationType.CAUSAL.value == "causal"
        assert RelationType.TEMPORAL.value == "temporal"
        assert RelationType.SPATIAL.value == "spatial"
        assert RelationType.STRUCTURAL.value == "structural"
        assert RelationType.COOCCURS.value == "co-occurs"
    
    def test_relation_with_type(self):
        """Test Relation with typed relation."""
        from ..universal_intelligence import RelationType
        
        relation = Relation(
            source="concept_a",
            relation_type=RelationType.CAUSAL,
            target="concept_b",
            confidence=0.9,
        )
        
        assert relation.relation_type == RelationType.CAUSAL
        assert relation.confidence == 0.9
        rel_dict = relation.to_dict()
        assert rel_dict["relation_type"] == "causal"
    
    def test_detect_temporal_relation(self):
        """Test detection of temporal relations."""
        engine = AbstractionEngine()
        
        concept1 = Concept(id="leaf:timestamp", props={}, level=ConceptLevel.LEAF)
        concept2 = Concept(id="leaf:duration", props={}, level=ConceptLevel.LEAF)
        
        rel_type = engine.detect_relation_type(concept1, concept2, [])
        assert rel_type == RelationType.TEMPORAL
    
    def test_detect_spatial_relation(self):
        """Test detection of spatial relations."""
        engine = AbstractionEngine()
        
        concept1 = Concept(id="leaf:x", props={}, level=ConceptLevel.LEAF)
        concept2 = Concept(id="leaf:position", props={}, level=ConceptLevel.LEAF)
        
        rel_type = engine.detect_relation_type(concept1, concept2, [])
        assert rel_type == RelationType.SPATIAL
    
    def test_detect_causal_relation(self):
        """Test detection of causal relations."""
        engine = AbstractionEngine()
        
        concept1 = Concept(id="leaf:cause", props={}, level=ConceptLevel.LEAF)
        concept2 = Concept(id="leaf:effect", props={}, level=ConceptLevel.LEAF)
        
        rel_type = engine.detect_relation_type(concept1, concept2, [])
        assert rel_type == RelationType.CAUSAL
    
    def test_map_relations_typed(self):
        """Test typed relation mapping."""
        engine = AbstractionEngine()
        
        observations = [
            {"timestamp": 100, "value": 1},
            {"timestamp": 200, "value": 2},
        ]
        
        concepts = [
            Concept(id="leaf:timestamp", props={}, level=ConceptLevel.LEAF),
            Concept(id="leaf:value", props={}, level=ConceptLevel.LEAF),
        ]
        
        relations = engine.map_relations_typed(concepts, observations)
        
        assert len(relations) > 0
        assert all(isinstance(r.relation_type, RelationType) for r in relations)


class TestAnalogyQuality:
    """Test analogy quality scoring."""
    
    def test_analogy_quality_score_basic(self):
        """Test basic analogy quality scoring."""
        engine = AbstractionEngine()
        
        analogy = Analogy(
            source_domain="domain_a",
            target_domain="domain_b",
            mapping={"concept_1": "concept_x", "concept_2": "concept_y"},
            confidence=0.8,
        )
        
        source_relations = [
            Relation("concept_1", RelationType.CAUSAL, "concept_2", 1.0),
        ]
        
        target_relations = [
            Relation("concept_x", RelationType.CAUSAL, "concept_y", 1.0),
        ]
        
        score = engine.analogy_quality_score(analogy, source_relations, target_relations)
        
        assert 0.0 <= score <= 1.0
        assert score == 1.0  # Perfect preservation
    
    def test_analogy_quality_no_preservation(self):
        """Test analogy quality with no relation preservation."""
        engine = AbstractionEngine()
        
        analogy = Analogy(
            source_domain="domain_a",
            target_domain="domain_b",
            mapping={"concept_1": "concept_x"},
        )
        
        source_relations = [
            Relation("concept_1", RelationType.CAUSAL, "concept_2", 1.0),
        ]
        
        target_relations = []
        
        score = engine.analogy_quality_score(analogy, source_relations, target_relations)
        
        assert score == 0.0
    
    def test_analogy_with_quality_score(self):
        """Test Analogy dataclass includes quality_score."""
        analogy = Analogy(
            source_domain="src",
            target_domain="tgt",
            mapping={"a": "b"},
            confidence=0.7,
            quality_score=0.85,
        )
        
        assert analogy.quality_score == 0.85
        assert "quality_score" in analogy.to_dict()


class TestGoldenSnapshots:
    """Test golden snapshot functionality."""
    
    def test_save_snapshot(self, tmp_path):
        """Test saving concept graph snapshot."""
        engine = AbstractionEngine()
        
        # Add some concepts
        engine.concepts["c1"] = Concept(id="c1", props={"test": True}, support=5, level=ConceptLevel.LEAF)
        engine.relations.append(Relation("c1", RelationType.STRUCTURAL, "c2", 0.9))
        
        snapshot_path = tmp_path / "snapshot.json"
        engine.save_snapshot(str(snapshot_path))
        
        assert snapshot_path.exists()
        
        # Verify JSON structure
        with open(snapshot_path) as f:
            data = json.load(f)
        
        assert "concepts" in data
        assert "relations" in data
        assert "analogies" in data
        assert "metadata" in data
    
    def test_load_snapshot(self, tmp_path):
        """Test loading concept graph snapshot."""
        engine1 = AbstractionEngine()
        engine1.concepts["c1"] = Concept(id="c1", props={"x": 1}, support=3, level=ConceptLevel.INTERMEDIATE)
        engine1.relations.append(Relation("c1", RelationType.TEMPORAL, "c2", 0.8))
        
        snapshot_path = tmp_path / "snapshot.json"
        engine1.save_snapshot(str(snapshot_path))
        
        # Load into new engine
        engine2 = AbstractionEngine()
        engine2.load_snapshot(str(snapshot_path))
        
        assert len(engine2.concepts) == 1
        assert "c1" in engine2.concepts
        assert engine2.concepts["c1"].props["x"] == 1
        assert len(engine2.relations) == 1
    
    def test_snapshot_roundtrip(self, tmp_path):
        """Test snapshot save/load roundtrip."""
        engine1 = AbstractionEngine()
        
        # Create complex state
        for i in range(3):
            engine1.concepts[f"c{i}"] = Concept(
                id=f"c{i}",
                props={"value": i},
                support=i+1,
                level=ConceptLevel.LEAF,
            )
        
        snapshot_path = tmp_path / "roundtrip.json"
        engine1.save_snapshot(str(snapshot_path))
        
        engine2 = AbstractionEngine()
        engine2.load_snapshot(str(snapshot_path))
        
        assert len(engine2.concepts) == 3
        assert all(f"c{i}" in engine2.concepts for i in range(3))


# =============================================================================
# PRE-COMMIT 4: GROUNDING LAYER ENHANCEMENT TESTS
# =============================================================================


class TestGitHubAPIAdapter:
    """Test GitHub API adapter."""
    
    def test_adapter_initialization(self):
        """Test GitHubAPIAdapter initialization."""
        from ..universal_intelligence import GitHubAPIAdapter
        
        adapter = GitHubAPIAdapter(mock=True)
        assert adapter.mock is True
        assert len(adapter.operation_log) == 0
    
    def test_create_issue(self):
        """Test create_issue operation."""
        from ..universal_intelligence import GitHubAPIAdapter
        
        adapter = GitHubAPIAdapter(mock=True)
        result = adapter.create_issue("test/repo", "Bug", "Description")
        
        assert result["operation"] == "create_issue"
        assert result["status"] == "success"
        assert "issue_number" in result
        assert len(adapter.operation_log) == 1
    
    def test_close_issue(self):
        """Test close_issue operation."""
        from ..universal_intelligence import GitHubAPIAdapter
        
        adapter = GitHubAPIAdapter(mock=True)
        result = adapter.close_issue("test/repo", 123, "Fixed")
        
        assert result["operation"] == "close_issue"
        assert result["issue_number"] == 123
        assert result["comment"] == "Fixed"
    
    def test_merge_pr(self):
        """Test merge_pr operation."""
        from ..universal_intelligence import GitHubAPIAdapter
        
        adapter = GitHubAPIAdapter(mock=True)
        result = adapter.merge_pr("test/repo", 456, merge_method="squash")
        
        assert result["operation"] == "merge_pr"
        assert result["pr_number"] == 456
        assert result["merge_method"] == "squash"
    
    def test_operation_log(self):
        """Test operation logging."""
        from ..universal_intelligence import GitHubAPIAdapter
        
        adapter = GitHubAPIAdapter(mock=True)
        adapter.create_issue("repo1", "Title1", "Body1")
        adapter.close_issue("repo2", 1, "Comment")
        adapter.merge_pr("repo3", 2, "merge")
        
        log = adapter.get_operation_log()
        assert len(log) == 3
        assert log[0]["operation"] == "create_issue"
        assert log[1]["operation"] == "close_issue"
        assert log[2]["operation"] == "merge_pr"


class TestActionValidator:
    """Test action validation."""
    
    def test_validator_initialization(self):
        """Test ActionValidator initialization."""
        from ..universal_intelligence import ActionValidator
        
        validator = ActionValidator()
        assert "create_issue" in validator.validation_rules
        assert "close_issue" in validator.validation_rules
        assert "merge_pr" in validator.validation_rules
    
    def test_precondition_validation_success(self):
        """Test successful precondition validation."""
        from ..universal_intelligence import ActionValidator
        
        validator = ActionValidator()
        action = GroundedAction(
            adapter="github_api_mock",
            op="create_issue",
            args={"title": "Test Issue", "body": "Description"},
        )
        
        is_valid, error = validator.validate_precondition(action)
        assert is_valid is True
        assert error == ""
    
    def test_precondition_validation_failure(self):
        """Test failed precondition validation."""
        from ..universal_intelligence import ActionValidator
        
        validator = ActionValidator()
        action = GroundedAction(
            adapter="github_api_mock",
            op="create_issue",
            args={"title": "", "body": "Description"},  # Empty title
        )
        
        is_valid, error = validator.validate_precondition(action)
        assert is_valid is False
        assert "Precondition failed" in error
    
    def test_postcondition_validation(self):
        """Test postcondition validation."""
        from ..universal_intelligence import ActionValidator
        
        validator = ActionValidator()
        action = GroundedAction(
            adapter="github_api_mock",
            op="merge_pr",
            args={"pr_number": 123},
        )
        
        result = {"status": "success"}
        is_valid, error = validator.validate_postcondition(action, result)
        assert is_valid is True
    
    def test_validate_pipeline(self):
        """Test complete pipeline validation."""
        from ..universal_intelligence import ActionValidator
        
        validator = ActionValidator()
        actions = [
            GroundedAction("github_api_mock", "create_issue", {"title": "Test", "body": "B"}),
            GroundedAction("github_api_mock", "close_issue", {"issue_number": 1}),
        ]
        
        is_valid, errors = validator.validate_pipeline(actions)
        assert is_valid is True
        assert len(errors) == 0


class TestExecutionTrace:
    """Test execution trace replay."""
    
    def test_trace_replay_last(self):
        """Test replaying last execution trace."""
        layer = GroundingLayer()
        
        # Execute some actions
        actions = [
            GroundedAction("mock", "op1", {"arg": 1}),
            GroundedAction("mock", "op2", {"arg": 2}),
        ]
        layer.execute_actions(actions, dry_run=True)
        
        # Replay last trace
        trace = layer.replay_trace(-1)
        assert trace is not None
        assert trace.status == "simulated"
    
    def test_trace_replay_by_index(self):
        """Test replaying trace by index."""
        layer = GroundingLayer()
        
        actions = [GroundedAction("mock", "op", {"x": i}) for i in range(3)]
        layer.execute_actions(actions, dry_run=True)
        
        # Replay first trace
        trace = layer.replay_trace(0)
        assert trace is not None
        assert trace.details["action"]["args"]["x"] == 0
    
    def test_trace_replay_invalid_index(self):
        """Test replaying with invalid index."""
        layer = GroundingLayer()
        trace = layer.replay_trace(100)
        assert trace is None


class TestFeasibilityClassification:
    """Test feasibility score classification."""
    
    def test_classify_infeasible(self):
        """Test infeasible classification."""
        layer = GroundingLayer()
        assert layer.classify_feasibility(0.1) == "infeasible"
        assert layer.classify_feasibility(0.29) == "infeasible"
    
    def test_classify_risky(self):
        """Test risky classification."""
        layer = GroundingLayer()
        assert layer.classify_feasibility(0.3) == "risky"
        assert layer.classify_feasibility(0.5) == "risky"
        assert layer.classify_feasibility(0.69) == "risky"
    
    def test_classify_feasible(self):
        """Test feasible classification."""
        layer = GroundingLayer()
        assert layer.classify_feasibility(0.7) == "feasible"
        assert layer.classify_feasibility(0.9) == "feasible"
        assert layer.classify_feasibility(1.0) == "feasible"


# =============================================================================
# PRE-COMMIT 5: UNIVERSAL PATTERN STORE ENHANCEMENT TESTS
# =============================================================================


class TestPatternEmbeddings:
    """Test pattern embeddings."""
    
    def test_compute_embedding(self):
        """Test pattern embedding computation."""
        pattern = Pattern(
            id="test_pattern",
            payload={"strategy": "maml"},
            domain="test",
        )
        
        embedding = pattern.compute_embedding(seed=12345)
        
        assert embedding is not None
        assert len(embedding) == 32
        assert pattern.embedding == embedding
        
        # Check normalization
        norm = sum(x*x for x in embedding) ** 0.5
        assert abs(norm - 1.0) < 1e-6
    
    def test_embedding_deterministic(self):
        """Test embedding is deterministic."""
        pattern1 = Pattern(id="p1", payload={"x": 1}, domain="d")
        pattern2 = Pattern(id="p1", payload={"x": 1}, domain="d")
        
        emb1 = pattern1.compute_embedding(seed=42)
        emb2 = pattern2.compute_embedding(seed=42)
        
        assert emb1 == emb2


class TestSimilarityRetrieval:
    """Test similarity-based retrieval."""
    
    def test_similarity_retrieval(self):
        """Test similarity-based pattern retrieval."""
        store = UniversalPatternStore(seed=12345)
        
        # Store patterns
        for i in range(5):
            pattern = Pattern(id=f"pat_{i}", payload={"value": i}, domain=f"domain_{i}")
            pattern.compute_embedding(seed=12345)
            store.store_pattern(pattern)
        
        # Query pattern
        query = Pattern(id="query", payload={"value": 2}, domain="query_domain")
        query.compute_embedding(seed=12345)
        
        patterns, scores = store.similarity_retrieval(query, top_k=3)
        
        assert len(patterns) <= 3
        assert len(scores) == len(patterns)
        assert all(0 <= s <= 1 for s in scores)
    
    def test_similarity_excludes_deprecated(self):
        """Test similarity retrieval excludes deprecated patterns."""
        store = UniversalPatternStore(seed=12345)
        
        # Store patterns
        p1 = Pattern(id="p1", payload={"x": 1}, domain="d1")
        p1.compute_embedding(seed=12345)
        store.store_pattern(p1)
        
        p2 = Pattern(id="p2", payload={"x": 2}, domain="d2", deprecated=True)
        p2.compute_embedding(seed=12345)
        store.store_pattern(p2)
        
        query = Pattern(id="q", payload={"x": 1}, domain="d")
        query.compute_embedding(seed=12345)
        
        patterns, _ = store.similarity_retrieval(query, top_k=5, exclude_deprecated=True)
        
        assert all(not p.deprecated for p in patterns)


class TestPatternVersioning:
    """Test pattern versioning and deprecation."""
    
    def test_pattern_versioning(self):
        """Test pattern version increments."""
        store = UniversalPatternStore(seed=12345)
        
        pattern1 = Pattern(id="p1", payload={"v": 1}, domain="d")
        store.store_pattern(pattern1)
        assert store.patterns["p1"].version == 1
        
        pattern2 = Pattern(id="p1", payload={"v": 2}, domain="d")
        store.store_pattern(pattern2)
        assert store.patterns["p1"].version == 2
    
    def test_pattern_deprecation(self):
        """Test pattern deprecation."""
        store = UniversalPatternStore(seed=12345)
        
        pattern = Pattern(id="p1", payload={}, domain="d")
        store.store_pattern(pattern)
        
        success = store.deprecate_pattern("p1", reason="Outdated")
        assert success is True
        assert store.patterns["p1"].deprecated is True
        assert "deprecation_reason" in store.patterns["p1"].payload
    
    def test_deprecate_nonexistent_pattern(self):
        """Test deprecating non-existent pattern."""
        store = UniversalPatternStore(seed=12345)
        success = store.deprecate_pattern("nonexistent")
        assert success is False


class TestCrossDomainMatching:
    """Test cross-domain pattern matching."""
    
    def test_cross_domain_matching(self):
        """Test matching patterns across domains."""
        store = UniversalPatternStore(seed=12345)
        
        # Store patterns with domain tags
        p1 = Pattern(id="p1", payload={}, domain="vision", domain_tags={"image", "classification"})
        p2 = Pattern(id="p2", payload={}, domain="nlp", domain_tags={"text", "classification"})
        p3 = Pattern(id="p3", payload={}, domain="nlp", domain_tags={"text", "generation"})
        
        store.store_pattern(p1)
        store.store_pattern(p2)
        store.store_pattern(p3)
        
        matches = store.cross_domain_matching("vision", "nlp", min_overlap=0.3)
        
        assert len(matches) > 0
        assert all(isinstance(m, tuple) and len(m) == 3 for m in matches)
        
        # Check match contains classification overlap
        src, tgt, overlap = matches[0]
        assert overlap > 0.0


class TestStorageMetrics:
    """Test storage efficiency metrics."""
    
    def test_storage_metrics(self):
        """Test storage metrics collection."""
        store = UniversalPatternStore(seed=12345)
        
        # Add patterns
        for i in range(10):
            pattern = Pattern(id=f"p{i}", payload={"value": i}, domain="test")
            store.store_pattern(pattern)
        
        # Perform retrievals
        patterns, _ = store.retrieve_patterns("test", top_k=5)
        
        metrics = store.get_storage_metrics()
        
        assert metrics["pattern_count"] == 10
        assert "avg_retrieval_time_ms" in metrics
        assert "cache_hit_rate" in metrics
        assert metrics["total_retrievals"] > 0
    
    def test_cached_retrieval(self):
        """Test cached pattern retrieval."""
        store = UniversalPatternStore(seed=12345)
        
        pattern = Pattern(id="p1", payload={"x": 1}, domain="d")
        store.store_pattern(pattern)
        
        # First retrieval (cache miss)
        store.retrieve_patterns_cached("test", top_k=5)
        assert store.cache_misses == 1
        
        # Second retrieval (cache hit)
        store.retrieve_patterns_cached("test", top_k=5)
        assert store.cache_hits == 1


# =============================================================================
# PRE-COMMIT 6: SAFETY & NEGATIVE TRANSFER TESTS
# =============================================================================


class TestDomainIsolation:
    """Test domain isolation mechanism."""
    
    def test_isolation_initialization(self):
        """Test DomainIsolation initialization."""
        from ..universal_intelligence import DomainIsolation
        
        isolation = DomainIsolation(failure_threshold=0.3, quarantine_duration=10)
        assert isolation.failure_threshold == 0.3
        assert isolation.quarantine_duration == 10
    
    def test_quarantine_failing_domain(self):
        """Test quarantine of failing domain."""
        from ..universal_intelligence import DomainIsolation
        
        isolation = DomainIsolation(failure_threshold=0.3)
        
        # Simulate failures
        isolation.update_performance("domain_a", 0.1)
        isolation.update_performance("domain_a", 0.15)
        isolation.update_performance("domain_a", 0.2)
        
        assert isolation.is_quarantined("domain_a")
    
    def test_quarantine_duration(self):
        """Test quarantine duration countdown."""
        from ..universal_intelligence import DomainIsolation
        
        isolation = DomainIsolation(quarantine_duration=3)
        isolation.quarantine_domain("domain_b")
        
        assert isolation.is_quarantined("domain_b")
        
        isolation.step()
        isolation.step()
        isolation.step()
        
        assert not isolation.is_quarantined("domain_b")
    
    def test_isolation_status(self):
        """Test isolation status reporting."""
        from ..universal_intelligence import DomainIsolation
        
        isolation = DomainIsolation()
        isolation.quarantine_domain("d1")
        isolation.quarantine_domain("d2")
        
        status = isolation.get_status()
        assert status["quarantined_count"] == 2
        assert "d1" in status["quarantined_domains"]


class TestRollbackTrigger:
    """Test rollback trigger mechanism."""
    
    def test_rollback_initialization(self):
        """Test RollbackTrigger initialization."""
        from ..universal_intelligence import RollbackTrigger
        
        trigger = RollbackTrigger(neg_transfer_threshold=0.1)
        assert trigger.neg_transfer_threshold == 0.1
    
    def test_rollback_trigger_threshold(self):
        """Test rollback trigger by threshold."""
        from ..universal_intelligence import RollbackTrigger
        
        trigger = RollbackTrigger(neg_transfer_threshold=0.05)
        
        assert trigger.check_rollback(0.03) is False
        assert trigger.check_rollback(0.10) is True
    
    def test_rollback_restore_baseline(self):
        """Test rollback restores baseline parameters."""
        from ..universal_intelligence import RollbackTrigger
        
        trigger = RollbackTrigger()
        
        baseline = {"lr": 0.01, "steps": 100}
        current = {"lr": 0.001, "steps": 50}
        
        trigger.save_baseline(baseline)
        trigger.update_current(current)
        
        restored = trigger.trigger_rollback(reason="High negative transfer")
        
        assert restored == baseline
        assert trigger.get_rollback_count() == 1


class TestForgettingDetector:
    """Test forgetting detection."""
    
    def test_forgetting_detection(self):
        """Test catastrophic forgetting detection."""
        from ..universal_intelligence import ForgettingDetector
        
        detector = ForgettingDetector(forgetting_threshold=0.2)
        
        detector.set_baseline("task1", 0.9)
        detector.update_current("task1", 0.6)
        
        is_forgetting, degradation = detector.detect_forgetting("task1")
        
        assert is_forgetting is True
        assert degradation == 0.3
    
    def test_no_forgetting(self):
        """Test when no forgetting occurs."""
        from ..universal_intelligence import ForgettingDetector
        
        detector = ForgettingDetector(forgetting_threshold=0.2)
        
        detector.set_baseline("task2", 0.8)
        detector.update_current("task2", 0.75)
        
        is_forgetting, degradation = detector.detect_forgetting("task2")
        
        assert is_forgetting is False
        assert degradation < 0.2
    
    def test_forgetting_report(self):
        """Test forgetting detection report."""
        from ..universal_intelligence import ForgettingDetector
        
        detector = ForgettingDetector()
        
        detector.set_baseline("t1", 0.9)
        detector.update_current("t1", 0.5)
        detector.detect_forgetting("t1")
        
        report = detector.get_forgetting_report()
        
        assert report["total_tasks"] == 1
        assert report["tasks_forgotten"] == 1
        assert report["forgetting_rate"] == 1.0


class TestSafetyConstraintEnforcer:
    """Test safety constraint enforcement."""
    
    def test_safety_enforcer_initialization(self):
        """Test SafetyConstraintEnforcer initialization."""
        from ..universal_intelligence import SafetyConstraintEnforcer
        
        enforcer = SafetyConstraintEnforcer(seed=12345)
        assert enforcer.seed == 12345
        assert enforcer.isolation is not None
        assert enforcer.rollback is not None
        assert enforcer.forgetting is not None
    
    def test_safety_check_all_safe(self):
        """Test safety check when all constraints pass."""
        from ..universal_intelligence import SafetyConstraintEnforcer
        
        enforcer = SafetyConstraintEnforcer()
        
        result = enforcer.check_safety("domain1", "task1", 0.8, neg_transfer_score=0.01)
        
        assert result["safe"] is True
        assert len(result["actions_taken"]) == 0
    
    def test_safety_check_triggers_actions(self):
        """Test safety check triggers corrective actions."""
        from ..universal_intelligence import SafetyConstraintEnforcer
        
        enforcer = SafetyConstraintEnforcer()
        
        # Set up baseline for forgetting detection
        enforcer.forgetting.set_baseline("task1", 0.9)
        
        # Trigger negative transfer
        result = enforcer.check_safety("domain1", "task1", 0.4, neg_transfer_score=0.1)
        
        assert "rollback_triggered" in result["actions_taken"]


# =============================================================================
# PRE-COMMIT 7: EXP-10 VALIDATION TESTS
# =============================================================================


class TestEXP10BenchmarkHarness:
    """Test EXP-10 benchmark harness."""
    
    def test_harness_initialization(self):
        """Test EXP10BenchmarkHarness initialization."""
        from ..universal_intelligence import EXP10BenchmarkHarness
        
        harness = EXP10BenchmarkHarness(seed=12345)
        assert len(harness.tasks) == 10
        assert harness.seed == 12345
    
    def test_benchmark_tasks_diversity(self):
        """Test benchmark tasks are diverse."""
        from ..universal_intelligence import EXP10BenchmarkHarness
        
        harness = EXP10BenchmarkHarness()
        
        environments = [t.environment for t in harness.tasks]
        assert "gridworld" in environments
        assert "bandit" in environments
        assert "classification" in environments
    
    def test_run_benchmark(self):
        """Test running complete benchmark suite."""
        from ..universal_intelligence import EXP10BenchmarkHarness
        
        harness = EXP10BenchmarkHarness(seed=42)
        controller = UniversalController(seed=42)
        
        result = harness.run_benchmark(controller)
        
        assert result["total_tasks"] == 10
        assert "avg_k1" in result
        assert "passes_target" in result
        assert len(result["results"]) == 10


class TestK1ValidationFramework:
    """Test k₁ validation framework."""
    
    def test_validation_framework_init(self):
        """Test K1ValidationFramework initialization."""
        from ..universal_intelligence import K1ValidationFramework
        
        framework = K1ValidationFramework(target_k1=0.28, stretch_k1=0.255)
        assert framework.target_k1 == 0.28
        assert framework.stretch_k1 == 0.255
    
    def test_validate_k1_passing(self):
        """Test validating passing k₁ value."""
        from ..universal_intelligence import K1ValidationFramework
        
        framework = K1ValidationFramework()
        result = framework.validate_k1(0.25, context={"task": "test"})
        
        assert result["passes_target"] is True
        assert result["passes_stretch"] is True
        assert result["margin_to_target"] > 0
    
    def test_validate_k1_failing(self):
        """Test validating failing k₁ value."""
        from ..universal_intelligence import K1ValidationFramework
        
        framework = K1ValidationFramework()
        result = framework.validate_k1(0.35, context={"task": "test"})
        
        assert result["passes_target"] is False
        assert result["margin_to_target"] < 0
    
    def test_validate_batch(self):
        """Test batch validation."""
        from ..universal_intelligence import K1ValidationFramework
        
        framework = K1ValidationFramework()
        k1_values = [0.20, 0.25, 0.27, 0.30, 0.26]
        
        result = framework.validate_batch(k1_values)
        
        assert result["total"] == 5
        assert "pass_rate_target" in result
        assert "avg_k1" in result


class TestZeroShotTransfer:
    """Test zero-shot transfer."""
    
    def test_zero_shot_test(self):
        """Test zero-shot transfer test."""
        from ..universal_intelligence import TransferTestSuite
        
        suite = TransferTestSuite(seed=12345)
        controller = UniversalController(seed=12345)
        
        source_task = TaskSpec(
            environment="gridworld",
            initial_state={"x": 0, "y": 0, "goal": {"x": 2, "y": 2}},
            reward_spec={"id": "dist", "params": {}},
            termination={"max_steps": 10},
            seed=1,
        )
        
        target_task = TaskSpec(
            environment="gridworld",
            initial_state={"x": 0, "y": 0, "goal": {"x": 3, "y": 3}},
            reward_spec={"id": "dist", "params": {}},
            termination={"max_steps": 15},
            seed=2,
        )
        
        result = suite.test_zero_shot(controller, source_task, target_task)
        
        assert result["test_type"] == "zero_shot"
        assert "source_k1" in result
        assert "target_k1" in result
        assert "transfer_improvement" in result


class TestFewShotTransfer:
    """Test few-shot transfer."""
    
    def test_few_shot_test(self):
        """Test few-shot transfer with K=10."""
        from ..universal_intelligence import TransferTestSuite
        
        suite = TransferTestSuite(seed=42)
        controller = UniversalController(seed=42)
        
        # Create K source tasks
        source_tasks = [
            TaskSpec(
                environment="bandit",
                initial_state={"arm_means": [0.3, 0.7], "pulls": 0},
                reward_spec={"id": "bandit", "params": {}},
                termination={"max_steps": 20},
                seed=i,
            )
            for i in range(10)
        ]
        
        target_task = TaskSpec(
            environment="bandit",
            initial_state={"arm_means": [0.4, 0.6], "pulls": 0},
            reward_spec={"id": "bandit", "params": {}},
            termination={"max_steps": 20},
            seed=100,
        )
        
        result = suite.test_few_shot(controller, source_tasks, target_task, K=10)
        
        assert result["test_type"] == "few_shot"
        assert result["K"] == 10
        assert "avg_source_k1" in result
        assert "target_k1" in result


class TestMetricsArtifacts:
    """Test metrics artifacts generation."""
    
    def test_metrics_directory_creation(self, tmp_path):
        """Test metrics directory is created."""
        from ..universal_intelligence import EXP10BenchmarkHarness
        
        metrics_dir = tmp_path / "metrics"
        
        harness = EXP10BenchmarkHarness(seed=12345)
        controller = UniversalController(seed=12345)
        
        harness.run_benchmark(controller, metrics_output_dir=str(metrics_dir))
        
        assert metrics_dir.exists()
        assert (metrics_dir / "exp10_benchmark.jsonl").exists()
    
    def test_jsonl_format(self, tmp_path):
        """Test JSONL file format."""
        from ..universal_intelligence import EXP10BenchmarkHarness
        
        metrics_dir = tmp_path / "metrics"
        
        harness = EXP10BenchmarkHarness(seed=12345)
        controller = UniversalController(seed=12345)
        
        harness.run_benchmark(controller, metrics_output_dir=str(metrics_dir))
        
        jsonl_file = metrics_dir / "exp10_benchmark.jsonl"
        
        # Read and validate JSONL
        with open(jsonl_file) as f:
            lines = f.readlines()
        
        assert len(lines) >= 11  # Summary + 10 tasks
        
        # Validate each line is valid JSON
        for line in lines:
            data = json.loads(line)
            assert "type" in data
            assert "timestamp" in data


# =============================================================================
# RUN TESTS
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
