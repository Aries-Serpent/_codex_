"""Comprehensive test suite for ensemble prediction system.

Test Coverage Targets:
- All 3 models tested independently
- Weighted voting logic verified
- Confidence calibration validated
- API endpoints tested
- Latency requirements verified (<200ms p99)
- Ensemble accuracy improvement confirmed
- Integration tests for full pipeline
"""


import numpy as np
import pytest

from src.codex.ensemble.calibration import CalibrationFramework
from src.codex.ensemble.ensemble_predictor import (
    EnsembleConfig,
    EnsemblePredictor,
)
from src.codex.ensemble.models import (
    HeuristicModel,
    MLModel,
    SymbolicModel,
)
from src.codex.ensemble.prediction_api import PredictionAPI
from src.codex.ensemble.types import (
    ModelType,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def test_features():
    """Generate test feature set."""
    return {
        "confidence": 0.75,
        "frequency": 50,
        "days_old": 5,
        "priority": 5,
        "category": "test",
    }


@pytest.fixture
def ensemble_config():
    """Create test ensemble configuration."""
    return EnsembleConfig(
        heuristic_weight=0.3,
        ml_weight=0.4,
        symbolic_weight=0.3,
        confidence_threshold=0.70,
        disagreement_threshold=0.15,
    )


@pytest.fixture
def ensemble_predictor(ensemble_config):
    """Create ensemble predictor instance."""
    return EnsemblePredictor(ensemble_config)


@pytest.fixture
def prediction_api(ensemble_config):
    """Create prediction API instance."""
    return PredictionAPI(ensemble_config)


@pytest.fixture
def synthetic_data():
    """Generate synthetic training/validation data."""
    np.random.seed(42)
    n_samples = 100
    n_features = 5

    X = np.random.randn(n_samples, n_features)
    y = (np.sum(X[:, :3], axis=1) > 0).astype(float)

    return X, y


# ============================================================================
# Test Cases
# ============================================================================


class TestHeuristicModel:
    """Test heuristic model component."""

    def test_heuristic_initialization(self):
        """Test heuristic model initialization."""
        model = HeuristicModel()
        assert model is not None
        assert model.get_model_type() == ModelType.HEURISTIC

    def test_heuristic_predict(self, test_features):
        """Test heuristic prediction."""
        model = HeuristicModel()
        result = model.predict(test_features)
        assert result.model_type == ModelType.HEURISTIC
        assert 0.0 <= result.confidence <= 1.0
        assert result.execution_time_ms > 0


class TestMLModel:
    """Test ML model component."""

    def test_ml_initialization(self):
        """Test ML model initialization."""
        model = MLModel()
        assert model is not None
        assert model.get_model_type() == ModelType.MACHINE_LEARNING

    def test_ml_predict(self, test_features):
        """Test ML prediction."""
        model = MLModel()
        result = model.predict(test_features)
        assert result.model_type == ModelType.MACHINE_LEARNING
        assert 0.0 <= result.confidence <= 1.0

    def test_ml_training(self, synthetic_data):
        """Test ML model training."""
        X, y = synthetic_data
        model = MLModel()
        metrics = model.train(X, y)
        assert "training_accuracy" in metrics


class TestSymbolicModel:
    """Test symbolic model component."""

    def test_symbolic_initialization(self):
        """Test symbolic model initialization."""
        model = SymbolicModel()
        assert model is not None
        assert model.get_model_type() == ModelType.SYMBOLIC

    def test_symbolic_predict(self, test_features):
        """Test symbolic prediction."""
        model = SymbolicModel()
        result = model.predict(test_features)
        assert result.model_type == ModelType.SYMBOLIC
        assert 0.0 <= result.confidence <= 1.0


class TestEnsemblePredictor:
    """Test main ensemble predictor."""

    def test_ensemble_initialization(self, ensemble_predictor):
        """Test ensemble initialization."""
        assert ensemble_predictor is not None
        assert len(ensemble_predictor.models) == 3

    def test_ensemble_predict(self, ensemble_predictor, test_features):
        """Test ensemble prediction."""
        result = ensemble_predictor.predict(test_features)
        assert result.prediction is not None
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.model_predictions) == 3

    def test_ensemble_latency_sla(self, ensemble_predictor, test_features):
        """Test ensemble meets latency SLA (<200ms p99)."""
        latencies = []
        for _ in range(10):
            result = ensemble_predictor.predict(test_features)
            latencies.append(result.total_execution_time_ms)

        p99 = np.percentile(latencies, 99)
        assert p99 < 200

    def test_ensemble_batch_predict(self, ensemble_predictor):
        """Test batch prediction."""
        features_list = [
            {"confidence": 0.8, "frequency": 50, "days_old": 5},
            {"confidence": 0.3, "frequency": 10, "days_old": 20},
        ]
        results = ensemble_predictor.batch_predict(features_list)
        assert len(results) == 2


class TestCalibration:
    """Test calibration framework."""

    def test_calibration_initialization(self):
        """Test calibration initialization."""
        framework = CalibrationFramework(k_folds=5)
        assert framework.k_folds == 5

    def test_cross_validation(self, synthetic_data):
        """Test cross-validation."""
        X, y = synthetic_data
        framework = CalibrationFramework(k_folds=5)
        results = framework.cross_validate(X, y, ModelType.HEURISTIC)
        assert len(results) == 5


class TestPredictionAPI:
    """Test prediction API."""

    def test_api_initialization(self, prediction_api):
        """Test API initialization."""
        assert prediction_api is not None

    def test_api_predict(self, prediction_api, test_features):
        """Test API predict."""
        response = prediction_api.predict(test_features, "classification")
        assert "prediction" in response
        assert "confidence" in response

    def test_api_batch_predict(self, prediction_api):
        """Test API batch predict."""
        features_list = [
            {"confidence": 0.8, "frequency": 50},
            {"confidence": 0.3, "frequency": 10},
        ]
        response = prediction_api.predict_batch(features_list, "classification")
        assert response["count"] == 2

    def test_api_health_check(self, prediction_api):
        """Test API health check."""
        response = prediction_api.health_check()
        assert response["status"] in ["healthy", "unhealthy"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
