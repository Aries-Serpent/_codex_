#!/usr/bin/env python3
"""
ML-based language predictor for code fences.

This module provides an optional ML classifier for detecting code fence languages.
Disabled by default - heuristic + parse path remains primary.

When enabled, uses character n-gram features with a linear classifier.
"""

import pickle
import warnings
from pathlib import Path
from typing import Optional


class LanguageClassifier:
    """ML-based language classifier using character n-grams."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the classifier.

        Args:
            model_path: Path to pickled model file. If None, classifier is disabled.
        """
        self.model = None
        self.vectorizer = None

        if model_path and Path(model_path).exists():
            try:
                # Use safe pickle loading to prevent code execution vulnerabilities
                from utils.safe_pickle import safe_pickle_load

                data = safe_pickle_load(
                    model_path,
                    use_restricted_unpickler=True  # Enable class whitelisting
                )
                self.model = data.get("model")
                self.vectorizer = data.get("vectorizer")
            except Exception as e:
                warnings.warn(f"Failed to load ML model: {e}")

    def predict(self, code: str, filename: Optional[str] = None) -> tuple[str, float]:
        """
        Predict language label and confidence.

        Args:
            code: Code snippet to classify
            filename: Optional filename for context

        Returns:
            Tuple of (language_label, confidence_score)
            Returns ("text", 0.0) if model is not available.
        """
        if not self.model or not self.vectorizer:
            return ("text", 0.0)

        try:
            # Extract features
            features = self.vectorizer.transform([code])

            # Get prediction probabilities
            probas = self.model.predict_proba(features)[0]

            # Get best prediction
            best_idx = probas.argmax()
            label = self.model.classes_[best_idx]
            confidence = probas[best_idx]

            return (label, float(confidence))

        except Exception as e:
            warnings.warn(f"ML prediction failed: {e}")
            return ("text", 0.0)

    def is_enabled(self) -> bool:
        """Check if ML classifier is enabled and loaded."""
        return self.model is not None and self.vectorizer is not None


def train_classifier(training_data: list, output_path: str):
    """
    Train a new language classifier.

    Args:
        training_data: List of (code_snippet, language_label) tuples
        output_path: Path to save the trained model

    This is a placeholder for future ML model training.
    Requires sklearn and proper training data collection.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        raise ImportError("sklearn required for training. Install: pip install scikit-learn")

    # Extract code samples and labels
    X = [sample[0] for sample in training_data]
    y = [sample[1] for sample in training_data]

    # Create vectorizer with character n-grams
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(1, 5),
        max_features=10000,
        min_df=2,
    )

    # Train classifier
    model = LogisticRegression(
        max_iter=1000,
        multi_class="multinomial",
        solver="lbfgs",
    )

    # Fit
    X_features = vectorizer.fit_transform(X)
    model.fit(X_features, y)

    # Save model and vectorizer
    model_data = {
        "model": model,
        "vectorizer": vectorizer,
        "classes": list(model.classes_),
        "n_samples": len(training_data),
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump(model_data, f)

    print(f"Model trained and saved to {output_path}")
    print(f"  Classes: {model.classes_}")
    print(f"  Training samples: {len(training_data)}")


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="ML language classifier")
    parser.add_argument("--test", action="store_true", help="Test classifier")
    parser.add_argument("--model", type=str, help="Path to model file")

    args = parser.parse_args()

    if args.test:
        classifier = LanguageClassifier(args.model)

        test_samples = [
            ("def hello():\n    print('world')", "python"),
            ("SELECT * FROM users", "sql"),
            ('{"name": "test"}', "json"),
        ]

        for code, expected in test_samples:
            pred_lang, conf = classifier.predict(code)
            status = "✓" if pred_lang == expected else "✗"
            print(f"{status} Expected: {expected}, Got: {pred_lang} (conf: {conf:.2f})")
