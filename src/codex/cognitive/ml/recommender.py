"""Resolution Recommender for Pattern Recognition.

This module provides recommendation of resolutions based on symptoms
using similarity-based retrieval and ranking.

Author: GitHub Copilot Coding Agent
Date: 2026-02-05
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .data_pipeline import FeatureExtractor, PatternSample


@dataclass
class Recommendation:
    """A recommended resolution with confidence score."""

    resolution: str
    confidence: float
    pattern_id: str
    category: str
    supporting_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resolution": self.resolution,
            "confidence": self.confidence,
            "pattern_id": self.pattern_id,
            "category": self.category,
            "supporting_evidence": self.supporting_evidence,
        }


@dataclass
class RecommendationResult:
    """Result of a recommendation request."""

    query_symptoms: list[str]
    recommendations: list[Recommendation]
    matched_patterns: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_symptoms": self.query_symptoms,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "matched_patterns": self.matched_patterns,
        }

    def top_recommendation(self) -> Recommendation | None:
        """Get the top recommendation."""
        return self.recommendations[0] if self.recommendations else None


class CosineSimilarity:
    """Compute cosine similarity between vectors."""

    @staticmethod
    def compute(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            Cosine similarity score between -1 and 1.
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class JaccardSimilarity:
    """Compute Jaccard similarity between sets."""

    @staticmethod
    def compute(set1: set[str], set2: set[str]) -> float:
        """Compute Jaccard similarity between two sets.

        Args:
            set1: First set.
            set2: Second set.

        Returns:
            Jaccard similarity score between 0 and 1.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0


class ResolutionIndex:
    """Index of resolutions for fast retrieval."""

    def __init__(self) -> None:
        """Initialize the index."""
        self._samples: list[PatternSample] = []
        self._symptom_tokens: list[set[str]] = []
        self._category_index: dict[str, list[int]] = {}
        self._pattern_index: dict[str, list[int]] = {}
        self._feature_extractor = FeatureExtractor()

    def _tokenize(self, text: str) -> set[str]:
        """Tokenize text into word set."""
        import re

        words = re.findall(r"\b[a-z_][a-z0-9_]*\b", text.lower())
        return set(words)

    def add(self, sample: PatternSample) -> None:
        """Add a sample to the index.

        Args:
            sample: Pattern sample to add.
        """
        idx = len(self._samples)
        self._samples.append(sample)

        # Index symptom tokens
        symptoms_text = " ".join(sample.symptoms)
        tokens = self._tokenize(symptoms_text)
        self._symptom_tokens.append(tokens)

        # Index by category
        if sample.category not in self._category_index:
            self._category_index[sample.category] = []
        self._category_index[sample.category].append(idx)

        # Index by pattern
        if sample.pattern_id not in self._pattern_index:
            self._pattern_index[sample.pattern_id] = []
        self._pattern_index[sample.pattern_id].append(idx)

    def build(self, samples: list[PatternSample]) -> None:
        """Build the index from samples.

        Args:
            samples: List of pattern samples.
        """
        self._samples = []
        self._symptom_tokens = []
        self._category_index = {}
        self._pattern_index = {}

        for sample in samples:
            self.add(sample)

    def search(
        self,
        symptoms: list[str],
        category: str | None = None,
        top_k: int = 5,
    ) -> list[tuple[PatternSample, float]]:
        """Search for similar samples.

        Args:
            symptoms: Query symptoms.
            category: Optional category filter.
            top_k: Number of results to return.

        Returns:
            List of (sample, similarity_score) tuples.
        """
        query_tokens = self._tokenize(" ".join(symptoms))

        # Determine candidates
        if category and category in self._category_index:
            candidates = self._category_index[category]
        else:
            candidates = list(range(len(self._samples)))

        # Compute similarities
        results: list[tuple[int, float]] = []
        for idx in candidates:
            sample_tokens = self._symptom_tokens[idx]
            similarity = JaccardSimilarity.compute(query_tokens, sample_tokens)
            results.append((idx, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top k
        return [(self._samples[idx], score) for idx, score in results[:top_k] if score > 0]

    def get_by_pattern(self, pattern_id: str) -> list[PatternSample]:
        """Get all samples for a pattern.

        Args:
            pattern_id: Pattern ID to lookup.

        Returns:
            List of samples for the pattern.
        """
        if pattern_id not in self._pattern_index:
            return []
        return [self._samples[idx] for idx in self._pattern_index[pattern_id]]

    def get_categories(self) -> list[str]:
        """Get all categories in the index."""
        return list(self._category_index.keys())

    def size(self) -> int:
        """Get number of indexed samples."""
        return len(self._samples)

    def save(self, path: str | Path) -> None:
        """Save index to file.

        Args:
            path: Path to save to.
        """
        data = {
            "samples": [s.to_dict() for s in self._samples],
            "symptom_tokens": [list(t) for t in self._symptom_tokens],
            "category_index": self._category_index,
            "pattern_index": self._pattern_index,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> ResolutionIndex:
        """Load index from file.

        Args:
            path: Path to load from.

        Returns:
            Loaded index.
        """
        with open(path) as f:
            data = json.load(f)

        index = cls()
        index._samples = [PatternSample.from_dict(s) for s in data["samples"]]
        index._symptom_tokens = [set(t) for t in data["symptom_tokens"]]
        index._category_index = data["category_index"]
        index._pattern_index = data["pattern_index"]

        return index


class ResolutionRecommender:
    """Main recommender for resolution suggestions.

    Uses symptom similarity matching and success rate weighting
    to recommend the best resolutions for given symptoms.
    """

    def __init__(
        self,
        success_weight: float = 0.3,
        similarity_weight: float = 0.7,
    ) -> None:
        """Initialize the recommender.

        Args:
            success_weight: Weight for success rate in scoring.
            similarity_weight: Weight for similarity in scoring.
        """
        self._success_weight = success_weight
        self._similarity_weight = similarity_weight
        self._index = ResolutionIndex()
        self._fitted = False

    def fit(self, samples: list[PatternSample]) -> ResolutionRecommender:
        """Train the recommender on samples.

        Args:
            samples: Training samples.

        Returns:
            Self.
        """
        self._index.build(samples)
        self._fitted = True
        return self

    def recommend(
        self,
        symptoms: list[str],
        category: str | None = None,
        top_k: int = 5,
        min_confidence: float = 0.1,
    ) -> RecommendationResult:
        """Recommend resolutions for symptoms.

        Args:
            symptoms: Query symptoms.
            category: Optional category filter.
            top_k: Maximum recommendations to return.
            min_confidence: Minimum confidence threshold.

        Returns:
            Recommendation result.
        """
        if not self._fitted:
            raise RuntimeError("Recommender not fitted. Call fit() first.")

        # Search for similar patterns
        matches = self._index.search(symptoms, category=category, top_k=top_k * 2)

        # Build recommendations
        recommendations: list[Recommendation] = []
        seen_resolutions: set[str] = set()

        for sample, similarity in matches:
            # Compute score
            success_score = sample.features.get("success_rate", 0.5)
            score = self._similarity_weight * similarity + self._success_weight * success_score

            if score < min_confidence:
                continue

            # Skip duplicate resolutions
            if sample.resolution in seen_resolutions:
                continue
            seen_resolutions.add(sample.resolution)

            recommendations.append(
                Recommendation(
                    resolution=sample.resolution,
                    confidence=score,
                    pattern_id=sample.pattern_id,
                    category=sample.category,
                    supporting_evidence=sample.symptoms[:3],  # Include top symptoms
                )
            )

        # Sort by confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        return RecommendationResult(
            query_symptoms=symptoms,
            recommendations=recommendations[:top_k],
            matched_patterns=len(matches),
        )

    def recommend_from_text(
        self,
        text: str,
        category: str | None = None,
        top_k: int = 5,
    ) -> RecommendationResult:
        """Recommend resolutions from free-form text.

        Args:
            text: Text containing symptoms/error description.
            category: Optional category filter.
            top_k: Maximum recommendations to return.

        Returns:
            Recommendation result.
        """
        # Extract symptom-like phrases from text
        import re

        # Split on common separators
        symptoms = re.split(r"[,;.\n]", text)
        symptoms = [s.strip() for s in symptoms if s.strip()]

        return self.recommend(symptoms, category=category, top_k=top_k)

    def get_resolutions_for_pattern(self, pattern_id: str) -> list[str]:
        """Get all resolutions for a pattern.

        Args:
            pattern_id: Pattern ID.

        Returns:
            List of resolutions.
        """
        samples = self._index.get_by_pattern(pattern_id)
        return list({s.resolution for s in samples})

    def get_categories(self) -> list[str]:
        """Get available categories."""
        return self._index.get_categories()

    def save(self, directory: str | Path) -> None:
        """Save recommender to directory.

        Args:
            directory: Directory to save to.
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        self._index.save(dir_path / "index.json")

        with open(dir_path / "config.json", "w") as f:
            json.dump(
                {
                    "success_weight": self._success_weight,
                    "similarity_weight": self._similarity_weight,
                    "fitted": self._fitted,
                },
                f,
            )

    @classmethod
    def load(cls, directory: str | Path) -> ResolutionRecommender:
        """Load recommender from directory.

        Args:
            directory: Directory to load from.

        Returns:
            Loaded recommender.
        """
        dir_path = Path(directory)

        with open(dir_path / "config.json") as f:
            config = json.load(f)

        recommender = cls(
            success_weight=config["success_weight"],
            similarity_weight=config["similarity_weight"],
        )
        recommender._index = ResolutionIndex.load(dir_path / "index.json")
        recommender._fitted = config["fitted"]

        return recommender

    def evaluate(
        self,
        samples: list[PatternSample],
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Evaluate recommender on test samples.

        Args:
            samples: Test samples.
            top_k: Number of recommendations to consider.

        Returns:
            Evaluation metrics.
        """
        if not self._fitted:
            raise RuntimeError("Recommender not fitted. Call fit() first.")

        hits_at_1 = 0
        hits_at_k = 0
        total = 0

        for sample in samples:
            result = self.recommend(sample.symptoms, top_k=top_k)

            # Check if correct resolution is in top recommendations
            recommended_resolutions = [r.resolution for r in result.recommendations]

            if sample.resolution in recommended_resolutions:
                hits_at_k += 1
                if (
                    result.recommendations
                    and result.recommendations[0].resolution == sample.resolution
                ):
                    hits_at_1 += 1

            total += 1

        return {
            "hit_rate_at_1": hits_at_1 / total if total > 0 else 0.0,
            f"hit_rate_at_{top_k}": hits_at_k / total if total > 0 else 0.0,
            "total_samples": total,
            "mean_recommendations": (
                sum(len(self.recommend(s.symptoms).recommendations) for s in samples) / total
                if total > 0
                else 0.0
            ),
        }


class SuccessPredictor:
    """Predict success probability for a resolution.

    Uses logistic regression-like scoring based on features.
    """

    def __init__(self) -> None:
        """Initialize the predictor."""
        self._weights: dict[str, float] = {}
        self._bias: float = 0.0
        self._fitted = False

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function."""
        if x < -500:
            return 0.0
        if x > 500:
            return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    def fit(
        self,
        samples: list[PatternSample],
        learning_rate: float = 0.01,
        epochs: int = 100,
    ) -> SuccessPredictor:
        """Train the predictor.

        Args:
            samples: Training samples.
            learning_rate: Learning rate for gradient descent.
            epochs: Number of training epochs.

        Returns:
            Self.
        """
        if not samples:
            self._fitted = True
            return self

        # Collect all feature names
        all_features: set[str] = set()
        for sample in samples:
            all_features.update(sample.features.keys())

        # Initialize weights
        self._weights = dict.fromkeys(all_features, 0.0)
        self._bias = 0.0

        # Training loop (simple gradient descent)
        for _ in range(epochs):
            for sample in samples:
                # Forward pass
                z = self._bias
                for f, w in self._weights.items():
                    z += w * sample.features.get(f, 0.0)

                pred = self._sigmoid(z)
                target = 1.0 if sample.success else 0.0
                error = pred - target

                # Backward pass
                self._bias -= learning_rate * error
                for f in self._weights:
                    self._weights[f] -= learning_rate * error * sample.features.get(f, 0.0)

        self._fitted = True
        return self

    def predict(self, features: dict[str, float]) -> float:
        """Predict success probability.

        Args:
            features: Feature dictionary.

        Returns:
            Success probability between 0 and 1.
        """
        if not self._fitted:
            raise RuntimeError("Predictor not fitted. Call fit() first.")

        z = self._bias
        for f, w in self._weights.items():
            z += w * features.get(f, 0.0)

        return self._sigmoid(z)

    def predict_sample(self, sample: PatternSample) -> float:
        """Predict success probability for a sample.

        Args:
            sample: Pattern sample.

        Returns:
            Success probability.
        """
        return self.predict(sample.features)

    def save(self, path: str | Path) -> None:
        """Save predictor to file."""
        with open(path, "w") as f:
            json.dump(
                {
                    "weights": self._weights,
                    "bias": self._bias,
                    "fitted": self._fitted,
                },
                f,
            )

    @classmethod
    def load(cls, path: str | Path) -> SuccessPredictor:
        """Load predictor from file."""
        with open(path) as f:
            data = json.load(f)

        predictor = cls()
        predictor._weights = data["weights"]
        predictor._bias = data["bias"]
        predictor._fitted = data["fitted"]

        return predictor

    def evaluate(self, samples: list[PatternSample], threshold: float = 0.5) -> dict[str, Any]:
        """Evaluate predictor on test samples.

        Args:
            samples: Test samples.
            threshold: Decision threshold.

        Returns:
            Evaluation metrics.
        """
        if not self._fitted:
            raise RuntimeError("Predictor not fitted. Call fit() first.")

        tp = fp = tn = fn = 0

        for sample in samples:
            pred = self.predict_sample(sample) >= threshold
            actual = sample.success

            if pred and actual:
                tp += 1
            elif pred and not actual:
                fp += 1
            elif not pred and actual:
                fn += 1
            else:
                tn += 1

        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        }
