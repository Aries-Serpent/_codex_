"""Integration adapters for ensemble predictions to downstream consumers."""

import logging
from typing import Any, Dict, List

from src.codex.ensemble.types import EnsemblePrediction, ModelPrediction

logger = logging.getLogger(__name__)


class IntegrationAdapter:
    """Base class for integration adapters."""

    def adapt(self, prediction: EnsemblePrediction) -> Dict[str, Any]:
        """Adapt ensemble prediction to target format.

        Args:
            prediction: EnsemblePrediction object

        Returns:
            Adapted prediction dictionary
        """
        raise NotImplementedError


class AnomalyCorrelationAdapter(IntegrationAdapter):
    """Adapter for Planset 011 (Advanced Anomaly Correlation).

    Provides predictions with causal inference context for anomaly detection.
    """

    def adapt(self, prediction: EnsemblePrediction) -> Dict[str, Any]:
        """Adapt prediction for anomaly correlation system.

        Args:
            prediction: Ensemble prediction

        Returns:
            Prediction formatted for anomaly correlation
        """
        return {
            "anomaly_score": 1.0 - prediction.confidence if prediction.prediction == "negative" else prediction.confidence,
            "confidence": prediction.confidence,
            "escalated": prediction.escalated,
            "escalation_reason": prediction.escalation_reason,
            "model_diversity": self._calculate_model_diversity(prediction.model_predictions),
            "disagreement_level": self._calculate_disagreement(prediction.model_predictions),
            "timestamp": prediction.timestamp,
            "prediction_type": prediction.prediction_type.value,
            "voting_scores": prediction.voting_scores,
            "model_predictions": [
                {
                    "model": m.model_type.value,
                    "prediction": m.prediction,
                    "confidence": m.confidence,
                    "reasoning": m.reasoning,
                }
                for m in prediction.model_predictions
            ],
        }

    def _calculate_model_diversity(self, model_predictions: List[ModelPrediction]) -> float:
        """Calculate diversity among model predictions.

        Args:
            model_predictions: List of model predictions

        Returns:
            Diversity score [0, 1]
        """
        if len(model_predictions) < 2:
            return 0.0

        confidences = [p.confidence for p in model_predictions]
        predictions = []

        for p in model_predictions:
            if isinstance(p.prediction, str):
                predictions.append(1.0 if p.prediction == "positive" else 0.0)
            else:
                predictions.append(float(p.prediction))

        # Calculate variance as diversity metric
        conf_variance = sum((c - sum(confidences) / len(confidences)) ** 2 for c in confidences) / len(
            confidences
        )
        pred_variance = sum((p - sum(predictions) / len(predictions)) ** 2 for p in predictions) / len(predictions)

        diversity = (conf_variance + pred_variance) / 2.0
        return min(1.0, diversity)

    def _calculate_disagreement(self, model_predictions: List[ModelPrediction]) -> str:
        """Calculate disagreement level among models.

        Args:
            model_predictions: List of model predictions

        Returns:
            Disagreement level: 'low', 'medium', 'high'
        """
        if len(model_predictions) < 2:
            return "low"

        predictions = []
        for p in model_predictions:
            if isinstance(p.prediction, str):
                predictions.append(1.0 if p.prediction == "positive" else 0.0)
            else:
                predictions.append(float(p.prediction))

        variance = sum((pred - sum(predictions) / len(predictions)) ** 2 for pred in predictions) / len(predictions)

        if variance < 0.05:
            return "low"
        elif variance < 0.15:
            return "medium"
        else:
            return "high"


class ForecastingAdapter(IntegrationAdapter):
    """Adapter for Planset 012 (Forecasting).

    Provides predictions with confidence intervals for time-series forecasting.
    """

    def adapt(self, prediction: EnsemblePrediction) -> Dict[str, Any]:
        """Adapt prediction for forecasting system.

        Args:
            prediction: Ensemble prediction

        Returns:
            Prediction formatted for forecasting
        """
        # Calculate confidence interval
        ci_lower, ci_upper = self._calculate_confidence_interval(prediction)

        return {
            "forecast_value": self._normalize_prediction(prediction.prediction),
            "confidence": prediction.confidence,
            "confidence_interval": {
                "lower": ci_lower,
                "upper": ci_upper,
                "confidence_level": 0.95,
            },
            "model_weights": {
                m.model_type.value: prediction.voting_scores.get(m.model_type.value, 0.0)
                for m in prediction.model_predictions
            },
            "ensemble_entropy": self._calculate_entropy(prediction),
            "timestamp": prediction.timestamp,
            "execution_time_ms": prediction.total_execution_time_ms,
            "model_convergence": self._calculate_convergence(prediction.model_predictions),
        }

    def _normalize_prediction(self, pred: Any) -> float:
        """Normalize prediction to float value.

        Args:
            pred: Prediction value (string or numeric)

        Returns:
            Normalized float
        """
        if isinstance(pred, str):
            return 1.0 if pred == "positive" else 0.0
        elif isinstance(pred, (int, float)):
            return float(pred)
        else:
            return 0.5

    def _calculate_confidence_interval(self, prediction: EnsemblePrediction) -> tuple:
        """Calculate 95% confidence interval.

        Args:
            prediction: Ensemble prediction

        Returns:
            Tuple of (lower, upper) bounds
        """
        # Use model variance to estimate CI width
        confidences = [m.confidence for m in prediction.model_predictions]
        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)

        # CI width based on variance
        ci_width = 1.96 * (variance ** 0.5)

        pred_value = self._normalize_prediction(prediction.prediction)
        lower = max(0.0, pred_value - ci_width / 2)
        upper = min(1.0, pred_value + ci_width / 2)

        return lower, upper

    def _calculate_entropy(self, prediction: EnsemblePrediction) -> float:
        """Calculate prediction entropy (uncertainty).

        Args:
            prediction: Ensemble prediction

        Returns:
            Entropy value [0, 1]
        """
        p = prediction.confidence
        if p <= 0 or p >= 1:
            return 0.0

        entropy = -p * (p ** 0.5) - (1 - p) * ((1 - p) ** 0.5)
        return min(1.0, max(0.0, entropy))

    def _calculate_convergence(self, model_predictions: List[ModelPrediction]) -> float:
        """Calculate model convergence (agreement).

        Args:
            model_predictions: List of model predictions

        Returns:
            Convergence score [0, 1]
        """
        confidences = [m.confidence for m in model_predictions]
        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)

        # Lower variance = higher convergence
        convergence = 1.0 - min(1.0, variance)
        return convergence


class SLAOptimizationAdapter(IntegrationAdapter):
    """Adapter for Planset 013 (SLA Optimization).

    Provides predictions with SLA-relevant metadata for resource optimization.
    """

    def _normalize_prediction(self, pred: Any) -> float:
        """Normalize prediction to float value.

        Args:
            pred: Prediction value (string or numeric)

        Returns:
            Normalized float
        """
        if isinstance(pred, str):
            return 1.0 if pred == "positive" else 0.0
        elif isinstance(pred, (int, float)):
            return float(pred)
        else:
            return 0.5

    def adapt(self, prediction: EnsemblePrediction) -> Dict[str, Any]:
        """Adapt prediction for SLA optimization system.

        Args:
            prediction: Ensemble prediction

        Returns:
            Prediction formatted for SLA optimization
        """
        sla_risk = self._calculate_sla_risk(prediction)

        return {
            "prediction": self._normalize_prediction(prediction.prediction),
            "confidence": prediction.confidence,
            "sla_risk_level": sla_risk["level"],
            "sla_risk_score": sla_risk["score"],
            "escalated": prediction.escalated,
            "requires_attention": sla_risk["level"] in ["high", "critical"],
            "recommended_action": self._recommend_action(sla_risk),
            "execution_time_ms": prediction.total_execution_time_ms,
            "timestamp": prediction.timestamp,
            "model_agreement": self._calculate_agreement(prediction.model_predictions),
            "uncertainty": 1.0 - prediction.confidence,
        }

    def _calculate_sla_risk(self, prediction: EnsemblePrediction) -> Dict[str, Any]:
        """Calculate SLA risk level.

        Args:
            prediction: Ensemble prediction

        Returns:
            Risk assessment dictionary
        """
        risk_factors = []

        # Low confidence = risk
        if prediction.confidence < 0.60:
            risk_factors.append(0.4)

        # Escalated = risk
        if prediction.escalated:
            risk_factors.append(0.3)

        # High execution time = risk
        if prediction.total_execution_time_ms > 150:
            risk_factors.append(0.2)

        # Calculate combined risk
        if not risk_factors:
            risk_score = 0.0
        else:
            risk_score = min(1.0, sum(risk_factors))

        if risk_score >= 0.7:
            risk_level = "critical"
        elif risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {"score": risk_score, "level": risk_level}

    def _recommend_action(self, sla_risk: Dict[str, Any]) -> str:
        """Recommend action based on SLA risk.

        Args:
            sla_risk: Risk assessment

        Returns:
            Recommended action
        """
        risk_level = sla_risk["level"]

        if risk_level == "critical":
            return "immediate_review_required"
        elif risk_level == "high":
            return "priority_monitoring"
        elif risk_level == "medium":
            return "standard_monitoring"
        else:
            return "normal_operation"

    def _calculate_agreement(self, model_predictions: List[ModelPrediction]) -> float:
        """Calculate model agreement (inverse of disagreement).

        Args:
            model_predictions: List of model predictions

        Returns:
            Agreement score [0, 1]
        """
        if len(model_predictions) < 2:
            return 1.0

        predictions = []
        for p in model_predictions:
            if isinstance(p.prediction, str):
                predictions.append(1.0 if p.prediction == "positive" else 0.0)
            else:
                predictions.append(float(p.prediction))

        # Calculate variance
        mean_pred = sum(predictions) / len(predictions)
        variance = sum((p - mean_pred) ** 2 for p in predictions) / len(predictions)

        # Agreement = 1 - variance
        agreement = 1.0 - min(1.0, variance * 2)
        return max(0.0, agreement)


class AdapterFactory:
    """Factory for creating integration adapters."""

    _adapters = {
        "anomaly_correlation": AnomalyCorrelationAdapter,
        "forecasting": ForecastingAdapter,
        "sla_optimization": SLAOptimizationAdapter,
    }

    @classmethod
    def get_adapter(cls, adapter_type: str) -> IntegrationAdapter:
        """Get adapter instance by type.

        Args:
            adapter_type: Type of adapter

        Returns:
            Integration adapter instance

        Raises:
            ValueError: If adapter type not found
        """
        if adapter_type not in cls._adapters:
            raise ValueError(f"Unknown adapter type: {adapter_type}")

        return cls._adapters[adapter_type]()

    @classmethod
    def register_adapter(cls, name: str, adapter_class: type) -> None:
        """Register custom adapter.

        Args:
            name: Adapter name
            adapter_class: Adapter class
        """
        cls._adapters[name] = adapter_class


def adapt_prediction_for_downstream(
    prediction: EnsemblePrediction,
    target_system: str,
) -> Dict[str, Any]:
    """Adapt prediction for specific downstream system.

    Args:
        prediction: Ensemble prediction
        target_system: Target system ('anomaly_correlation', 'forecasting', 'sla_optimization')

    Returns:
        Adapted prediction dictionary

    Raises:
        ValueError: If target system not supported
    """
    adapter = AdapterFactory.get_adapter(target_system)
    return adapter.adapt(prediction)


def batch_adapt_predictions(
    predictions: List[EnsemblePrediction],
    target_system: str,
) -> List[Dict[str, Any]]:
    """Batch adapt predictions for downstream system.

    Args:
        predictions: List of ensemble predictions
        target_system: Target system

    Returns:
        List of adapted predictions
    """
    adapter = AdapterFactory.get_adapter(target_system)
    return [adapter.adapt(pred) for pred in predictions]
