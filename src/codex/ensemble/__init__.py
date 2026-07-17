"""
Multi-Model Ensemble Prediction System.

Phase 4F Planset 009 implementation providing 3-model ensemble prediction
with weighted voting, confidence thresholds, and real-time API.

Components:
- EnsemblePredictor: Main orchestrator with weighted voting
- EnsembleConfig: Configuration for ensemble models
- BaseModel: Fast heuristic-based predictions (75-80% accuracy)
- MLModel: Gradient boosting patterns (85-90% accuracy)
- SymbolicModel: Knowledge graph reasoning (80-85% accuracy)
- WeightedVoter: Ensemble voting logic with confidence scoring
- PredictionAPI: REST API wrapper for predictions
- PredictionAPIServer: FastAPI server for real-time API
- CalibrationFramework: Cross-validation and confidence calibration
- DiversityValidator: Model diversity validation (correlation <0.6)
- EnsembleEvaluator: Comprehensive ensemble evaluation
- LoadTester: Load testing framework (1000 req/s target)
- Integration Adapters: Format for downstream consumers (010, 011, 012)
"""

from src.codex.ensemble.calibration import CalibrationFramework
from src.codex.ensemble.ensemble_evaluator import (
    DiversityMetrics,
    DiversityValidator,
    EnsembleEvaluationResult,
    EnsembleEvaluator,
)
from src.codex.ensemble.ensemble_predictor import EnsembleConfig, EnsemblePredictor, WeightedVoter
from src.codex.ensemble.fastapi_server import (
    BatchPredictionRequest,
    PredictionAPIServer,
    PredictionRequest,
)
from src.codex.ensemble.integration_adapters import (
    AdapterFactory,
    AnomalyCorrelationAdapter,
    ForecastingAdapter,
    IntegrationAdapter,
    SLAOptimizationAdapter,
    adapt_prediction_for_downstream,
    batch_adapt_predictions,
)
from src.codex.ensemble.load_testing import LoadTestConfig, LoadTester, LoadTestResult
from src.codex.ensemble.models import BaseModel, HeuristicModel, MLModel, SymbolicModel
from src.codex.ensemble.prediction_api import PredictionAPI
from src.codex.ensemble.types import (
    CalibrationMetrics,
    CrossValidationResult,
    EnsemblePrediction,
    ModelPrediction,
    ModelType,
    PredictionType,
)

__all__ = [
    # Core ensemble
    "EnsemblePredictor",
    "EnsembleConfig",
    "WeightedVoter",
    # Models
    "BaseModel",
    "HeuristicModel",
    "MLModel",
    "SymbolicModel",
    # API
    "PredictionAPI",
    "PredictionAPIServer",
    "PredictionRequest",
    "BatchPredictionRequest",
    # Calibration & Validation
    "CalibrationFramework",
    "DiversityValidator",
    "DiversityMetrics",
    "EnsembleEvaluator",
    "EnsembleEvaluationResult",
    # Load Testing
    "LoadTester",
    "LoadTestConfig",
    "LoadTestResult",
    # Integration
    "IntegrationAdapter",
    "AnomalyCorrelationAdapter",
    "ForecastingAdapter",
    "SLAOptimizationAdapter",
    "AdapterFactory",
    "adapt_prediction_for_downstream",
    "batch_adapt_predictions",
    # Types
    "PredictionType",
    "ModelType",
    "ModelPrediction",
    "EnsemblePrediction",
    "CrossValidationResult",
    "CalibrationMetrics",
]
