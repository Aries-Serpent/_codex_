"""Main ensemble predictor orchestrator."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from src.codex.ensemble.models import (
    BaseModel,
    HeuristicModel,
    MLModel,
    SymbolicModel,
)
from src.codex.ensemble.types import (
    EnsemblePrediction,
    ModelPrediction,
    ModelType,
    PredictionType,
)

logger = logging.getLogger(__name__)


@dataclass
class EnsembleConfig:
    """Configuration for ensemble predictor."""

    heuristic_weight: float = 0.3
    ml_weight: float = 0.4
    symbolic_weight: float = 0.3
    confidence_threshold: float = 0.70
    disagreement_threshold: float = 0.15
    enable_fallback_cascade: bool = True
    max_execution_time_ms: float = 200.0


class WeightedVoter:
    """Voting mechanism for ensemble predictions."""

    def __init__(self, config: EnsembleConfig):
        """Initialize voter with configuration."""
        self.config = config
        self.weights = {
            ModelType.HEURISTIC: config.heuristic_weight,
            ModelType.MACHINE_LEARNING: config.ml_weight,
            ModelType.SYMBOLIC: config.symbolic_weight,
        }

    def vote(
        self, model_predictions: List[ModelPrediction]
    ) -> tuple[Any, float, Dict[str, float]]:
        """Aggregate predictions via weighted voting.

        Args:
            model_predictions: List of predictions from ensemble models

        Returns:
            Tuple of (ensemble_prediction, confidence, voting_scores)
        """
        if not model_predictions:
            raise ValueError("No model predictions provided")

        # Extract numerical scores for voting
        scores = {}
        confidences = {}

        for pred in model_predictions:
            model_type = pred.model_type
            weight = self.weights.get(model_type, 0.0)

            # Normalize prediction to numerical score
            if isinstance(pred.prediction, str):
                pred_score = 1.0 if pred.prediction == "positive" else 0.0
            elif isinstance(pred.prediction, (int, float)):
                pred_score = float(pred.prediction)
            else:
                pred_score = 0.5  # Default neutral

            scores[model_type.value] = pred_score * weight
            confidences[model_type.value] = pred.confidence * weight

        # Weighted average for final prediction
        total_weight = sum(self.weights.values())
        weighted_score = sum(scores.values()) / total_weight if total_weight > 0 else 0.5

        # Weighted average for confidence
        weighted_confidence = sum(confidences.values()) / total_weight if total_weight > 0 else 0.5

        # Convert to prediction
        final_prediction = "positive" if weighted_score >= 0.5 else "negative"

        return final_prediction, weighted_confidence, scores

    def calculate_disagreement(
        self, model_predictions: List[ModelPrediction]
    ) -> float:
        """Calculate disagreement between models.

        Args:
            model_predictions: List of model predictions

        Returns:
            Disagreement score [0, 1]
        """
        if len(model_predictions) < 2:
            return 0.0

        confidences = [p.confidence for p in model_predictions]
        predictions = []

        for p in model_predictions:
            if p.prediction is None:
                predictions.append(0.5)  # Handle None predictions
            elif isinstance(p.prediction, str):
                predictions.append(1.0 if p.prediction == "positive" else 0.0)
            else:
                try:
                    predictions.append(float(p.prediction))
                except (TypeError, ValueError):
                    predictions.append(0.5)

        # Variance in predictions normalized by confidence range
        pred_variance = np.var(predictions) if len(predictions) > 1 else 0.0
        conf_variance = np.var(confidences) if len(confidences) > 1 else 0.0

        # Disagreement is combination of variance metrics
        disagreement = (pred_variance + conf_variance) / 2.0

        return float(disagreement)


class EnsemblePredictor:
    """Main multi-model ensemble predictor.

    Combines predictions from 3 models:
    - HeuristicModel: Fast, interpretable rules (75-80% accuracy)
    - MLModel: Gradient boosting (85-90% accuracy)
    - SymbolicModel: Knowledge graph reasoning (80-85% accuracy)

    Ensemble targets ≥best_model + 3% accuracy improvement.
    """

    def __init__(self, config: Optional[EnsembleConfig] = None):
        """Initialize ensemble predictor.

        Args:
            config: Optional ensemble configuration
        """
        self.config = config or EnsembleConfig()
        self.models: Dict[ModelType, BaseModel] = {}
        self.voter = WeightedVoter(self.config)
        self.prediction_history: List[EnsemblePrediction] = []

        # Initialize individual models
        self._init_models()

        logger.info(f"EnsemblePredictor initialized with config: {self.config}")

    def _init_models(self) -> None:
        """Initialize all ensemble models."""
        self.models[ModelType.HEURISTIC] = HeuristicModel()
        self.models[ModelType.MACHINE_LEARNING] = MLModel()
        self.models[ModelType.SYMBOLIC] = SymbolicModel()

        logger.info(f"Initialized {len(self.models)} models")

    def predict(
        self, features: Dict[str, Any], prediction_type: PredictionType = PredictionType.CLASSIFICATION
    ) -> EnsemblePrediction:
        """Make an ensemble prediction.

        Args:
            features: Input feature dictionary
            prediction_type: Type of prediction (classification/regression/anomaly)

        Returns:
            EnsemblePrediction with all model outputs and voting results
        """
        overall_start = time.time()
        model_predictions: List[ModelPrediction] = []

        # Get predictions from all models
        for model_type, model in self.models.items():
            try:
                pred = model.predict(features)
                model_predictions.append(pred)
            except Exception as e:
                logger.error(f"Model {model_type} failed: {e}")
                # Continue with other models

        if not model_predictions:
            raise RuntimeError("All models failed to produce predictions")

        # Apply weighted voting
        ensemble_pred, confidence, voting_scores = self.voter.vote(model_predictions)

        # Calculate disagreement
        disagreement = self.voter.calculate_disagreement(model_predictions)

        # Check for escalation
        escalated = False
        escalation_reason = None

        if self.config.enable_fallback_cascade:
            if confidence < self.config.confidence_threshold:
                escalated = True
                escalation_reason = f"Low confidence: {confidence:.3f}"

            elif disagreement > self.config.disagreement_threshold:
                escalated = True
                escalation_reason = f"High disagreement: {disagreement:.3f}"

        total_execution_time = (time.time() - overall_start) * 1000

        # Create ensemble prediction object
        ensemble_prediction = EnsemblePrediction(
            prediction=ensemble_pred,
            confidence=max(0.0, min(1.0, confidence)),
            prediction_type=prediction_type,
            model_predictions=model_predictions,
            voting_scores=voting_scores,
            escalated=escalated,
            escalation_reason=escalation_reason,
            total_execution_time_ms=total_execution_time,
        )

        # Store in history
        self.prediction_history.append(ensemble_prediction)

        # Check latency SLA
        if total_execution_time > self.config.max_execution_time_ms:
            logger.warning(
                f"Prediction exceeded latency SLA: {total_execution_time:.1f}ms "
                f"(threshold: {self.config.max_execution_time_ms}ms)"
            )

        return ensemble_prediction

    def batch_predict(
        self,
        features_list: List[Dict[str, Any]],
        prediction_type: PredictionType = PredictionType.CLASSIFICATION,
    ) -> List[EnsemblePrediction]:
        """Make batch predictions.

        Args:
            features_list: List of feature dictionaries
            prediction_type: Type of prediction

        Returns:
            List of ensemble predictions
        """
        predictions = []

        for features in features_list:
            try:
                pred = self.predict(features, prediction_type)
                predictions.append(pred)
            except Exception as e:
                logger.error("Batch prediction failed: %s", str(type(e).__name__))

        return predictions

    def get_model_accuracy_estimates(self) -> Dict[str, float]:
        """Get estimated accuracy for each model based on prediction history.

        Returns:
            Dictionary of model accuracies (simplified estimate)
        """
        if not self.prediction_history:
            return {
                ModelType.HEURISTIC.value: 0.75,
                ModelType.MACHINE_LEARNING.value: 0.87,
                ModelType.SYMBOLIC.value: 0.82,
            }

        # Simple accuracy calculation: average of individual model confidences
        accuracies = {}

        for model_type in ModelType:
            confidences = []

            for ensemble_pred in self.prediction_history:
                for model_pred in ensemble_pred.model_predictions:
                    if model_pred.model_type == model_type:
                        confidences.append(model_pred.confidence)

            if confidences:
                accuracies[model_type.value] = float(np.mean(confidences))
            else:
                # Return default estimates
                if model_type == ModelType.HEURISTIC:
                    accuracies[model_type.value] = 0.75
                elif model_type == ModelType.MACHINE_LEARNING:
                    accuracies[model_type.value] = 0.87
                else:
                    accuracies[model_type.value] = 0.82

        return accuracies

    def get_ensemble_performance(self) -> Dict[str, Any]:
        """Get performance metrics for ensemble.

        Returns:
            Dictionary with ensemble performance metrics
        """
        if not self.prediction_history:
            return {"error": "No prediction history"}

        predictions = self.prediction_history
        execution_times = [p.total_execution_time_ms for p in predictions]
        confidences = [p.confidence for p in predictions]
        escalation_count = sum(1 for p in predictions if p.escalated)

        return {
            "total_predictions": len(predictions),
            "escalated_predictions": escalation_count,
            "escalation_rate": escalation_count / len(predictions) if predictions else 0.0,
            "avg_execution_time_ms": float(np.mean(execution_times)),
            "p95_execution_time_ms": float(np.percentile(execution_times, 95)),
            "p99_execution_time_ms": float(np.percentile(execution_times, 99)),
            "avg_confidence": float(np.mean(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
        }

    def clear_history(self) -> None:
        """Clear prediction history."""
        self.prediction_history.clear()

    def get_prediction_history(self) -> List[EnsemblePrediction]:
        """Get prediction history.

        Returns:
            List of ensemble predictions
        """
        return self.prediction_history.copy()
