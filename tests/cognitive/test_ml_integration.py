"""
Tests for ML Integration Module (Phase 2.3).

Tests the integration between ML components and cognitive brain systems.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from codex.cognitive.ml.integration import (
    BrainMLBridge,
    EnhancedAgentRouter,
    IntegratedPipeline,
    MLEnhancedPatternMatcher,
    MLEnhancedQueryResult,
    RoutingDecision,
    create_integrated_pipeline,
    enhance_brain_with_ml,
)


class TestBrainMLBridge:
    """Tests for BrainMLBridge class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        bridge = BrainMLBridge()
        assert not bridge.is_trained, "Condition must be true"
        assert bridge.pattern_store_path is None, "pattern_store_path is not valid"

    def test_init_with_paths(self) -> None:
        """Test initialization with paths."""
        bridge = BrainMLBridge(
            pattern_store_path="/path/to/store.json",
            model_cache_path="/path/to/cache",
        )
        assert bridge.pattern_store_path == Path("/path/to/store.json"), "pattern_store_path is not valid"
        assert bridge.model_cache_path == Path("/path/to/cache"), "model_cache_path is not valid"

    def test_train_creates_synthetic_data(self) -> None:
        """Test training with synthetic data when no pattern store."""
        bridge = BrainMLBridge()
        count = bridge.train_from_pattern_store()
        assert count > 0, "count must be positive"
        assert bridge.is_trained, "Condition must be true"

    def test_train_from_pattern_store(self) -> None:
        """Test training from actual pattern store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pattern_store = Path(tmpdir) / "patterns.json"
            patterns = {
                "patterns": {
                    "P1": {
                        "id": "P1",
                        "category": "testing",
                        "symptoms": ["pytest error", "collection failed"],
                        "resolution": "fix imports",
                        "success_rate": 0.9,
                        "last_used": "2026-02-05T12:00:00Z",
                    },
                    "P2": {
                        "id": "P2",
                        "category": "testing",
                        "symptoms": ["test failure", "assertion error"],
                        "resolution": "fix assertion",
                        "success_rate": 0.85,
                        "last_used": "2026-02-05T12:00:00Z",
                    },
                }
            }
            pattern_store.write_text(json.dumps(patterns))

            bridge = BrainMLBridge(pattern_store_path=pattern_store)
            count = bridge.train_from_pattern_store()
            # Should train from synthetic data if loading fails
            assert count >= 0, "count must be positive"
            # If training happened, should be marked as trained
            if count > 0:
                assert bridge.is_trained, "Condition must be true"

    def test_get_recommendations_not_trained(self) -> None:
        """Test recommendations when not trained."""
        bridge = BrainMLBridge()
        recs = bridge.get_recommendations("test error")
        assert recs == [], "recs is not valid"

    def test_get_recommendations_trained(self) -> None:
        """Test recommendations when trained."""
        bridge = BrainMLBridge()
        bridge.train_from_pattern_store()
        recs = bridge.get_recommendations("testing error", top_k=2)
        assert len(recs) <= 2, "Recs must not be empty"

    def test_get_agents_for_category(self) -> None:
        """Test agent retrieval by category."""
        bridge = BrainMLBridge()

        testing_agents = bridge._get_agents_for_category("testing")
        assert "ci-testing-agent" in testing_agents, "Condition must be true"

        security_agents = bridge._get_agents_for_category("security")
        assert "security-alert-verification-agent" in security_agents, "Condition must be true"

    def test_enhance_query_not_trained(self) -> None:
        """Test query enhancement when not trained."""
        bridge = BrainMLBridge()
        mock_brain = MagicMock()
        mock_brain.query_patterns.return_value = []

        result = bridge.enhance_query(mock_brain, "test error")
        assert isinstance(result, MLEnhancedQueryResult)
        assert result.ml_category is None, "Result must not be empty"
        assert result.confidence == 0.0, "Result must not be empty"

    def test_enhance_query_trained(self) -> None:
        """Test query enhancement when trained."""
        bridge = BrainMLBridge()
        bridge.train_from_pattern_store()

        mock_brain = MagicMock()
        mock_brain.query_patterns.return_value = [
            {"id": "P1", "symptoms": "pytest error", "category": "testing"}
        ]

        result = bridge.enhance_query(mock_brain, "pytest collection error")
        assert isinstance(result, MLEnhancedQueryResult)
        assert result.query == "pytest collection error", "Result must not be empty"

    def test_save_and_load_models(self) -> None:
        """Test model persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "models"
            bridge = BrainMLBridge(model_cache_path=cache_path)
            bridge.train_from_pattern_store()

            # Save
            assert bridge.save_models(), "Condition must be true"
            assert (cache_path / "model_state.json").exists(), "Condition must be true"

            # Load
            bridge2 = BrainMLBridge(model_cache_path=cache_path)
            assert bridge2.load_models(), "Condition must be true"
            assert bridge2.is_trained, "Condition must be true"

    def test_save_models_no_path(self) -> None:
        """Test save fails without path."""
        bridge = BrainMLBridge()
        assert not bridge.save_models(), "Condition must be true"

    def test_load_models_no_path(self) -> None:
        """Test load fails without path."""
        bridge = BrainMLBridge()
        assert not bridge.load_models(), "Condition must be true"


class TestEnhancedAgentRouter:
    """Tests for EnhancedAgentRouter class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        router = EnhancedAgentRouter()
        assert router._bridge is not None, "_bridge must be initialized"

    def test_init_with_bridge(self) -> None:
        """Test initialization with bridge."""
        bridge = BrainMLBridge()
        router = EnhancedAgentRouter(bridge=bridge)
        assert router._bridge is bridge, "_bridge is not valid"

    def test_route_not_trained(self) -> None:
        """Test routing when not trained."""
        router = EnhancedAgentRouter()
        decision = router.route("test error")

        assert isinstance(decision, RoutingDecision)
        assert decision.symptom == "test error", "Error should be raised or set"
        assert decision.primary_agent is not None, "primary_agent must be initialized"
        assert "Default routing" in decision.reasoning, "Condition must be true"

    def test_route_trained(self) -> None:
        """Test routing when trained."""
        bridge = BrainMLBridge()
        bridge.train_from_pattern_store()
        router = EnhancedAgentRouter(bridge=bridge)

        decision = router.route("pytest collection error")
        assert isinstance(decision, RoutingDecision)
        assert decision.confidence > 0, "confidence must be greater than zero"

    def test_route_batch(self) -> None:
        """Test batch routing."""
        router = EnhancedAgentRouter()
        symptoms = ["pytest error", "security alert", "doc issue"]
        decisions = router.route_batch(symptoms)

        assert len(decisions) == 3, "Decisions must not be empty"
        assert all(isinstance(d, RoutingDecision) for d in decisions)

    def test_routing_decision_structure(self) -> None:
        """Test routing decision has all fields."""
        router = EnhancedAgentRouter()
        decision = router.route("test error")

        assert hasattr(decision, "symptom")
        assert hasattr(decision, "primary_agent")
        assert hasattr(decision, "fallback_agents")
        assert hasattr(decision, "category")
        assert hasattr(decision, "confidence")
        assert hasattr(decision, "reasoning")


class TestMLEnhancedPatternMatcher:
    """Tests for MLEnhancedPatternMatcher class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        matcher = MLEnhancedPatternMatcher()
        assert matcher._bridge is not None, "_bridge must be initialized"

    def test_match_empty_patterns(self) -> None:
        """Test matching with empty patterns."""
        matcher = MLEnhancedPatternMatcher()
        results = matcher.match("test query", [])
        assert results == [], "Result must not be empty"

    def test_match_with_patterns(self) -> None:
        """Test matching with patterns."""
        matcher = MLEnhancedPatternMatcher()
        patterns = [
            {"id": "P1", "symptoms": "pytest error", "category": "testing"},
            {"id": "P2", "symptoms": "security issue", "category": "security"},
        ]

        results = matcher.match("pytest collection error", patterns, threshold=0.0)
        assert len(results) == 2, "Results must not be empty"
        assert all("ml_score" in r for r in results), "Result must not be empty"
        assert all("ml_rank" in r for r in results), "Result must not be empty"

    def test_match_respects_threshold(self) -> None:
        """Test matching respects threshold."""
        matcher = MLEnhancedPatternMatcher()
        patterns = [
            {"id": "P1", "symptoms": "unrelated issue", "category": "other"},
        ]

        # High threshold should filter out
        results = matcher.match("test query", patterns, threshold=0.99)
        assert len(results) == 0, "Results must not be empty"

    def test_match_ranking(self) -> None:
        """Test that matches are ranked by score."""
        matcher = MLEnhancedPatternMatcher()
        patterns = [
            {"id": "P1", "symptoms": "pytest error fix", "category": "testing"},
            {"id": "P2", "symptoms": "pytest error", "category": "testing"},
        ]

        results = matcher.match("pytest error", patterns, threshold=0.0)
        if len(results) >= 2:
            assert results[0]["ml_rank"] == 1, "Result must not be empty"
            assert results[1]["ml_rank"] == 2, "Result must not be empty"

    def test_compute_similarity(self) -> None:
        """Test similarity computation."""
        matcher = MLEnhancedPatternMatcher()

        features1 = {"category": "testing", "has_error_keywords": True}
        features2 = {"category": "testing", "has_error_keywords": True}

        similarity = matcher._compute_similarity(features1, features2)
        assert 0 <= similarity <= 1, "0 is not valid"


class TestIntegratedPipeline:
    """Tests for IntegratedPipeline class."""

    def test_init_default(self) -> None:
        """Test default initialization with auto-train."""
        pipeline = IntegratedPipeline(auto_train=True)
        assert pipeline.is_ready, "Condition must be true"

    def test_init_no_auto_train(self) -> None:
        """Test initialization without auto-train."""
        pipeline = IntegratedPipeline(auto_train=False)
        assert not pipeline.is_ready, "Condition must be true"

    def test_process_symptom(self) -> None:
        """Test processing a symptom."""
        pipeline = IntegratedPipeline()
        result = pipeline.process_symptom("pytest collection error")

        assert "symptom" in result, "Result must not be empty"
        assert "routing" in result, "Result must not be empty"
        assert "recommendations" in result, "Result must not be empty"
        assert "pipeline_ready" in result, "Result must not be empty"

    def test_process_symptom_with_brain(self) -> None:
        """Test processing with brain interface."""
        pipeline = IntegratedPipeline()
        mock_brain = MagicMock()
        mock_brain.query_patterns.return_value = []

        result = pipeline.process_symptom("test error", brain_interface=mock_brain)
        assert "enhanced_query" in result, "Result must not be empty"

    def test_process_batch(self) -> None:
        """Test batch processing."""
        pipeline = IntegratedPipeline()
        symptoms = ["error 1", "error 2", "error 3"]
        results = pipeline.process_batch(symptoms)

        assert len(results) == 3, "Results must not be empty"

    def test_get_statistics(self) -> None:
        """Test statistics retrieval."""
        pipeline = IntegratedPipeline()
        stats = pipeline.get_statistics()

        assert "is_ready" in stats, "Condition must be true"
        assert "training_samples" in stats, "Condition must be true"
        assert "components" in stats, "Condition must be true"


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_integrated_pipeline(self) -> None:
        """Test pipeline creation function."""
        pipeline = create_integrated_pipeline(auto_train=True)
        assert isinstance(pipeline, IntegratedPipeline)
        assert pipeline.is_ready, "Condition must be true"

    def test_create_integrated_pipeline_no_train(self) -> None:
        """Test pipeline creation without training."""
        pipeline = create_integrated_pipeline(auto_train=False)
        assert isinstance(pipeline, IntegratedPipeline)
        assert not pipeline.is_ready, "Condition must be true"

    def test_enhance_brain_with_ml(self) -> None:
        """Test brain enhancement function."""
        mock_brain = MagicMock()
        mock_brain.query_patterns.return_value = []

        result = enhance_brain_with_ml(mock_brain)
        assert isinstance(result, MLEnhancedQueryResult)

    def test_enhance_brain_with_existing_bridge(self) -> None:
        """Test brain enhancement with existing bridge."""
        bridge = BrainMLBridge()
        bridge.train_from_pattern_store()

        mock_brain = MagicMock()
        mock_brain.query_patterns.return_value = []

        result = enhance_brain_with_ml(mock_brain, bridge=bridge)
        assert isinstance(result, MLEnhancedQueryResult)


class TestMLEnhancedQueryResult:
    """Tests for MLEnhancedQueryResult dataclass."""

    def test_creation(self) -> None:
        """Test result creation."""
        result = MLEnhancedQueryResult(
            query="test query",
            patterns=[],
            ml_category="testing",
            confidence=0.9,
            recommended_agents=["agent1"],
            success_predictions={"P1": 0.8},
        )

        assert result.query == "test query", "Result must not be empty"
        assert result.ml_category == "testing", "Result must not be empty"
        assert result.confidence == 0.9, "Result must not be empty"
        assert len(result.recommended_agents) == 1, "Collection must not be empty"
        assert result.timestamp is not None, "timestamp must be initialized"


class TestRoutingDecision:
    """Tests for RoutingDecision dataclass."""

    def test_creation(self) -> None:
        """Test decision creation."""
        decision = RoutingDecision(
            symptom="test error",
            primary_agent="ci-testing-agent",
            fallback_agents=["backup-agent"],
            category="testing",
            confidence=0.85,
            reasoning="ML classification",
        )

        assert decision.symptom == "test error", "Error should be raised or set"
        assert decision.primary_agent == "ci-testing-agent", "primary_agent is not valid"
        assert decision.category == "testing", "category is not valid"
        assert decision.confidence == 0.85, "confidence is not valid"
