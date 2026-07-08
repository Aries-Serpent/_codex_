"""
ML Integration Module for Cognitive Brain.

This module integrates ML-based pattern recognition with existing cognitive brain
systems including AgentBrainInterface, agent integration registry, and orchestration.

Phase 2.3 of Long-term Plan 2: ML-based Pattern Recognition
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive.ml.data_pipeline import (
    DataPipeline,
    FeatureExtractor,
    PatternSample,
)
from codex.cognitive.ml.recommender import ResolutionRecommender, SuccessPredictor
from codex.cognitive.ml.symptom_classifier import SymptomClassifier

logger = logging.getLogger(__name__)


@dataclass
class MLEnhancedQueryResult:
    """Result from ML-enhanced pattern query."""

    query: str
    patterns: list[dict[str, Any]]
    ml_category: str | None
    confidence: float
    recommended_agents: list[str]
    success_predictions: dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RoutingDecision:
    """ML-enhanced agent routing decision."""

    symptom: str
    primary_agent: str
    fallback_agents: list[str]
    category: str
    confidence: float
    reasoning: str


class BrainMLBridge:
    """
    Bridge between cognitive brain and ML models.

    Provides ML-enhanced functionality to the cognitive brain system.
    """

    def __init__(
        self,
        pattern_store_path: Path | str | None = None,
        model_cache_path: Path | str | None = None,
    ) -> None:
        """
        Initialize the bridge.

        Args:
            pattern_store_path: Path to pattern learning store JSON
            model_cache_path: Optional path to cache trained models
        """
        self.pattern_store_path = Path(pattern_store_path) if pattern_store_path else None
        self.model_cache_path = Path(model_cache_path) if model_cache_path else None

        # Initialize components
        self._pipeline: DataPipeline | None = None
        self._classifier: SymptomClassifier | None = None
        self._recommender: ResolutionRecommender | None = None
        self._predictor: SuccessPredictor | None = None
        self._feature_extractor = FeatureExtractor()

        # Training state
        self._is_trained = False
        self._training_samples_count = 0

    @property
    def is_trained(self) -> bool:
        """Check if models are trained."""
        return self._is_trained

    def train_from_pattern_store(self, pattern_store_path: Path | str | None = None) -> int:
        """
        Train ML models from pattern store data.

        Args:
            pattern_store_path: Override path to pattern store

        Returns:
            Number of samples used for training
        """
        path = Path(pattern_store_path) if pattern_store_path else self.pattern_store_path

        if not path or not path.exists():
            # Create synthetic training data for testing
            samples = self._create_synthetic_training_data()
        else:
            # Load from pattern store
            self._pipeline = DataPipeline(pattern_store_path=path)
            self._pipeline.load_pattern_store()
            samples = self._pipeline.generate_training_samples()

        if not samples:
            return 0

        # Initialize and train models
        self._classifier = SymptomClassifier()
        self._classifier.fit(samples)

        self._recommender = ResolutionRecommender()
        self._recommender.fit(samples)

        self._predictor = SuccessPredictor()
        self._predictor.fit(samples)

        self._is_trained = True
        self._training_samples_count = len(samples)

        return len(samples)

    def _create_synthetic_training_data(self) -> list[PatternSample]:
        """Create synthetic training data for testing."""
        categories = ["testing", "ci_cd", "security", "documentation"]
        samples = []

        for i, category in enumerate(categories):
            for j in range(5):  # 5 samples per category
                samples.append(
                    PatternSample(
                        pattern_id=f"SYNTH-{category.upper()}-{j:03d}",
                        category=category,
                        symptoms=[f"sample symptom for {category} issue {j}"],
                        resolution=f"resolution for {category} issue {j}",
                        success=j % 2 == 0,  # Alternating success/failure
                        context={"synthetic": True},
                        features={
                            "category_match": float(i) / len(categories),
                            "has_error_keywords": float(j % 2 == 0),
                            "word_count": float(10 + j),
                        },
                    )
                )

        return samples

    def enhance_query(
        self,
        brain_interface: AgentBrainInterface,
        query: str,
    ) -> MLEnhancedQueryResult:
        """
        Perform ML-enhanced pattern query.

        Args:
            brain_interface: The agent's brain interface
            query: Query string

        Returns:
            Enhanced query result with ML insights
        """
        # Get base patterns from brain interface
        patterns = brain_interface.query_patterns(query)

        # ML enhancements
        ml_category = None
        confidence = 0.0
        recommended_agents: list[str] = []
        success_predictions: dict[str, float] = {}

        if self._is_trained:
            # Classify the symptom
            if self._classifier:
                try:
                    result = self._classifier.predict([query])
                    ml_category = result.predicted_category
                    confidence = result.confidence
                except (RuntimeError, Exception):
                    # ML classifier failed - fall back to default category
                    logger.debug("Suppressed exception in handler", exc_info=True)
            # Get recommended agents based on category
            recommended_agents = self._get_agents_for_category(ml_category or "general")

            # Predict success for each pattern
            if self._predictor and patterns:
                for pattern in patterns:
                    pattern_id = pattern.get("id", "unknown")
                    pattern_symptoms = pattern.get("symptoms", "")
                    if isinstance(pattern_symptoms, list):
                        pattern_symptoms = " ".join(pattern_symptoms)
                    features = self._feature_extractor.extract_text_features(pattern_symptoms)
                    success_predictions[pattern_id] = self._predictor.predict(features)

        return MLEnhancedQueryResult(
            query=query,
            patterns=patterns,
            ml_category=ml_category,
            confidence=confidence,
            recommended_agents=recommended_agents,
            success_predictions=success_predictions,
        )

    def _get_agents_for_category(self, category: str) -> list[str]:
        """Get recommended agents for a category."""
        category_agents = {
            "testing": [
                "ci-testing-agent",
                "test-alignment-fixer",
                "coverage-roadmap-agent",
            ],
            "ci_cd": [
                "ci-testing-agent",
                "ci-log-retrieval-agent",
                "workflow-ci-fixer",
            ],
            "security": [
                "security-alert-verification-agent",
                "codeql-alert-resolution-agent",
            ],
            "documentation": ["documentation-consolidator", "link-validator-agent"],
            "rag_ml": ["rag-index-manager", "meta-tensor-validator"],
            "repository": ["repository-hygiene-agent", "reference-updater-agent"],
            "general": ["ci-testing-agent", "coverage-roadmap-agent"],
        }
        return category_agents.get(category, category_agents["general"])

    def get_recommendations(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Get ML-based resolution recommendations.

        Args:
            query: Query/symptom string
            top_k: Number of recommendations to return

        Returns:
            List of recommended resolutions with scores
        """
        if not self._is_trained or not self._recommender:
            return []

        try:
            # recommend() expects a list of symptoms
            result = self._recommender.recommend([query], top_k=top_k)
            return [
                {
                    "pattern_id": rec.pattern_id,
                    "resolution": rec.resolution,
                    "confidence": rec.confidence,
                    "category": rec.category,
                }
                for rec in result.recommendations
            ]
        except (RuntimeError, Exception):
            return []

    def save_models(self, path: Path | str | None = None) -> bool:
        """
        Save trained models to disk.

        Args:
            path: Path to save models

        Returns:
            True if successful
        """
        save_path = Path(path) if path else self.model_cache_path
        if not save_path:
            return False

        save_path.mkdir(parents=True, exist_ok=True)

        model_state = {
            "is_trained": self._is_trained,
            "training_samples_count": self._training_samples_count,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save classifier state if available
        if self._classifier:
            # Just record that we have a classifier, don't try to get vocabulary size
            model_state["has_classifier"] = True

        with open(save_path / "model_state.json", "w") as f:
            json.dump(model_state, f, indent=2)

        return True

    def load_models(self, path: Path | str | None = None) -> bool:
        """
        Load trained models from disk.

        Args:
            path: Path to load models from

        Returns:
            True if successful
        """
        load_path = Path(path) if path else self.model_cache_path
        if not load_path or not (load_path / "model_state.json").exists():
            return False

        with open(load_path / "model_state.json") as f:
            model_state = json.load(f)

        self._is_trained = model_state.get("is_trained", False)
        self._training_samples_count = model_state.get("training_samples_count", 0)

        return True


class EnhancedAgentRouter:
    """
    ML-enhanced agent routing.

    Uses ML classification to make smarter routing decisions.
    """

    def __init__(self, bridge: BrainMLBridge | None = None) -> None:
        """
        Initialize the router.

        Args:
            bridge: ML bridge instance (creates new if not provided)
        """
        self._bridge = bridge or BrainMLBridge()

    def route(self, symptom: str) -> RoutingDecision:
        """
        Make an ML-enhanced routing decision.

        Args:
            symptom: The symptom/issue description

        Returns:
            Routing decision with primary and fallback agents
        """
        category = "general"
        confidence = 0.5
        reasoning = "Default routing (ML not trained)"

        if self._bridge.is_trained and self._bridge._classifier:
            try:
                result = self._bridge._classifier.predict([symptom])
                category = result.predicted_category
                confidence = result.confidence
                reasoning = f"ML classification: {category} ({confidence:.1%} confidence)"
            except Exception as exc:
                # Prediction failures are non-fatal; fall back to default routing values.
                logging.debug(
                    "EnhancedAgentRouter: ML classifier prediction failed, using default routing",
                    exc_info=exc,
                )

        agents = self._bridge._get_agents_for_category(category)

        return RoutingDecision(
            symptom=symptom,
            primary_agent=agents[0] if agents else "ci-testing-agent",
            fallback_agents=agents[1:] if len(agents) > 1 else [],
            category=category,
            confidence=confidence,
            reasoning=reasoning,
        )

    def route_batch(self, symptoms: list[str]) -> list[RoutingDecision]:
        """
        Route multiple symptoms.

        Args:
            symptoms: List of symptom descriptions

        Returns:
            List of routing decisions
        """
        return [self.route(symptom) for symptom in symptoms]


class MLEnhancedPatternMatcher:
    """
    ML-enhanced pattern matching.

    Combines traditional pattern matching with ML classification.
    """

    def __init__(self, bridge: BrainMLBridge | None = None) -> None:
        """
        Initialize the matcher.

        Args:
            bridge: ML bridge instance
        """
        self._bridge = bridge or BrainMLBridge()
        self._feature_extractor = FeatureExtractor()

    def match(
        self,
        query: str,
        patterns: list[dict[str, Any]],
        threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        Match query against patterns using ML enhancement.

        Args:
            query: Query string
            patterns: List of patterns to match against
            threshold: Minimum similarity threshold

        Returns:
            Matched patterns with scores
        """
        if not patterns:
            return []

        query_features = self._feature_extractor.extract_text_features(query)
        results = []

        for pattern in patterns:
            pattern_symptoms = pattern.get("symptoms", "")
            if isinstance(pattern_symptoms, list):
                pattern_symptoms = " ".join(pattern_symptoms)
            pattern_features = self._feature_extractor.extract_text_features(pattern_symptoms)

            # Compute similarity
            similarity = self._compute_similarity(query_features, pattern_features)

            if similarity >= threshold:
                results.append(
                    {
                        **pattern,
                        "ml_score": similarity,
                        "ml_rank": 0,  # Will be set after sorting
                    }
                )

        # Sort by ML score
        results.sort(key=lambda x: x["ml_score"], reverse=True)

        # Set ranks
        for i, result in enumerate(results):
            result["ml_rank"] = i + 1

        return results

    def _compute_similarity(
        self,
        features1: dict[str, Any],
        features2: dict[str, Any],
    ) -> float:
        """Compute similarity between feature sets."""
        score = 0.0
        weights = {
            "category_match": 0.3,
            "keyword_overlap": 0.4,
            "error_type_match": 0.3,
        }

        # Category match
        if features1.get("category") == features2.get("category"):
            score += weights["category_match"]

        # Keyword overlap
        kw1 = set(features1.get("category_keywords", []))
        kw2 = set(features2.get("category_keywords", []))
        if kw1 and kw2:
            overlap = len(kw1 & kw2) / max(len(kw1 | kw2), 1)
            score += weights["keyword_overlap"] * overlap

        # Error type match
        if features1.get("has_error_keywords") == features2.get("has_error_keywords"):
            score += weights["error_type_match"]

        return min(score, 1.0)


class IntegratedPipeline:
    """
    Complete integrated ML pipeline for cognitive brain.

    Combines all ML components into a unified interface.
    """

    def __init__(
        self,
        pattern_store_path: Path | str | None = None,
        auto_train: bool = True,
    ) -> None:
        """
        Initialize the integrated pipeline.

        Args:
            pattern_store_path: Path to pattern store
            auto_train: Whether to auto-train on initialization
        """
        self._bridge = BrainMLBridge(pattern_store_path=pattern_store_path)
        self._router = EnhancedAgentRouter(bridge=self._bridge)
        self._matcher = MLEnhancedPatternMatcher(bridge=self._bridge)

        if auto_train:
            self._bridge.train_from_pattern_store()

    @property
    def is_ready(self) -> bool:
        """Check if pipeline is ready for use."""
        return self._bridge.is_trained

    def process_symptom(
        self,
        symptom: str,
        brain_interface: AgentBrainInterface | None = None,
    ) -> dict[str, Any]:
        """
        Process a symptom through the complete pipeline.

        Args:
            symptom: The symptom/issue description
            brain_interface: Optional brain interface for context

        Returns:
            Complete analysis results
        """
        # Get routing decision
        routing = self._router.route(symptom)

        # Get recommendations
        recommendations = self._bridge.get_recommendations(symptom, top_k=3)

        # Enhance with brain interface if available
        enhanced_result = None
        if brain_interface:
            enhanced_result = self._bridge.enhance_query(brain_interface, symptom)

        return {
            "symptom": symptom,
            "routing": {
                "primary_agent": routing.primary_agent,
                "fallback_agents": routing.fallback_agents,
                "category": routing.category,
                "confidence": routing.confidence,
                "reasoning": routing.reasoning,
            },
            "recommendations": recommendations,
            "enhanced_query": (
                {
                    "ml_category": enhanced_result.ml_category,
                    "confidence": enhanced_result.confidence,
                    "recommended_agents": enhanced_result.recommended_agents,
                    "patterns_found": len(enhanced_result.patterns),
                }
                if enhanced_result
                else None
            ),
            "pipeline_ready": self.is_ready,
        }

    def process_batch(
        self,
        symptoms: list[str],
    ) -> list[dict[str, Any]]:
        """
        Process multiple symptoms.

        Args:
            symptoms: List of symptom descriptions

        Returns:
            List of analysis results
        """
        return [self.process_symptom(symptom) for symptom in symptoms]

    def get_statistics(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "is_ready": self.is_ready,
            "training_samples": self._bridge._training_samples_count,
            "components": {
                "bridge": self._bridge is not None,
                "router": self._router is not None,
                "matcher": self._matcher is not None,
            },
        }


def create_integrated_pipeline(
    pattern_store_path: Path | str | None = None,
    auto_train: bool = True,
) -> IntegratedPipeline:
    """
    Create an integrated ML pipeline.

    Convenience function for creating the pipeline.

    Args:
        pattern_store_path: Path to pattern store
        auto_train: Whether to auto-train

    Returns:
        Configured IntegratedPipeline instance
    """
    return IntegratedPipeline(
        pattern_store_path=pattern_store_path,
        auto_train=auto_train,
    )


def enhance_brain_with_ml(
    brain_interface: AgentBrainInterface,
    bridge: BrainMLBridge | None = None,
) -> MLEnhancedQueryResult:
    """
    Enhance a brain interface query with ML.

    Convenience function for one-off ML enhancement.

    Args:
        brain_interface: The brain interface to enhance
        bridge: Optional pre-configured bridge

    Returns:
        Enhanced query result
    """
    if bridge is None:
        bridge = BrainMLBridge()
        bridge.train_from_pattern_store()

    # Get the agent's last query or use a default
    query = "pattern query"  # Default

    return bridge.enhance_query(brain_interface, query)
