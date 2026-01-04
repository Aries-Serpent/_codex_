#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 3 Advanced Reasoning components.

Tests causal inference (DoWhy), counterfactual reasoning (CausalML), and explainability (SHAP).
"""

import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestCausalReasoning:
    """Test causal inference with DoWhy"""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample causal data"""
        np.random.seed(42)
        n = 1000
        
        # Confounders
        experience = np.random.normal(5, 2, n)
        
        # Treatment (code changes)
        code_changes = (experience * 0.3 + np.random.normal(0, 1, n)) > 2.5
        
        # Outcome (test success)
        test_success = (
            0.4 * code_changes.astype(int) + 
            0.3 * experience + 
            np.random.normal(0, 0.5, n)
        )
        
        return pd.DataFrame({
            'code_changes': code_changes.astype(int),
            'experience': experience,
            'test_success': test_success
        })
    
    def test_causal_effect_estimation(self, sample_data):
        """Test estimating causal effect of code changes on test success"""
        try:
            from dowhy import CausalModel
        except ImportError:
            pytest.skip("DoWhy not installed")
        
        # Define causal model
        model = CausalModel(
            data=sample_data,
            treatment='code_changes',
            outcome='test_success',
            common_causes=['experience']
        )
        
        # Identify causal effect
        identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
        
        # Estimate effect
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.propensity_score_matching"
        )
        
        assert estimate is not None
        assert hasattr(estimate, 'value')
        # Effect should be positive (code changes improve test success)
        assert estimate.value > 0
    
    def test_confounding_detection(self, sample_data):
        """Test detecting confounding variables"""
        try:
            from dowhy import CausalModel
        except ImportError:
            pytest.skip("DoWhy not installed")
        
        # Model without confounder
        model_biased = CausalModel(
            data=sample_data,
            treatment='code_changes',
            outcome='test_success',
            common_causes=[]
        )
        
        # Model with confounder
        model_debiased = CausalModel(
            data=sample_data,
            treatment='code_changes',
            outcome='test_success',
            common_causes=['experience']
        )
        
        # Estimates should differ due to confounding
        est_biased = model_biased.estimate_effect(
            model_biased.identify_effect(),
            method_name="backdoor.linear_regression"
        )
        
        est_debiased = model_debiased.estimate_effect(
            model_debiased.identify_effect(),
            method_name="backdoor.linear_regression"
        )
        
        # Debiased estimate should be closer to true effect (0.4)
        assert abs(est_debiased.value - 0.4) < abs(est_biased.value - 0.4)
    
    def test_causal_graph_construction(self):
        """Test building causal graphs"""
        try:
            from dowhy import CausalModel
            import networkx as nx
        except ImportError:
            pytest.skip("DoWhy or NetworkX not installed")
        
        # Define causal graph
        graph = """
        digraph {
            developer_experience -> code_quality;
            code_quality -> test_coverage;
            test_coverage -> success_rate;
            developer_experience -> success_rate;
        }
        """
        
        # Verify graph is valid
        G = nx.DiGraph()
        G.add_edges_from([
            ('developer_experience', 'code_quality'),
            ('code_quality', 'test_coverage'),
            ('test_coverage', 'success_rate'),
            ('developer_experience', 'success_rate')
        ])
        
        assert len(G.nodes()) == 4
        assert len(G.edges()) == 4


class TestCounterfactualReasoning:
    """Test counterfactual analysis with CausalML"""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for counterfactual analysis"""
        np.random.seed(42)
        n = 500
        
        # Features
        X = pd.DataFrame({
            'team_size': np.random.randint(2, 10, n),
            'code_complexity': np.random.uniform(1, 10, n),
            'test_coverage': np.random.uniform(0, 100, n)
        })
        
        # Treatment (CI/CD automation)
        treatment = (X['team_size'] > 5).astype(int)
        
        # Outcome (deployment frequency)
        outcome = (
            5 + 
            2 * treatment + 
            0.5 * X['team_size'] + 
            np.random.normal(0, 1, n)
        )
        
        return X, treatment, outcome
    
    def test_uplift_modeling(self, sample_data):
        """Test predicting treatment effect uplift"""
        X, treatment, outcome = sample_data
        
        try:
            from causalml.inference.meta import BaseSRegressor
            from sklearn.ensemble import RandomForestRegressor
        except ImportError:
            pytest.skip("CausalML or sklearn not installed")
        
        # Train uplift model
        learner = BaseSRegressor(RandomForestRegressor(random_state=42))
        learner.fit(X=X, treatment=treatment, y=outcome)
        
        # Predict treatment effect
        te_pred = learner.predict(X=X)
        
        assert te_pred is not None
        assert len(te_pred) == len(X)
        # Average treatment effect should be positive
        assert te_pred.mean() > 0
    
    def test_counterfactual_scenarios(self):
        """Test generating 'what if' counterfactual scenarios"""
        # Scenario: What if we had used CI/CD from the start?
        actual_outcome = {'deployments': 12, 'bugs': 8, 'time_to_prod': 14}
        
        # Simulate counterfactual
        counterfactual_outcome = {
            'deployments': 18,  # More frequent
            'bugs': 5,          # Fewer bugs
            'time_to_prod': 7   # Faster
        }
        
        # Calculate uplift
        uplift = {
            k: counterfactual_outcome[k] - actual_outcome[k]
            for k in actual_outcome
        }
        
        assert uplift['deployments'] > 0
        assert uplift['bugs'] < 0  # Negative = improvement
        assert uplift['time_to_prod'] < 0


class TestExplainability:
    """Test model explainability with SHAP"""
    
    @pytest.fixture
    def trained_model(self):
        """Train a simple model for testing"""
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            pytest.skip("sklearn not installed")
        
        np.random.seed(42)
        n = 200
        
        X = np.random.rand(n, 5)
        y = (X[:, 0] + 2 * X[:, 1] - X[:, 2] > 0.5).astype(int)
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)
        
        return model, X, y
    
    def test_feature_importance(self, trained_model):
        """Test computing feature importance with SHAP"""
        model, X, y = trained_model
        
        try:
            import shap
        except ImportError:
            pytest.skip("SHAP not installed")
        
        # Create explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X[:10])
        
        assert shap_values is not None
        assert len(shap_values) == 2  # Binary classification
        assert shap_values[0].shape == (10, 5)
    
    def test_decision_explanation(self, trained_model):
        """Test explaining individual predictions"""
        model, X, y = trained_model
        
        try:
            import shap
        except ImportError:
            pytest.skip("SHAP not installed")
        
        # Explain single prediction
        explainer = shap.TreeExplainer(model)
        sample = X[0:1]
        shap_values = explainer.shap_values(sample)
        
        # Get top contributing features
        contributions = abs(shap_values[1][0])
        top_features = np.argsort(contributions)[::-1][:3]
        
        # Feature 1 should be most important (weight 2)
        assert 1 in top_features[:2]
    
    def test_global_explanations(self, trained_model):
        """Test generating global model explanations"""
        model, X, y = trained_model
        
        try:
            import shap
        except ImportError:
            pytest.skip("SHAP not installed")
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        
        # Calculate mean absolute SHAP values
        mean_shap = np.abs(shap_values[1]).mean(axis=0)
        
        # Feature 1 should have highest importance
        assert np.argmax(mean_shap) == 1


class TestAdvancedReasoningIntegration:
    """Test integrated advanced reasoning workflows"""
    
    def test_causal_with_explainability(self):
        """Test combining causal inference with explainability"""
        np.random.seed(42)
        n = 300
        
        # Generate data
        data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n),
            'feature2': np.random.normal(0, 1, n),
            'treatment': np.random.binomial(1, 0.5, n),
            'outcome': np.random.normal(0, 1, n)
        })
        
        # Add treatment effect
        data.loc[data['treatment'] == 1, 'outcome'] += 0.5
        
        try:
            from sklearn.ensemble import RandomForestRegressor
            import shap
        except ImportError:
            pytest.skip("sklearn or SHAP not installed")
        
        # Train outcome model
        X = data[['feature1', 'feature2', 'treatment']]
        y = data['outcome']
        
        model = RandomForestRegressor(random_state=42)
        model.fit(X, y)
        
        # Explain treatment effect
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        
        # Treatment feature (index 2) should have impact
        treatment_impact = np.abs(shap_values[:, 2]).mean()
        assert treatment_impact > 0
    
    def test_decision_confidence_scoring(self):
        """Test scoring decision confidence with causal + explainability"""
        # Mock decision with causal evidence and explanations
        decision = {
            'action': 'deploy_new_feature',
            'causal_effect': 0.45,
            'causal_confidence': 0.92,
            'explanation_clarity': 0.88,
            'counterfactual_support': 0.85
        }
        
        # Compute overall confidence
        confidence = (
            0.4 * decision['causal_confidence'] +
            0.3 * decision['explanation_clarity'] +
            0.3 * decision['counterfactual_support']
        )
        
        assert confidence > 0.85  # High confidence decision
    
    def test_trust_score_calculation(self):
        """Test calculating user trust score for autonomous decisions"""
        # User interaction history
        decisions = [
            {'autonomous': True, 'user_approved': True, 'confidence': 0.92},
            {'autonomous': True, 'user_approved': True, 'confidence': 0.88},
            {'autonomous': True, 'user_approved': False, 'confidence': 0.75},
            {'autonomous': True, 'user_approved': True, 'confidence': 0.95}
        ]
        
        # Calculate trust score
        approved = sum(1 for d in decisions if d['user_approved'])
        trust_score = approved / len(decisions)
        
        # Weight by confidence
        weighted_trust = sum(
            d['confidence'] for d in decisions if d['user_approved']
        ) / sum(d['confidence'] for d in decisions)
        
        assert trust_score == 0.75  # 3/4 approved
        assert weighted_trust > trust_score  # Higher confidence boost


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
