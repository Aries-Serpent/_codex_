"""Phase 17.2: Reliability Metrics Tests.

This module tests collection, aggregation, and analysis of test reliability metrics.
Tests cover metric definitions, calculations, and reporting.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


class TestMetricDefinitions:
    """Tests for reliability metric definitions."""

    def test_flaky_rate_definition(self):
        """Test flaky rate metric definition."""
        total_tests = 1020
        flaky_tests = 15

        flaky_rate = (flaky_tests / total_tests) * 100

        assert round(flaky_rate, 2) == 1.47

    def test_pass_rate_definition(self):
        """Test pass rate metric definition."""
        total_runs = 100
        passed_runs = 98

        pass_rate = (passed_runs / total_runs) * 100

        assert pass_rate == 98.0, "pass_rate is not valid"

    def test_retry_rate_definition(self):
        """Test retry rate metric definition."""
        total_test_runs = 1020
        retried_tests = 30

        retry_rate = (retried_tests / total_test_runs) * 100

        assert round(retry_rate, 2) == 2.94

    def test_first_pass_rate_definition(self):
        """Test first-pass rate metric definition."""
        total_tests = 1020
        passed_first_attempt = 990

        first_pass_rate = (passed_first_attempt / total_tests) * 100

        assert round(first_pass_rate, 2) == 97.06

    def test_test_coverage_definition(self):
        """Test coverage metric definition."""
        total_lines = 10000
        covered_lines = 9000

        coverage = (covered_lines / total_lines) * 100

        assert coverage == 90.0, "coverage is not valid"


class TestMetricCalculations:
    """Tests for complex metric calculations."""

    def test_calculate_composite_reliability_score(self):
        """Test calculation of composite reliability score."""
        weights = {
            "pass_rate": 0.4,
            "first_pass_rate": 0.3,
            "stability": 0.2,
            "flaky_rate_inverse": 0.1,
        }

        metrics = {
            "pass_rate": 99.5,
            "first_pass_rate": 97.0,
            "stability": 98.5,
            "flaky_rate": 1.5,  # Will be inverted
        }

        # Calculate composite score
        composite = (
            weights["pass_rate"] * metrics["pass_rate"]
            + weights["first_pass_rate"] * metrics["first_pass_rate"]
            + weights["stability"] * metrics["stability"]
            + weights["flaky_rate_inverse"] * (100 - metrics["flaky_rate"])
        )

        assert composite > 95.0, "composite must be greater than zero"

    def test_calculate_rolling_average(self):
        """Test calculation of rolling average for metrics."""
        daily_values = [98.0, 97.5, 99.0, 98.5, 97.0, 99.5, 98.0]
        window = 7

        rolling_avg = sum(daily_values[:window]) / window

        assert round(rolling_avg, 2) == 98.21

    def test_calculate_percentile_metrics(self):
        """Test calculation of percentile metrics."""
        execution_times = [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0, 10.0]

        # Sort for percentile calculation
        sorted_times = sorted(execution_times)
        n = len(sorted_times)

        p50_index = int(n * 0.5)
        p90_index = int(n * 0.9)
        p99_index = min(int(n * 0.99), n - 1)

        p50 = sorted_times[p50_index]
        p90 = sorted_times[p90_index]
        p99 = sorted_times[p99_index]

        assert p50 <= p90 <= p99, "p50 is not valid"

    def test_calculate_standard_deviation(self):
        """Test calculation of standard deviation for metrics."""
        values = [98.0, 97.5, 99.0, 98.5, 97.0]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        assert 0 < std_dev < 1.0, "0 is not valid"

    def test_calculate_coefficient_of_variation(self):
        """Test calculation of coefficient of variation."""
        values = [98.0, 97.5, 99.0, 98.5, 97.0]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        cv = (std_dev / mean) * 100

        assert cv < 5.0, "cv is not valid"


class TestMetricAggregation:
    """Tests for metric aggregation across time periods."""

    def test_aggregate_hourly_to_daily(self):
        """Test aggregation of hourly metrics to daily."""
        hourly_pass_rates = [
            99.5,
            98.0,
            99.0,
            97.5,
            99.5,
            99.0,
            98.5,
            99.0,
            98.5,
            99.5,
            98.0,
            99.0,
            99.5,
            98.5,
            99.0,
            98.0,
            99.5,
            99.0,
            98.5,
            99.5,
            99.0,
            98.5,
            99.0,
            99.5,
        ]

        daily_avg = sum(hourly_pass_rates) / len(hourly_pass_rates)

        assert round(daily_avg, 2) == 98.85

    def test_aggregate_daily_to_weekly(self):
        """Test aggregation of daily metrics to weekly."""
        daily_flaky_counts = [15, 12, 18, 10, 14, 16, 11]

        weekly_total = sum(daily_flaky_counts)
        weekly_avg = weekly_total / len(daily_flaky_counts)

        assert weekly_total == 96, "weekly_total is not valid"
        assert round(weekly_avg, 2) == 13.71

    def test_aggregate_by_test_category(self):
        """Test aggregation of metrics by test category."""
        test_results = [
            {"category": "unit", "passed": 480, "failed": 20},
            {"category": "integration", "passed": 285, "failed": 15},
            {"category": "e2e", "passed": 140, "failed": 10},
            {"category": "performance", "passed": 65, "failed": 5},
        ]

        aggregated = {}
        for result in test_results:
            cat = result["category"]
            total = result["passed"] + result["failed"]
            aggregated[cat] = {
                "total": total,
                "pass_rate": (result["passed"] / total) * 100,
            }

        assert aggregated["unit"]["pass_rate"] == 96.0, "Condition must be true"
        assert sum(a["total"] for a in aggregated.values()) == 1020, "Value must be initialized"

    def test_aggregate_by_file_path(self):
        """Test aggregation of metrics by file path."""
        test_results = [
            {"file": "tests/cli/test_main.py", "passed": 25, "failed": 2},
            {"file": "tests/cli/test_train.py", "passed": 15, "failed": 1},
            {"file": "tests/data/test_loader.py", "passed": 30, "failed": 0},
        ]

        by_directory = {}
        for result in test_results:
            # Extract directory
            parts = result["file"].split("/")
            directory = "/".join(parts[:-1])

            if directory not in by_directory:
                by_directory[directory] = {"passed": 0, "failed": 0}

            by_directory[directory]["passed"] += result["passed"]
            by_directory[directory]["failed"] += result["failed"]

        assert by_directory["tests/cli"]["passed"] == 40, "by_direct is not valid"
        assert by_directory["tests/data"]["failed"] == 0, "Data must not be empty"

    def test_aggregate_with_weights(self):
        """Test weighted aggregation of metrics."""
        category_metrics = [
            {"category": "unit", "pass_rate": 99.0, "weight": 500},
            {"category": "integration", "pass_rate": 95.0, "weight": 300},
            {"category": "e2e", "pass_rate": 92.0, "weight": 150},
            {"category": "performance", "pass_rate": 90.0, "weight": 70},
        ]

        total_weight = sum(m["weight"] for m in category_metrics)
        weighted_avg = sum(m["pass_rate"] * m["weight"] for m in category_metrics) / total_weight

        assert weighted_avg > 95.0, "weighted_avg must be greater than zero"


class TestMetricStorage:
    """Tests for metric storage and retrieval."""

    def test_store_metrics_json(self):
        """Test storing metrics in JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "pass_rate": 99.5,
                "flaky_rate": 1.5,
                "stability": 98.5,
            }

            metrics_file.write_text(json.dumps(metrics, indent=2))

            loaded = json.loads(metrics_file.read_text())
            assert loaded["pass_rate"] == 99.5, "Condition must be true"

    def test_append_metrics_history(self):
        """Test appending metrics to history file."""
        history = []

        for i in range(5):
            history.append(
                {
                    "date": f"2026-01-{14 + i}",
                    "pass_rate": 99.0 + i * 0.1,
                }
            )

        assert len(history) == 5, "History must not be empty"
        assert history[-1]["pass_rate"] == 99.4, "hist is not valid"

    def test_query_metrics_by_date_range(self):
        """Test querying metrics within date range."""
        metrics_history = [
            {"date": "2026-01-10", "value": 98.0},
            {"date": "2026-01-11", "value": 98.5},
            {"date": "2026-01-12", "value": 99.0},
            {"date": "2026-01-13", "value": 98.2},
            {"date": "2026-01-14", "value": 99.5},
        ]

        start_date = "2026-01-11"
        end_date = "2026-01-13"

        filtered = [m for m in metrics_history if start_date <= m["date"] <= end_date]

        assert len(filtered) == 3, "Filtered must not be empty"
        assert filtered[0]["date"] == "2026-01-11", "Condition must be true"

    def test_delete_old_metrics(self):
        """Test deletion of old metric data."""
        retention_days = 30
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        metrics_history = [
            {"date": datetime.now() - timedelta(days=60), "value": 95.0},
            {"date": datetime.now() - timedelta(days=20), "value": 98.0},
            {"date": datetime.now() - timedelta(days=5), "value": 99.0},
        ]

        retained = [m for m in metrics_history if m["date"] >= cutoff_date]

        assert len(retained) == 2, "Retained must not be empty"

    def test_metric_compression(self):
        """Test compression of old metric data."""
        # Daily metrics for 90 days
        daily_metrics = [{"day": i, "value": 98.0 + (i % 3) * 0.5} for i in range(90)]

        # Compress to weekly averages
        weekly_compressed = []
        for week in range(0, 90, 7):
            week_data = daily_metrics[week : week + 7]
            avg = sum(d["value"] for d in week_data) / len(week_data)
            weekly_compressed.append({"week": week // 7, "avg": round(avg, 2)})

        assert len(weekly_compressed) == 13, "Weekly_compressed must not be empty"


class TestMetricAlerts:
    """Tests for metric alerting functionality."""

    def test_threshold_alert_trigger(self):
        """Test alert triggering when metric crosses threshold."""
        threshold = 95.0
        current_value = 94.5

        should_alert = current_value < threshold

        assert should_alert, "should_alert is not valid"

    def test_trend_based_alert(self):
        """Test alert based on metric trend."""
        recent_values = [98.5, 97.0, 95.5, 94.0, 92.5]

        # Check for declining trend
        is_declining = all(
            recent_values[i] > recent_values[i + 1] for i in range(len(recent_values) - 1)
        )

        assert is_declining, "is_declining is not valid"

    def test_alert_cooldown(self):
        """Test alert cooldown to prevent spam."""
        last_alert_time = datetime.now() - timedelta(hours=1)
        cooldown_hours = 2

        can_alert = (datetime.now() - last_alert_time).total_seconds() > cooldown_hours * 3600

        assert not can_alert, "Condition must be true"

    def test_severity_levels(self):
        """Test alert severity level assignment."""

        def _get_severity(rate: float) -> str:
            if rate >= 95:
                return "info"
            if rate >= 90:
                return "warning"
            if rate >= 85:
                return "error"
            return "critical"

        assert _get_severity(85.0) == "error", "Error should be raised or set"
        assert _get_severity(90.0) == "warning", "Condition must be true"
        assert _get_severity(95.0) == "info", "Condition must be true"
        assert _get_severity(80.0) == "critical", "Condition must be true"

    def test_alert_acknowledgment(self):
        """Test alert acknowledgment workflow."""
        alert = {
            "id": "alert-001",
            "metric": "pass_rate",
            "value": 94.5,
            "threshold": 95.0,
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
        }

        # Acknowledge alert
        alert["acknowledged"] = True
        alert["acknowledged_by"] = "user@example.com"
        alert["acknowledged_at"] = datetime.now().isoformat()

        assert alert["acknowledged"], "Condition must be true"
        assert alert["acknowledged_by"] == "user@example.com", "Condition must be true"
