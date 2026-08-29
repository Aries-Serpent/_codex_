#         assert (abs(, "Condition must be true"
#                 (
#                     engine.compliance_score_weight
#                     + engine.risk_weight
#                     + engine.impact_weight
#                     + engine.mitigation_weight
#                 )
#                 - 1.0
#             )
#             < 1e-6
#         )
# from cognitive_brain.quantum.adaptive_scoring import (
#     AdaptiveScoringOptimizer,
#     ScoringWeights,
# )
#         assert 0.0 <= engine.risk_weight <= 1.0, "0 is not valid"
#         assert (abs(, "Condition must be true"
#                 (
#                     engine.compliance_score_weight
#                     + engine.risk_weight
#                     + engine.impact_weight
#                     + engine.mitigation_weight
#                 )
#                 - 1.0
#             )
#             < 1e-6
#         )
#         compliance_score_weight=0.38,
#         risk_weight=0.32,
#         cost_weight=None,
#         impact_weight=None,
#         learning_rate=0.12,
#     ):
#     ):
#         """Initialize with explicit weights for testing."""
#         # Validate weights
#         if compliance_score_weight < 0 or risk_weight < 0:
#             raise ValueError("Weights must be non-negative")
#         if cost_weight is None and impact_weight is None:
#             if compliance_score_weight + risk_weight > 1.0 + _WEIGHT_SUM_TOLERANCE:
#                 raise ValueError(
#                     f"Weights must sum to 1.0 (got {compliance_score_weight + risk_weight})"
#                 )
#             remaining = 1.0 - compliance_score_weight - risk_weight
#             cost_weight = remaining / 2
#             impact_weight = remaining / 2
#         elif cost_weight is None:
#             cost_weight = 1.0 - compliance_score_weight - risk_weight - impact_weight
#         elif impact_weight is None:
#             impact_weight = 1.0 - compliance_score_weight - risk_weight - cost_weight
# 
#         # Validate sum
#         total = compliance_score_weight + risk_weight + cost_weight + impact_weight
#         if abs(total - 1.0) > _WEIGHT_SUM_TOLERANCE:
#             raise ValueError(f"Weights must sum to 1.0 (got {total})")
#             raise ValueError(f"Weights must sum to 1.0 (got {total})")
# 
#         self.optimizer = AdaptiveScoringOptimizer(learning_rate=learning_rate)
#         self.optimizer.weights = ScoringWeights(
#             compliance_score_weight=compliance_score_weight,
#             risk_weight=risk_weight,
#             cost_weight=cost_weight,
#             impact_weight=impact_weight,
#         )
#         self.learning_rate = learning_rate
# 
#     @property
#     def compliance_score_weight(self):
#         return self.optimizer.weights.compliance_score_weight
# 
#     @property
#     def risk_weight(self):
#         return self.optimizer.weights.risk_weight
# 
#     @property
#     def impact_weight(self):
#         return self.optimizer.weights.impact_weight
# 
#     @property
#     def mitigation_weight(self):
#         # cost_weight acts as the mitigation/remediation weight in this schema
#         return self.optimizer.weights.cost_weight
# 
#     def compute_score(self, scenario):
#     def compute_score(self, scenario):
#         """Compute score from scenario tuple or dict."""
#         # Handle tuple format from generate_complex_scenarios
#         if isinstance(scenario, tuple):
#             audit, _ground_truth, _complexity = scenario
#             # Extract features from AuditResult
#             features = {
#                 "compliance_score": audit.score if audit.score is not None else 0.5,
#                 "risk_score": _RISK_LEVEL_SCORES.get(audit.risk_level, 0.5),
#                 "cost_score": (
#                     min(1.0, audit.remediation_cost / _MAX_REMEDIATION_COST)
#                     if audit.remediation_cost
#                     else 0.5
#                 ),
#                 "impact_score": audit.business_impact if audit.business_impact else 0.5,
#             }
#             return self.optimizer.compute_score(features)
#         # Handle dict format
#         return self.optimizer.compute_score(scenario)
#     def train(self, scenarios, epochs=10):
#     def train(self, scenarios, epochs=10):
#         """Mock training method for tests."""
#         if not scenarios:
#             raise ValueError("Cannot train on empty scenarios")
#         # Just run through scenarios without updating weights if learning_rate is 0
#         for _ in range(epochs):
#             for scenario in scenarios:
#                 _ = self.compute_score(scenario)
#         assert (abs(, "Condition must be true"
#                 (
#                     engine.compliance_score_weight
#                     + engine.risk_weight
#                     + engine.impact_weight
#                     + engine.mitigation_weight
#                 )
#                 - 1.0
#             )
#             < 1e-6
#         )
#         for scenario in scenarios[:5]:
#             score = engine.compute_score(scenario)
#             assert isinstance(score, (int, float))
#             assert score >= 0.0, "score must be greater than zero"
# 
#     def test_weights_at_upper_boundary(self):
#     def test_weights_at_upper_boundary(self):
#         """Test weights at maximum boundary (1.0)."""
#         engine = AdaptiveScoringEngine(
#             compliance_score_weight=1.0, risk_weight=0.0, learning_rate=0.01
#         )
#         scenarios = generate_complex_scenarios(10, seed=42)
#         for scenario in scenarios[:5]:
#             score = engine.compute_score(scenario)
#             assert isinstance(score, (int, float))
#             assert 0.0 <= score <= 100.0, "0 is not valid"
#     def test_invalid_negative_weights(self):
#     def test_invalid_negative_weights(self):
#         """Test error handling for negative weights."""
#         with pytest.raises(ValueError, match="Weights must be non-negative"):
#             AdaptiveScoringEngine(compliance_score_weight=-0.1, risk_weight=0.3, learning_rate=0.1)
#     def test_invalid_weights_sum_exceeds_one(self):
#     def test_invalid_weights_sum_exceeds_one(self):
#         """Test error handling when weights sum > 1.0."""
#         with pytest.raises(ValueError, match="Weights must sum to 1.0"):
#             AdaptiveScoringEngine(compliance_score_weight=0.6, risk_weight=0.6, learning_rate=0.1)
#     def test_zero_learning_rate(self):
#     def test_zero_learning_rate(self):
#         """Test convergence with zero learning rate (no updates)."""
#         engine = AdaptiveScoringEngine(
#             compliance_score_weight=0.38, risk_weight=0.32, learning_rate=0.0
#         )
#         scenarios = generate_complex_scenarios(10, seed=42)
#         initial_weights = (engine.compliance_score_weight, engine.risk_weight)
#         engine.train(scenarios[:5], epochs=10)
#         final_weights = (engine.compliance_score_weight, engine.risk_weight)
#         # Weights should not change with zero learning rate
#         assert initial_weights == final_weights, "initial_weights is not valid"
#         assert initial_weights == final_weights, "initial_weights is not valid"
# 
#     def test_max_iterations_convergence(self):
#     def test_max_iterations_convergence(self):
#         """Test behavior at maximum training iterations."""
#         engine = AdaptiveScoringEngine(
#             compliance_score_weight=0.38, risk_weight=0.32, learning_rate=0.12
#         )
#         scenarios = generate_complex_scenarios(50, seed=42)
#         engine.train(scenarios, epochs=100)
# 
#         # Weights should still be valid
#         assert 0.0 <= engine.compliance_score_weight <= 1.0, "0 is not valid"
#         assert 0.0 <= engine.risk_weight <= 1.0, "0 is not valid"
#         assert (abs(, "Condition must be true"
#                 (
#                     engine.compliance_score_weight
#                     + engine.risk_weight
#                     + engine.impact_weight
#                     + engine.mitigation_weight
#                 )
#                 - 1.0
#             )
#             < 1e-6
#         )
#         )
# 
#     def test_empty_scenarios_list(self):
#     def test_empty_scenarios_list(self):
#         """Test error handling for empty scenarios."""
#         engine = AdaptiveScoringEngine()
#         with pytest.raises(ValueError, match="Cannot train on empty scenarios"):
#             engine.train([], epochs=10)
# 
#     def test_single_scenario_training(self):
#     def test_single_scenario_training(self):
#         """Test training with minimal data (1 scenario)."""
#         engine = AdaptiveScoringEngine()
#         scenarios = generate_complex_scenarios(1, seed=42)
#         engine.train(scenarios, epochs=5)
#         assert engine.compliance_score_weight > 0, "compliance_score_weight must be greater than zero"
#         assert engine.compliance_score_weight > 0, "compliance_score_weight must be greater than zero"
# 
#     def test_duplicate_scenario_ids(self):
#     def test_duplicate_scenario_ids(self):
#         """Test handling of duplicate scenario IDs."""
#         scenarios = generate_complex_scenarios(10, seed=42)
#         # Force duplicate IDs by modifying the AuditResult (index 0 of tuple)
#         audit0, _gt0, _c0 = scenarios[0]
#         audit5, _gt5, _c5 = scenarios[5]
#         audit5.audit_id = audit0.audit_id
#         engine = AdaptiveScoringEngine()
#         # Should handle duplicates gracefully (deduplicate or process both)
#         engine.train(scenarios, epochs=5)
#         assert engine.compliance_score_weight > 0, "compliance_score_weight must be greater than zero"
# 
#     def test_missing_features_in_scenario(self):
#     def test_missing_features_in_scenario(self):
#         """Test integration with scenarios missing expected features."""
#         scenarios = generate_complex_scenarios(5, seed=42)
#         # Remove a feature from one scenario
#         if hasattr(scenarios[0], "risk_level"):
#             delattr(scenarios[0], "risk_level")
#         engine = AdaptiveScoringEngine()
#         # Should handle missing features with defaults
#         try:
#             score = engine.compute_score(scenarios[0])
#             assert isinstance(score, (int, float))
#         except AttributeError:
#             # Expected if no fallback mechanism
#             _ = None  # suppressed: no action needed
# 
#     def test_nan_in_scenario_features(self):
#     def test_nan_in_scenario_features(self):
#         """Test handling of NaN values in features."""
#         scenarios = generate_complex_scenarios(5, seed=42)
#         # Inject NaN into ScenarioComplexity (index 2 of the (audit, gt, complexity) tuple)
#         _audit, _gt, complexity = scenarios[0]
#         complexity.ambiguity_score = float("nan")
#         engine = AdaptiveScoringEngine()
#         score = engine.compute_score(scenarios[0])
#         # Should not return NaN
#         assert not np.isnan(score, "Condition must be true"
#         ), "Condition must be true"
# 
#     def test_inf_in_scenario_features(self):
#     def test_inf_in_scenario_features(self):
#         """Test handling of infinite values in features."""
#         scenarios = generate_complex_scenarios(5, seed=42)
#         # Inject infinity into ScenarioComplexity (index 2 of the (audit, gt, complexity) tuple)
#         _audit, _gt, complexity = scenarios[0]
#         complexity.ambiguity_score = float("inf")
#         engine = AdaptiveScoringEngine()
#         score = engine.compute_score(scenarios[0])
#         # Should clamp or handle infinity
#         assert np.isfinite(score), "Condition must be true"
# 
#     def test_very_high_ambiguity_score(self):
#     def test_very_high_ambiguity_score(self):
#         """Test scenarios with maximum ambiguity."""
#         scenarios = generate_complex_scenarios(5, seed=42)
#         _audit, _gt, complexity = scenarios[0]
#         complexity.ambiguity_score = 1.0  # Maximum ambiguity
#         engine = AdaptiveScoringEngine()
#         score = engine.compute_score(scenarios[0])
#         # Should produce valid score even at max ambiguity
#         assert 0.0 <= score <= 100.0, "0 is not valid"
# 
#     def test_convergence_with_conflicting_data(self):
#     def test_convergence_with_conflicting_data(self):
#         """Test training on conflicting scenario patterns."""
#         scenarios = generate_complex_scenarios(20, seed=42)
#         # Create conflicting patterns (high compliance + high risk)
#         # AuditResult is at index 0 of each (audit, gt, complexity) tuple
#         for i in range(0, 10, 2):
#             audit, _gt, _c = scenarios[i]
#             audit.score = 0.9
#             audit.risk_level = "high"
#         for i in range(1, 10, 2):
#             audit, _gt, _c = scenarios[i]
#             audit.score = 0.1
#             audit.risk_level = "low"
#         engine = AdaptiveScoringEngine()
#         engine.train(scenarios, epochs=20)
#         # Should converge to some stable weights despite conflicts
#         assert 0.0 <= engine.compliance_score_weight <= 1.0, "0 is not valid"
#         assert 0.0 <= engine.risk_weight <= 1.0, "0 is not valid"
#         assert 0.0 <= engine.risk_weight <= 1.0, "0 is not valid"
# 
#     def test_weight_normalization_after_training(self):
#     def test_weight_normalization_after_training(self):
#         """Test that weights remain normalized after training."""
#         engine = AdaptiveScoringEngine()
#         scenarios = generate_complex_scenarios(30, seed=42)
#         engine.train(scenarios, epochs=50)
#         # Weights must sum to 1.0 (within floating point tolerance)
#         weight_sum = (
#             engine.compliance_score_weight
#             + engine.risk_weight
#             + engine.impact_weight
#             + engine.mitigation_weight
#         )
#         assert abs(weight_sum - 1.0) < 1e-5, f"Weights sum to {weight_sum}, expected 1.0"
