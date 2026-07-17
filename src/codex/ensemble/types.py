"""Type definitions for ensemble prediction system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PredictionType(str, Enum):
    """Types of predictions the ensemble can make."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelType(str, Enum):
    """Individual model types in the ensemble."""

    HEURISTIC = "heuristic"
    MACHINE_LEARNING = "ml"
    SYMBOLIC = "symbolic"


@dataclass
class ModelPrediction:
    """Prediction output from a single model."""

    model_type: ModelType
    prediction: Any
    confidence: float
    reasoning: str
    execution_time_ms: float
    features_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_type": self.model_type.value,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "execution_time_ms": self.execution_time_ms,
            "features_used": self.features_used,
        }


@dataclass
class EnsemblePrediction:
    """Final ensemble prediction with voting results."""

    prediction: Any
    confidence: float
    prediction_type: PredictionType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    model_predictions: List[ModelPrediction] = field(default_factory=list)
    voting_scores: Dict[str, float] = field(default_factory=dict)
    escalated: bool = False
    escalation_reason: Optional[str] = None
    total_execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prediction": self.prediction,
            "confidence": self.confidence,
            "prediction_type": self.prediction_type.value,
            "timestamp": self.timestamp,
            "model_predictions": [m.to_dict() for m in self.model_predictions],
            "voting_scores": self.voting_scores,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
            "total_execution_time_ms": self.total_execution_time_ms,
        }


@dataclass
class CrossValidationResult:
    """Results from k-fold cross-validation."""

    model_type: ModelType
    fold_number: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    brier_score: float
    confusion_matrix: Dict[str, int]
    execution_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_type": self.model_type.value,
            "fold_number": self.fold_number,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "brier_score": self.brier_score,
            "confusion_matrix": self.confusion_matrix,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class CalibrationMetrics:
    """Calibration metrics for confidence scoring."""

    model_type: ModelType
    brier_score: float
    expected_calibration_error: float
    maximum_calibration_error: float
    confidence_bins: Dict[str, float]
    recommended_threshold: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_type": self.model_type.value,
            "brier_score": self.brier_score,
            "expected_calibration_error": self.expected_calibration_error,
            "maximum_calibration_error": self.maximum_calibration_error,
            "confidence_bins": self.confidence_bins,
            "recommended_threshold": self.recommended_threshold,
        }
