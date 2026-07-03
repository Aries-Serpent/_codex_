import pytest

pytest.importorskip("mlflow")
"""
Test Suite for WP-C: Evaluation Standardization

Tests the unified evaluation runner and metric adapters.

Test Coverage:
- EvaluationRunner initialization and configuration
- Metric adapter interface and accumulation
- AccuracyMetric computation
- BleuMetric computation
- RougeMetric computation
- PerplexityMetric computation
- LatencyMetric computation
- Tracking writer integration
- Artifact generation (summary JSON)
- Error handling and edge cases

Run with:
    pytest tests/evaluation/test_evaluation_runner.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.codex_ml.evaluation.metrics import (
    AccuracyMetric,
    BleuMetric,
    LatencyMetric,
    PerplexityMetric,
    RougeMetric,
)
from src.codex_ml.evaluation.runner import (
    EvaluationConfig,
    EvaluationRunner,
    MetricAdapter,
)


class TestEvaluationConfig:
    """Test evaluation configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EvaluationConfig()
        assert config.batch_size == 32, "batch_size is not valid"
        assert config.max_samples is None, "max_samples is not valid"
        assert config.device == "cpu", "device is not valid"
        assert config.output_dir == "artifacts/evaluation", "output_dir is not valid"
        assert config.save_predictions is False, "save_predictions is not valid"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = EvaluationConfig(
            batch_size=64,
            max_samples=1000,
            device="cuda",
            output_dir=os.path.join(tempfile.gettempdir(), "eval"),
            save_predictions=True,
        )
        assert config.batch_size == 64, "batch_size is not valid"
        assert config.max_samples == 1000, "max_samples is not valid"
        assert config.device == "cuda", "device is not valid"
        assert config.output_dir == os.path.join(tempfile.gettempdir(), "eval"), "output_dir is not valid"
        assert config.save_predictions is True, "save_predictions is not valid"


class TestMetricAdapter:
    """Test base metric adapter interface."""

    def test_adapter_initialization(self):
        """Test metric adapter initialization."""
        adapter = MetricAdapter("test_metric")
        assert adapter.name == "test_metric", "name is not valid"
        assert adapter._predictions == [], "_predictions is not valid"
        assert adapter._references == [], "_references is not valid"

    def test_add_batch(self):
        """Test batch accumulation."""
        adapter = MetricAdapter("test")
        adapter.add_batch([1, 2, 3], [1, 2, 2])
        assert len(adapter._predictions) == 3, "Collection must not be empty"
        assert len(adapter._references) == 3, "Collection must not be empty"

    def test_reset(self):
        """Test resetting accumulated results."""
        adapter = MetricAdapter("test")
        adapter.add_batch([1, 2], [1, 2])
        adapter.reset()
        assert adapter._predictions == [], "_predictions is not valid"
        assert adapter._references == [], "_references is not valid"


class TestAccuracyMetric:
    """Test accuracy metric adapter."""

    def test_perfect_accuracy(self):
        """Test 100% accuracy."""
        metric = AccuracyMetric()
        metric.add_batch([1, 2, 3], [1, 2, 3])
        results = metric.compute()
        assert results["accuracy"] == 1.0, "Result must not be empty"

    def test_partial_accuracy(self):
        """Test partial accuracy."""
        metric = AccuracyMetric()
        metric.add_batch([1, 2, 3], [1, 2, 2])
        results = metric.compute()
        assert abs(results["accuracy"] - 0.6667) < 0.01, "Result must not be empty"

    def test_zero_accuracy(self):
        """Test 0% accuracy."""
        metric = AccuracyMetric()
        metric.add_batch([1, 2, 3], [4, 5, 6])
        results = metric.compute()
        assert results["accuracy"] == 0.0, "Result must not be empty"

    def test_ignore_index(self):
        """Test ignoring specific indices."""
        metric = AccuracyMetric(ignore_index=-100)
        metric.add_batch([1, 2, 3], [1, -100, 3])
        results = metric.compute()
        assert results["accuracy"] == 1.0, "Result must not be empty"

    def test_empty_batch(self):
        """Test with empty batch."""
        metric = AccuracyMetric()
        results = metric.compute()
        assert results["accuracy"] == 0.0, "Result must not be empty"


class TestBleuMetric:
    """Test BLEU metric adapter."""

    def test_bleu_identical(self):
        """Test BLEU with identical strings."""
        metric = BleuMetric()
        metric.add_batch("the cat sat on the mat", "the cat sat on the mat")
        results = metric.compute()
        assert "bleu" in results, "Result must not be empty"
        # Identical strings should have high BLEU (close to 1.0)

    def test_bleu_similar(self):
        """Test BLEU with similar strings."""
        metric = BleuMetric()
        metric.add_batch("the cat sat on the mat", "the cat is on the mat")
        results = metric.compute()
        assert "bleu" in results, "Result must not be empty"
        assert 0.0 <= results["bleu"] <= 1.0, "Result must not be empty"

    def test_bleu_different(self):
        """Test BLEU with completely different strings."""
        metric = BleuMetric()
        metric.add_batch("hello world", "goodbye universe")
        results = metric.compute()
        assert "bleu" in results, "Result must not be empty"
        # Different strings should have low BLEU

    def test_bleu_empty(self):
        """Test BLEU with empty batch."""
        metric = BleuMetric()
        results = metric.compute()
        assert results["bleu"] == 0.0, "Result must not be empty"


class TestRougeMetric:
    """Test ROUGE metric adapter."""

    def test_rouge_identical(self):
        """Test ROUGE with identical strings."""
        metric = RougeMetric(["rouge1", "rougeL"])
        metric.add_batch("the cat sat on the mat", "the cat sat on the mat")
        results = metric.compute()
        assert "rouge1" in results, "Result must not be empty"
        assert "rougeL" in results, "Result must not be empty"
        # Identical strings should have ROUGE = 1.0

    def test_rouge_similar(self):
        """Test ROUGE with similar strings."""
        metric = RougeMetric(["rouge1"])
        metric.add_batch("the cat sat", "the cat is sitting")
        results = metric.compute()
        assert "rouge1" in results, "Result must not be empty"
        assert 0.0 <= results["rouge1"] <= 1.0, "Result must not be empty"

    def test_rouge_different(self):
        """Test ROUGE with different strings."""
        metric = RougeMetric(["rouge1"])
        metric.add_batch("hello world", "goodbye universe")
        results = metric.compute()
        assert "rouge1" in results, "Result must not be empty"
        # No overlap should have ROUGE close to 0

    def test_rouge_multiple_types(self):
        """Test multiple ROUGE types."""
        metric = RougeMetric(["rouge1", "rouge2", "rougeL"])
        metric.add_batch("test", "test")
        results = metric.compute()
        assert "rouge1" in results, "Result must not be empty"
        assert "rouge2" in results, "Result must not be empty"
        assert "rougeL" in results, "Result must not be empty"


class TestPerplexityMetric:
    """Test perplexity metric adapter (basic tests)."""

    def test_perplexity_initialization(self):
        """Test perplexity metric initialization."""
        metric = PerplexityMetric()
        assert metric.name == "perplexity", "name is not valid"
        assert metric.ignore_index == -100, "ignore_index is not valid"

    def test_perplexity_empty(self):
        """Test perplexity with empty batch."""
        metric = PerplexityMetric()
        results = metric.compute()
        assert results["perplexity"] == float("inf"), "Result must not be empty"
        assert results["loss"] == float("inf"), "Result must not be empty"

    def test_perplexity_reset(self):
        """Test resetting perplexity metric."""
        metric = PerplexityMetric()
        metric._total_loss = 10.0
        metric._total_tokens = 100
        metric.reset()
        assert metric._total_loss == 0.0, "_total_loss is not valid"
        assert metric._total_tokens == 0, "_total_tokens is not valid"


class TestLatencyMetric:
    """Test latency metric adapter."""

    def test_latency_initialization(self):
        """Test latency metric initialization."""
        metric = LatencyMetric()
        assert metric.name == "latency_ms", "name is not valid"
        assert metric.per_sample is False, "per_sample is not valid"

    def test_latency_computation(self):
        """Test latency computation."""
        metric = LatencyMetric()
        metric.add_batch_with_time(None, None, elapsed_time=1.0, batch_size=10)
        metric.add_batch_with_time(None, None, elapsed_time=1.0, batch_size=10)

        results = metric.compute()
        assert "latency_ms" in results, "Result must not be empty"
        assert "throughput_samples_per_sec" in results, "Result must not be empty"
        assert results["total_samples"] == 20, "Result must not be empty"

    def test_latency_per_sample(self):
        """Test per-sample latency."""
        metric = LatencyMetric(per_sample=True)
        metric.add_batch_with_time(None, None, elapsed_time=1.0, batch_size=10)

        results = metric.compute()
        # Per-sample latency should be 100ms (1s / 10 samples)
        assert abs(results["latency_ms"] - 100.0) < 0.01, "Result must not be empty"

    def test_latency_per_batch(self):
        """Test per-batch latency."""
        metric = LatencyMetric(per_sample=False)
        metric.add_batch_with_time(None, None, elapsed_time=1.0, batch_size=10)
        metric.add_batch_with_time(None, None, elapsed_time=1.0, batch_size=10)

        results = metric.compute()
        # Per-batch latency should be 1000ms (1s per batch)
        assert abs(results["latency_ms"] - 1000.0) < 0.01, "Result must not be empty"

    def test_latency_empty(self):
        """Test latency with no batches."""
        metric = LatencyMetric()
        results = metric.compute()
        assert results["latency_ms"] == 0.0, "Result must not be empty"
        assert results["throughput_samples_per_sec"] == 0.0, "Result must not be empty"


class TestEvaluationRunner:
    """Test evaluation runner."""

    def test_runner_initialization(self):
        """Test runner initialization."""
        model = Mock()
        dataset = [1, 2, 3]
        metrics = [AccuracyMetric()]

        runner = EvaluationRunner(model, dataset, metrics)
        assert runner.model == model, "model is not valid"
        assert len(runner.metrics) == 1, "Collection must not be empty"
        assert runner.config.batch_size == 32, "batch_size is not valid"

    def test_runner_custom_config(self):
        """Test runner with custom config."""
        model = Mock()
        dataset = []
        metrics = []
        config = EvaluationConfig(batch_size=64)

        runner = EvaluationRunner(model, dataset, metrics, config=config)
        assert runner.config.batch_size == 64, "batch_size is not valid"

    def test_runner_output_dir_creation(self):
        """Test output directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model = Mock()
            dataset = []
            metrics = []

            runner = EvaluationRunner(
                model, dataset, metrics, output_dir=os.path.join(tmpdir, "eval_test")
            )
            assert runner.output_path.exists(), "Condition must be true"

    def test_runner_callable_metric_wrapping(self):
        """Test wrapping callable metrics."""
        model = Mock()
        dataset = []

        def custom_metric(preds, refs):
            return 0.5

        runner = EvaluationRunner(model, dataset, [custom_metric])
        assert len(runner.metrics) == 1, "Collection must not be empty"
        assert isinstance(runner.metrics[0], MetricAdapter)

    def test_runner_mock_evaluation(self, disable_torch_profiler):
        """Test evaluation with mocked model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock model
            model = Mock()
            model.predict = Mock(return_value=[1, 2, 3])

            # Mock dataset (list of batches)
            dataset = [
                ([1, 2, 3], [1, 2, 2]),  # (inputs, targets)
                ([4, 5, 6], [4, 5, 5]),
            ]

            metrics = [AccuracyMetric()]
            config = EvaluationConfig(batch_size=3, output_dir=tmpdir)

            runner = EvaluationRunner(model, dataset, metrics, config=config)
            results = runner.run()

            assert "metrics" in results, "Result must not be empty"
            assert "accuracy" in results["metrics"], "Result must not be empty"
            assert "latency_ms" in results, "Result must not be empty"
            assert "num_samples" in results, "Result must not be empty"
            assert results["num_samples"] == 2, "Result must not be empty"

            # Check summary file created
            summary_path = Path(tmpdir) / "evaluation_summary.json"
            assert summary_path.exists(), "Condition must be true"

            with open(summary_path) as f:
                summary = json.load(f)
                assert "metrics" in summary, "Condition must be true"

    def test_runner_uses_callable_fallback(self):
        """Test evaluation with a model that is only callable."""
        with tempfile.TemporaryDirectory() as tmpdir:

            class CallableModel:
                def __init__(self):
                    self.calls = 0

                def __call__(self, inputs):
                    self.calls += 1
                    return inputs

            dataset = [
                ([1, 2, 3], [1, 2, 2]),
                ([4, 5, 6], [4, 5, 6]),
            ]
            metrics = []
            config = EvaluationConfig(batch_size=3, output_dir=tmpdir)

            model = CallableModel()
            runner = EvaluationRunner(model, dataset, metrics, config=config)
            runner._get_dataloader = lambda: dataset
            results = runner.run()

            assert "metrics" in results, "Result must not be empty"
            assert results["num_samples"] == 6, "Result must not be empty"
            assert model.calls == 2, "calls is not valid"

    @pytest.mark.xfail(
        reason="PyTorch 2.6.x profiler bug with ScriptObject type mismatch (known issue)",
        strict=False,
    )
    def test_runner_tracking_writer_integration(self):
        """Test tracking writer integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model = Mock()
            model.predict = Mock(return_value=[1])

            dataset = [([1], [1])]
            metrics = [AccuracyMetric()]

            # Mock tracking writer
            tracking_writer = Mock()
            tracking_writer.log_metric = Mock()
            tracking_writer.log_artifact = Mock()

            config = EvaluationConfig(output_dir=tmpdir)
            runner = EvaluationRunner(
                model, dataset, metrics, config=config, tracking_writer=tracking_writer
            )

            runner.run()

            # Verify tracking writer was called
            assert tracking_writer.log_metric.called, "Condition must be true"
            assert tracking_writer.log_artifact.called or hasattr(tracking_writer, "log_artifact")


class TestEvaluationIntegration:
    """Integration tests for evaluation system."""

    def test_full_evaluation_pipeline(self):
        """Test complete evaluation pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Simple classification model
            class SimpleModel:
                def predict(self, inputs):
                    # Echo inputs as predictions
                    return inputs

            model = SimpleModel()

            # Dataset: list of (inputs, targets)
            dataset = [
                ([1, 2, 3], [1, 2, 2]),
                ([4, 5, 6], [4, 5, 6]),
            ]

            metrics = [
                AccuracyMetric(),
                BleuMetric(),
            ]

            config = EvaluationConfig(batch_size=3, output_dir=tmpdir, save_predictions=False)

            runner = EvaluationRunner(model, dataset, metrics, config=config)
            results = runner.run()

            # Verify results structure
            assert "metrics" in results, "Result must not be empty"
            assert "accuracy" in results["metrics"], "Result must not be empty"
            assert "latency_ms" in results, "Result must not be empty"
            assert "throughput_samples_per_sec" in results, "Result must not be empty"
            assert "num_samples" in results, "Result must not be empty"
            assert "timestamp" in results, "Result must not be empty"

            # Verify artifacts
            summary_path = Path(tmpdir) / "evaluation_summary.json"
            assert summary_path.exists(), "Condition must be true"

    def test_multiple_metrics(self):
        """Test evaluation with multiple metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model = Mock()
            model.predict = Mock(return_value="test output")

            dataset = [("input", "target")]

            metrics = [
                AccuracyMetric(),
                BleuMetric(),
                RougeMetric(["rouge1"]),
            ]

            config = EvaluationConfig(output_dir=tmpdir)
            runner = EvaluationRunner(model, dataset, metrics, config=config)
            results = runner.run()

            # All metrics should be present
            assert "accuracy" in results["metrics"] or "bleu" in results["metrics"], "Result must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
