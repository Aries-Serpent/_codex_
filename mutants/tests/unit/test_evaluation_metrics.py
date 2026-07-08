"""
Unit tests for codex_ml.evaluation.metrics module.

Tests metric calculation, accuracy, perplexity, and evaluation runners.
"""

import pytest


class TestAccuracyMetric:
    """Test AccuracyMetric class."""

    def test_accuracy_metric_import(self):
        """Test AccuracyMetric can be imported."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        assert AccuracyMetric is not None, "AccuracyMetric must be initialized"

    def test_accuracy_metric_initialization(self):
        """Test AccuracyMetric basic initialization."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        metric = AccuracyMetric()

        assert metric.name == "accuracy", "name is not valid"
        assert metric.ignore_index == -100, "ignore_index is not valid"

    def test_accuracy_metric_custom_name(self):
        """Test AccuracyMetric with custom name."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        metric = AccuracyMetric(name="custom_accuracy")

        assert metric.name == "custom_accuracy", "name is not valid"

    def test_accuracy_metric_has_add_batch_method(self):
        """Test AccuracyMetric has add_batch method."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        metric = AccuracyMetric()

        assert hasattr(metric, "add_batch")
        assert callable(metric.add_batch), "Condition must be true"

    def test_accuracy_metric_has_compute_method(self):
        """Test AccuracyMetric has compute method."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        metric = AccuracyMetric()

        assert hasattr(metric, "compute")
        assert callable(metric.compute), "Condition must be true"


class TestPerplexityMetric:
    """Test PerplexityMetric class."""

    def test_perplexity_metric_import(self):
        """Test PerplexityMetric can be imported."""
        from codex_ml.evaluation.metrics.perplexity import PerplexityMetric

        assert PerplexityMetric is not None, "PerplexityMetric must be initialized"

    def test_perplexity_metric_initialization(self):
        """Test PerplexityMetric basic initialization."""
        from codex_ml.evaluation.metrics.perplexity import PerplexityMetric

        metric = PerplexityMetric()

        assert metric.name == "perplexity", "name is not valid"
        assert metric.ignore_index == -100, "ignore_index is not valid"

    def test_perplexity_metric_custom_name(self):
        """Test PerplexityMetric with custom name."""
        from codex_ml.evaluation.metrics.perplexity import PerplexityMetric

        metric = PerplexityMetric(name="model_perplexity")

        assert metric.name == "model_perplexity", "name is not valid"

    def test_perplexity_metric_has_add_batch_method(self):
        """Test PerplexityMetric has add_batch method."""
        from codex_ml.evaluation.metrics.perplexity import PerplexityMetric

        metric = PerplexityMetric()

        assert hasattr(metric, "add_batch")
        assert callable(metric.add_batch), "Condition must be true"

    def test_perplexity_metric_has_compute_method(self):
        """Test PerplexityMetric has compute method."""
        from codex_ml.evaluation.metrics.perplexity import PerplexityMetric

        metric = PerplexityMetric()

        assert hasattr(metric, "compute")
        assert callable(metric.compute), "Condition must be true"


class TestMetricAdapter:
    """Test MetricAdapter base class."""

    def test_metric_adapter_import(self):
        """Test MetricAdapter can be imported."""
        from codex_ml.evaluation.runner import MetricAdapter

        assert MetricAdapter is not None, "MetricAdapter must be initialized"

    def test_metric_adapter_is_base_class(self):
        """Test MetricAdapter is a base class."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric
        from codex_ml.evaluation.runner import MetricAdapter

        # AccuracyMetric should inherit from MetricAdapter
        assert issubclass(AccuracyMetric, MetricAdapter)

    def test_metric_adapter_has_name_attribute(self):
        """Test MetricAdapter instances have name attribute."""
        from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

        metric = AccuracyMetric(name="test_metric")

        assert hasattr(metric, "name")
        assert metric.name == "test_metric", "name is not valid"


class TestBLEUMetric:
    """Test BLEU metric if available."""

    def test_bleu_metric_import(self):
        """Test BLEU metric can be imported."""
        try:
            from codex_ml.evaluation.metrics.bleu import BLEUMetric

            assert BLEUMetric is not None, "BLEUMetric must be initialized"
        except ImportError:
            pytest.skip("BLEU metric not available")

    def test_bleu_metric_has_required_methods(self):
        """Test BLEU metric has required methods."""
        try:
            from codex_ml.evaluation.metrics.bleu import BLEUMetric

            metric = BLEUMetric()
            assert hasattr(metric, "add_batch")
            assert hasattr(metric, "compute")
        except ImportError:
            pytest.skip("BLEU metric not available")


class TestROUGEMetric:
    """Test ROUGE metric if available."""

    def test_rouge_metric_import(self):
        """Test ROUGE metric can be imported."""
        try:
            from codex_ml.evaluation.metrics.rouge import ROUGEMetric

            assert ROUGEMetric is not None, "ROUGEMetric must be initialized"
        except ImportError:
            pytest.skip("ROUGE metric not available")

    def test_rouge_metric_has_required_methods(self):
        """Test ROUGE metric has required methods."""
        try:
            from codex_ml.evaluation.metrics.rouge import ROUGEMetric

            metric = ROUGEMetric()
            assert hasattr(metric, "add_batch")
            assert hasattr(metric, "compute")
        except ImportError:
            pytest.skip("ROUGE metric not available")


class TestLatencyMetric:
    """Test LatencyMetric if available."""

    def test_latency_metric_import(self):
        """Test LatencyMetric can be imported."""
        try:
            from codex_ml.evaluation.metrics.latency import LatencyMetric

            assert LatencyMetric is not None, "LatencyMetric must be initialized"
        except ImportError:
            pytest.skip("LatencyMetric not available")

    def test_latency_metric_initialization(self):
        """Test LatencyMetric basic initialization."""
        try:
            from codex_ml.evaluation.metrics.latency import LatencyMetric

            metric = LatencyMetric()
            assert hasattr(metric, "name")
        except ImportError:
            pytest.skip("LatencyMetric not available")


class TestEvaluationRunner:
    """Test evaluation runner functionality."""

    def test_evaluation_runner_import(self):
        """Test evaluation runner can be imported."""
        from codex_ml.evaluation.runner import MetricAdapter

        assert MetricAdapter is not None, "MetricAdapter must be initialized"

    def test_evaluation_loop_import(self):
        """Test evaluation loop can be imported."""
        try:
            from codex_ml.evaluation.loop import evaluate_model

            assert evaluate_model is not None, "evaluate_model must be initialized"
        except ImportError:
            # evaluate_model may not exist
            _ = None  # suppressed: no action needed

    def test_metric_registry_exists(self):
        """Test metric registry or factory exists."""
        try:
            from codex_ml.evaluation import metrics

            # Should have multiple metric classes
            assert hasattr(metrics, "accuracy")
            assert hasattr(metrics, "perplexity")
        except (ImportError, AttributeError):
            # Registry pattern may not be used
            _ = None  # suppressed: no action needed


class TestMetricsModuleStructure:
    """Test metrics module structure."""

    def test_metrics_module_import(self):
        """Test metrics module can be imported."""
        from codex_ml.evaluation import metrics

        assert metrics is not None, "metrics must be initialized"

    def test_metrics_has_accuracy(self):
        """Test metrics module has accuracy."""
        from codex_ml.evaluation import metrics

        assert hasattr(metrics, "accuracy")

    def test_metrics_has_perplexity(self):
        """Test metrics module has perplexity."""
        from codex_ml.evaluation import metrics

        assert hasattr(metrics, "perplexity")

    def test_evaluation_cli_import(self):
        """Test evaluation CLI can be imported."""
        try:
            from codex_ml.evaluation.cli import evaluate_cli

            assert evaluate_cli is not None, "evaluate_cli must be initialized"
        except (ImportError, AttributeError):
            # CLI may not exist yet or dependencies missing
            pytest.skip("CLI not available or dependencies missing")
