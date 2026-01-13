"""Comprehensive test suite for ML Threat Detection model."""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ml_model import MLThreatDetector, ThreatFeatures
from feature_extraction import FeatureExtractor, SecurityFeatures


class TestFeatureExtraction:
    """Test feature extraction functionality."""

    def setup_method(self):
        self.extractor = FeatureExtractor()

    def test_extract_20_features(self):
        """Verify exactly 20 features are extracted."""
        code = "def test(): pass"
        features = self.extractor.extract(code)
        feature_dict = vars(features)
        assert len(feature_dict) == 20, "Must extract exactly 20 features"

    def test_vulnerable_code_detection(self):
        """Test detection of vulnerable code patterns."""
        vulnerable_code = """
import subprocess
subprocess.run("ls", shell=True)
eval(user_input)
"""
        features = self.extractor.extract(vulnerable_code)
        assert features.subprocess_calls > 0
        assert features.shell_true_usage > 0
        assert features.eval_exec_calls > 0

    def test_safe_code_features(self):
        """Test feature extraction from safe code."""
        safe_code = """
def add(a, b):
    return a + b
"""
        features = self.extractor.extract(safe_code)
        assert features.subprocess_calls == 0
        assert features.shell_true_usage == 0
        assert features.eval_exec_calls == 0

    def test_complexity_calculation(self):
        """Test cyclomatic complexity calculation."""
        complex_code = """
def complex(x):
    if x > 0:
        if x < 10:
            for i in range(x):
                while i > 0:
                    i -= 1
    return x
"""
        features = self.extractor.extract(complex_code)
        assert features.cyclomatic_complexity >= 5

    def test_nesting_depth(self):
        """Test nesting depth calculation."""
        nested_code = """
def nested():
    if True:
        if True:
            if True:
                return 1
"""
        features = self.extractor.extract(nested_code)
        assert features.max_nesting_depth >= 3


class TestMLModel:
    """Test ML threat detection model."""

    def setup_method(self):
        self.detector = MLThreatDetector()

    def test_model_initialization(self):
        """Test model initializes correctly."""
        assert self.detector.model is None
        assert self.detector.threshold_high == 0.7
        assert self.detector.threshold_medium == 0.4

    def test_feature_extraction_integration(self):
        """Test model's feature extraction matches expected format."""
        code = "import os\nos.system('ls')"
        features = self.detector.extract_features(code)
        assert isinstance(features, ThreatFeatures)
        assert hasattr(features, "subprocess_calls")

    def test_training_with_sample_data(self):
        """Test model training with synthetic data."""
        # Generate synthetic training data
        training_data = []
        
        # 50 vulnerable examples
        for i in range(50):
            vuln_code = f"""
import subprocess
subprocess.run("cmd", shell=True)
eval(input())
"""
            training_data.append((vuln_code, 1, {"previous_vulnerabilities": 2, "change_frequency": 5, "author_security_score": 0.3}))
        
        # 50 safe examples
        for i in range(50):
            safe_code = f"""
def safe_function_{i}(x, y):
    result = x + y
    return result
"""
            training_data.append((safe_code, 0, {"previous_vulnerabilities": 0, "change_frequency": 1, "author_security_score": 0.9}))

        metrics = self.detector.train(training_data)
        
        # Check metrics exist
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        
        # Model should be trained
        assert self.detector.model is not None

    def test_accuracy_target_85_percent(self):
        """Test model meets 85%+ accuracy target with good data."""
        # Generate more training data for better accuracy
        training_data = []
        
        # 100 clear vulnerable examples
        vulnerable_patterns = [
            "subprocess.run('ls', shell=True)",
            "eval(user_input)",
            "exec(code)",
            "pickle.loads(data)",
            "os.system(cmd)",
        ]
        
        for i in range(100):
            pattern = vulnerable_patterns[i % len(vulnerable_patterns)]
            vuln_code = f"""
import subprocess
import pickle
def vuln_{i}():
    {pattern}
"""
            training_data.append((vuln_code, 1, {"previous_vulnerabilities": 3, "change_frequency": 8, "author_security_score": 0.2}))
        
        # 100 clear safe examples
        for i in range(100):
            safe_code = f"""
def safe_function_{i}(a, b):
    c = a + b
    d = c * 2
    return d
"""
            training_data.append((safe_code, 0, {"previous_vulnerabilities": 0, "change_frequency": 1, "author_security_score": 0.95}))

        metrics = self.detector.train(training_data)
        
        # Verify 85%+ accuracy target
        assert metrics["accuracy"] >= 0.85, f"Accuracy {metrics['accuracy']:.2%} below 85% target"

    def test_risk_prediction(self):
        """Test risk prediction on new code."""
        # Train with minimal data
        training_data = [
            ("subprocess.run('ls', shell=True)\neval(x)", 1, {"previous_vulnerabilities": 2, "change_frequency": 5, "author_security_score": 0.3}),
            ("def safe(): return 1", 0, {"previous_vulnerabilities": 0, "change_frequency": 1, "author_security_score": 0.9}),
        ] * 50  # Repeat to have enough data

        self.detector.train(training_data)
        
        # Test prediction
        risky_code = "subprocess.run(cmd, shell=True)"
        result = self.detector.predict_risk(risky_code)
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "confidence" in result
        assert result["risk_level"] in ["low", "medium", "high", "critical"]

    def test_ensemble_model_components(self):
        """Test that ensemble includes Random Forest and Gradient Boosting."""
        training_data = [
            ("subprocess.run('ls', shell=True)", 1, {}),
            ("def safe(): return 1", 0, {}),
        ] * 50

        self.detector.train(training_data)
        
        # Check ensemble components
        assert self.detector.model is not None
        estimators = dict(self.detector.model.estimators)
        assert "rf" in estimators  # Random Forest
        assert "gb" in estimators  # Gradient Boosting


class TestModelPersistence:
    """Test model saving and loading."""

    def test_save_and_load_model(self, tmp_path):
        """Test model can be saved and loaded."""
        detector = MLThreatDetector()
        
        # Train model
        training_data = [
            ("subprocess.run('ls', shell=True)", 1, {}),
            ("def safe(): return 1", 0, {}),
        ] * 50

        detector.train(training_data)
        
        # Save model
        model_path = tmp_path / "test_model.pkl"
        detector.save_model(model_path)
        assert model_path.exists()
        
        # Load model in new detector
        detector2 = MLThreatDetector(model_path)
        assert detector2.model is not None
        
        # Test prediction with loaded model
        result = detector2.predict_risk("import os")
        assert "risk_score" in result


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_end_to_end_workflow(self, tmp_path):
        """Test complete workflow from feature extraction to prediction."""
        # 1. Extract features
        extractor = FeatureExtractor()
        code1 = "subprocess.run('ls', shell=True)"
        features1 = extractor.extract(code1)
        assert isinstance(features1, SecurityFeatures)
        
        # 2. Train model
        detector = MLThreatDetector()
        training_data = [
            (code1, 1, {}),
            ("def safe(): return 1", 0, {}),
        ] * 50
        
        metrics = detector.train(training_data)
        assert metrics["accuracy"] > 0.5
        
        # 3. Predict on new code
        new_code = "eval(input())"
        prediction = detector.predict_risk(new_code)
        assert prediction["risk_score"] >= 0.0
        assert prediction["risk_score"] <= 1.0
        
        # 4. Save model
        model_path = tmp_path / "model.pkl"
        detector.save_model(model_path)
        assert model_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
