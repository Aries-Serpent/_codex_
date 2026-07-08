#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
# 
# 
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
# 
# 
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
#     def monitor(self):
#         return FeatureHealthMonitor(freshness_threshold_minutes=5)
# 
#     def test_record_feature_update(self, monitor):
#     def test_record_feature_update(self, monitor):
#         """Test recording feature updates."""
#         monitor.record_feature_update("test_feature")
#         assert "test_feature" in monitor.feature_updates, "Condition must be true"
#         assert monitor.feature_updates["test_feature"] is not None, "monit must be initialized"
# 
#     def test_check_healthy_feature(self, monitor):
#     def test_check_healthy_feature(self, monitor):
#         """Test checking a healthy feature."""
#         monitor.record_feature_update("healthy_feature")
#         status = monitor.check_feature_health("healthy_feature")
#         assert status.is_healthy, "Condition must be true"
#         assert status.feature_name == "healthy_feature", "feature_name is not valid"
#         assert status.freshness_level == "FRESH", "freshness_level is not valid"
# 
#     def test_check_stale_feature(self, monitor):
#     def test_check_stale_feature(self, monitor):
#         """Test checking a stale feature."""
#         # Manually set old update time (>6 hours for STALE)
#         monitor.feature_updates["stale_feature"] = datetime.now(UTC) - timedelta(hours=12)
#         status = monitor.check_feature_health("stale_feature")
#         assert not status.is_healthy, "Condition must be true"
#         assert status.freshness_minutes > 360, "freshness_minutes must be greater than zero"
#         assert status.freshness_level in ["STALE", "VERY_STALE"]
# 
#     def test_check_never_updated_feature(self, monitor):
#     def test_check_never_updated_feature(self, monitor):
#         """Test checking a feature that was never updated."""
#         status = monitor.check_feature_health("never_updated")
#         assert not status.is_healthy, "Condition must be true"
#         assert status.last_updated == "never", "last_updated is not valid"
#         assert status.freshness_level == "UNKNOWN", "freshness_level is not valid"
#         assert len(status.warnings) > 0, "Collection must not be empty"
# 
#     def test_record_feature_error(self, monitor):
#     def test_record_feature_error(self, monitor):
#         """Test recording feature errors."""
#         monitor.record_feature_error("error_feature")
#         monitor.record_feature_error("error_feature")
#         monitor.record_feature_error("error_feature")
#         assert monitor.error_counts["error_feature"] == 3, "Error should be raised or set"
# 
#     def test_check_feature_with_errors(self, monitor):
#     def test_check_feature_with_errors(self, monitor):
#         """Test checking feature with errors."""
#         monitor.record_feature_update("error_feature")
#         for _ in range(7):
#             monitor.record_feature_error("error_feature")
#             monitor.record_feature_error("error_feature")
# 
#         status = monitor.check_feature_health("error_feature")
#         assert not status.is_healthy, "Condition must be true"
#         assert status.error_count == 7, "Error should be raised or set"
#         assert len(status.warnings) > 0, "Collection must not be empty"
# 
#     def test_freshness_levels(self, monitor):
#     def test_freshness_levels(self, monitor):
#         """Test freshness level classification."""
#         # Fresh (< 1 hour)
#         assert monitor.get_freshness_level(30) == "FRESH", "monit is not valid"
#         assert monitor.get_freshness_level(120) == "ACCEPTABLE", "monit is not valid"
# 
#         # Stale (6-24 hours)
#         assert monitor.get_freshness_level(600) == "STALE", "monit is not valid"
# 
#         # Very stale (> 24 hours)
#         assert monitor.get_freshness_level(1500) == "VERY_STALE", "monit is not valid"
#         assert monitor.get_freshness_level(1500) == "VERY_STALE", "monit is not valid"
# 
#     def test_check_all_features(self, monitor):
#     def test_check_all_features(self, monitor):
#         """Test checking all features at once."""
#         monitor.record_feature_update("feat1")
#         monitor.record_feature_update("feat2")
#         monitor.record_feature_update("feat3")
#         results = monitor.check_all_features(["feat1", "feat2", "feat3"])
# 
#         assert len(results) == 3, "Results must not be empty"
#         assert all(isinstance(status, FeatureHealthStatus) for status in results.values())
# 
#     def test_freshness_report(self, monitor):
#     def test_freshness_report(self, monitor):
#         """Test freshness distribution report."""
#         monitor.record_feature_update("fresh1")
#         monitor.record_feature_update("fresh2")
#         monitor.feature_updates["stale1"] = datetime.now(UTC) - timedelta(hours=12)
#         report = monitor.get_freshness_report()
# 
#         assert "FRESH" in report, "Condition must be true"
#         assert "STALE" in report, "Condition must be true"
#         assert report["FRESH"] >= 2, "rep must be greater than zero"
# 
#     def test_alert_stale_features(self, monitor):
#     def test_alert_stale_features(self, monitor):
#         """Test alerting for stale features."""
#         monitor.record_feature_update("fresh")
#         monitor.feature_updates["stale"] = datetime.now(UTC) - timedelta(hours=25)
#         stale_features = monitor.alert_stale_features(threshold_hours=24)
# 
#         assert "stale" in stale_features, "Condition must be true"
#         assert "fresh" not in stale_features, "Condition must be true"
# 
#     def test_reset_error_counts(self, monitor):
#     def test_reset_error_counts(self, monitor):
#         """Test resetting error counts."""
#         monitor.record_feature_error("feat1")
#         monitor.record_feature_error("feat2")
#         assert len(monitor.error_counts) == 2, "Collection must not be empty"
# 
#         monitor.reset_error_counts()
# 
#         assert len(monitor.error_counts) == 0, "Collection must not be empty"
# 
#     def test_time_until_stale(self, monitor):
#     def test_time_until_stale(self, monitor):
#         """Test calculating time until feature becomes stale."""
#         monitor.record_feature_update("recent")
#         time_left = monitor.get_time_until_stale("recent", threshold_hours=24)
#         # Should be close to 24 hours
#         assert time_left > 23, "time_left must be greater than zero"
#         assert time_left <= 24, "time_left is not valid"
#         assert time_left <= 24, "time_left is not valid"
# 
#     def test_freshness_distribution(self, monitor):
#     def test_freshness_distribution(self, monitor):
#         """Test freshness distribution as percentages."""
#         monitor.record_feature_update("f1")
#         monitor.record_feature_update("f2")
#         monitor.feature_updates["f3"] = datetime.now(UTC) - timedelta(hours=12)
#         distribution = monitor.get_freshness_distribution()
# 
#         assert "FRESH" in distribution, "Condition must be true"
#         assert "STALE" in distribution, "Condition must be true"
#         assert sum(distribution.values()) == pytest.approx(100.0), "Value must be initialized"
# 
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
#     @pytest.fixture
#     def monitor(self):
#         return FeatureHealthMonitor(freshness_threshold_minutes=120)
# 
#     def test_generate_alerts_critical(self, monitor):
#     def test_generate_alerts_critical(self, monitor):
#         """Test generating critical alerts."""
#         health_statuses = {
#             "never_updated": FeatureHealthStatus(
#                 feature_name="never_updated",
#                 is_healthy=False,
#                 last_updated="never",
#                 freshness_minutes=0,
#                 freshness_level="UNKNOWN",
#             ),
#         }
#         alerts = monitor.generate_alerts(health_statuses)
# 
#         assert len(alerts) > 0, "Alerts must not be empty"
#         assert any(alert.severity == "CRITICAL" for alert in alerts), "severity is not valid"
# 
#     def test_generate_alerts_warning(self, monitor):
#     def test_generate_alerts_warning(self, monitor):
#         """Test generating warning alerts."""
#         health_statuses = {
#             "approaching_sla": FeatureHealthStatus(
#                 feature_name="approaching_sla",
#                 is_healthy=True,
#                 last_updated=datetime.now(UTC).isoformat(),
#                 freshness_minutes=100,  # 100/120 = 83% of SLA
#                 freshness_level="ACCEPTABLE",
#             ),
#         }
#         alerts = monitor.generate_alerts(health_statuses, sla_minutes=120)
# 
#         assert len(alerts) > 0, "Alerts must not be empty"
#         assert any(alert.severity == "WARNING" for alert in alerts), "severity is not valid"
# 
#     def test_generate_alerts_high_errors(self, monitor):
#     def test_generate_alerts_high_errors(self, monitor):
#         """Test generating alerts for high error rates."""
#         health_statuses = {
#             "error_feature": FeatureHealthStatus(
#                 feature_name="error_feature",
#                 is_healthy=False,
#                 last_updated=datetime.now(UTC).isoformat(),
#                 freshness_minutes=10,
#                 error_count=10,
#                 freshness_level="FRESH",
#             ),
#         }
#         alerts = monitor.generate_alerts(health_statuses)
# 
#         assert len(alerts) > 0, "Alerts must not be empty"
#         assert any("error" in alert.message.lower() for alert in alerts), "Error should be raised or set"
# 
#     def test_alert_to_dict(self):
#     def test_alert_to_dict(self):
#         """Test converting alert to dictionary."""
#         alert = HealthAlert(
#             feature_name="test",
#             severity="WARNING",
#             message="Test alert",
#             timestamp=datetime.now(UTC).isoformat(),
#             metric_value=50.0,
#         )
#         alert_dict = alert.to_dict()
# 
#         assert alert_dict["feature_name"] == "test", "Condition must be true"
#         assert alert_dict["severity"] == "WARNING", "Condition must be true"
#         assert alert_dict["metric_value"] == 50.0, "Value must be initialized"
# 
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
#     @pytest.fixture
#     def monitor(self):
#         return FeatureHealthMonitor()
# 
#     @pytest.fixture
#     def sample_statuses(self):
#         return {
#         return {
#             "healthy1": FeatureHealthStatus(
#                 feature_name="healthy1",
#                 is_healthy=True,
#                 last_updated=datetime.now(UTC).isoformat(),
#                 freshness_minutes=10,
#                 freshness_level="FRESH",
#             ),
#             "stale1": FeatureHealthStatus(
#                 feature_name="stale1",
#                 is_healthy=False,
#                 last_updated=(datetime.now(UTC) - timedelta(hours=12)).isoformat(),
#                 freshness_minutes=720,
#                 freshness_level="STALE",
#             ),
#         }
#     def test_generate_json_report(self, monitor, sample_statuses):
#     def test_generate_json_report(self, monitor, sample_statuses):
#         """Test generating JSON health report."""
#         import json
#         report_str = monitor.generate_health_report(
#             sample_statuses,
#             format="json",
#             include_recommendations=True,
#         )
# 
#         report = json.loads(report_str)
# 
#         assert "timestamp" in report, "Condition must be true"
#         assert "summary" in report, "Condition must be true"
#         assert "features" in report, "Condition must be true"
#         assert "alerts" in report, "Condition must be true"
#         assert "recommendations" in report, "Condition must be true"
#         assert report["summary"]["total_features"] == 2, "rep is not valid"
# 
#     def test_generate_markdown_report(self, monitor, sample_statuses):
#     def test_generate_markdown_report(self, monitor, sample_statuses):
#         """Test generating Markdown health report."""
#         report_str = monitor.generate_health_report(
#             sample_statuses,
#             format="markdown",
#             include_recommendations=True,
#         )
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "healthy1" in report_str, "Condition must be true"
#         assert "stale1" in report_str, "Condition must be true"
# 
#     def test_generate_recommendations(self, monitor, sample_statuses):
#     def test_generate_recommendations(self, monitor, sample_statuses):
#         """Test generating recommendations."""
#         recommendations = monitor._generate_recommendations(sample_statuses)
#         assert len(recommendations) > 0, "Recommendations must not be empty"
#         assert any("stale" in rec.lower() for rec in recommendations), "Condition must be true"


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
        monitor.feature_updates["transaction_amount"] = datetime.now(UTC) - timedelta(hours=2)

        # Check all features
        statuses = monitor.check_all_features(features)

        # Generate report
        report = monitor.generate_health_report(statuses, format="json")

        assert report is not None, "report must be initialized"
        assert len(statuses) == 3, "Statuses must not be empty"

    def test_sla_compliance_monitoring(self):
        """Test SLA compliance monitoring."""
        monitor = FeatureHealthMonitor()

        # Record updates at different times
        monitor.record_feature_update("sla_compliant")
        monitor.feature_updates["sla_warning"] = datetime.now(UTC) - timedelta(hours=23)
        monitor.feature_updates["sla_violation"] = datetime.now(UTC) - timedelta(hours=26)

        features = ["sla_compliant", "sla_warning", "sla_violation"]
        statuses = monitor.check_all_features(features)
        alerts = monitor.generate_alerts(statuses, sla_minutes=1440)  # 24 hours

        # Should have alerts for warning and violation
        assert len(alerts) > 0, "Alerts must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
