"""Complete Feature Health Monitoring tests."""

import pytest
import time
from datetime import datetime, timedelta
from codex_ml.features.monitoring import FeatureHealthMonitor, FeatureHealthStatus, HealthAlert


class TestFeatureHealthMonitor:
    """Test complete feature health monitoring."""

    @pytest.fixture
    def monitor(self):
        return FeatureHealthMonitor(freshness_threshold_minutes=5)

    def test_record_feature_update(self, monitor):
        """Test recording feature updates."""
        monitor.record_feature_update("test_feature")
        
        assert "test_feature" in monitor.feature_updates
        assert monitor.feature_updates["test_feature"] is not None

    def test_check_healthy_feature(self, monitor):
        """Test checking a healthy feature."""
        monitor.record_feature_update("healthy_feature")
        
        status = monitor.check_feature_health("healthy_feature")
        assert status.is_healthy
        assert status.feature_name == "healthy_feature"
        assert status.freshness_level == "FRESH"

    def test_check_stale_feature(self, monitor):
        """Test checking a stale feature."""
        # Manually set old update time
        monitor.feature_updates["stale_feature"] = datetime.now() - timedelta(hours=2)
        
        status = monitor.check_feature_health("stale_feature")
        assert not status.is_healthy
        assert status.freshness_minutes > 60
        assert status.freshness_level in ["STALE", "VERY_STALE"]

    def test_check_never_updated_feature(self, monitor):
        """Test checking a feature that was never updated."""
        status = monitor.check_feature_health("never_updated")
        
        assert not status.is_healthy
        assert status.last_updated == "never"
        assert status.freshness_level == "UNKNOWN"
        assert len(status.warnings) > 0

    def test_record_feature_error(self, monitor):
        """Test recording feature errors."""
        monitor.record_feature_error("error_feature")
        monitor.record_feature_error("error_feature")
        monitor.record_feature_error("error_feature")
        
        assert monitor.error_counts["error_feature"] == 3

    def test_check_feature_with_errors(self, monitor):
        """Test checking feature with errors."""
        monitor.record_feature_update("error_feature")
        
        # Record multiple errors
        for _ in range(7):
            monitor.record_feature_error("error_feature")
        
        status = monitor.check_feature_health("error_feature")
        assert not status.is_healthy
        assert status.error_count == 7
        assert len(status.warnings) > 0

    def test_freshness_levels(self, monitor):
        """Test freshness level classification."""
        # Fresh (< 1 hour)
        assert monitor.get_freshness_level(30) == "FRESH"
        
        # Acceptable (1-6 hours)
        assert monitor.get_freshness_level(120) == "ACCEPTABLE"
        
        # Stale (6-24 hours)
        assert monitor.get_freshness_level(600) == "STALE"
        
        # Very stale (> 24 hours)
        assert monitor.get_freshness_level(1500) == "VERY_STALE"

    def test_check_all_features(self, monitor):
        """Test checking all features at once."""
        monitor.record_feature_update("feat1")
        monitor.record_feature_update("feat2")
        monitor.record_feature_update("feat3")
        
        results = monitor.check_all_features(["feat1", "feat2", "feat3"])
        
        assert len(results) == 3
        assert all(isinstance(status, FeatureHealthStatus) for status in results.values())

    def test_freshness_report(self, monitor):
        """Test freshness distribution report."""
        monitor.record_feature_update("fresh1")
        monitor.record_feature_update("fresh2")
        monitor.feature_updates["stale1"] = datetime.now() - timedelta(hours=12)
        
        report = monitor.get_freshness_report()
        
        assert "FRESH" in report
        assert "STALE" in report
        assert report["FRESH"] >= 2

    def test_alert_stale_features(self, monitor):
        """Test alerting for stale features."""
        monitor.record_feature_update("fresh")
        monitor.feature_updates["stale"] = datetime.now() - timedelta(hours=25)
        
        stale_features = monitor.alert_stale_features(threshold_hours=24)
        
        assert "stale" in stale_features
        assert "fresh" not in stale_features

    def test_reset_error_counts(self, monitor):
        """Test resetting error counts."""
        monitor.record_feature_error("feat1")
        monitor.record_feature_error("feat2")
        
        assert len(monitor.error_counts) == 2
        
        monitor.reset_error_counts()
        
        assert len(monitor.error_counts) == 0

    def test_time_until_stale(self, monitor):
        """Test calculating time until feature becomes stale."""
        monitor.record_feature_update("recent")
        
        time_left = monitor.get_time_until_stale("recent", threshold_hours=24)
        
        # Should be close to 24 hours
        assert time_left > 23
        assert time_left <= 24

    def test_freshness_distribution(self, monitor):
        """Test freshness distribution as percentages."""
        monitor.record_feature_update("f1")
        monitor.record_feature_update("f2")
        monitor.feature_updates["f3"] = datetime.now() - timedelta(hours=12)
        
        distribution = monitor.get_freshness_distribution()
        
        assert "FRESH" in distribution
        assert "STALE" in distribution
        assert sum(distribution.values()) == pytest.approx(100.0)


class TestHealthAlerts:
    """Test health alert generation."""

    @pytest.fixture
    def monitor(self):
        return FeatureHealthMonitor(freshness_threshold_minutes=120)

    def test_generate_alerts_critical(self, monitor):
        """Test generating critical alerts."""
        health_statuses = {
            "never_updated": FeatureHealthStatus(
                feature_name="never_updated",
                is_healthy=False,
                last_updated="never",
                freshness_minutes=0,
                freshness_level="UNKNOWN",
            ),
        }
        
        alerts = monitor.generate_alerts(health_statuses)
        
        assert len(alerts) > 0
        assert any(alert.severity == "CRITICAL" for alert in alerts)

    def test_generate_alerts_warning(self, monitor):
        """Test generating warning alerts."""
        health_statuses = {
            "approaching_sla": FeatureHealthStatus(
                feature_name="approaching_sla",
                is_healthy=True,
                last_updated=datetime.now().isoformat(),
                freshness_minutes=100,  # 100/120 = 83% of SLA
                freshness_level="ACCEPTABLE",
            ),
        }
        
        alerts = monitor.generate_alerts(health_statuses, sla_minutes=120)
        
        assert len(alerts) > 0
        assert any(alert.severity == "WARNING" for alert in alerts)

    def test_generate_alerts_high_errors(self, monitor):
        """Test generating alerts for high error rates."""
        health_statuses = {
            "error_feature": FeatureHealthStatus(
                feature_name="error_feature",
                is_healthy=False,
                last_updated=datetime.now().isoformat(),
                freshness_minutes=10,
                error_count=10,
                freshness_level="FRESH",
            ),
        }
        
        alerts = monitor.generate_alerts(health_statuses)
        
        assert len(alerts) > 0
        assert any("error" in alert.message.lower() for alert in alerts)

    def test_alert_to_dict(self):
        """Test converting alert to dictionary."""
        alert = HealthAlert(
            feature_name="test",
            severity="WARNING",
            message="Test alert",
            timestamp=datetime.now().isoformat(),
            metric_value=50.0,
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["feature_name"] == "test"
        assert alert_dict["severity"] == "WARNING"
        assert alert_dict["metric_value"] == 50.0


class TestHealthReports:
    """Test health report generation."""

    @pytest.fixture
    def monitor(self):
        return FeatureHealthMonitor()

    @pytest.fixture
    def sample_statuses(self):
        return {
            "healthy1": FeatureHealthStatus(
                feature_name="healthy1",
                is_healthy=True,
                last_updated=datetime.now().isoformat(),
                freshness_minutes=10,
                freshness_level="FRESH",
            ),
            "stale1": FeatureHealthStatus(
                feature_name="stale1",
                is_healthy=False,
                last_updated=(datetime.now() - timedelta(hours=12)).isoformat(),
                freshness_minutes=720,
                freshness_level="STALE",
            ),
        }

    def test_generate_json_report(self, monitor, sample_statuses):
        """Test generating JSON health report."""
        import json
        
        report_str = monitor.generate_health_report(
            sample_statuses,
            format="json",
            include_recommendations=True,
        )
        
        report = json.loads(report_str)
        
        assert "timestamp" in report
        assert "summary" in report
        assert "features" in report
        assert "alerts" in report
        assert "recommendations" in report
        assert report["summary"]["total_features"] == 2

    def test_generate_markdown_report(self, monitor, sample_statuses):
        """Test generating Markdown health report."""
        report_str = monitor.generate_health_report(
            sample_statuses,
            format="markdown",
            include_recommendations=True,
        )
        
        assert "# Feature Health Report" in report_str
        assert "## Summary" in report_str
        assert "healthy1" in report_str
        assert "stale1" in report_str

    def test_generate_recommendations(self, monitor, sample_statuses):
        """Test generating recommendations."""
        recommendations = monitor._generate_recommendations(sample_statuses)
        
        assert len(recommendations) > 0
        assert any("stale" in rec.lower() for rec in recommendations)


class TestFeatureHealthIntegration:
    """Test integration scenarios."""

    def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        monitor = FeatureHealthMonitor(freshness_threshold_minutes=60)
        
        # Record some feature updates
        features = ["user_age", "user_score", "transaction_amount"]
        for feature in features:
            monitor.record_feature_update(feature)
        
        # Simulate some errors
        monitor.record_feature_error("user_score")
        monitor.record_feature_error("user_score")
        
        # Make one feature stale
        monitor.feature_updates["transaction_amount"] = datetime.now() - timedelta(hours=2)
        
        # Check all features
        statuses = monitor.check_all_features(features)
        
        # Generate report
        report = monitor.generate_health_report(statuses, format="json")
        
        assert report is not None
        assert len(statuses) == 3

    def test_sla_compliance_monitoring(self):
        """Test SLA compliance monitoring."""
        monitor = FeatureHealthMonitor()
        
        # Record updates at different times
        monitor.record_feature_update("sla_compliant")
        monitor.feature_updates["sla_warning"] = datetime.now() - timedelta(hours=23)
        monitor.feature_updates["sla_violation"] = datetime.now() - timedelta(hours=26)
        
        features = ["sla_compliant", "sla_warning", "sla_violation"]
        statuses = monitor.check_all_features(features)
        alerts = monitor.generate_alerts(statuses, sla_minutes=1440)  # 24 hours
        
        # Should have alerts for warning and violation
        assert len(alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
