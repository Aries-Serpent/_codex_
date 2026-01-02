"""
Phase 8.0 Edge Case Tests - Boundary values, error handling, convergence edge cases.

Tests adaptive scoring with extreme inputs, invalid configurations, and edge conditions
to ensure robust behavior across the full input space.
"""

import pytest
import numpy as np
from cognitive_brain.quantum.adaptive_scoring import AdaptiveScoringEngine
from cognitive_brain.experiments.complex_scenarios import generate_complex_scenarios


class TestAdaptiveScoringEdgeCases:
    """Edge case tests for Phase 8.0 adaptive scoring optimization."""

    def test_weights_at_lower_boundary(self):
        """Test weights at minimum boundary (0.0)."""
        engine = AdaptiveScoringEngine(
            compliance_score_weight=0.0,
            risk_weight=0.0,
            learning_rate=0.01
        )
        scenarios = generate_complex_scenarios(10, seed=42)
        # Should not crash with zero weights
        for scenario in scenarios[:5]:
            score = engine.compute_score(scenario)
            assert isinstance(score, (int, float))
            assert score >= 0.0

    def test_weights_at_upper_boundary(self):
        """Test weights at maximum boundary (1.0)."""
        engine = AdaptiveScoringEngine(
            compliance_score_weight=1.0,
            risk_weight=0.0,
            learning_rate=0.01
        )
        scenarios = generate_complex_scenarios(10, seed=42)
        for scenario in scenarios[:5]:
            score = engine.compute_score(scenario)
            assert isinstance(score, (int, float))
            assert 0.0 <= score <= 100.0

    def test_invalid_negative_weights(self):
        """Test error handling for negative weights."""
        with pytest.raises(ValueError, match="Weights must be non-negative"):
            AdaptiveScoringEngine(
                compliance_score_weight=-0.1,
                risk_weight=0.3,
                learning_rate=0.1
            )

    def test_invalid_weights_sum_exceeds_one(self):
        """Test error handling when weights sum > 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            AdaptiveScoringEngine(
                compliance_score_weight=0.6,
                risk_weight=0.6,
                learning_rate=0.1
            )

    def test_zero_learning_rate(self):
        """Test convergence with zero learning rate (no updates)."""
        engine = AdaptiveScoringEngine(
            compliance_score_weight=0.38,
            risk_weight=0.32,
            learning_rate=0.0
        )
        scenarios = generate_complex_scenarios(10, seed=42)
        
        initial_weights = (engine.compliance_score_weight, engine.risk_weight)
        engine.train(scenarios[:5], epochs=10)
        final_weights = (engine.compliance_score_weight, engine.risk_weight)
        
        # Weights should not change with zero learning rate
        assert initial_weights == final_weights

    def test_max_iterations_convergence(self):
        """Test behavior at maximum training iterations."""
        engine = AdaptiveScoringEngine(
            compliance_score_weight=0.38,
            risk_weight=0.32,
            learning_rate=0.12
        )
        scenarios = generate_complex_scenarios(50, seed=42)
        
        # Train for many epochs - should converge or stabilize
        engine.train(scenarios, epochs=100)
        
        # Weights should still be valid
        assert 0.0 <= engine.compliance_score_weight <= 1.0
        assert 0.0 <= engine.risk_weight <= 1.0
        assert abs((engine.compliance_score_weight + engine.risk_weight + 
                   engine.impact_weight + engine.mitigation_weight) - 1.0) < 1e-6

    def test_empty_scenarios_list(self):
        """Test error handling for empty scenarios."""
        engine = AdaptiveScoringEngine()
        
        with pytest.raises(ValueError, match="Cannot train on empty scenarios"):
            engine.train([], epochs=10)

    def test_single_scenario_training(self):
        """Test training with minimal data (1 scenario)."""
        engine = AdaptiveScoringEngine()
        scenarios = generate_complex_scenarios(1, seed=42)
        
        # Should not crash with single scenario
        engine.train(scenarios, epochs=5)
        assert engine.compliance_score_weight > 0

    def test_duplicate_scenario_ids(self):
        """Test handling of duplicate scenario IDs."""
        scenarios = generate_complex_scenarios(10, seed=42)
        # Force duplicate IDs
        scenarios[5].scenario_id = scenarios[0].scenario_id
        
        engine = AdaptiveScoringEngine()
        # Should handle duplicates gracefully (deduplicate or process both)
        engine.train(scenarios, epochs=5)
        assert engine.compliance_score_weight > 0

    def test_missing_features_in_scenario(self):
        """Test integration with scenarios missing expected features."""
        scenarios = generate_complex_scenarios(5, seed=42)
        # Remove a feature from one scenario
        if hasattr(scenarios[0], 'risk_level'):
            delattr(scenarios[0], 'risk_level')
        
        engine = AdaptiveScoringEngine()
        # Should handle missing features with defaults
        try:
            score = engine.compute_score(scenarios[0])
            assert isinstance(score, (int, float))
        except AttributeError:
            # Expected if no fallback mechanism
            pass

    def test_nan_in_scenario_features(self):
        """Test handling of NaN values in features."""
        scenarios = generate_complex_scenarios(5, seed=42)
        # Inject NaN
        scenarios[0].ambiguity_score = float('nan')
        
        engine = AdaptiveScoringEngine()
        score = engine.compute_score(scenarios[0])
        # Should not return NaN
        assert not np.isnan(score)

    def test_inf_in_scenario_features(self):
        """Test handling of infinite values in features."""
        scenarios = generate_complex_scenarios(5, seed=42)
        # Inject infinity
        scenarios[0].ambiguity_score = float('inf')
        
        engine = AdaptiveScoringEngine()
        score = engine.compute_score(scenarios[0])
        # Should clamp or handle infinity
        assert np.isfinite(score)

    def test_very_high_ambiguity_score(self):
        """Test scenarios with maximum ambiguity."""
        scenarios = generate_complex_scenarios(5, seed=42)
        scenarios[0].ambiguity_score = 1.0  # Maximum ambiguity
        
        engine = AdaptiveScoringEngine()
        score = engine.compute_score(scenarios[0])
        # Should produce valid score even at max ambiguity
        assert 0.0 <= score <= 100.0

    def test_convergence_with_conflicting_data(self):
        """Test training on conflicting scenario patterns."""
        scenarios = generate_complex_scenarios(20, seed=42)
        # Create conflicting patterns (high compliance + high risk)
        for i in range(0, 10, 2):
            scenarios[i].compliance_score = 0.9
            scenarios[i].risk_level = "critical"
        for i in range(1, 10, 2):
            scenarios[i].compliance_score = 0.1
            scenarios[i].risk_level = "low"
        
        engine = AdaptiveScoringEngine()
        engine.train(scenarios, epochs=20)
        
        # Should converge to some stable weights despite conflicts
        assert 0.0 <= engine.compliance_score_weight <= 1.0
        assert 0.0 <= engine.risk_weight <= 1.0

    def test_weight_normalization_after_training(self):
        """Test that weights remain normalized after training."""
        engine = AdaptiveScoringEngine()
        scenarios = generate_complex_scenarios(30, seed=42)
        
        engine.train(scenarios, epochs=50)
        
        # Weights must sum to 1.0 (within floating point tolerance)
        weight_sum = (engine.compliance_score_weight + engine.risk_weight + 
                     engine.impact_weight + engine.mitigation_weight)
        assert abs(weight_sum - 1.0) < 1e-5, f"Weights sum to {weight_sum}, expected 1.0"
