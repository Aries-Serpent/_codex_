"""Model diversity validation and ensemble evaluation."""

import logging
from typing import Dict, List, Any, Tuple
import numpy as np
from scipy.stats import spearmanr, pearsonr
from dataclasses import dataclass

from src.codex.ensemble.ensemble_predictor import EnsemblePredictor, EnsembleConfig
from src.codex.ensemble.types import ModelType, EnsemblePrediction

logger = logging.getLogger(__name__)


@dataclass
class DiversityMetrics:
    """Model diversity metrics."""

    pearson_heuristic_ml: float
    pearson_ml_symbolic: float
    pearson_heuristic_symbolic: float
    spearman_heuristic_ml: float
    spearman_ml_symbolic: float
    spearman_heuristic_symbolic: float
    avg_pearson_correlation: float
    avg_spearman_correlation: float
    diversity_score: float  # 1 - avg_correlation (higher is better)
    diversity_acceptable: bool  # < 0.6 threshold


@dataclass
class EnsembleEvaluationResult:
    """Comprehensive ensemble evaluation result."""

    ensemble_accuracy: float
    best_single_model_accuracy: float
    accuracy_improvement: float
    improvement_meets_gate: bool
    model_accuracies: Dict[str, float]
    diversity_metrics: DiversityMetrics
    diversity_acceptable: bool
    median_p99_latency_ms: float
    p99_latency_meets_gate: bool
    median_f1_score: float
    f1_meets_gate: bool
    calibration_metrics: Dict[str, Any]
    false_positive_rate: float
    false_positive_acceptable: bool


class DiversityValidator:
    """Validate model diversity in ensemble."""

    @staticmethod
    def calculate_diversity(
        predictions_list: List[List[float]],
    ) -> DiversityMetrics:
        """Calculate model diversity metrics.

        Args:
            predictions_list: List of model prediction arrays

        Returns:
            DiversityMetrics with correlation analysis
        """
        if len(predictions_list) != 3:
            raise ValueError("Expected 3 model predictions")

        heuristic_preds = np.array(predictions_list[0])
        ml_preds = np.array(predictions_list[1])
        symbolic_preds = np.array(predictions_list[2])

        # Pearson correlation (handle NaN from constant inputs)
        try:
            pearson_hm, _ = pearsonr(heuristic_preds, ml_preds)
        except:
            pearson_hm = 0.0
        try:
            pearson_ms, _ = pearsonr(ml_preds, symbolic_preds)
        except:
            pearson_ms = 0.0
        try:
            pearson_hs, _ = pearsonr(heuristic_preds, symbolic_preds)
        except:
            pearson_hs = 0.0

        # Spearman correlation (handle NaN from constant inputs)
        try:
            spearman_hm, _ = spearmanr(heuristic_preds, ml_preds)
        except:
            spearman_hm = 0.0
        try:
            spearman_ms, _ = spearmanr(ml_preds, symbolic_preds)
        except:
            spearman_ms = 0.0
        try:
            spearman_hs, _ = spearmanr(heuristic_preds, symbolic_preds)
        except:
            spearman_hs = 0.0

        # Handle NaN values
        pearson_hm = 0.0 if np.isnan(pearson_hm) else abs(pearson_hm)
        pearson_ms = 0.0 if np.isnan(pearson_ms) else abs(pearson_ms)
        pearson_hs = 0.0 if np.isnan(pearson_hs) else abs(pearson_hs)
        spearman_hm = 0.0 if np.isnan(spearman_hm) else abs(spearman_hm)
        spearman_ms = 0.0 if np.isnan(spearman_ms) else abs(spearman_ms)
        spearman_hs = 0.0 if np.isnan(spearman_hs) else abs(spearman_hs)

        # Average correlations
        avg_pearson = (pearson_hm + pearson_ms + pearson_hs) / 3.0
        avg_spearman = (spearman_hm + spearman_ms + spearman_hs) / 3.0

        # Diversity score (inverse of correlation)
        diversity_score = 1.0 - avg_pearson

        # Check if diversity is acceptable (correlation < 0.6)
        diversity_acceptable = avg_pearson < 0.6

        return DiversityMetrics(
            pearson_heuristic_ml=float(pearson_hm),
            pearson_ml_symbolic=float(pearson_ms),
            pearson_heuristic_symbolic=float(pearson_hs),
            spearman_heuristic_ml=float(spearman_hm),
            spearman_ml_symbolic=float(spearman_ms),
            spearman_heuristic_symbolic=float(spearman_hs),
            avg_pearson_correlation=float(avg_pearson),
            avg_spearman_correlation=float(avg_spearman),
            diversity_score=float(diversity_score),
            diversity_acceptable=diversity_acceptable,
        )

    @staticmethod
    def print_diversity_report(metrics: DiversityMetrics) -> None:
        """Print diversity metrics report.

        Args:
            metrics: DiversityMetrics object
        """
        print("\n" + "=" * 70)
        print("MODEL DIVERSITY ANALYSIS")
        print("=" * 70)
        print(f"\nPearson Correlations:")
        print(f"  Heuristic ↔ ML:        {metrics.pearson_heuristic_ml:+.4f}")
        print(f"  ML ↔ Symbolic:         {metrics.pearson_ml_symbolic:+.4f}")
        print(f"  Heuristic ↔ Symbolic:  {metrics.pearson_heuristic_symbolic:+.4f}")
        print(f"  Average:               {metrics.avg_pearson_correlation:.4f}")
        print(f"\nSpearman Correlations:")
        print(f"  Heuristic ↔ ML:        {metrics.spearman_heuristic_ml:+.4f}")
        print(f"  ML ↔ Symbolic:         {metrics.spearman_ml_symbolic:+.4f}")
        print(f"  Heuristic ↔ Symbolic:  {metrics.spearman_heuristic_symbolic:+.4f}")
        print(f"  Average:               {metrics.avg_spearman_correlation:.4f}")
        print(f"\nDiversity Metrics:")
        print(f"  Diversity Score:       {metrics.diversity_score:.4f} (1 = perfect diversity)")
        print(f"  Acceptable (<0.6):     {'✓ PASS' if metrics.diversity_acceptable else '✗ FAIL'}")
        print("=" * 70 + "\n")


class EnsembleEvaluator:
    """Comprehensive ensemble evaluator."""

    def __init__(self, predictor: EnsemblePredictor, config: EnsembleConfig):
        """Initialize ensemble evaluator.

        Args:
            predictor: EnsemblePredictor instance
            config: EnsembleConfig instance
        """
        self.predictor = predictor
        self.config = config

    def generate_test_data(self, n_samples: int = 100) -> Tuple[List[Dict[str, Any]], List[int]]:
        """Generate synthetic test data.

        Args:
            n_samples: Number of test samples

        Returns:
            Tuple of (features_list, labels)
        """
        features_list = []
        labels = []

        for _ in range(n_samples):
            confidence = np.random.uniform(0.2, 0.95)
            frequency = np.random.randint(10, 100)
            days_old = np.random.randint(0, 90)
            priority = np.random.randint(1, 10)
            category = np.random.choice(["critical", "urgent", "high", "general", "low"])

            features = {
                "confidence": confidence,
                "frequency": frequency,
                "days_old": days_old,
                "priority": priority,
                "category": category,
            }
            features_list.append(features)

            # Generate synthetic label based on features
            score = confidence * 0.3 + (frequency / 100) * 0.3 + (priority / 10) * 0.2
            label = 1 if score >= 0.5 else 0
            labels.append(label)

        return features_list, labels

    def evaluate_ensemble(
        self,
        features_list: List[Dict[str, Any]],
        labels: List[int],
    ) -> EnsembleEvaluationResult:
        """Evaluate ensemble performance against gate criteria.

        Args:
            features_list: List of feature dictionaries
            labels: List of true labels

        Returns:
            EnsembleEvaluationResult with all metrics
        """
        logger.info(f"Evaluating ensemble on {len(features_list)} samples...")

        # Make predictions
        predictions = self.predictor.batch_predict(features_list)

        # Calculate metrics
        ensemble_preds = []
        model_preds = {
            ModelType.HEURISTIC: [],
            ModelType.MACHINE_LEARNING: [],
            ModelType.SYMBOLIC: [],
        }
        latencies = []
        confidences = []
        escalation_count = 0

        for pred in predictions:
            ensemble_preds.append(pred.prediction)
            confidences.append(pred.confidence)
            latencies.append(pred.total_execution_time_ms)
            if pred.escalated:
                escalation_count += 1

            for model_pred in pred.model_predictions:
                model_type = model_pred.model_type
                if isinstance(model_pred.prediction, str):
                    score = 1.0 if model_pred.prediction == "positive" else 0.0
                else:
                    score = float(model_pred.prediction)
                model_preds[model_type].append(score)

        # Convert to numpy arrays
        ensemble_preds_array = np.array(
            [1.0 if p == "positive" else 0.0 for p in ensemble_preds]
        )
        labels_array = np.array(labels)
        latencies_array = np.array(latencies)
        confidences_array = np.array(confidences)

        # Calculate ensemble accuracy
        ensemble_accuracy = np.mean(ensemble_preds_array == labels_array)

        # Calculate individual model accuracies
        model_accuracies = {}
        for model_type, preds in model_preds.items():
            if preds:
                acc = np.mean(np.array(preds) == labels_array)
                model_accuracies[model_type.value] = float(acc)

        best_single_model_accuracy = max(model_accuracies.values())
        accuracy_improvement = ensemble_accuracy - best_single_model_accuracy

        # Calculate F1 score
        tp = np.sum((ensemble_preds_array == 1) & (labels_array == 1))
        fp = np.sum((ensemble_preds_array == 1) & (labels_array == 0))
        fn = np.sum((ensemble_preds_array == 0) & (labels_array == 1))
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Calculate latency metrics
        p99_latency = float(np.percentile(latencies_array, 99))

        # Calculate model diversity
        diversity_metrics = DiversityValidator.calculate_diversity(
            [model_preds[ModelType.HEURISTIC], model_preds[ModelType.MACHINE_LEARNING],
             model_preds[ModelType.SYMBOLIC]]
        )

        # Calculate false positive rate
        false_positives = fp
        actual_negatives = np.sum(labels_array == 0)
        false_positive_rate = false_positives / actual_negatives if actual_negatives > 0 else 0.0

        # Check gate criteria
        improvement_meets_gate = accuracy_improvement >= 0.03
        p99_latency_meets_gate = p99_latency < 200.0
        f1_meets_gate = f1_score > 0.90
        false_positive_acceptable = false_positive_rate < 0.05

        result = EnsembleEvaluationResult(
            ensemble_accuracy=float(ensemble_accuracy),
            best_single_model_accuracy=float(best_single_model_accuracy),
            accuracy_improvement=float(accuracy_improvement),
            improvement_meets_gate=improvement_meets_gate,
            model_accuracies=model_accuracies,
            diversity_metrics=diversity_metrics,
            diversity_acceptable=diversity_metrics.diversity_acceptable,
            median_p99_latency_ms=p99_latency,
            p99_latency_meets_gate=p99_latency_meets_gate,
            median_f1_score=float(f1_score),
            f1_meets_gate=f1_meets_gate,
            calibration_metrics={
                "mean_confidence": float(np.mean(confidences_array)),
                "std_confidence": float(np.std(confidences_array)),
                "min_confidence": float(np.min(confidences_array)),
                "max_confidence": float(np.max(confidences_array)),
                "calibration_error": float(abs(np.mean(confidences_array) - ensemble_accuracy)),
                "escalation_rate": escalation_count / len(predictions) if predictions else 0.0,
            },
            false_positive_rate=false_positive_rate,
            false_positive_acceptable=false_positive_acceptable,
        )

        return result

    @staticmethod
    def print_evaluation_report(result: EnsembleEvaluationResult) -> None:
        """Print comprehensive evaluation report.

        Args:
            result: EnsembleEvaluationResult object
        """
        print("\n" + "=" * 70)
        print("ENSEMBLE EVALUATION REPORT")
        print("=" * 70)

        print(f"\nAccuracy Metrics:")
        print(f"  Ensemble Accuracy:          {result.ensemble_accuracy:.4f}")
        print(f"  Best Single Model:          {result.best_single_model_accuracy:.4f}")
        print(f"  Improvement:                {result.accuracy_improvement:+.4f} (Gate: ≥0.03)")
        print(f"  Status:                     {'✓ PASS' if result.improvement_meets_gate else '✗ FAIL'}")

        print(f"\nModel Accuracies:")
        for model_name, accuracy in result.model_accuracies.items():
            print(f"  {model_name:20s}: {accuracy:.4f}")

        print(f"\nF1 Score:")
        print(f"  F1 Score:                   {result.median_f1_score:.4f} (Gate: >0.90)")
        print(f"  Status:                     {'✓ PASS' if result.f1_meets_gate else '✗ FAIL'}")

        print(f"\nLatency Metrics:")
        print(f"  p99 Latency:                {result.median_p99_latency_ms:.2f}ms (Gate: <200ms)")
        print(f"  Status:                     {'✓ PASS' if result.p99_latency_meets_gate else '✗ FAIL'}")

        print(f"\nCalibration Metrics:")
        print(f"  Mean Confidence:            {result.calibration_metrics['mean_confidence']:.4f}")
        print(f"  Confidence Calibration:     {result.calibration_metrics['calibration_error']:.4f}")
        print(f"  Escalation Rate:            {result.calibration_metrics['escalation_rate']:.2%}")

        print(f"\nFalse Positive Rate:")
        print(f"  FP Rate:                    {result.false_positive_rate:.4f} (Gate: <5%)")
        print(f"  Status:                     {'✓ PASS' if result.false_positive_acceptable else '✗ FAIL'}")

        print(f"\nModel Diversity:")
        print(f"  Diversity Score:            {result.diversity_metrics.diversity_score:.4f}")
        print(f"  Avg Pearson Corr:           {result.diversity_metrics.avg_pearson_correlation:.4f}")
        print(f"  Status:                     {'✓ PASS' if result.diversity_acceptable else '✗ FAIL'}")

        gate_results = [
            result.improvement_meets_gate,
            result.p99_latency_meets_gate,
            result.f1_meets_gate,
            not (result.false_positive_rate >= 0.05),
            result.diversity_acceptable,
        ]
        gates_passed = sum(gate_results)
        gates_total = len(gate_results)

        print(f"\nOverall Gate Status: {gates_passed}/{gates_total} PASS")
        print("=" * 70 + "\n")
