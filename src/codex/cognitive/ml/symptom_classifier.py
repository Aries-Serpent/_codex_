"""Symptom Classifier for Pattern Recognition.

This module provides lightweight ML-based classification of symptoms
into pattern categories. It uses TF-IDF vectorization and simple
classifiers for offline-capable, fast inference.

Author: GitHub Copilot Coding Agent
Date: 2026-02-05
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .data_pipeline import PatternSample


class BaseClassifier(Protocol):
    """Protocol for sklearn-compatible classifiers."""

    def fit(self, X: Any, y: Any) -> Any:
        """Fit the classifier."""

    def predict(self, X: Any) -> Any:
        """Predict labels."""

    def predict_proba(self, X: Any) -> Any:
        """Predict probabilities."""


@dataclass
class ClassificationResult:
    """Result of symptom classification."""

    predicted_category: str
    confidence: float
    all_probabilities: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "predicted_category": self.predicted_category,
            "confidence": self.confidence,
            "all_probabilities": self.all_probabilities,
        }


class TfidfVectorizer:
    """Simple TF-IDF vectorizer without external dependencies.

    This is a lightweight implementation that can work offline
    without requiring scikit-learn for basic operations.
    """

    def __init__(
        self,
        max_features: int = 1000,
        min_df: int = 1,
        max_df: float = 0.95,
    ) -> None:
        """Initialize the vectorizer.

        Args:
            max_features: Maximum number of features.
            min_df: Minimum document frequency.
            max_df: Maximum document frequency (as ratio).
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df

        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._fitted = False

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words.

        Args:
            text: Input text.

        Returns:
            List of tokens.
        """
        # Simple word tokenization
        return re.findall(r"\b[a-z_][a-z0-9_]*\b", text.lower())

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Compute term frequency.

        Args:
            tokens: List of tokens.

        Returns:
            Dictionary of term frequencies.
        """
        tf: dict[str, float] = {}
        total = len(tokens)
        if total == 0:
            return tf

        for token in tokens:
            tf[token] = tf.get(token, 0) + 1

        # Normalize by document length
        for token in tf:
            tf[token] /= total

        return tf

    def fit(self, texts: list[str]) -> TfidfVectorizer:
        """Fit the vectorizer on texts.

        Args:
            texts: List of text documents.

        Returns:
            Self.
        """
        import math

        # Count document frequency for each term
        doc_freq: dict[str, int] = {}
        all_tokens: list[set[str]] = []

        for text in texts:
            tokens = set(self._tokenize(text))
            all_tokens.append(tokens)
            for token in tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        n_docs = len(texts)
        max_doc_freq = int(n_docs * self.max_df)

        # Filter by document frequency
        valid_terms = [
            term for term, freq in doc_freq.items() if self.min_df <= freq <= max_doc_freq
        ]

        # Sort by frequency and take top features
        valid_terms.sort(key=lambda t: doc_freq[t], reverse=True)
        valid_terms = valid_terms[: self.max_features]

        # Build vocabulary
        self._vocabulary = {term: idx for idx, term in enumerate(valid_terms)}

        # Compute IDF
        for term in valid_terms:
            # IDF with smoothing
            self._idf[term] = math.log((n_docs + 1) / (doc_freq[term] + 1)) + 1

        self._fitted = True
        return self

    def transform(self, texts: list[str]) -> list[list[float]]:
        """Transform texts to TF-IDF vectors.

        Args:
            texts: List of text documents.

        Returns:
            List of TF-IDF vectors.
        """
        if not self._fitted:
            raise RuntimeError("Vectorizer not fitted. Call fit() first.")

        vectors: list[list[float]] = []
        n_features = len(self._vocabulary)

        for text in texts:
            tokens = self._tokenize(text)
            tf = self._compute_tf(tokens)

            # Build vector
            vector = [0.0] * n_features
            for term, idx in self._vocabulary.items():
                if term in tf:
                    vector[idx] = tf[term] * self._idf.get(term, 1.0)

            vectors.append(vector)

        return vectors

    def fit_transform(self, texts: list[str]) -> list[list[float]]:
        """Fit and transform in one step.

        Args:
            texts: List of text documents.

        Returns:
            List of TF-IDF vectors.
        """
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> list[str]:
        """Get ordered list of feature names."""
        return [term for term, _ in sorted(self._vocabulary.items(), key=lambda x: x[1])]

    def save(self, path: str | Path) -> None:
        """Save vectorizer state."""
        with open(path, "w") as f:
            json.dump(
                {
                    "vocabulary": self._vocabulary,
                    "idf": self._idf,
                    "max_features": self.max_features,
                    "min_df": self.min_df,
                    "max_df": self.max_df,
                },
                f,
            )

    @classmethod
    def load(cls, path: str | Path) -> TfidfVectorizer:
        """Load vectorizer state."""
        with open(path) as f:
            data = json.load(f)

        vectorizer = cls(
            max_features=data["max_features"],
            min_df=data["min_df"],
            max_df=data["max_df"],
        )
        vectorizer._vocabulary = data["vocabulary"]
        vectorizer._idf = data["idf"]
        vectorizer._fitted = True
        return vectorizer


class NaiveBayesClassifier:
    """Simple Naive Bayes classifier without external dependencies.

    This is a lightweight implementation for offline-capable classification.
    """

    def __init__(self, alpha: float = 1.0) -> None:
        """Initialize the classifier.

        Args:
            alpha: Smoothing parameter.
        """
        self.alpha = alpha

        self._classes: list[str] = []
        self._class_priors: dict[str, float] = {}
        self._feature_log_probs: dict[str, list[float]] = {}
        self._n_features = 0
        self._fitted = False

    def fit(self, X: list[list[float]], y: list[str]) -> NaiveBayesClassifier:
        """Fit the classifier.

        Args:
            X: Feature matrix.
            y: Labels.

        Returns:
            Self.
        """
        import math

        self._classes = list(set(y))
        self._n_features = len(X[0]) if X else 0
        n_samples = len(y)

        # Compute class priors
        class_counts: dict[str, int] = {}
        for label in y:
            class_counts[label] = class_counts.get(label, 0) + 1

        for cls in self._classes:
            self._class_priors[cls] = math.log(class_counts.get(cls, 1) / n_samples)

        # Compute feature probabilities per class
        for cls in self._classes:
            class_samples = [X[i] for i, label in enumerate(y) if label == cls]
            if not class_samples:
                self._feature_log_probs[cls] = [0.0] * self._n_features
                continue

            # Sum features for this class
            feature_sums = [0.0] * self._n_features
            for sample in class_samples:
                for i, val in enumerate(sample):
                    feature_sums[i] += val

            # Total with smoothing
            total = sum(feature_sums) + self.alpha * self._n_features

            # Log probabilities
            self._feature_log_probs[cls] = [
                math.log((fs + self.alpha) / total) for fs in feature_sums
            ]

        self._fitted = True
        return self

    def predict(self, X: list[list[float]]) -> list[str]:
        """Predict labels.

        Args:
            X: Feature matrix.

        Returns:
            Predicted labels.
        """
        probas = self.predict_proba(X)
        predictions = []

        for proba in probas:
            best_class = max(proba, key=proba.get)  # type: ignore[arg-type]
            predictions.append(best_class)

        return predictions

    def predict_proba(self, X: list[list[float]]) -> list[dict[str, float]]:
        """Predict probabilities.

        Args:
            X: Feature matrix.

        Returns:
            List of probability dictionaries.
        """
        import math

        if not self._fitted:
            raise RuntimeError("Classifier not fitted. Call fit() first.")

        probabilities: list[dict[str, float]] = []

        for sample in X:
            log_probs: dict[str, float] = {}

            for cls in self._classes:
                log_prob = self._class_priors[cls]
                for i, val in enumerate(sample):
                    if val > 0:
                        log_prob += val * self._feature_log_probs[cls][i]
                log_probs[cls] = log_prob

            # Convert to probabilities using softmax
            max_log = max(log_probs.values())
            exp_probs = {cls: math.exp(lp - max_log) for cls, lp in log_probs.items()}
            total = sum(exp_probs.values())

            probs = {cls: ep / total for cls, ep in exp_probs.items()}
            probabilities.append(probs)

        return probabilities

    def save(self, path: str | Path) -> None:
        """Save classifier state."""
        with open(path, "w") as f:
            json.dump(
                {
                    "classes": self._classes,
                    "class_priors": self._class_priors,
                    "feature_log_probs": self._feature_log_probs,
                    "n_features": self._n_features,
                    "alpha": self.alpha,
                },
                f,
            )

    @classmethod
    def load(cls, path: str | Path) -> NaiveBayesClassifier:
        """Load classifier state."""
        with open(path) as f:
            data = json.load(f)

        classifier = cls(alpha=data["alpha"])
        classifier._classes = data["classes"]
        classifier._class_priors = data["class_priors"]
        classifier._feature_log_probs = data["feature_log_probs"]
        classifier._n_features = data["n_features"]
        classifier._fitted = True
        return classifier


class SymptomClassifier:
    """Main symptom classifier for pattern recognition.

    Uses TF-IDF vectorization and Naive Bayes classification
    to categorize symptoms into pattern categories.
    """

    def __init__(
        self,
        max_features: int = 500,
        min_df: int = 1,
    ) -> None:
        """Initialize the classifier.

        Args:
            max_features: Maximum features for vectorizer.
            min_df: Minimum document frequency.
        """
        self._vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
        )
        self._classifier = NaiveBayesClassifier()
        self._fitted = False
        self._categories: list[str] = []

    def fit(self, samples: list[PatternSample]) -> SymptomClassifier:
        """Train the classifier on samples.

        Args:
            samples: Training samples.

        Returns:
            Self.
        """
        # Prepare training data
        texts = [" ".join(s.symptoms) for s in samples]
        labels = [s.category for s in samples]

        # Fit vectorizer
        X = self._vectorizer.fit_transform(texts)

        # Fit classifier
        self._classifier.fit(X, labels)

        self._categories = list(set(labels))
        self._fitted = True
        return self

    def predict(self, symptoms: list[str]) -> ClassificationResult:
        """Classify symptoms into a category.

        Args:
            symptoms: List of symptom strings.

        Returns:
            Classification result.
        """
        if not self._fitted:
            raise RuntimeError("Classifier not fitted. Call fit() first.")

        text = " ".join(symptoms)
        X = self._vectorizer.transform([text])

        predictions = self._classifier.predict(X)
        probas = self._classifier.predict_proba(X)

        return ClassificationResult(
            predicted_category=predictions[0],
            confidence=max(probas[0].values()),
            all_probabilities=probas[0],
        )

    def predict_batch(self, symptoms_list: list[list[str]]) -> list[ClassificationResult]:
        """Classify multiple symptom sets.

        Args:
            symptoms_list: List of symptom lists.

        Returns:
            List of classification results.
        """
        if not self._fitted:
            raise RuntimeError("Classifier not fitted. Call fit() first.")

        texts = [" ".join(symptoms) for symptoms in symptoms_list]
        X = self._vectorizer.transform(texts)

        predictions = self._classifier.predict(X)
        probas = self._classifier.predict_proba(X)

        results = []
        for pred, proba in zip(predictions, probas, strict=False):
            results.append(
                ClassificationResult(
                    predicted_category=pred,
                    confidence=max(proba.values()),
                    all_probabilities=proba,
                )
            )

        return results

    def get_categories(self) -> list[str]:
        """Get list of known categories."""
        return self._categories.copy()

    def save(self, directory: str | Path) -> None:
        """Save classifier to directory.

        Args:
            directory: Directory to save model files.
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        self._vectorizer.save(dir_path / "vectorizer.json")
        self._classifier.save(dir_path / "classifier.json")

        # Save metadata
        with open(dir_path / "metadata.json", "w") as f:
            json.dump(
                {
                    "categories": self._categories,
                    "fitted": self._fitted,
                },
                f,
            )

    @classmethod
    def load(cls, directory: str | Path) -> SymptomClassifier:
        """Load classifier from directory.

        Args:
            directory: Directory containing model files.

        Returns:
            Loaded classifier.
        """
        dir_path = Path(directory)

        classifier = cls()
        classifier._vectorizer = TfidfVectorizer.load(dir_path / "vectorizer.json")
        classifier._classifier = NaiveBayesClassifier.load(dir_path / "classifier.json")

        with open(dir_path / "metadata.json") as f:
            metadata = json.load(f)

        classifier._categories = metadata["categories"]
        classifier._fitted = metadata["fitted"]

        return classifier

    def evaluate(
        self,
        samples: list[PatternSample],
    ) -> dict[str, Any]:
        """Evaluate classifier on test samples.

        Args:
            samples: Test samples.

        Returns:
            Evaluation metrics.
        """
        if not self._fitted:
            raise RuntimeError("Classifier not fitted. Call fit() first.")

        correct = 0
        total = len(samples)
        category_metrics: dict[str, dict[str, int]] = {}

        # Initialize metrics per category
        for cat in self._categories:
            category_metrics[cat] = {"tp": 0, "fp": 0, "fn": 0}

        for sample in samples:
            result = self.predict(sample.symptoms)
            predicted = result.predicted_category
            actual = sample.category

            if predicted == actual:
                correct += 1
                if actual in category_metrics:
                    category_metrics[actual]["tp"] += 1
            else:
                if predicted in category_metrics:
                    category_metrics[predicted]["fp"] += 1
                if actual in category_metrics:
                    category_metrics[actual]["fn"] += 1

        # Compute per-category precision/recall
        category_scores: dict[str, dict[str, float]] = {}
        for cat, metrics in category_metrics.items():
            tp = metrics["tp"]
            fp = metrics["fp"]
            fn = metrics["fn"]

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            category_scores[cat] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

        return {
            "accuracy": correct / total if total > 0 else 0.0,
            "total_samples": total,
            "correct": correct,
            "category_scores": category_scores,
        }
