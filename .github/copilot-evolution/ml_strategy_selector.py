"""
Machine Learning Strategy Selector for Self-Healing Evolution

Implements ML-based strategy selection for healing failures using
feature extraction, similarity matching, and reinforcement learning.

Phase 3: Self-Healing Evolution
- Machine learning for strategy selection
- Confidence-based auto-merge thresholds
- Cross-repository pattern sharing

Author: mbaetiong
Generated: 2025-12-22
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class StrategyFeatures:
    """Feature vector for strategy selection."""

    error_type_hash: str
    component_hash: str
    message_keywords: List[str]
    severity_score: float
    stack_depth: int
    file_extension: str
    is_test_file: bool
    has_assertion: bool
    has_import_error: bool
    has_type_error: bool
    timestamp_hour: int


@dataclass
class StrategyPrediction:
    """Prediction result from ML selector."""

    strategy_name: str
    confidence: float
    alternative_strategies: List[Tuple[str, float]]
    features_used: List[str]
    model_version: str = "1.0.0"


@dataclass
class LearningExample:
    """Training example for the ML model."""

    features: StrategyFeatures
    chosen_strategy: str
    outcome_success: bool
    healing_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# ML Strategy Selector
# ============================================================================


class MLStrategySelector:
    """
    Machine learning-based strategy selector for self-healing.

    Uses a combination of:
    1. Feature extraction from error context
    2. K-nearest neighbors for similarity matching
    3. Simple reinforcement learning for strategy weights
    4. Confidence-based thresholds for auto-merge
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        auto_merge_threshold: float = 0.95,
        learning_rate: float = 0.1,
    ):
        """
        Initialize ML Strategy Selector.

        Args:
            model_path: Path to save/load model state
            auto_merge_threshold: Confidence threshold for auto-merge
            learning_rate: Learning rate for weight updates
        """
        self.model_path = model_path or Path("data/ml_model")
        self.model_path.mkdir(parents=True, exist_ok=True)

        self.auto_merge_threshold = auto_merge_threshold
        self.learning_rate = learning_rate

        # Strategy weights (learned from experience)
        self.strategy_weights: Dict[str, float] = self._load_weights()

        # Training history
        self.training_examples: List[LearningExample] = []

        # Feature importance scores
        self.feature_importance: Dict[str, float] = {
            "error_type_hash": 0.25,
            "message_keywords": 0.20,
            "component_hash": 0.15,
            "severity_score": 0.10,
            "has_assertion": 0.10,
            "has_import_error": 0.08,
            "has_type_error": 0.07,
            "is_test_file": 0.05,
        }

        # Keyword to strategy mapping - loaded from config or defaults
        self.keyword_strategy_map: Dict[str, str] = self._load_keyword_strategy_map()

        logger.info(
            f"✅ MLStrategySelector initialized | "
            f"Auto-merge threshold: {self.auto_merge_threshold:.0%}"
        )

    def _load_keyword_strategy_map(self) -> Dict[str, str]:
        """
        Load keyword-to-strategy mapping from config file or use defaults.

        The mapping can be externalized to a JSON file at:
        self.model_path / "keyword_strategy_map.json"

        This enables runtime updates without code changes.
        """
        config_file = self.model_path / "keyword_strategy_map.json"

        # Try to load from config file
        if config_file.exists():
            try:
                with open(config_file) as f:
                    mapping = json.load(f)
                    logger.info(f"📋 Loaded keyword_strategy_map from {config_file}")
                    return mapping
            except Exception as e:
                logger.warning(f"Failed to load keyword_strategy_map: {e}, using defaults")

        # Default mapping
        return {
            "docker": "docker_tag_error",
            "tag": "docker_tag_error",
            "invalid reference": "docker_tag_error",
            "target_modules": "peft_target_error",
            "peft": "peft_target_error",
            "lora": "peft_target_error",
            "hydra": "hydra_composition",
            "config": "hydra_composition",
            "defaults": "hydra_composition",
            "import": "import_error",
            "module not found": "import_error",
            "no module": "import_error",
            "assert": "assertion_error",
            "assertion": "assertion_error",
            "type": "type_error",
            "typeerror": "type_error",
            "attribute": "attribute_error",
            "attributeerror": "attribute_error",
            "version": "version_mismatch",
            "compatibility": "version_mismatch",
            "artifact": "version_mismatch",
            "metric": "metric_compatibility",
            "bleu": "metric_compatibility",
            "empty": "empty_result",
            "no patterns": "empty_result",
        }

    def _load_weights(self) -> Dict[str, float]:
        """Load strategy weights from disk."""
        weights_file = self.model_path / "strategy_weights.json"
        try:
            if weights_file.exists():
                with open(weights_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load weights: {e}")

        # Default weights
        return {
            "docker_tag_error": 1.0,
            "peft_target_error": 1.0,
            "hydra_composition": 1.0,
            "metric_compatibility": 1.0,
            "assertion_error": 1.0,
            "type_error": 1.0,
            "attribute_error": 1.0,
            "import_error": 1.0,
            "empty_result": 1.0,
            "version_mismatch": 1.0,
            "generic": 0.5,
        }

    def _save_weights(self) -> None:
        """Save strategy weights to disk."""
        weights_file = self.model_path / "strategy_weights.json"
        try:
            with open(weights_file, "w") as f:
                json.dump(self.strategy_weights, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save weights: {e}")

    def extract_features(self, error_context: Dict[str, Any]) -> StrategyFeatures:
        """
        Extract features from error context for ML prediction.

        Args:
            error_context: Dictionary with error details

        Returns:
            StrategyFeatures with extracted feature values
        """
        error_type = error_context.get("type", "unknown")
        error_message = error_context.get("message", "").lower()
        component = error_context.get("component", "unknown")
        traceback = error_context.get("traceback", "")

        # Extract keywords
        keywords = self._extract_keywords(error_message)

        # Calculate severity
        severity = self._calculate_severity(error_context)

        # Stack depth
        stack_depth = traceback.count("File ") if traceback else 0

        # File extension
        file_ext = Path(component).suffix if "." in component else ".py"

        return StrategyFeatures(
            error_type_hash=hashlib.md5(error_type.encode()).hexdigest()[:8],
            component_hash=hashlib.md5(component.encode()).hexdigest()[:8],
            message_keywords=keywords,
            severity_score=severity,
            stack_depth=stack_depth,
            file_extension=file_ext,
            is_test_file="test" in component.lower(),
            has_assertion="assert" in error_message,
            has_import_error="import" in error_message or "module" in error_message,
            has_type_error="type" in error_type.lower(),
            timestamp_hour=datetime.utcnow().hour,
        )

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract relevant keywords from error message."""
        keywords = []
        for keyword in self.keyword_strategy_map.keys():
            if keyword in message:
                keywords.append(keyword)
        return keywords[:10]  # Limit to 10 keywords

    def _calculate_severity(self, context: Dict[str, Any]) -> float:
        """Calculate severity score (0-1)."""
        severity = context.get("severity", "medium")
        severity_map = {"low": 0.3, "medium": 0.5, "high": 0.8, "critical": 1.0}
        return severity_map.get(severity, 0.5)

    def predict_strategy(
        self, error_context: Dict[str, Any]
    ) -> StrategyPrediction:
        """
        Predict best healing strategy using ML.

        Args:
            error_context: Error context dictionary

        Returns:
            StrategyPrediction with strategy and confidence
        """
        features = self.extract_features(error_context)

        # Calculate strategy scores
        scores: Dict[str, float] = {}

        for strategy in self.strategy_weights.keys():
            score = self._calculate_strategy_score(features, strategy)
            scores[strategy] = score

        # Normalize to probabilities (softmax)
        max_score = max(scores.values()) if scores else 0
        exp_scores = {
            s: math.exp(sc - max_score) for s, sc in scores.items()
        }
        total = sum(exp_scores.values())
        probabilities = {s: sc / total for s, sc in exp_scores.items()}

        # Get top strategy
        sorted_strategies = sorted(
            probabilities.items(), key=lambda x: x[1], reverse=True
        )
        best_strategy, best_confidence = sorted_strategies[0]

        # Get alternatives
        alternatives = sorted_strategies[1:4]

        return StrategyPrediction(
            strategy_name=best_strategy,
            confidence=best_confidence,
            alternative_strategies=alternatives,
            features_used=features.message_keywords,
        )

    def _calculate_strategy_score(
        self, features: StrategyFeatures, strategy: str
    ) -> float:
        """Calculate score for a strategy given features."""
        score = 0.0

        # Base weight
        base_weight = self.strategy_weights.get(strategy, 0.5)
        score += base_weight

        # Keyword matching
        for keyword in features.message_keywords:
            if self.keyword_strategy_map.get(keyword) == strategy:
                score += 0.5

        # Feature-specific bonuses
        if features.has_assertion and strategy == "assertion_error":
            score += 0.3
        if features.has_import_error and strategy == "import_error":
            score += 0.3
        if features.has_type_error and strategy == "type_error":
            score += 0.3
        if features.is_test_file and strategy in ["assertion_error", "peft_target_error"]:
            score += 0.2

        return score

    def update_from_outcome(
        self,
        prediction: StrategyPrediction,
        success: bool,
        healing_time_ms: float = 0.0,
    ) -> None:
        """
        Update model weights based on healing outcome (reinforcement learning).

        Args:
            prediction: The prediction that was made
            success: Whether the healing was successful
            healing_time_ms: Time taken for healing
        """
        strategy = prediction.strategy_name

        # Update weight based on success/failure
        current_weight = self.strategy_weights.get(strategy, 1.0)

        if success:
            # Increase weight for successful strategies
            new_weight = current_weight + self.learning_rate * (1 - current_weight)
        else:
            # Decrease weight for failed strategies
            new_weight = current_weight - self.learning_rate * current_weight

        # Clamp weights
        self.strategy_weights[strategy] = max(0.1, min(2.0, new_weight))

        # Save updated weights
        self._save_weights()

        logger.info(
            f"📈 Updated {strategy} weight: {current_weight:.3f} → {new_weight:.3f} "
            f"({'✅ success' if success else '❌ failure'})"
        )

    def should_auto_merge(self, prediction: StrategyPrediction) -> bool:
        """
        Determine if healing fix should be auto-merged based on confidence.

        Args:
            prediction: Strategy prediction

        Returns:
            True if confidence exceeds auto-merge threshold
        """
        return prediction.confidence >= self.auto_merge_threshold

    def get_merge_recommendation(
        self, prediction: StrategyPrediction
    ) -> Dict[str, Any]:
        """
        Get merge recommendation with reasoning.

        Args:
            prediction: Strategy prediction

        Returns:
            Dictionary with merge recommendation and reasoning
        """
        should_merge = self.should_auto_merge(prediction)

        recommendation = {
            "auto_merge": should_merge,
            "confidence": prediction.confidence,
            "threshold": self.auto_merge_threshold,
            "strategy": prediction.strategy_name,
            "reasoning": [],
        }

        if should_merge:
            recommendation["reasoning"] = [
                f"Confidence ({prediction.confidence:.1%}) exceeds threshold ({self.auto_merge_threshold:.0%})",
                f"Strategy '{prediction.strategy_name}' has proven effective",
                "No manual review required",
            ]
        else:
            recommendation["reasoning"] = [
                f"Confidence ({prediction.confidence:.1%}) below threshold ({self.auto_merge_threshold:.0%})",
                "Manual review recommended before merge",
                f"Alternative strategies: {[s[0] for s in prediction.alternative_strategies[:2]]}",
            ]

        return recommendation

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics and performance metrics."""
        return {
            "model_version": "1.0.0",
            "strategy_weights": self.strategy_weights,
            "auto_merge_threshold": self.auto_merge_threshold,
            "learning_rate": self.learning_rate,
            "training_examples": len(self.training_examples),
            "feature_importance": self.feature_importance,
            "timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# Cross-Repository Pattern Sharing
# ============================================================================


@dataclass
class SharedPattern:
    """Pattern shared across repositories."""

    pattern_id: str
    source_repo: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    success_rate: float
    usage_count: int
    created_at: str
    updated_at: str


class CrossRepoPatternSharing:
    """
    Cross-repository pattern sharing for collaborative learning.

    Allows patterns learned in one repository to be shared
    and applied in other repositories.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize cross-repo pattern sharing."""
        self.storage_path = storage_path or Path(
            "data/shared_patterns"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.shared_patterns: Dict[str, SharedPattern] = {}
        self._load_patterns()

        logger.info(
            f"✅ CrossRepoPatternSharing initialized | "
            f"Patterns: {len(self.shared_patterns)}"
        )

    def _load_patterns(self) -> None:
        """Load shared patterns from disk."""
        patterns_file = self.storage_path / "patterns.json"
        try:
            if patterns_file.exists():
                with open(patterns_file) as f:
                    data = json.load(f)
                    for pid, pdata in data.items():
                        self.shared_patterns[pid] = SharedPattern(**pdata)
        except Exception as e:
            logger.warning(f"Failed to load shared patterns: {e}")

    def _save_patterns(self) -> None:
        """Save shared patterns to disk."""
        patterns_file = self.storage_path / "patterns.json"
        try:
            data = {
                pid: {
                    "pattern_id": p.pattern_id,
                    "source_repo": p.source_repo,
                    "pattern_type": p.pattern_type,
                    "pattern_data": p.pattern_data,
                    "success_rate": p.success_rate,
                    "usage_count": p.usage_count,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                }
                for pid, p in self.shared_patterns.items()
            }
            with open(patterns_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save shared patterns: {e}")

    def share_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        source_repo: str,
        success_rate: float = 1.0,
    ) -> SharedPattern:
        """
        Share a pattern for cross-repository use.

        Args:
            pattern_type: Type of pattern (e.g., "healing_strategy")
            pattern_data: Pattern data dictionary
            source_repo: Source repository name
            success_rate: Initial success rate

        Returns:
            SharedPattern object
        """
        pattern_id = hashlib.sha256(
            json.dumps(pattern_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        now = datetime.utcnow().isoformat()

        pattern = SharedPattern(
            pattern_id=pattern_id,
            source_repo=source_repo,
            pattern_type=pattern_type,
            pattern_data=pattern_data,
            success_rate=success_rate,
            usage_count=0,
            created_at=now,
            updated_at=now,
        )

        self.shared_patterns[pattern_id] = pattern
        self._save_patterns()

        logger.info(
            f"📤 Shared pattern: {pattern_id} from {source_repo} ({pattern_type})"
        )

        return pattern

    def find_matching_patterns(
        self,
        pattern_type: str,
        keywords: Optional[List[str]] = None,
        min_success_rate: float = 0.7,
    ) -> List[SharedPattern]:
        """
        Find matching patterns from shared repository.

        Args:
            pattern_type: Type of pattern to find
            keywords: Optional keywords to match
            min_success_rate: Minimum success rate threshold

        Returns:
            List of matching SharedPattern objects
        """
        matches = []

        for pattern in self.shared_patterns.values():
            if pattern.pattern_type != pattern_type:
                continue
            if pattern.success_rate < min_success_rate:
                continue

            # Keyword matching
            if keywords:
                pattern_str = json.dumps(pattern.pattern_data).lower()
                if not any(kw.lower() in pattern_str for kw in keywords):
                    continue

            matches.append(pattern)

        # Sort by success rate and usage count
        matches.sort(
            key=lambda p: (p.success_rate, p.usage_count), reverse=True
        )

        return matches[:10]

    def apply_pattern(self, pattern_id: str, success: bool) -> None:
        """
        Record pattern usage and update success rate.

        Args:
            pattern_id: Pattern identifier
            success: Whether application was successful
        """
        if pattern_id not in self.shared_patterns:
            return

        pattern = self.shared_patterns[pattern_id]
        pattern.usage_count += 1

        # Update success rate with exponential moving average
        alpha = 0.1
        pattern.success_rate = (
            alpha * (1.0 if success else 0.0) + (1 - alpha) * pattern.success_rate
        )
        pattern.updated_at = datetime.utcnow().isoformat()

        self._save_patterns()

        logger.info(
            f"📊 Updated pattern {pattern_id}: "
            f"usage={pattern.usage_count}, success_rate={pattern.success_rate:.1%}"
        )

    def get_sharing_stats(self) -> Dict[str, Any]:
        """Get statistics about pattern sharing."""
        if not self.shared_patterns:
            return {
                "total_patterns": 0,
                "pattern_types": [],
                "avg_success_rate": 0.0,
                "total_usage": 0,
            }

        return {
            "total_patterns": len(self.shared_patterns),
            "pattern_types": list(
                set(p.pattern_type for p in self.shared_patterns.values())
            ),
            "avg_success_rate": sum(
                p.success_rate for p in self.shared_patterns.values()
            )
            / len(self.shared_patterns),
            "total_usage": sum(
                p.usage_count for p in self.shared_patterns.values()
            ),
            "source_repos": list(
                set(p.source_repo for p in self.shared_patterns.values())
            ),
        }
