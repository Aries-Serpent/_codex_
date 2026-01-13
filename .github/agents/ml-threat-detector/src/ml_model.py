"""ML-based threat detection for security vulnerabilities."""

import ast
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split


@dataclass
class ThreatFeatures:
    """Features extracted from code for threat detection."""

    # Code complexity
    lines_of_code: int
    cyclomatic_complexity: int
    nesting_depth: int

    # Security-sensitive operations
    subprocess_calls: int
    shell_usage: int
    file_operations: int
    network_operations: int
    crypto_operations: int
    eval_usage: int
    exec_usage: int

    # External dependencies
    import_count: int
    external_lib_count: int

    # Data handling
    pickle_usage: int
    xml_parsing: int
    user_input_handling: int

    # Authentication/Authorization
    auth_operations: int
    permission_checks: int

    # Historical context
    previous_vulnerabilities: int
    file_change_frequency: int
    author_security_score: float


class MLThreatDetector:
    """ML model for predicting security vulnerabilities in code."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize detector."""
        self.model: Optional[VotingClassifier] = None
        self.feature_names: Optional[List[str]] = None
        self.threshold_high = 0.7  # High risk threshold
        self.threshold_medium = 0.4  # Medium risk threshold

        if model_path and model_path.exists():
            self.load_model(model_path)

    def extract_features(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> ThreatFeatures:
        """Extract threat features from code."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If code doesn't parse, assign high complexity
            tree = None

        # Code complexity metrics
        lines = code.split("\n")
        loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

        complexity = self._calculate_complexity(tree) if tree else 20
        nesting = self._max_nesting_depth(tree) if tree else 10

        # Security-sensitive patterns
        subprocess_calls = len(re.findall(r"subprocess\.(run|call|Popen)", code))
        shell_usage = len(re.findall(r"shell\s*=\s*True", code))
        file_ops = len(re.findall(r"open\(|file\(", code))
        network_ops = len(re.findall(r"requests\.|urllib\.|http\.|socket\.", code))
        crypto_ops = len(re.findall(r"hashlib\.|hmac\.|Crypto\.", code))
        eval_usage = len(re.findall(r"\beval\(|\bexec\(", code))

        # External dependencies
        imports = len(re.findall(r"^import |^from .* import", code, re.M))
        external_libs = len(set(re.findall(r"import (\w+)", code)))

        # Data handling
        pickle_usage = len(re.findall(r"pickle\.(load|loads|dump)", code))
        xml_parsing = len(re.findall(r"xml\.etree|ElementTree", code))
        user_input = len(re.findall(r"input\(|request\.|argv|environ", code))

        # Auth/Authz
        auth_ops = len(re.findall(r"authenticate|authorize|login|password", code, re.I))
        perm_checks = len(re.findall(r"permission|check_access|require_auth", code, re.I))

        # Historical context from metadata
        metadata = metadata or {}
        prev_vulns = metadata.get("previous_vulnerabilities", 0)
        change_freq = metadata.get("change_frequency", 0.0)
        author_score = metadata.get("author_security_score", 0.5)

        return ThreatFeatures(
            lines_of_code=loc,
            cyclomatic_complexity=complexity,
            nesting_depth=nesting,
            subprocess_calls=subprocess_calls,
            shell_usage=shell_usage,
            file_operations=file_ops,
            network_operations=network_ops,
            crypto_operations=crypto_ops,
            eval_usage=eval_usage,
            exec_usage=eval_usage,  # Same pattern
            import_count=imports,
            external_lib_count=external_libs,
            pickle_usage=pickle_usage,
            xml_parsing=xml_parsing,
            user_input_handling=user_input,
            auth_operations=auth_ops,
            permission_checks=perm_checks,
            previous_vulnerabilities=prev_vulns,
            file_change_frequency=change_freq,
            author_security_score=author_score,
        )

    def _calculate_complexity(self, tree: Optional[ast.AST]) -> int:
        """Calculate cyclomatic complexity."""
        if not tree:
            return 0

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _max_nesting_depth(self, tree: Optional[ast.AST]) -> int:
        """Calculate maximum nesting depth."""
        if not tree:
            return 0

        def depth(node: ast.AST, current: int = 0) -> int:
            max_d = current
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    max_d = max(max_d, depth(child, current + 1))
                else:
                    max_d = max(max_d, depth(child, current))
            return max_d

        return depth(tree)

    def train(
        self, training_data: List[Tuple[str, int, Dict[str, Any]]], model_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Train ML model on historical data.

        Args:
            training_data: List of (code, label, metadata) tuples
                          label: 0 = safe, 1 = vulnerable
            model_path: Path to save trained model

        Returns:
            Training metrics dictionary
        """
        # Extract features
        X = []
        y = []

        for code, label, metadata in training_data:
            features = self.extract_features(code, metadata)
            X.append(list(asdict(features).values()))
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        # Store feature names
        self.feature_names = list(ThreatFeatures.__annotations__.keys())

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Create ensemble model
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1
        )

        gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)

        self.model = VotingClassifier(estimators=[("rf", rf), ("gb", gb)], voting="soft", n_jobs=-1)

        # Train model
        print("Training ensemble model (Random Forest + Gradient Boosting)...")
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", zero_division=0)

        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = 0.0

        print(f"\n✅ Training Complete")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Precision: {precision:.2%}")
        print(f"Recall: {recall:.2%}")
        print(f"F1 Score: {f1:.2%}")
        print(f"ROC AUC: {auc:.2%}")

        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, n_jobs=-1)
        print(f"Cross-validation: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["Safe", "Vulnerable"], zero_division=0))

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(auc),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
        }

        # Save model if path provided and accuracy meets threshold
        if model_path and accuracy >= 0.85:
            self.save_model(model_path)
            print(f"🎉 Model saved to {model_path} (meets 85%+ accuracy requirement)")
        elif model_path:
            print(f"⚠️ Model accuracy {accuracy:.2%} below 85% threshold, not saving")

        return metrics

    def predict_risk(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predict security risk for new code.

        Args:
            code: Source code to analyze
            metadata: Historical metadata about the file

        Returns:
            Risk assessment dictionary
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        features = self.extract_features(code, metadata)
        feature_vector = np.array([list(asdict(features).values())])

        risk_prob = self.model.predict_proba(feature_vector)[0][1]

        if risk_prob >= 0.8:
            risk_level = "critical"
        elif risk_prob >= 0.6:
            risk_level = "high"
        elif risk_prob >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        confidence = max(risk_prob, 1 - risk_prob)

        return {
            "risk_score": float(risk_prob),
            "risk_level": risk_level,
            "confidence": float(confidence),
            "features": asdict(features),
        }

    def save_model(self, path: Path) -> None:
        """Save trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save")

        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "feature_names": self.feature_names}, path)
        print(f"✅ Model saved to {path}")

    def load_model(self, path: Path) -> None:
        """Load trained model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        print(f"✅ Model loaded from {path}")


if __name__ == "__main__":
    # Example usage
    detector = MLThreatDetector()

    # Example training data (in production, load from collected data)
    training_data = [
        (
            "import subprocess\nsubprocess.run(['ls'], shell=True)",
            1,
            {"previous_vulnerabilities": 2, "change_frequency": 0.5, "author_security_score": 0.3},
        ),
        ("def safe_function():\n    return 42", 0, {"previous_vulnerabilities": 0, "change_frequency": 0.1, "author_security_score": 0.9}),
        # Add more training data...
    ]

    print("Training model with example data...")
    metrics = detector.train(training_data, Path("ml_threat_detector_model.pkl"))

    print(f"\nFinal metrics: {metrics}")
