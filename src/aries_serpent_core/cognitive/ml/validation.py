"""
Long-term Plan 2 Phase 2.4: Validation & Tuning Module

This module provides ML model validation, hyperparameter tuning,
performance tracking, and model registry functionality.

Security Note: This module uses the standard `random` module for
hyperparameter search (random_search). This is intentional and acceptable
because these random values are used for ML experimentation (selecting
parameter combinations), not for security/cryptographic purposes.
"""

from __future__ import annotations

import json
import random  # nosec B311 - used for ML hyperparameter search, not security
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class MetricType(Enum):
    """Types of metrics to track."""

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LOSS = "loss"


@dataclass
class ValidationMetrics:
    """Container for validation metrics."""

    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    fold_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "confusion_matrix": self.confusion_matrix,
            "fold_scores": self.fold_scores,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationMetrics:
        """Create from dictionary."""
        return cls(
            accuracy=data.get("accuracy", 0.0),
            precision=data.get("precision", 0.0),
            recall=data.get("recall", 0.0),
            f1_score=data.get("f1_score", 0.0),
            confusion_matrix=data.get("confusion_matrix", {}),
            fold_scores=data.get("fold_scores", []),
        )


@dataclass
class TuningResult:
    """Result of hyperparameter tuning."""

    best_params: dict[str, Any]
    best_score: float
    all_results: list[dict[str, Any]]
    search_method: str
    iterations: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "best_params": self.best_params,
            "best_score": self.best_score,
            "all_results": self.all_results,
            "search_method": self.search_method,
            "iterations": self.iterations,
        }


@dataclass
class ModelVersion:
    """Model version metadata."""

    version: str
    model_type: str
    metrics: ValidationMetrics
    created_at: str
    params: dict[str, Any]
    status: str = "staged"  # staged, production, archived

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "model_type": self.model_type,
            "metrics": self.metrics.to_dict(),
            "created_at": self.created_at,
            "params": self.params,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelVersion:
        """Create from dictionary."""
        return cls(
            version=data["version"],
            model_type=data["model_type"],
            metrics=ValidationMetrics.from_dict(data.get("metrics", {})),
            created_at=data["created_at"],
            params=data.get("params", {}),
            status=data.get("status", "staged"),
        )


class ModelValidator:
    """Validates ML models with cross-validation and metrics."""

    def __init__(self, n_folds: int = 5):
        """Initialize validator.

        Args:
            n_folds: Number of folds for cross-validation
        """
        self.n_folds = n_folds
        self._last_metrics: ValidationMetrics | None = None

    def validate(
        self,
        model: Any,
        X: list[list[float]],
        y: list[str],
        fit_method: str = "fit",
        predict_method: str = "predict",
    ) -> ValidationMetrics:
        """Perform k-fold cross-validation.

        Args:
            model: Model with fit and predict methods
            X: Feature vectors
            y: Labels
            fit_method: Name of fit method
            predict_method: Name of predict method

        Returns:
            Validation metrics
        """
        if len(X) == 0 or len(y) == 0:
            return ValidationMetrics()

        # Shuffle data
        indices = list(range(len(X)))
        random.shuffle(indices)
        X_shuffled = [X[i] for i in indices]
        y_shuffled = [y[i] for i in indices]

        # Calculate fold size
        fold_size = max(1, len(X) // self.n_folds)
        fold_scores = []
        all_predictions = []
        all_true = []

        for fold in range(self.n_folds):
            # Split into train and validation
            start = fold * fold_size
            end = min(start + fold_size, len(X))

            X_val = X_shuffled[start:end]
            y_val = y_shuffled[start:end]
            X_train = X_shuffled[:start] + X_shuffled[end:]
            y_train = y_shuffled[:start] + y_shuffled[end:]

            if len(X_train) == 0 or len(X_val) == 0:
                continue

            # Train and predict
            fit_fn = getattr(model, fit_method, None)
            predict_fn = getattr(model, predict_method, None)

            if fit_fn and predict_fn:
                fit_fn(X_train, y_train)
                predictions = predict_fn(X_val)

                # Calculate fold accuracy
                correct = sum(1 for p, t in zip(predictions, y_val, strict=False) if p == t)
                fold_accuracy = correct / len(y_val) if y_val else 0
                fold_scores.append(fold_accuracy)

                all_predictions.extend(predictions)
                all_true.extend(y_val)

        # Calculate overall metrics
        metrics = self._calculate_metrics(all_true, all_predictions)
        metrics.fold_scores = fold_scores

        self._last_metrics = metrics
        return metrics

    def _calculate_metrics(
        self,
        y_true: list[str],
        y_pred: list[str],
    ) -> ValidationMetrics:
        """Calculate classification metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Validation metrics
        """
        if not y_true or not y_pred:
            return ValidationMetrics()

        # Confusion matrix
        labels = sorted(set(y_true) | set(y_pred))
        confusion = {label: dict.fromkeys(labels, 0) for label in labels}

        for true, pred in zip(y_true, y_pred, strict=False):
            confusion[true][pred] += 1

        # Accuracy
        correct = sum(1 for t, p in zip(y_true, y_pred, strict=False) if t == p)
        accuracy = correct / len(y_true)

        # Per-class precision and recall
        precisions = []
        recalls = []

        for label in labels:
            tp = confusion[label][label]
            fp = sum(confusion[other][label] for other in labels if other != label)
            fn = sum(confusion[label][other] for other in labels if other != label)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0

            precisions.append(precision)
            recalls.append(recall)

        # Macro averages
        avg_precision = sum(precisions) / len(precisions) if precisions else 0
        avg_recall = sum(recalls) / len(recalls) if recalls else 0

        # F1 score
        f1 = (
            2 * avg_precision * avg_recall / (avg_precision + avg_recall)
            if (avg_precision + avg_recall) > 0
            else 0
        )

        return ValidationMetrics(
            accuracy=accuracy,
            precision=avg_precision,
            recall=avg_recall,
            f1_score=f1,
            confusion_matrix=confusion,
        )

    def get_last_metrics(self) -> ValidationMetrics | None:
        """Get metrics from last validation."""
        return self._last_metrics


class HyperparameterTuner:
    """Tunes model hyperparameters using grid or random search."""

    def __init__(
        self,
        validator: ModelValidator | None = None,
        metric: MetricType = MetricType.ACCURACY,
    ):
        """Initialize tuner.

        Args:
            validator: Model validator instance
            metric: Metric to optimize
        """
        self.validator = validator or ModelValidator()
        self.metric = metric
        self._last_result: TuningResult | None = None

    def grid_search(
        self,
        model_factory: Callable[..., Any],
        param_grid: dict[str, list[Any]],
        X: list[list[float]],
        y: list[str],
    ) -> TuningResult:
        """Perform grid search over parameter space.

        Args:
            model_factory: Function that creates model with params
            param_grid: Dictionary of parameter names to value lists
            X: Feature vectors
            y: Labels

        Returns:
            Tuning result with best parameters
        """
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        combinations = self._generate_combinations(param_names, param_values)

        all_results = []
        best_score = -1
        best_params: dict[str, Any] = {}

        for params in combinations:
            model = model_factory(**params)
            metrics = self.validator.validate(model, X, y)
            score = self._get_metric_value(metrics)

            all_results.append(
                {
                    "params": params,
                    "score": score,
                    "metrics": metrics.to_dict(),
                }
            )

            if score > best_score:
                best_score = score  # type: ignore[assignment]
                best_params = params

        result = TuningResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            search_method="grid",
            iterations=len(combinations),
        )

        self._last_result = result
        return result

    def random_search(
        self,
        model_factory: Callable[..., Any],
        param_distributions: dict[str, list[Any]],
        X: list[list[float]],
        y: list[str],
        n_iterations: int = 10,
    ) -> TuningResult:
        """Perform random search over parameter space.

        Args:
            model_factory: Function that creates model with params
            param_distributions: Dictionary of parameter names to value distributions
            X: Feature vectors
            y: Labels
            n_iterations: Number of random samples

        Returns:
            Tuning result with best parameters
        """
        all_results = []
        best_score = -1
        best_params: dict[str, Any] = {}

        for _ in range(n_iterations):
            # Sample random parameters
            params = {
                name: random.choice(values) for name, values in param_distributions.items()
            }  # nosec B311 — non-cryptographic ML sampling/shuffling

            model = model_factory(**params)
            metrics = self.validator.validate(model, X, y)
            score = self._get_metric_value(metrics)

            all_results.append(
                {
                    "params": params,
                    "score": score,
                    "metrics": metrics.to_dict(),
                }
            )

            if score > best_score:
                best_score = score  # type: ignore[assignment]
                best_params = params

        result = TuningResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            search_method="random",
            iterations=n_iterations,
        )

        self._last_result = result
        return result

    def _generate_combinations(
        self,
        names: list[str],
        values: list[list[Any]],
    ) -> list[dict[str, Any]]:
        """Generate all combinations of parameters."""
        if not names:
            return [{}]

        combinations = []
        first_name = names[0]
        first_values = values[0]
        rest_combinations = self._generate_combinations(names[1:], values[1:])

        for value in first_values:
            for rest in rest_combinations:
                combo = {first_name: value}
                combo.update(rest)
                combinations.append(combo)

        return combinations

    def _get_metric_value(self, metrics: ValidationMetrics) -> float:
        """Get value of target metric."""
        if self.metric == MetricType.ACCURACY:
            return metrics.accuracy
        if self.metric == MetricType.PRECISION:
            return metrics.precision
        if self.metric == MetricType.RECALL:
            return metrics.recall
        if self.metric == MetricType.F1_SCORE:
            return metrics.f1_score
        return metrics.accuracy

    def get_last_result(self) -> TuningResult | None:
        """Get result from last tuning."""
        return self._last_result


@dataclass
class PerformanceRecord:
    """Record of performance at a point in time."""

    timestamp: str
    metrics: ValidationMetrics
    model_version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "metrics": self.metrics.to_dict(),
            "model_version": self.model_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerformanceRecord:
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            metrics=ValidationMetrics.from_dict(data.get("metrics", {})),
            model_version=data["model_version"],
        )


class PerformanceTracker:
    """Tracks model performance over time."""

    def __init__(self, alert_threshold: float = 0.1):
        """Initialize tracker.

        Args:
            alert_threshold: Threshold for performance drop alerts
        """
        self.alert_threshold = alert_threshold
        self._records: list[PerformanceRecord] = []
        self._alerts: list[dict[str, Any]] = []

    def record(
        self,
        metrics: ValidationMetrics,
        model_version: str,
    ) -> PerformanceRecord:
        """Record performance metrics.

        Args:
            metrics: Validation metrics
            model_version: Version of model

        Returns:
            Performance record
        """
        record = PerformanceRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics=metrics,
            model_version=model_version,
        )

        # Check for performance drop
        if self._records:
            last_accuracy = self._records[-1].metrics.accuracy
            drop = last_accuracy - metrics.accuracy

            if drop > self.alert_threshold:
                self._alerts.append(
                    {
                        "type": "performance_drop",
                        "timestamp": record.timestamp,
                        "previous_accuracy": last_accuracy,
                        "current_accuracy": metrics.accuracy,
                        "drop": drop,
                    }
                )

        self._records.append(record)
        return record

    def get_trend(
        self,
        metric: MetricType = MetricType.ACCURACY,
        window: int = 5,
    ) -> dict[str, Any]:
        """Get performance trend.

        Args:
            metric: Metric to analyze
            window: Number of recent records to consider

        Returns:
            Trend analysis
        """
        if len(self._records) < 2:
            return {"trend": "insufficient_data", "change": 0.0}

        recent = self._records[-window:]
        values = [self._get_metric_value(r.metrics, metric) for r in recent]

        # Calculate trend
        if len(values) >= 2:
            change = values[-1] - values[0]
            avg_change = change / (len(values) - 1)

            if avg_change > 0.01:
                trend = "improving"
            elif avg_change < -0.01:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            change = 0.0

        return {
            "trend": trend,
            "change": change,
            "values": values,
            "window": len(recent),
        }

    def _get_metric_value(
        self,
        metrics: ValidationMetrics,
        metric: MetricType,
    ) -> float:
        """Get value of specific metric."""
        if metric == MetricType.ACCURACY:
            return metrics.accuracy
        if metric == MetricType.PRECISION:
            return metrics.precision
        if metric == MetricType.RECALL:
            return metrics.recall
        if metric == MetricType.F1_SCORE:
            return metrics.f1_score
        return metrics.accuracy

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get all performance alerts."""
        return self._alerts

    def get_records(self) -> list[PerformanceRecord]:
        """Get all performance records."""
        return self._records

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self._alerts = []

    def save(self, path: Path) -> None:
        """Save tracker state to file."""
        data = {
            "records": [r.to_dict() for r in self._records],
            "alerts": self._alerts,
            "alert_threshold": self.alert_threshold,
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> PerformanceTracker:
        """Load tracker from file."""
        data = json.loads(path.read_text())
        tracker = cls(alert_threshold=data.get("alert_threshold", 0.1))
        tracker._records = [PerformanceRecord.from_dict(r) for r in data.get("records", [])]
        tracker._alerts = data.get("alerts", [])
        return tracker


class ModelRegistry:
    """Registry for model versions with A/B testing support."""

    def __init__(self, storage_path: Path | None = None):
        """Initialize registry.

        Args:
            storage_path: Path to store registry data
        """
        self.storage_path = storage_path
        self._versions: dict[str, ModelVersion] = {}
        self._production_version: str | None = None
        self._ab_tests: list[dict[str, Any]] = []

    def register(
        self,
        version: str,
        model_type: str,
        metrics: ValidationMetrics,
        params: dict[str, Any] | None = None,
    ) -> ModelVersion:
        """Register a new model version.

        Args:
            version: Version string
            model_type: Type of model
            metrics: Validation metrics
            params: Model parameters

        Returns:
            Registered model version
        """
        model_version = ModelVersion(
            version=version,
            model_type=model_type,
            metrics=metrics,
            created_at=datetime.now(timezone.utc).isoformat(),
            params=params or {},
            status="staged",
        )

        self._versions[version] = model_version
        return model_version

    def promote_to_production(self, version: str) -> bool:
        """Promote a version to production.

        Args:
            version: Version to promote

        Returns:
            True if promoted successfully
        """
        if version not in self._versions:
            return False

        # Archive current production
        if self._production_version:
            self._versions[self._production_version].status = "archived"

        # Promote new version
        self._versions[version].status = "production"
        self._production_version = version
        return True

    def get_production_version(self) -> ModelVersion | None:
        """Get current production version."""
        if self._production_version:
            return self._versions.get(self._production_version)
        return None

    def get_version(self, version: str) -> ModelVersion | None:
        """Get specific version."""
        return self._versions.get(version)

    def list_versions(self) -> list[ModelVersion]:
        """List all versions."""
        return list(self._versions.values())

    def start_ab_test(
        self,
        version_a: str,
        version_b: str,
        traffic_split: float = 0.5,
    ) -> dict[str, Any]:
        """Start an A/B test between two versions.

        Args:
            version_a: First version
            version_b: Second version
            traffic_split: Fraction of traffic to version A

        Returns:
            A/B test configuration
        """
        ab_test = {
            "id": f"ab_{len(self._ab_tests)}",
            "version_a": version_a,
            "version_b": version_b,
            "traffic_split": traffic_split,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "results": {"a_samples": 0, "b_samples": 0},
        }
        self._ab_tests.append(ab_test)
        return ab_test

    def get_ab_tests(self) -> list[dict[str, Any]]:
        """Get all A/B tests."""
        return self._ab_tests

    def route_ab_traffic(self, test_id: str) -> str | None:
        """Route traffic for A/B test.

        Args:
            test_id: A/B test ID

        Returns:
            Version to use, or None if test not found
        """
        test = next((t for t in self._ab_tests if t["id"] == test_id), None)
        if not test or test["status"] != "running":
            return None

        # Random routing based on traffic split
        if (
            random.random() < test["traffic_split"]
        ):  # nosec B311 — non-cryptographic ML sampling/shuffling
            test["results"]["a_samples"] += 1
            return test["version_a"]
        test["results"]["b_samples"] += 1
        return test["version_b"]

    def compare_versions(
        self,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """Compare two model versions.

        Args:
            version_a: First version
            version_b: Second version

        Returns:
            Comparison results
        """
        a = self._versions.get(version_a)
        b = self._versions.get(version_b)

        if not a or not b:
            return {"error": "Version not found"}

        return {
            "version_a": {
                "version": a.version,
                "accuracy": a.metrics.accuracy,
                "f1_score": a.metrics.f1_score,
            },
            "version_b": {
                "version": b.version,
                "accuracy": b.metrics.accuracy,
                "f1_score": b.metrics.f1_score,
            },
            "winner": version_a if a.metrics.accuracy > b.metrics.accuracy else version_b,
            "accuracy_diff": a.metrics.accuracy - b.metrics.accuracy,
        }

    def save(self) -> None:
        """Save registry to storage."""
        if not self.storage_path:
            return

        data = {
            "versions": {k: v.to_dict() for k, v in self._versions.items()},
            "production_version": self._production_version,
            "ab_tests": self._ab_tests,
        }
        self.storage_path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> ModelRegistry:
        """Load registry from storage."""
        data = json.loads(path.read_text())
        registry = cls(storage_path=path)
        registry._versions = {
            k: ModelVersion.from_dict(v) for k, v in data.get("versions", {}).items()
        }
        registry._production_version = data.get("production_version")
        registry._ab_tests = data.get("ab_tests", [])
        return registry


class TuningPipeline:
    """Complete end-to-end tuning pipeline."""

    def __init__(
        self,
        validator: ModelValidator | None = None,
        tuner: HyperparameterTuner | None = None,
        tracker: PerformanceTracker | None = None,
        registry: ModelRegistry | None = None,
    ):
        """Initialize pipeline.

        Args:
            validator: Model validator
            tuner: Hyperparameter tuner
            tracker: Performance tracker
            registry: Model registry
        """
        self.validator = validator or ModelValidator()
        self.tuner = tuner or HyperparameterTuner(self.validator)
        self.tracker = tracker or PerformanceTracker()
        self.registry = registry or ModelRegistry()
        self._version_counter = 0

    def run_tuning_pipeline(
        self,
        model_factory: Callable[..., Any],
        model_type: str,
        param_grid: dict[str, list[Any]],
        X: list[list[float]],
        y: list[str],
        search_method: str = "grid",
        n_iterations: int = 10,
    ) -> dict[str, Any]:
        """Run complete tuning pipeline.

        Args:
            model_factory: Function to create model
            model_type: Type of model
            param_grid: Parameter grid for tuning
            X: Feature vectors
            y: Labels
            search_method: 'grid' or 'random'
            n_iterations: Iterations for random search

        Returns:
            Pipeline results
        """
        # Tune hyperparameters
        if search_method == "grid":
            result = self.tuner.grid_search(model_factory, param_grid, X, y)
        else:
            result = self.tuner.random_search(model_factory, param_grid, X, y, n_iterations)

        # Train final model with best params
        final_model = model_factory(**result.best_params)
        metrics = self.validator.validate(final_model, X, y)

        # Generate version
        self._version_counter += 1
        version = f"v{self._version_counter}.0.0"

        # Register model
        model_version = self.registry.register(
            version=version,
            model_type=model_type,
            metrics=metrics,
            params=result.best_params,
        )

        # Track performance
        self.tracker.record(metrics, version)

        return {
            "version": version,
            "best_params": result.best_params,
            "metrics": metrics.to_dict(),
            "search_iterations": result.iterations,
            "model_version": model_version.to_dict(),
        }

    def validate_and_register(
        self,
        model: Any,
        model_type: str,
        X: list[list[float]],
        y: list[str],
        params: dict[str, Any] | None = None,
    ) -> ModelVersion:
        """Validate model and register if performance is good.

        Args:
            model: Trained model
            model_type: Type of model
            X: Feature vectors
            y: Labels
            params: Model parameters

        Returns:
            Registered model version
        """
        # Validate
        metrics = self.validator.validate(model, X, y)

        # Generate version
        self._version_counter += 1
        version = f"v{self._version_counter}.0.0"

        # Register
        model_version = self.registry.register(
            version=version,
            model_type=model_type,
            metrics=metrics,
            params=params,
        )

        # Track
        self.tracker.record(metrics, version)

        return model_version

    def auto_promote(self, threshold: float = 0.8) -> bool:
        """Automatically promote best model if threshold met.

        Args:
            threshold: Minimum accuracy for promotion

        Returns:
            True if a model was promoted
        """
        versions = self.registry.list_versions()
        if not versions:
            return False

        # Find best staged version
        staged = [v for v in versions if v.status == "staged"]
        if not staged:
            return False

        best = max(staged, key=lambda v: v.metrics.accuracy)

        if best.metrics.accuracy >= threshold:
            return self.registry.promote_to_production(best.version)

        return False

    def get_summary(self) -> dict[str, Any]:
        """Get pipeline summary."""
        versions = self.registry.list_versions()
        production = self.registry.get_production_version()
        trend = self.tracker.get_trend()

        return {
            "total_versions": len(versions),
            "production_version": production.version if production else None,
            "performance_trend": trend,
            "alerts": self.tracker.get_alerts(),
            "staged_count": sum(1 for v in versions if v.status == "staged"),
            "archived_count": sum(1 for v in versions if v.status == "archived"),
        }


# Convenience functions


def create_validator(n_folds: int = 5) -> ModelValidator:
    """Create a model validator."""
    return ModelValidator(n_folds=n_folds)


def create_tuner(
    metric: MetricType = MetricType.ACCURACY,
) -> HyperparameterTuner:
    """Create a hyperparameter tuner."""
    return HyperparameterTuner(metric=metric)


def create_tracker(alert_threshold: float = 0.1) -> PerformanceTracker:
    """Create a performance tracker."""
    return PerformanceTracker(alert_threshold=alert_threshold)


def create_registry(storage_path: Path | None = None) -> ModelRegistry:
    """Create a model registry."""
    return ModelRegistry(storage_path=storage_path)


def create_tuning_pipeline() -> TuningPipeline:
    """Create a complete tuning pipeline."""
    return TuningPipeline()
