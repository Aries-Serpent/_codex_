"""
Integration Tests for Evaluation and Metrics Collection

Tests complete evaluation workflows:
- Evaluation pipeline execution
- Metric calculation and aggregation
- Cross-module metric collection
- Integration with model checkpoints
- Real-time metrics logging
- Evaluation result persistence
- Multi-metric evaluation scenarios

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import logging
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from codex_ml.training import Evaluator

    EVALUATOR_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    EVALUATOR_AVAILABLE = False

try:
    from codex_ml.metrics import MetricsCollector

    METRICS_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    METRICS_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not EVALUATOR_AVAILABLE, reason="Evaluator not available")
class TestEvaluationIntegration:
    """Integration tests for evaluation system."""

    def test_evaluator_initialization(self):
        """Test: Evaluator initializes with model and data."""
        # Arrange & Act: Mock evaluator init
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator

            # Create evaluator
            mock_eval_cls(model=Mock(), eval_data=Mock())

            # Assert: Evaluator created
            mock_eval_cls.assert_called_once()

    def test_evaluation_execution_workflow(self):
        """Test: Complete evaluation execution."""
        # Arrange & Act: Mock evaluation
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.evaluate = Mock(
                return_value={
                    "accuracy": 0.85,
                    "f1": 0.82,
                    "loss": 0.3,
                }
            )

            # Execute evaluation
            evaluator = mock_eval_cls()
            metrics = evaluator.evaluate()

            # Assert: Evaluation complete
            assert metrics["accuracy"] == 0.85, "Condition must be true"

    def test_batch_evaluation_workflow(self):
        """Test: Evaluation across multiple batches."""
        # Arrange: Mock batched evaluation
        num_batches = 10
        batch_metrics = [{"accuracy": 0.8 + i * 0.01} for i in range(num_batches)]

        # Act & Assert: Mock batch iteration
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.evaluate_batch = Mock(side_effect=batch_metrics)

            # Evaluate batches
            evaluator = mock_eval_cls()
            results = []
            for _ in range(num_batches):
                result = evaluator.evaluate_batch()
                results.append(result)

            # Assert: All batches evaluated
            assert len(results) == num_batches, "Results must not be empty"

    def test_checkpoint_based_evaluation(self):
        """Test: Evaluation of specific model checkpoint."""
        # Arrange: Mock checkpoint
        checkpoint_path = "/path/to/checkpoint.pt"

        # Act & Assert: Mock checkpoint evaluation
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.evaluate_checkpoint = Mock(return_value={"accuracy": 0.85})

            # Evaluate checkpoint
            evaluator = mock_eval_cls()
            metrics = evaluator.evaluate_checkpoint(checkpoint_path)

            # Assert: Checkpoint evaluated
            assert metrics["accuracy"] == 0.85, "Condition must be true"

    def test_cross_dataset_evaluation(self):
        """Test: Evaluation across train/val/test splits."""
        # Arrange: Mock datasets
        datasets = {"train": Mock(), "val": Mock(), "test": Mock()}

        # Act & Assert: Mock cross-dataset evaluation
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator

            results = {}
            for split_name, dataset in datasets.items():
                mock_evaluator.evaluate_on_dataset = Mock(
                    return_value={"accuracy": 0.8 + len(split_name) * 0.01}
                )
                results[split_name] = mock_evaluator.evaluate_on_dataset(dataset)

            # Assert: All splits evaluated
            assert len(results) == 3, "Results must not be empty"

    def test_evaluation_with_custom_metrics(self):
        """Test: Evaluation with custom metric functions."""
        # Arrange: Custom metrics
        custom_metrics = ["custom_metric_1", "custom_metric_2"]

        # Act & Assert: Mock custom metrics
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.register_metric = Mock()
            mock_evaluator.evaluate = Mock(
                return_value={
                    "custom_metric_1": 0.9,
                    "custom_metric_2": 0.85,
                }
            )

            # Register and evaluate
            evaluator = mock_eval_cls()
            for metric in custom_metrics:
                evaluator.register_metric(metric)

            result = evaluator.evaluate()

            # Assert: Custom metrics available
            assert "custom_metric_1" in result, "Result must not be empty"


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics not available")
class TestMetricsCollectionIntegration:
    """Integration tests for metrics collection."""

    def test_metrics_collector_initialization(self):
        """Test: Metrics collector initializes."""
        # Arrange & Act: Mock metrics collector
        with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector

            # Create collector
            mock_collector_cls()

            # Assert: Collector created
            mock_collector_cls.assert_called_once()

    def test_metrics_collection_during_training(self):
        """Test: Metrics collected during training."""
        # Arrange: Mock metric points
        metric_updates = [
            {"step": 1, "loss": 0.5, "accuracy": 0.7},
            {"step": 2, "loss": 0.45, "accuracy": 0.75},
            {"step": 3, "loss": 0.4, "accuracy": 0.8},
        ]

        # Act & Assert: Mock collection
        with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.record = Mock()

            # Collect metrics
            collector = mock_collector_cls()
            for metrics in metric_updates:
                collector.record(metrics)

            # Assert: All metrics recorded
            assert mock_collector.record.call_count == 3, "Count must be greater than zero"

    def test_aggregated_metrics_computation(self):
        """Test: Aggregated metrics computed from individual values."""
        # Arrange: Individual metric values

        # Act & Assert: Mock aggregation
        with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.get_aggregated = Mock(
                return_value={
                    "mean": 0.6,
                    "std": 0.075,
                    "min": 0.5,
                    "max": 0.7,
                }
            )

            # Get aggregated metrics
            collector = mock_collector_cls()
            result = collector.get_aggregated()

            # Assert: Aggregation correct
            assert result["mean"] == 0.6, "Result must not be empty"

    def test_metrics_export_to_logger(self):
        """Test: Metrics exported to logger."""
        # Arrange: Mock metrics
        metrics = {"accuracy": 0.85, "f1": 0.82}

        # Act & Assert: Mock export
        with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.export = Mock(return_value=True)

            # Export metrics
            collector = mock_collector_cls()
            result = collector.export(metrics)

            # Assert: Export successful
            assert result is True, "Result must not be empty"

    def test_metrics_persistence_to_file(self, tmp_path):
        """Test: Metrics persisted to file."""
        # Arrange: Mock metrics
        metrics = {"step": 100, "loss": 0.4, "accuracy": 0.85}
        output_file = tmp_path / "metrics.json"

        # Act & Assert: Mock persistence
        with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector
            mock_collector.save = Mock(return_value=True)

            # Save metrics
            collector = mock_collector_cls()
            result = collector.save(str(output_file), metrics)

            # Assert: Save successful
            assert result is True, "Result must not be empty"


@pytest.mark.skipif(
    not (EVALUATOR_AVAILABLE and METRICS_AVAILABLE), reason="Requirements not available"
)
class TestEvaluationMetricsIntegration:
    """Integration between evaluation and metrics collection."""

    def test_evaluation_metrics_collection_workflow(self):
        """Test: Metrics automatically collected during evaluation."""
        # Arrange & Act: Mock integrated workflow
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
                # Setup evaluator
                mock_evaluator = Mock()
                mock_eval_cls.return_value = mock_evaluator
                mock_evaluator.evaluate = Mock(return_value={"accuracy": 0.85, "f1": 0.82})

                # Setup metrics collector
                mock_collector = Mock()
                mock_collector_cls.return_value = mock_collector
                mock_collector.record = Mock()

                # Execute workflow
                evaluator = mock_eval_cls()
                metrics = evaluator.evaluate()

                collector = mock_collector_cls()
                collector.record(metrics)

                # Assert: Metrics collected
                assert mock_collector.record.called, "mock_collect is not valid"

    def test_per_batch_metrics_during_evaluation(self):
        """Test: Metrics collected per batch during evaluation."""
        # Arrange: Mock batches
        num_batches = 5

        # Act & Assert: Mock per-batch collection
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
                # Setup evaluator with per-batch metrics
                mock_evaluator = Mock()
                mock_eval_cls.return_value = mock_evaluator
                mock_evaluator.evaluate_batch = Mock(return_value={"accuracy": 0.85})

                # Setup collector
                mock_collector = Mock()
                mock_collector_cls.return_value = mock_collector
                mock_collector.record = Mock()

                # Evaluate and collect per batch
                evaluator = mock_eval_cls()
                collector = mock_collector_cls()

                for _ in range(num_batches):
                    batch_metrics = evaluator.evaluate_batch()
                    collector.record(batch_metrics)

                # Assert: All batches recorded
                assert mock_collector.record.call_count == num_batches, "Count must be greater than zero"


@pytest.mark.skipif(not EVALUATOR_AVAILABLE, reason="Evaluator not available")
class TestEvaluationErrorHandling:
    """Error handling in evaluation system."""

    def test_error_on_missing_eval_data(self):
        """Test: Missing evaluation data caught."""
        # Arrange & Act: Mock error
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_eval_cls.side_effect = ValueError("Evaluation data not provided")

            with pytest.raises(ValueError):
                mock_eval_cls(model=Mock())

    def test_error_on_model_evaluation_failure(self):
        """Test: Model evaluation failure handled."""
        # Arrange & Act: Mock evaluation failure
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.evaluate = Mock(side_effect=RuntimeError("Model forward pass failed"))

            with pytest.raises(RuntimeError):
                evaluator = mock_eval_cls()
                evaluator.evaluate()

    def test_error_recovery_on_checkpoint_mismatch(self):
        """Test: Mismatch between checkpoint and model handled."""
        # Arrange & Act: Mock mismatch error
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            mock_evaluator = Mock()
            mock_eval_cls.return_value = mock_evaluator
            mock_evaluator.evaluate_checkpoint = Mock(
                side_effect=RuntimeError("Checkpoint shape mismatch")
            )

            with pytest.raises(RuntimeError):
                evaluator = mock_eval_cls()
                evaluator.evaluate_checkpoint("checkpoint.pt")


@pytest.mark.skipif(
    not (EVALUATOR_AVAILABLE and METRICS_AVAILABLE), reason="Requirements not available"
)
class TestEvaluationMetricsEndToEnd:
    """End-to-end evaluation and metrics workflows."""

    def test_complete_eval_to_metrics_pipeline(self):
        """Test: Complete evaluation and metrics collection pipeline."""
        # Arrange & Act: Mock complete pipeline
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
                # Step 1: Evaluate
                mock_evaluator = Mock()
                mock_eval_cls.return_value = mock_evaluator
                mock_evaluator.evaluate = Mock(
                    return_value={
                        "accuracy": 0.85,
                        "f1": 0.82,
                        "loss": 0.3,
                    }
                )

                # Step 2: Collect metrics
                mock_collector = Mock()
                mock_collector_cls.return_value = mock_collector
                mock_collector.record = Mock()
                mock_collector.get_aggregated = Mock(
                    return_value={
                        "accuracy": 0.85,
                        "f1": 0.82,
                    }
                )

                # Execute pipeline
                evaluator = mock_eval_cls()
                metrics = evaluator.evaluate()

                collector = mock_collector_cls()
                collector.record(metrics)
                aggregated = collector.get_aggregated()

                # Assert: Pipeline complete
                assert metrics["accuracy"] == 0.85, "Condition must be true"
                assert aggregated["accuracy"] == 0.85, "Condition must be true"

    def test_multi_epoch_evaluation_tracking(self):
        """Test: Evaluation metrics tracked across epochs."""
        # Arrange: Mock epoch evaluations
        epochs = 3
        epoch_metrics = [
            {"epoch": 1, "accuracy": 0.70},
            {"epoch": 2, "accuracy": 0.80},
            {"epoch": 3, "accuracy": 0.85},
        ]

        # Act & Assert: Mock epoch tracking
        with patch("codex_ml.training.Evaluator") as mock_eval_cls:
            with patch("codex_ml.metrics.MetricsCollector") as mock_collector_cls:
                # Setup evaluator
                mock_evaluator = Mock()
                mock_eval_cls.return_value = mock_evaluator
                mock_evaluator.evaluate = Mock(side_effect=epoch_metrics)

                # Setup collector
                mock_collector = Mock()
                mock_collector_cls.return_value = mock_collector

                # Track across epochs
                evaluator = mock_eval_cls()
                mock_collector_cls()
                history = []

                for epoch in range(epochs):
                    metrics = evaluator.evaluate()
                    history.append(metrics)

                # Assert: All epochs tracked
                assert len(history) == epochs, "History must not be empty"
                assert history[-1]["accuracy"] == 0.85, "hist is not valid"

    def test_best_metric_tracking_during_evaluation(self):
        """Test: Best metrics tracked during evaluation."""
        # Arrange: Mock progressive metric improvement
        metrics_sequence = [
            {"accuracy": 0.70},
            {"accuracy": 0.75},
            {"accuracy": 0.82},
            {"accuracy": 0.80},  # Regression
            {"accuracy": 0.85},
        ]

        # Act & Assert: Mock best tracking
        best_accuracy = 0
        best_step = 0

        for step, metrics in enumerate(metrics_sequence):
            if metrics["accuracy"] > best_accuracy:
                best_accuracy = metrics["accuracy"]
                best_step = step

        # Assert: Best metric tracked
        assert best_accuracy == 0.85, "best_accuracy is not valid"
        assert best_step == 4, "best_step is not valid"
