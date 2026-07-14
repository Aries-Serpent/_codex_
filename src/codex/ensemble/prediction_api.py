"""REST API for ensemble predictions."""

import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.codex.ensemble.ensemble_predictor import EnsemblePredictor, EnsembleConfig
from src.codex.ensemble.types import PredictionType, EnsemblePrediction

logger = logging.getLogger(__name__)


class PredictionAPI:
    """REST API wrapper for ensemble predictions."""

    def __init__(self, config: Optional[EnsembleConfig] = None):
        """Initialize prediction API.

        Args:
            config: Optional ensemble configuration
        """
        self.predictor = EnsemblePredictor(config)
        self.config = config or EnsembleConfig()

    def predict(
        self,
        features: Dict[str, Any],
        prediction_type: str = "classification",
    ) -> Dict[str, Any]:
        """Make a single prediction.

        Args:
            features: Input features dictionary
            prediction_type: Type of prediction

        Returns:
            Prediction response dictionary
        """
        try:
            # Validate prediction type
            pred_type = PredictionType[prediction_type.upper()]
        except KeyError:
            return {
                "error": f"Invalid prediction_type: {prediction_type}",
                "valid_types": [pt.value for pt in PredictionType],
            }

        try:
            result = self.predictor.predict(features, pred_type)
            return self._format_prediction(result)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    def predict_batch(
        self,
        features_list: List[Dict[str, Any]],
        prediction_type: str = "classification",
    ) -> Dict[str, Any]:
        """Make batch predictions.

        Args:
            features_list: List of feature dictionaries
            prediction_type: Type of prediction

        Returns:
            Batch prediction response
        """
        try:
            pred_type = PredictionType[prediction_type.upper()]
        except KeyError:
            return {
                "error": f"Invalid prediction_type: {prediction_type}",
                "valid_types": [pt.value for pt in PredictionType],
            }

        try:
            results = self.predictor.batch_predict(features_list, pred_type)
            return {
                "predictions": [self._format_prediction(r) for r in results],
                "count": len(results),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get ensemble performance metrics.

        Returns:
            Performance metrics dictionary
        """
        try:
            performance = self.predictor.get_ensemble_performance()
            accuracies = self.predictor.get_model_accuracy_estimates()

            return {
                "performance": performance,
                "model_accuracies": accuracies,
                "configuration": {
                    "heuristic_weight": self.config.heuristic_weight,
                    "ml_weight": self.config.ml_weight,
                    "symbolic_weight": self.config.symbolic_weight,
                    "confidence_threshold": self.config.confidence_threshold,
                    "disagreement_threshold": self.config.disagreement_threshold,
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Health check for API.

        Returns:
            Health status dictionary
        """
        try:
            # Try to make a test prediction
            test_features = {
                "confidence": 0.7,
                "frequency": 50,
                "days_old": 5,
                "priority": 5,
                "category": "test",
            }

            result = self.predictor.predict(test_features)

            return {
                "status": "healthy",
                "models": {
                    "heuristic": "ok",
                    "ml": "ok",
                    "symbolic": "ok",
                },
                "test_prediction": self._format_prediction(result),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    def _format_prediction(self, pred: EnsemblePrediction) -> Dict[str, Any]:
        """Format ensemble prediction for API response.

        Args:
            pred: Ensemble prediction

        Returns:
            Formatted dictionary
        """
        return {
            "prediction": pred.prediction,
            "confidence": pred.confidence,
            "prediction_type": pred.prediction_type.value,
            "timestamp": pred.timestamp,
            "models": [m.to_dict() for m in pred.model_predictions],
            "voting_scores": pred.voting_scores,
            "escalated": pred.escalated,
            "escalation_reason": pred.escalation_reason,
            "execution_time_ms": pred.total_execution_time_ms,
        }
