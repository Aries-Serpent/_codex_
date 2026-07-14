"""Calibration and cross-validation framework."""

import logging
import time
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

import numpy as np

from src.codex.ensemble.types import (
    CrossValidationResult,
    CalibrationMetrics,
    ModelType,
)
from src.codex.ensemble.models import (
    HeuristicModel,
    MLModel,
    SymbolicModel,
)

logger = logging.getLogger(__name__)


class CalibrationFramework:
    """Cross-validation and calibration for ensemble models."""

    def __init__(self, k_folds: int = 5):
        """Initialize calibration framework.

        Args:
            k_folds: Number of folds for cross-validation
        """
        self.k_folds = k_folds

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_type: ModelType,
    ) -> List[CrossValidationResult]:
        """Perform k-fold cross-validation on a model.

        Args:
            X: Feature matrix
            y: Target values
            model_type: Type of model to validate

        Returns:
            List of cross-validation results per fold
        """
        logger.info(
            f"Starting {self.k_folds}-fold cross-validation for {model_type.value}"
        )

        # Create fold splits
        fold_size = len(X) // self.k_folds
        results = []

        for fold in range(self.k_folds):
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < self.k_folds - 1 else len(X)

            # Create train/val splits
            test_indices = set(range(start_idx, end_idx))
            train_indices = set(range(len(X))) - test_indices

            X_train = X[list(train_indices)]
            y_train = y[list(train_indices)]
            X_test = X[list(test_indices)]
            y_test = y[list(test_indices)]

            # Train and evaluate
            fold_start = time.time()
            result = self._evaluate_fold(
                X_train, y_train, X_test, y_test, model_type, fold
            )
            result.execution_time_ms = (time.time() - fold_start) * 1000

            results.append(result)
            logger.info(
                f"Fold {fold + 1}: Accuracy={result.accuracy:.3f}, "
                f"F1={result.f1_score:.3f}, Brier={result.brier_score:.3f}"
            )

        return results

    def _evaluate_fold(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_type: ModelType,
        fold_number: int,
    ) -> CrossValidationResult:
        """Evaluate a single fold.

        Args:
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            model_type: Model type
            fold_number: Fold index

        Returns:
            CrossValidationResult
        """
        # Initialize model
        if model_type == ModelType.HEURISTIC:
            model = HeuristicModel()
        elif model_type == ModelType.MACHINE_LEARNING:
            model = MLModel()
        elif model_type == ModelType.SYMBOLIC:
            model = SymbolicModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Make predictions
        predictions = []
        confidences = []

        for sample in X_test:
            try:
                # Convert sample to feature dict
                features = {f"feature_{i}": val for i, val in enumerate(sample)}
                pred = model.predict(features)

                # Extract prediction value
                if isinstance(pred.prediction, str):
                    pred_val = 1.0 if pred.prediction == "positive" else 0.0
                else:
                    pred_val = float(pred.prediction)

                predictions.append(pred_val)
                confidences.append(pred.confidence)
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                predictions.append(0.5)
                confidences.append(0.0)

        predictions = np.array(predictions)
        confidences = np.array(confidences)

        # Calculate metrics
        accuracy = self._calculate_accuracy(predictions, y_test)
        precision = self._calculate_precision(predictions, y_test)
        recall = self._calculate_recall(predictions, y_test)
        f1_score = self._calculate_f1(precision, recall)
        brier_score = self._calculate_brier_score(confidences, y_test)
        confusion_matrix = self._calculate_confusion_matrix(predictions, y_test)

        return CrossValidationResult(
            model_type=model_type,
            fold_number=fold_number,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            brier_score=brier_score,
            confusion_matrix=confusion_matrix,
            execution_time_ms=0.0,  # Updated by caller
        )

    def _calculate_accuracy(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate accuracy."""
        binary_preds = (predictions >= 0.5).astype(int)
        binary_targets = (targets >= 0.5).astype(int)
        accuracy = np.mean(binary_preds == binary_targets)
        return float(accuracy)

    def _calculate_precision(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate precision."""
        binary_preds = (predictions >= 0.5).astype(int)
        binary_targets = (targets >= 0.5).astype(int)

        tp = np.sum((binary_preds == 1) & (binary_targets == 1))
        fp = np.sum((binary_preds == 1) & (binary_targets == 0))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        return float(precision)

    def _calculate_recall(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate recall."""
        binary_preds = (predictions >= 0.5).astype(int)
        binary_targets = (targets >= 0.5).astype(int)

        tp = np.sum((binary_preds == 1) & (binary_targets == 1))
        fn = np.sum((binary_preds == 0) & (binary_targets == 1))

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return float(recall)

    def _calculate_f1(self, precision: float, recall: float) -> float:
        """Calculate F1 score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _calculate_brier_score(
        self, confidences: np.ndarray, targets: np.ndarray
    ) -> float:
        """Calculate Brier score (MSE of probabilities).

        Args:
            confidences: Predicted probabilities [0, 1]
            targets: True labels [0, 1]

        Returns:
            Brier score
        """
        binary_targets = (targets >= 0.5).astype(int)
        brier = np.mean((confidences - binary_targets) ** 2)
        return float(brier)

    def _calculate_confusion_matrix(
        self, predictions: np.ndarray, targets: np.ndarray
    ) -> Dict[str, int]:
        """Calculate confusion matrix."""
        binary_preds = (predictions >= 0.5).astype(int)
        binary_targets = (targets >= 0.5).astype(int)

        tp = int(np.sum((binary_preds == 1) & (binary_targets == 1)))
        fp = int(np.sum((binary_preds == 1) & (binary_targets == 0)))
        tn = int(np.sum((binary_preds == 0) & (binary_targets == 0)))
        fn = int(np.sum((binary_preds == 0) & (binary_targets == 1)))

        return {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
        }

    def calibrate_confidence(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray,
        model_type: ModelType,
    ) -> CalibrationMetrics:
        """Calibrate confidence scores for a model.

        Args:
            X_val: Validation features
            y_val: Validation targets
            model_type: Model type

        Returns:
            Calibration metrics
        """
        logger.info(f"Calibrating confidence for {model_type.value}")

        # Initialize model
        if model_type == ModelType.HEURISTIC:
            model = HeuristicModel()
        elif model_type == ModelType.MACHINE_LEARNING:
            model = MLModel()
        elif model_type == ModelType.SYMBOLIC:
            model = SymbolicModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Get predictions
        confidences = []
        targets = []

        for sample in X_val:
            try:
                features = {f"feature_{i}": val for i, val in enumerate(sample)}
                pred = model.predict(features)
                confidences.append(pred.confidence)
                targets.append(y_val[len(targets)])
            except Exception as e:
                logger.error(f"Prediction failed: {e}")

        confidences = np.array(confidences)
        targets = np.array(targets)

        # Calculate calibration metrics
        brier_score = self._calculate_brier_score(confidences, targets)

        # Expected Calibration Error (ECE)
        num_bins = 10
        bin_edges = np.linspace(0, 1, num_bins + 1)
        ece = 0.0
        mce = 0.0

        confidence_bins = {}

        for i in range(num_bins):
            mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
            if np.sum(mask) > 0:
                bin_confidence = np.mean(confidences[mask])
                bin_accuracy = np.mean((confidences[mask] >= 0.5) == (targets[mask] >= 0.5))
                bin_error = abs(bin_confidence - bin_accuracy)

                ece += np.sum(mask) / len(confidences) * bin_error
                mce = max(mce, bin_error)

                confidence_bins[f"bin_{i}"] = float(bin_accuracy)

        # Recommended threshold (maximizes F1)
        thresholds = np.linspace(0, 1, 11)
        best_f1 = 0.0
        best_threshold = 0.5

        for threshold in thresholds:
            preds = (confidences >= threshold).astype(int)
            targets_binary = (targets >= 0.5).astype(int)

            tp = np.sum((preds == 1) & (targets_binary == 1))
            fp = np.sum((preds == 1) & (targets_binary == 0))
            fn = np.sum((preds == 0) & (targets_binary == 1))

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        return CalibrationMetrics(
            model_type=model_type,
            brier_score=float(brier_score),
            expected_calibration_error=float(ece),
            maximum_calibration_error=float(mce),
            confidence_bins=confidence_bins,
            recommended_threshold=float(best_threshold),
        )
