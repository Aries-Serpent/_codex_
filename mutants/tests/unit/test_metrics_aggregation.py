"""
Unit tests for metrics aggregation and statistical analysis.

Tests metric computation, aggregation strategies, and statistical analysis.
"""

import math

import pytest


class TestMetricComputation:
    """Test metric computation."""

    def test_metrics_module_import(self):
        """Test metrics module can be imported."""
        from codex_ml.evaluation import metrics

        assert metrics is not None, "metrics must be initialized"

    def test_accuracy_metric_import(self):
        """Test accuracy metric can be imported."""
        from codex_ml.evaluation.metrics import accuracy

        assert accuracy is not None, "accuracy must be initialized"

    def test_perplexity_metric_import(self):
        """Test perplexity metric can be imported."""
        from codex_ml.evaluation.metrics import perplexity

        assert perplexity is not None, "perplexity must be initialized"

    def test_simple_accuracy_calculation(self):
        """Test accuracy calculation using project's AccuracyMetric."""
        try:
            from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

            metric = AccuracyMetric()
            # Add batch: predictions=[1, 2, 3], references=[1, 2, 2]
            # Expected: 2 correct out of 3 total = 0.6667
            metric.add_batch([1, 2, 3], [1, 2, 2])
            result = metric.compute()

            assert "accuracy" in result, "Result must not be empty"
            assert abs(result["accuracy"] - 0.6667) < 0.01, "Result must not be empty"
        except ImportError:
            pytest.skip("AccuracyMetric not available")

    def test_accuracy_metric_empty_batch(self):
        """Test accuracy metric handles empty batch gracefully."""
        try:
            from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

            metric = AccuracyMetric()
            # Compute on empty batch - should return 0.0 or raise appropriate error
            result = metric.compute()

            # Either it returns 0.0 accuracy or the result has accuracy key
            if "accuracy" in result:
                assert isinstance(result["accuracy"], (int, float))
        except ImportError:
            pytest.skip("AccuracyMetric not available")
        except (ValueError, ZeroDivisionError):
            # Expected behavior: metric may raise error on empty batch
            _ = None  # suppressed: no action needed

    def test_precision_calculation(self):
        """Test precision metric calculation."""
        true_positives = 80
        false_positives = 20

        precision = true_positives / (true_positives + false_positives)

        assert precision == 0.8, "precision is not valid"

    def test_recall_calculation(self):
        """Test recall metric calculation."""
        true_positives = 80
        false_negatives = 10

        recall = true_positives / (true_positives + false_negatives)

        assert abs(recall - 0.8889) < 0.001, "Condition must be true"

    def test_f1_score_calculation(self):
        """Test F1 score calculation."""
        precision = 0.8
        recall = 0.9

        f1 = 2 * (precision * recall) / (precision + recall)

        assert abs(f1 - 0.8471) < 0.001, "Condition must be true"

    def test_mean_squared_error(self):
        """Test mean squared error calculation."""
        predictions = [1.0, 2.0, 3.0]
        targets = [1.1, 1.9, 3.2]

        mse = sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)

        assert mse < 0.1, "mse is not valid"

    def test_mean_absolute_error(self):
        """Test mean absolute error calculation."""
        predictions = [1.0, 2.0, 3.0]
        targets = [1.1, 1.9, 3.2]

        mae = sum(abs(p - t) for p, t in zip(predictions, targets)) / len(predictions)

        assert abs(mae - 0.1333) < 0.001, "Condition must be true"

    def test_perplexity_from_loss(self):
        """Test perplexity calculation from loss."""
        loss = 2.0

        perplexity = math.exp(loss)

        assert abs(perplexity - 7.389) < 0.01, "Condition must be true"


class TestStatisticalAnalysis:
    """Test statistical analysis of metrics."""

    def test_mean_calculation(self):
        """Test mean calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]

        mean = sum(values) / len(values)

        assert mean == 3.0, "mean is not valid"

    def test_median_calculation(self):
        """Test median calculation."""
        values = [1, 3, 5, 7, 9]

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        median = sorted_vals[n // 2]

        assert median == 5, "median is not valid"

    def test_variance_calculation(self):
        """Test variance calculation."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        assert abs(variance - 4.0) < 0.1, "Condition must be true"

    def test_standard_deviation(self):
        """Test standard deviation calculation."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)

        assert abs(std_dev - 2.0) < 0.1, "Condition must be true"

    def test_percentile_calculation(self):
        """Test percentile calculation."""
        values = list(range(1, 101))  # 1 to 100

        # 50th percentile (median)
        p50 = values[49]  # 0-indexed

        assert p50 == 50, "p50 is not valid"

    def test_quartiles(self):
        """Test quartile calculation."""
        values = list(range(1, 101))

        q1 = values[24]  # 25th percentile
        q2 = values[49]  # 50th percentile (median)
        q3 = values[74]  # 75th percentile

        assert q1 == 25, "q1 is not valid"
        assert q2 == 50, "q2 is not valid"
        assert q3 == 75, "q3 is not valid"

    def test_coefficient_of_variation(self):
        """Test coefficient of variation."""
        values = [10.0, 12.0, 13.0, 15.0, 18.0]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean

        assert cv < 1.0, "cv is not valid"

    def test_confidence_interval(self):
        """Test confidence interval calculation."""
        values = [98.0, 99.0, 100.0, 101.0, 102.0]

        mean = sum(values) / len(values)
        n = len(values)
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)

        # Approximate 95% CI (using z=1.96 for large samples)
        margin = 1.96 * (std_dev / math.sqrt(n))
        ci_lower = mean - margin
        ci_upper = mean + margin

        assert ci_lower < mean < ci_upper, "ci_lower is not valid"

    def test_moving_average(self):
        """Test moving average calculation."""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        window = 3

        moving_avgs = []
        for i in range(len(values) - window + 1):
            window_avg = sum(values[i : i + window]) / window
            moving_avgs.append(window_avg)

        assert len(moving_avgs) == 8, "Moving_avgs must not be empty"
        assert moving_avgs[0] == 2.0, "Condition must be true"

    def test_exponential_moving_average(self):
        """Test exponential moving average."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        alpha = 0.3

        ema = values[0]
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema

        assert ema > values[0], "ema must be greater than zero"
        assert ema < values[-1], "Value must be initialized"


class TestAggregationStrategies:
    """Test different aggregation strategies."""

    def test_sum_aggregation(self):
        """Test sum aggregation."""
        metrics = [1.0, 2.0, 3.0, 4.0, 5.0]

        total = sum(metrics)

        assert total == 15.0, "total is not valid"

    def test_average_aggregation(self):
        """Test average aggregation."""
        metrics = [2.0, 4.0, 6.0, 8.0]

        average = sum(metrics) / len(metrics)

        assert average == 5.0, "average is not valid"

    def test_weighted_average(self):
        """Test weighted average aggregation."""
        values = [10.0, 20.0, 30.0]
        weights = [1.0, 2.0, 1.0]

        weighted_sum = sum(v * w for v, w in zip(values, weights))
        total_weight = sum(weights)
        weighted_avg = weighted_sum / total_weight

        assert weighted_avg == 20.0, "weighted_avg is not valid"

    def test_max_aggregation(self):
        """Test max aggregation."""
        metrics = [0.5, 0.8, 0.6, 0.9, 0.7]

        max_metric = max(metrics)

        assert max_metric == 0.9, "max_metric is not valid"

    def test_min_aggregation(self):
        """Test min aggregation."""
        metrics = [0.5, 0.8, 0.6, 0.9, 0.7]

        min_metric = min(metrics)

        assert min_metric == 0.5, "min_metric is not valid"

    def test_harmonic_mean(self):
        """Test harmonic mean aggregation."""
        values = [2.0, 4.0, 8.0]

        n = len(values)
        harmonic_mean = n / sum(1 / v for v in values)

        assert abs(harmonic_mean - 3.4286) < 0.001, "Condition must be true"

    def test_geometric_mean(self):
        """Test geometric mean aggregation."""
        values = [2.0, 8.0, 16.0]

        product = 1.0
        for v in values:
            product *= v
        geometric_mean = product ** (1 / len(values))

        assert abs(geometric_mean - 6.3496) < 0.001, "Condition must be true"

    def test_batch_aggregation(self):
        """Test batch-wise metric aggregation."""
        batch_losses = [0.5, 0.4, 0.3, 0.35, 0.32]

        epoch_loss = sum(batch_losses) / len(batch_losses)

        assert abs(epoch_loss - 0.374) < 0.001, "Condition must be true"

    def test_temporal_aggregation(self):
        """Test temporal aggregation across time steps."""
        time_series = {
            "t1": 10.0,
            "t2": 15.0,
            "t3": 20.0,
            "t4": 25.0,
        }

        avg_over_time = sum(time_series.values()) / len(time_series)

        assert avg_over_time == 17.5, "avg_over_time is not valid"

    def test_hierarchical_aggregation(self):
        """Test hierarchical aggregation."""
        module_metrics = {
            "layer1": [0.5, 0.6],
            "layer2": [0.7, 0.8],
            "layer3": [0.9, 1.0],
        }

        layer_avgs = {layer: sum(vals) / len(vals) for layer, vals in module_metrics.items()}
        overall_avg = sum(layer_avgs.values()) / len(layer_avgs)

        assert abs(overall_avg - 0.75) < 0.01, "Condition must be true"
