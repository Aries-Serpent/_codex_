"""
Tests for Long-term Plan 2 Phase 2.4: Validation & Tuning

Tests cover:
- ModelValidator: K-fold cross-validation
- HyperparameterTuner: Grid search, random search
- PerformanceTracker: Metric tracking, alerts
- ModelRegistry: Versioning, A/B testing
- TuningPipeline: Complete pipeline
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from codex.cognitive.ml.validation import (
    HyperparameterTuner,
    MetricType,
    ModelRegistry,
    ModelValidator,
    ModelVersion,
    PerformanceRecord,
    PerformanceTracker,
    TuningPipeline,
    TuningResult,
    ValidationMetrics,
    create_registry,
    create_tracker,
    create_tuner,
    create_tuning_pipeline,
    create_validator,
)

# =============================================================================
# ValidationMetrics Tests
# =============================================================================


class TestValidationMetrics:
    """Tests for ValidationMetrics dataclass."""

    def test_create_default(self):
        """Test creating with defaults."""
        metrics = ValidationMetrics()
        assert metrics.accuracy == 0.0, "accuracy is not valid"
        assert metrics.precision == 0.0, "precision is not valid"
        assert metrics.recall == 0.0, "recall is not valid"
        assert metrics.f1_score == 0.0, "f1_score is not valid"

    def test_create_with_values(self):
        """Test creating with values."""
        metrics = ValidationMetrics(
            accuracy=0.85,
            precision=0.80,
            recall=0.90,
            f1_score=0.85,
        )
        assert metrics.accuracy == 0.85, "accuracy is not valid"
        assert metrics.precision == 0.80, "precision is not valid"

    def test_to_dict(self):
        """Test serialization."""
        metrics = ValidationMetrics(accuracy=0.9, precision=0.8)
        data = metrics.to_dict()
        assert data["accuracy"] == 0.9, "Data must not be empty"
        assert data["precision"] == 0.8, "Data must not be empty"

    def test_from_dict(self):
        """Test deserialization."""
        data = {"accuracy": 0.85, "f1_score": 0.82}
        metrics = ValidationMetrics.from_dict(data)
        assert metrics.accuracy == 0.85, "accuracy is not valid"
        assert metrics.f1_score == 0.82, "f1_score is not valid"


# =============================================================================
# ModelValidator Tests
# =============================================================================


class TestModelValidator:
    """Tests for ModelValidator class."""

    def test_create_validator(self):
        """Test creating validator."""
        validator = ModelValidator(n_folds=5)
        assert validator.n_folds == 5, "n_folds is not valid"

    def test_validate_empty_data(self):
        """Test validation with empty data."""
        validator = ModelValidator()
        metrics = validator.validate(MagicMock(), [], [])
        assert metrics.accuracy == 0.0, "accuracy is not valid"

    def test_validate_with_mock_model(self):
        """Test validation with mock model."""
        # Create mock model
        model = MagicMock()
        model.predict.return_value = ["a", "b", "a", "b", "a"]

        X = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
        y = ["a", "b", "a", "b", "a"]

        validator = ModelValidator(n_folds=2)
        _ = validator.validate(model, X, y)  # Result validates internally

        # Should have called fit and predict
        assert model.fit.called, "Condition must be true"
        assert model.predict.called, "Condition must be true"

    def test_calculate_metrics(self):
        """Test metric calculation."""
        validator = ModelValidator()
        y_true = ["a", "a", "b", "b"]
        y_pred = ["a", "a", "b", "b"]

        metrics = validator._calculate_metrics(y_true, y_pred)
        assert metrics.accuracy == 1.0, "accuracy is not valid"

    def test_calculate_metrics_with_errors(self):
        """Test metric calculation with errors."""
        validator = ModelValidator()
        y_true = ["a", "a", "b", "b"]
        y_pred = ["a", "b", "a", "b"]

        metrics = validator._calculate_metrics(y_true, y_pred)
        assert metrics.accuracy == 0.5, "accuracy is not valid"

    def test_confusion_matrix(self):
        """Test confusion matrix generation."""
        validator = ModelValidator()
        y_true = ["a", "a", "b"]
        y_pred = ["a", "b", "b"]

        metrics = validator._calculate_metrics(y_true, y_pred)
        assert "a" in metrics.confusion_matrix, "Condition must be true"
        assert "b" in metrics.confusion_matrix, "Condition must be true"

    def test_get_last_metrics(self):
        """Test getting last metrics."""
        validator = ModelValidator()
        assert validator.get_last_metrics() is None, "validat is not valid"


# =============================================================================
# HyperparameterTuner Tests
# =============================================================================


class TestHyperparameterTuner:
    """Tests for HyperparameterTuner class."""

    def test_create_tuner(self):
        """Test creating tuner."""
        tuner = HyperparameterTuner()
        assert tuner.metric == MetricType.ACCURACY, "metric is not valid"

    def test_create_tuner_with_metric(self):
        """Test creating tuner with specific metric."""
        tuner = HyperparameterTuner(metric=MetricType.F1_SCORE)
        assert tuner.metric == MetricType.F1_SCORE, "metric is not valid"

    def test_grid_search(self):
        """Test grid search."""

        def model_factory(alpha=1.0, beta=1.0):
            model = MagicMock()
            model.alpha = alpha
            model.beta = beta
            model.predict.return_value = ["a", "b"]
            return model

        tuner = HyperparameterTuner()
        X = [[1, 2], [3, 4], [5, 6], [7, 8]]
        y = ["a", "b", "a", "b"]

        result = tuner.grid_search(model_factory, {"alpha": [0.1, 1.0], "beta": [0.5, 1.0]}, X, y)

        assert isinstance(result, TuningResult)
        assert result.search_method == "grid", "Result must not be empty"
        assert result.iterations == 4, "Result must not be empty"

    def test_random_search(self):
        """Test random search."""

        def model_factory(alpha=1.0):
            model = MagicMock()
            model.predict.return_value = ["a"]
            return model

        tuner = HyperparameterTuner()
        X = [[1, 2], [3, 4]]
        y = ["a", "b"]

        result = tuner.random_search(
            model_factory, {"alpha": [0.1, 0.5, 1.0]}, X, y, n_iterations=5
        )

        assert result.search_method == "random", "Result must not be empty"
        assert result.iterations == 5, "Result must not be empty"

    def test_generate_combinations(self):
        """Test parameter combination generation."""
        tuner = HyperparameterTuner()
        combinations = tuner._generate_combinations(["a", "b"], [[1, 2], [3, 4]])
        assert len(combinations) == 4, "Combinations must not be empty"

    def test_get_metric_value(self):
        """Test getting metric values."""
        tuner = HyperparameterTuner(metric=MetricType.PRECISION)
        metrics = ValidationMetrics(accuracy=0.9, precision=0.8)
        assert tuner._get_metric_value(metrics) == 0.8, "Value must be initialized"

    def test_get_last_result(self):
        """Test getting last result."""
        tuner = HyperparameterTuner()
        assert tuner.get_last_result() is None, "Result must not be empty"


# =============================================================================
# PerformanceTracker Tests
# =============================================================================


class TestPerformanceTracker:
    """Tests for PerformanceTracker class."""

    def test_create_tracker(self):
        """Test creating tracker."""
        tracker = PerformanceTracker(alert_threshold=0.15)
        assert tracker.alert_threshold == 0.15, "alert_threshold is not valid"

    def test_record_performance(self):
        """Test recording performance."""
        tracker = PerformanceTracker()
        metrics = ValidationMetrics(accuracy=0.9)
        record = tracker.record(metrics, "v1.0.0")

        assert isinstance(record, PerformanceRecord)
        assert record.model_version == "v1.0.0", "model_version is not valid"

    def test_performance_drop_alert(self):
        """Test alert on performance drop."""
        tracker = PerformanceTracker(alert_threshold=0.1)

        # Good performance
        tracker.record(ValidationMetrics(accuracy=0.9), "v1.0")
        # Big drop
        tracker.record(ValidationMetrics(accuracy=0.7), "v2.0")

        alerts = tracker.get_alerts()
        assert len(alerts) == 1, "Alerts must not be empty"
        assert alerts[0]["type"] == "performance_drop", "Condition must be true"

    def test_get_trend_improving(self):
        """Test trend detection - improving."""
        tracker = PerformanceTracker()
        tracker.record(ValidationMetrics(accuracy=0.7), "v1")
        tracker.record(ValidationMetrics(accuracy=0.8), "v2")
        tracker.record(ValidationMetrics(accuracy=0.9), "v3")

        trend = tracker.get_trend()
        assert trend["trend"] == "improving", "Condition must be true"

    def test_get_trend_declining(self):
        """Test trend detection - declining."""
        tracker = PerformanceTracker()
        tracker.record(ValidationMetrics(accuracy=0.9), "v1")
        tracker.record(ValidationMetrics(accuracy=0.8), "v2")
        tracker.record(ValidationMetrics(accuracy=0.7), "v3")

        trend = tracker.get_trend()
        assert trend["trend"] == "declining", "Condition must be true"

    def test_get_trend_insufficient_data(self):
        """Test trend with insufficient data."""
        tracker = PerformanceTracker()
        trend = tracker.get_trend()
        assert trend["trend"] == "insufficient_data", "Data must not be empty"

    def test_clear_alerts(self):
        """Test clearing alerts."""
        tracker = PerformanceTracker(alert_threshold=0.1)
        tracker.record(ValidationMetrics(accuracy=0.9), "v1")
        tracker.record(ValidationMetrics(accuracy=0.7), "v2")

        tracker.clear_alerts()
        assert len(tracker.get_alerts()) == 0, "Collection must not be empty"

    def test_save_and_load(self):
        """Test save and load."""
        tracker = PerformanceTracker()
        tracker.record(ValidationMetrics(accuracy=0.85), "v1.0")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
            tracker.save(path)

            loaded = PerformanceTracker.load(path)
            assert len(loaded.get_records()) == 1, "Collection must not be empty"


# =============================================================================
# ModelRegistry Tests
# =============================================================================


class TestModelRegistry:
    """Tests for ModelRegistry class."""

    def test_create_registry(self):
        """Test creating registry."""
        registry = ModelRegistry()
        assert registry._production_version is None, "_production_version is not valid"

    def test_register_model(self):
        """Test registering model."""
        registry = ModelRegistry()
        metrics = ValidationMetrics(accuracy=0.9)

        version = registry.register("v1.0.0", "classifier", metrics)

        assert version.version == "v1.0.0", "version is not valid"
        assert version.status == "staged", "status is not valid"

    def test_promote_to_production(self):
        """Test promoting to production."""
        registry = ModelRegistry()
        metrics = ValidationMetrics(accuracy=0.9)
        registry.register("v1.0.0", "classifier", metrics)

        result = registry.promote_to_production("v1.0.0")

        assert result is True, "Result must not be empty"
        assert registry.get_production_version().version == "v1.0.0", "version is not valid"

    def test_promote_archives_old(self):
        """Test that promotion archives old version."""
        registry = ModelRegistry()
        metrics = ValidationMetrics(accuracy=0.9)
        registry.register("v1.0.0", "classifier", metrics)
        registry.register("v2.0.0", "classifier", metrics)

        registry.promote_to_production("v1.0.0")
        registry.promote_to_production("v2.0.0")

        v1 = registry.get_version("v1.0.0")
        assert v1.status == "archived", "status is not valid"

    def test_get_version(self):
        """Test getting specific version."""
        registry = ModelRegistry()
        registry.register("v1.0", "classifier", ValidationMetrics())

        version = registry.get_version("v1.0")
        assert version is not None, "version must be initialized"
        assert version.version == "v1.0", "version is not valid"

    def test_list_versions(self):
        """Test listing versions."""
        registry = ModelRegistry()
        registry.register("v1.0", "classifier", ValidationMetrics())
        registry.register("v2.0", "classifier", ValidationMetrics())

        versions = registry.list_versions()
        assert len(versions) == 2, "Versions must not be empty"

    def test_start_ab_test(self):
        """Test starting A/B test."""
        registry = ModelRegistry()
        registry.register("v1.0", "classifier", ValidationMetrics())
        registry.register("v2.0", "classifier", ValidationMetrics())

        test = registry.start_ab_test("v1.0", "v2.0", traffic_split=0.5)

        assert test["status"] == "running", "Condition must be true"
        assert test["version_a"] == "v1.0", "Condition must be true"

    def test_route_ab_traffic(self):
        """Test A/B traffic routing."""
        registry = ModelRegistry()
        registry.register("v1.0", "classifier", ValidationMetrics())
        registry.register("v2.0", "classifier", ValidationMetrics())
        test = registry.start_ab_test("v1.0", "v2.0")

        version = registry.route_ab_traffic(test["id"])
        assert version in ["v1.0", "v2.0"]

    def test_compare_versions(self):
        """Test version comparison."""
        registry = ModelRegistry()
        registry.register("v1.0", "classifier", ValidationMetrics(accuracy=0.8))
        registry.register("v2.0", "classifier", ValidationMetrics(accuracy=0.9))

        comparison = registry.compare_versions("v1.0", "v2.0")

        assert comparison["winner"] == "v2.0", "Condition must be true"
        assert abs(comparison["accuracy_diff"] - (-0.1)) < 0.0001, "Condition must be true"

    def test_save_and_load(self):
        """Test save and load."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

            registry = ModelRegistry(storage_path=path)
            registry.register("v1.0", "classifier", ValidationMetrics(accuracy=0.9))
            registry.save()

            loaded = ModelRegistry.load(path)
            assert "v1.0" in [v.version for v in loaded.list_versions()], "Condition must be true"


# =============================================================================
# TuningPipeline Tests
# =============================================================================


class TestTuningPipeline:
    """Tests for TuningPipeline class."""

    def test_create_pipeline(self):
        """Test creating pipeline."""
        pipeline = TuningPipeline()
        assert pipeline.validator is not None, "validator must be initialized"
        assert pipeline.tuner is not None, "tuner must be initialized"

    def test_run_tuning_pipeline(self):
        """Test running tuning pipeline."""

        def model_factory(alpha=1.0):
            model = MagicMock()
            model.predict.return_value = ["a", "b"]
            return model

        pipeline = TuningPipeline()
        X = [[1, 2], [3, 4], [5, 6], [7, 8]]
        y = ["a", "b", "a", "b"]

        result = pipeline.run_tuning_pipeline(
            model_factory, "test_model", {"alpha": [0.1, 1.0]}, X, y
        )

        assert "version" in result, "Result must not be empty"
        assert "best_params" in result, "Result must not be empty"
        assert "metrics" in result, "Result must not be empty"

    def test_validate_and_register(self):
        """Test validate and register."""
        model = MagicMock()
        model.predict.return_value = ["a", "b", "a", "b"]

        pipeline = TuningPipeline()
        X = [[1, 2], [3, 4], [5, 6], [7, 8]]
        y = ["a", "b", "a", "b"]

        version = pipeline.validate_and_register(model, "test_model", X, y)

        assert isinstance(version, ModelVersion)

    def test_auto_promote(self):
        """Test auto-promotion."""
        pipeline = TuningPipeline()

        # Register a good model
        pipeline.registry.register("v1.0", "classifier", ValidationMetrics(accuracy=0.85))

        result = pipeline.auto_promote(threshold=0.8)
        assert result is True, "Result must not be empty"
        assert pipeline.registry.get_production_version().version == "v1.0", "version is not valid"

    def test_auto_promote_below_threshold(self):
        """Test auto-promotion below threshold."""
        pipeline = TuningPipeline()

        pipeline.registry.register("v1.0", "classifier", ValidationMetrics(accuracy=0.7))

        result = pipeline.auto_promote(threshold=0.8)
        assert result is False, "Result must not be empty"

    def test_get_summary(self):
        """Test getting summary."""
        pipeline = TuningPipeline()
        pipeline.registry.register("v1.0", "classifier", ValidationMetrics())

        summary = pipeline.get_summary()

        assert "total_versions" in summary, "Condition must be true"
        assert "performance_trend" in summary, "Condition must be true"
        assert summary["total_versions"] == 1, "Condition must be true"


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_validator(self):
        """Test create_validator function."""
        validator = create_validator(n_folds=3)
        assert validator.n_folds == 3, "n_folds is not valid"

    def test_create_tuner(self):
        """Test create_tuner function."""
        tuner = create_tuner(metric=MetricType.F1_SCORE)
        assert tuner.metric == MetricType.F1_SCORE, "metric is not valid"

    def test_create_tracker(self):
        """Test create_tracker function."""
        tracker = create_tracker(alert_threshold=0.2)
        assert tracker.alert_threshold == 0.2, "alert_threshold is not valid"

    def test_create_registry(self):
        """Test create_registry function."""
        registry = create_registry()
        assert registry is not None, "registry must be initialized"

    def test_create_tuning_pipeline(self):
        """Test create_tuning_pipeline function."""
        pipeline = create_tuning_pipeline()
        assert isinstance(pipeline, TuningPipeline)
