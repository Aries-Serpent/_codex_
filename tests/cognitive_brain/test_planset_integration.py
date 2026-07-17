"""Integration Tests for Planset 008 → Downstream Plansets (009, 010, 011).

Validates that Cognitive Reasoning Engine output format is compatible with
and suitable for downstream planset processing.
"""

import json

import pytest

from src.codex.cognitive_brain.integration_adapters import (
    PlansetIntegrationAdapter,
)
from src.codex.cognitive_brain.reasoning_engine import (
    ReasoningEngine,
)


class TestPlanset009Integration:
    """Test integration with Planset 009: Multi-Model Ensemble."""
    
    @pytest.fixture
    def engine(self):
        """Create reasoning engine."""
        return ReasoningEngine()
    
    @pytest.fixture
    def adapter(self):
        """Create integration adapter."""
        return PlansetIntegrationAdapter()
    
    def test_adapt_decision_for_ensemble(self, engine, adapter):
        """Test adaptation of reasoning decision for ensemble model."""
        # Make a decision
        decision = engine.make_decision(
            goal="optimize_performance",
            constraints=["latency < 500ms"],
            decision_history=[],
            current_state={"cpu": 45.0},
            category="performance",
        )
        
        # Adapt for Planset 009
        ensemble_input = adapter.adapt_for_planset_009(decision, "performance")
        
        assert ensemble_input.reasoning_decision_id == decision.id
        assert ensemble_input.confidence_score == decision.confidence
        assert ensemble_input.confidence_level == decision.confidence_level.value
        assert ensemble_input.decision_option == decision.option
        assert ensemble_input.strategy_used == decision.strategy.value
        assert ensemble_input.candidate_count == len(decision.candidates)
        assert ensemble_input.domain_validation_passed == decision.domain_validation
        assert ensemble_input.latency_ms == decision.latency_ms
        assert ensemble_input.category == "performance"
    
    def test_ensemble_feature_vector_structure(self, engine, adapter):
        """Test that feature vector has expected structure."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        ensemble_input = adapter.adapt_for_planset_009(decision, "test")
        
        # Check feature vector
        fv = ensemble_input.feature_vector
        assert "confidence" in fv
        assert "confidence_normalized" in fv
        assert "latency_factor" in fv
        assert "ensemble_bonus" in fv
        assert "domain_validation_factor" in fv
        
        # All values should be normalized floats
        for key, value in fv.items():
            assert isinstance(value, (int, float))
            assert 0.0 <= value <= 1.0
    
    def test_ensemble_input_json_serialization(self, engine, adapter):
        """Test that ensemble input serializes to valid JSON."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        ensemble_input = adapter.adapt_for_planset_009(decision, "test")
        json_str = ensemble_input.to_json()
        
        # Parse back to verify validity
        parsed = json.loads(json_str)
        assert parsed["reasoning_decision_id"] == decision.id
        assert parsed["confidence_score"] == decision.confidence
        assert "feature_vector" in parsed


class TestPlanset010Integration:
    """Test integration with Planset 010: Enterprise Scaling & Multi-Tenant."""
    
    @pytest.fixture
    def engine(self):
        """Create reasoning engine."""
        return ReasoningEngine()
    
    @pytest.fixture
    def adapter(self):
        """Create integration adapter."""
        return PlansetIntegrationAdapter()
    
    def test_adapt_decision_for_multi_tenant(self, engine, adapter):
        """Test adaptation of reasoning decision for multi-tenant isolation."""
        decision = engine.make_decision(
            goal="scale_infrastructure",
            constraints=["safety_first"],
            decision_history=[],
            current_state={"load": 85.0},
            category="scaling",
        )
        
        # Adapt for Planset 010
        tenant_input = adapter.adapt_for_planset_010(
            decision,
            tenant_id="tenant-123",
            resource_constraints={"cpu": 4, "memory": 8192},
        )
        
        assert tenant_input.reasoning_decision_id == decision.id
        assert tenant_input.confidence_score == decision.confidence
        assert tenant_input.tenant_id == "tenant-123"
        assert tenant_input.resource_constraints == {"cpu": 4, "memory": 8192}
    
    def test_isolation_decision_logic(self, engine, adapter):
        """Test that isolation decisions are derived from reasoning output."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        tenant_input = adapter.adapt_for_planset_010(decision)
        
        # If not safe for production, isolation should be required
        if not tenant_input.safe_for_production:
            assert tenant_input.isolation_required is True
        
        # Safe for production requires: domain validation, low latency, high confidence
        if tenant_input.domain_validation_passed and tenant_input.decision_latency_ms < 100 and tenant_input.confidence_score >= 0.80:
            assert tenant_input.safe_for_production is True
    
    def test_confidence_threshold_evaluation(self, engine, adapter):
        """Test confidence threshold for Planset 010."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        tenant_input = adapter.adapt_for_planset_010(decision)
        
        # Confidence threshold is 0.75
        # Convert numpy bool to Python bool for comparison
        threshold_met = bool(tenant_input.confidence_threshold_met)
        if decision.confidence >= 0.75:
            assert threshold_met is True
        else:
            assert threshold_met is False
    
    def test_tenant_input_json_serialization(self, engine, adapter):
        """Test that tenant input serializes to valid JSON."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        tenant_input = adapter.adapt_for_planset_010(
            decision,
            tenant_id="test-tenant",
        )
        json_str = tenant_input.to_json()
        
        # Parse back to verify validity
        parsed = json.loads(json_str)
        assert parsed["reasoning_decision_id"] == decision.id
        assert parsed["tenant_id"] == "test-tenant"


class TestPlanset011Integration:
    """Test integration with Planset 011: Root Cause Analysis & Anomaly Correlation."""
    
    @pytest.fixture
    def engine(self):
        """Create reasoning engine."""
        return ReasoningEngine()
    
    @pytest.fixture
    def adapter(self):
        """Create integration adapter."""
        return PlansetIntegrationAdapter()
    
    def test_adapt_decision_for_root_cause(self, engine, adapter):
        """Test adaptation of reasoning decision for root cause analysis."""
        decision = engine.make_decision(
            goal="diagnose_issue",
            constraints=["latency > 1000ms"],
            decision_history=[],
            current_state={"error_rate": 0.15},
            category="diagnosis",
        )
        
        # Adapt for Planset 011
        rca_input = adapter.adapt_for_planset_011(
            decision,
            constraints=["latency > 1000ms"],
            anomaly_indicators={"latency_p99": 2500, "error_rate": 0.15},
        )
        
        assert rca_input.reasoning_decision_id == decision.id
        assert rca_input.decision_option == decision.option
        assert rca_input.confidence_score == decision.confidence
        assert rca_input.reasoning_text == decision.reasoning
        assert rca_input.strategy_used == decision.strategy.value
    
    def test_candidate_options_extraction(self, engine, adapter):
        """Test that candidate options are properly extracted."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        rca_input = adapter.adapt_for_planset_011(decision, constraints=[])
        
        # Should have same number of candidate options as candidates
        assert len(rca_input.candidate_options) == len(decision.candidates)
        
        # Each should match a candidate
        for i, option in enumerate(rca_input.candidate_options):
            assert option == decision.candidates[i].option
    
    def test_validation_rules_aggregation(self, engine, adapter):
        """Test that validation rules are aggregated from all candidates."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        rca_input = adapter.adapt_for_planset_011(decision, constraints=[])
        
        # Collect all validation rules from candidates
        expected_rules = set()
        for candidate in decision.candidates:
            expected_rules.update(candidate.validation_rules)
        
        # Should match aggregated rules (may have duplicates)
        actual_rules = set(rca_input.validation_rules_applied)
        assert actual_rules.issubset(expected_rules) or actual_rules == expected_rules
    
    def test_anomaly_indicators_tracking(self, engine, adapter):
        """Test anomaly indicators for correlation."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        anomaly_indicators = {
            "cpu_spike": 0.92,
            "memory_leak": 0.78,
            "latency_increase": 0.65,
        }
        
        rca_input = adapter.adapt_for_planset_011(
            decision,
            constraints=[],
            anomaly_indicators=anomaly_indicators,
        )
        
        assert rca_input.anomaly_indicators == anomaly_indicators
    
    def test_historical_decisions_tracking(self, engine, adapter):
        """Test that historical decisions are tracked for pattern analysis."""
        import time
        
        # Make multiple decisions with delays to ensure unique IDs
        decisions = []
        for i in range(5):
            decision = engine.make_decision(
                goal=f"decision_{i}",
                constraints=[],
                decision_history=[],
                current_state={"iteration": i},
                category="test",
            )
            decisions.append(decision)
            adapter.add_decision_to_history(decision)
            time.sleep(0.001)  # Small delay to ensure unique timestamps
        
        # Latest decision should reference previous ones
        rca_input = adapter.adapt_for_planset_011(
            decisions[-1],
            constraints=[],
        )
        
        # Should have history of previous decisions (excluding the latest)
        # Since we added 5 decisions, history should have 4 (latest is excluded)
        assert len(rca_input.historical_decisions) == len(decisions) - 1
        
        # Most recent should be last decision (excluding current)
        # The historical decisions should reference the decisions we added
        assert rca_input.historical_decisions[-1] == decisions[-2].id
    
    def test_rca_input_json_serialization(self, engine, adapter):
        """Test that RCA input serializes to valid JSON."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        rca_input = adapter.adapt_for_planset_011(decision, constraints=[])
        json_str = rca_input.to_json()
        
        # Parse back to verify validity
        parsed = json.loads(json_str)
        assert parsed["reasoning_decision_id"] == decision.id
        assert "anomaly_indicators" in parsed
        assert "historical_decisions" in parsed


class TestCrossPlansetsConsistency:
    """Test consistency across all planset adapters."""
    
    @pytest.fixture
    def engine(self):
        """Create reasoning engine."""
        return ReasoningEngine()
    
    @pytest.fixture
    def adapter(self):
        """Create integration adapter."""
        return PlansetIntegrationAdapter()
    
    def test_all_adapters_same_decision_id(self, engine, adapter):
        """Test that all adapters preserve same decision ID."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        p009 = adapter.adapt_for_planset_009(decision, "test")
        p010 = adapter.adapt_for_planset_010(decision)
        p011 = adapter.adapt_for_planset_011(decision, constraints=[])
        
        assert p009.reasoning_decision_id == decision.id
        assert p010.reasoning_decision_id == decision.id
        assert p011.reasoning_decision_id == decision.id
    
    def test_all_adapters_consistent_confidence(self, engine, adapter):
        """Test that all adapters use consistent confidence scores."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        p009 = adapter.adapt_for_planset_009(decision, "test")
        p010 = adapter.adapt_for_planset_010(decision)
        p011 = adapter.adapt_for_planset_011(decision, constraints=[])
        
        # All should have same confidence from original decision
        assert p009.confidence_score == decision.confidence
        assert p010.confidence_score == decision.confidence
        assert p011.confidence_score == decision.confidence
    
    def test_adapter_history_isolation(self, engine):
        """Test that adapter histories don't interfere."""
        adapter1 = PlansetIntegrationAdapter()
        adapter2 = PlansetIntegrationAdapter()
        
        # Make decisions with adapter1
        for i in range(5):
            decision = engine.make_decision(
                goal=f"test_{i}",
                constraints=[],
                decision_history=[],
                current_state={},
                category="test",
            )
            adapter1.add_decision_to_history(decision)
        
        # adapter2 should have empty history
        assert len(adapter2.decision_history) == 0
        assert len(adapter1.decision_history) == 5
    
    def test_all_adapters_json_compatible(self, engine, adapter):
        """Test that all adapters produce valid JSON."""
        decision = engine.make_decision(
            goal="test",
            constraints=[],
            decision_history=[],
            current_state={},
            category="test",
        )
        
        p009 = adapter.adapt_for_planset_009(decision, "test")
        p010 = adapter.adapt_for_planset_010(decision)
        p011 = adapter.adapt_for_planset_011(decision, constraints=[])
        
        # All should serialize to valid JSON
        json009 = json.loads(p009.to_json())
        json010 = json.loads(p010.to_json())
        json011 = json.loads(p011.to_json())
        
        # All should have required fields
        assert "reasoning_decision_id" in json009
        assert "reasoning_decision_id" in json010
        assert "reasoning_decision_id" in json011
        
        # All should deserialize back
        assert json009["reasoning_decision_id"] == decision.id
        assert json010["reasoning_decision_id"] == decision.id
        assert json011["reasoning_decision_id"] == decision.id
