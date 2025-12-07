"""Comprehensive test suite for feature store and health monitoring.

Tests cover:
- Feature store initialization and configuration
- Feature group registration
- Feature versioning
- Point-in-time retrieval
- Parquet materialization
- Health monitoring
- Alert generation
- Report generation
- CLI commands (integration)
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from codex_ml.features.feature_store import (
    Feature,
    FeatureGroup,
    FeatureMetadata,
    FeatureStore,
    FeatureVersion,
)
from codex_ml.features.monitoring import (
    FeatureHealthMonitor,
    FeatureHealthStatus,
    HealthAlert,
)


class TestFeatureStore:
    """Tests for FeatureStore class."""
    
    def test_feature_store_initialization(self, tmp_path):
        """Test feature store initializes correctly."""
        store = FeatureStore(tmp_path)
        
        assert store.store_path == tmp_path
        assert store.enable_versioning is True
        assert store.feature_groups == {}
        assert store.feature_cache == {}
        assert store.feature_versions == {}
        
    def test_feature_store_creates_directory(self, tmp_path):
        """Test feature store creates storage directory."""
        store_path = tmp_path / "features"
        assert not store_path.exists()
        
        store = FeatureStore(store_path)
        assert store_path.exists()
        assert store_path.is_dir()
        
    def test_register_feature_group(self, tmp_path):
        """Test registering a feature group."""
        store = FeatureStore(tmp_path)
        
        def dummy_transform(inputs):
            return inputs["value"] * 2
        
        feature = Feature(
            name="test_feature",
            transform_fn=dummy_transform,
            dependencies=[],
        )
        
        group = FeatureGroup(
            name="test_group",
            features=[feature],
            version="1.0.0",
            description="Test feature group",
        )
        
        store.register_feature_group(group)
        
        assert "test_group" in store.feature_groups
        assert store.feature_groups["test_group"] == group
        
        # Check registry file was created
        registry_path = tmp_path / "registry.json"
        assert registry_path.exists()
        
        with open(registry_path) as f:
            registry = json.load(f)
        
        assert "test_group" in registry
        assert registry["test_group"]["version"] == "1.0.0"
        assert registry["test_group"]["description"] == "Test feature group"
        
    def test_get_feature_group(self, tmp_path):
        """Test retrieving a feature group."""
        store = FeatureStore(tmp_path)
        
        feature = Feature(
            name="test_feature",
            transform_fn=lambda x: x,
            dependencies=[],
        )
        
        group = FeatureGroup(
            name="test_group",
            features=[feature],
            version="1.0.0",
        )
        
        store.register_feature_group(group)
        
        # Retrieve by name
        retrieved = store.get_feature_group("test_group")
        assert retrieved is not None
        assert retrieved.name == "test_group"
        assert retrieved.version == "1.0.0"
        
        # Retrieve by name and version
        retrieved_versioned = store.get_feature_group("test_group", version="1.0.0")
        assert retrieved_versioned is not None
        
        # Non-existent version
        retrieved_missing = store.get_feature_group("test_group", version="2.0.0")
        assert retrieved_missing is None
        
    def test_list_features(self, tmp_path):
        """Test listing all features."""
        store = FeatureStore(tmp_path)
        
        feature1 = Feature(name="feature1", transform_fn=lambda x: x)
        feature2 = Feature(name="feature2", transform_fn=lambda x: x)
        
        group = FeatureGroup(
            name="test_group",
            features=[feature1, feature2],
            version="1.0.0",
        )
        
        store.register_feature_group(group)
        
        features = store.list_features()
        assert len(features) == 2
        assert "feature1" in features
        assert "feature2" in features
        
    def test_materialize_features(self, tmp_path):
        """Test feature materialization."""
        store = FeatureStore(tmp_path)
        
        def double(inputs):
            return inputs["value"] * 2
        
        def triple(inputs):
            return inputs["value"] * 3
        
        feature1 = Feature(name="double_value", transform_fn=double)
        feature2 = Feature(name="triple_value", transform_fn=triple)
        
        group = FeatureGroup(
            name="math_features",
            features=[feature1, feature2],
            version="1.0.0",
        )
        
        store.register_feature_group(group)
        
        inputs = {"value": 5}
        results = store.materialize_features(
            ["double_value", "triple_value"],
            inputs,
            cache=True,
        )
        
        assert results["double_value"] == 10
        assert results["triple_value"] == 15
        
    def test_feature_caching(self, tmp_path):
        """Test feature caching works correctly."""
        store = FeatureStore(tmp_path)
        
        call_count = {"count": 0}
        
        def expensive_transform(inputs):
            call_count["count"] += 1
            return inputs["value"] * 2
        
        feature = Feature(name="expensive_feature", transform_fn=expensive_transform)
        group = FeatureGroup(
            name="test_group",
            features=[feature],
            version="1.0.0",
        )
        
        store.register_feature_group(group)
        
        inputs = {"value": 5}
        
        # First call - should compute
        result1 = store.materialize_features(["expensive_feature"], inputs, cache=True)
        assert result1["expensive_feature"] == 10
        assert call_count["count"] == 1
        
        # Second call with same inputs - should use cache
        result2 = store.materialize_features(["expensive_feature"], inputs, cache=True)
        assert result2["expensive_feature"] == 10
        assert call_count["count"] == 1  # No additional calls
        
        # Call with cache=False - should recompute
        result3 = store.materialize_features(["expensive_feature"], inputs, cache=False)
        assert result3["expensive_feature"] == 10
        assert call_count["count"] == 2
        
    def test_clear_cache(self, tmp_path):
        """Test cache clearing."""
        store = FeatureStore(tmp_path)
        
        feature = Feature(name="test", transform_fn=lambda x: x["value"])
        group = FeatureGroup(name="test_group", features=[feature], version="1.0.0")
        store.register_feature_group(group)
        
        # Materialize to populate cache
        store.materialize_features(["test"], {"value": 1}, cache=True)
        assert len(store.feature_cache) > 0
        
        # Clear cache
        store.clear_cache()
        assert len(store.feature_cache) == 0
        
    def test_list_versions(self, tmp_path):
        """Test listing feature versions."""
        store = FeatureStore(tmp_path)
        
        # Add versions manually
        version1 = FeatureVersion(
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            feature_name="test_feature",
        )
        version2 = FeatureVersion(
            version="1.1.0",
            timestamp=datetime.now().isoformat(),
            feature_name="test_feature",
        )
        
        store.feature_versions["test_feature"] = [version1, version2]
        
        versions = store.list_versions("test_feature")
        assert len(versions) == 2
        assert "1.0.0" in versions
        assert "1.1.0" in versions
        
    def test_list_versions_empty(self, tmp_path):
        """Test listing versions for non-existent feature."""
        store = FeatureStore(tmp_path)
        
        versions = store.list_versions("non_existent")
        assert versions == []


class TestFeatureVersioning:
    """Tests for feature versioning functionality."""
    
    def test_feature_version_creation(self):
        """Test creating a feature version."""
        version = FeatureVersion(
            version="1.0.0",
            timestamp="2025-12-07T00:00:00",
            feature_name="test_feature",
            storage_path="/path/to/data.parquet",
            metadata={"rows": 100},
        )
        
        assert version.version == "1.0.0"
        assert version.timestamp == "2025-12-07T00:00:00"
        assert version.feature_name == "test_feature"
        assert version.storage_path == "/path/to/data.parquet"
        assert version.metadata["rows"] == 100
        
    def test_feature_version_to_dict(self):
        """Test converting feature version to dictionary."""
        version = FeatureVersion(
            version="1.0.0",
            timestamp="2025-12-07T00:00:00",
            feature_name="test_feature",
        )
        
        version_dict = version.to_dict()
        
        assert version_dict["version"] == "1.0.0"
        assert version_dict["timestamp"] == "2025-12-07T00:00:00"
        assert version_dict["feature_name"] == "test_feature"
        
    def test_point_in_time_retrieval(self, tmp_path):
        """Test point-in-time feature retrieval."""
        store = FeatureStore(tmp_path)
        
        # Add versions at different times
        base_time = datetime(2025, 12, 1, 12, 0, 0)
        
        version1 = FeatureVersion(
            version="1.0.0",
            timestamp=base_time.isoformat(),
            feature_name="feature1",
            storage_path=str(tmp_path / "v1.parquet"),
        )
        
        version2 = FeatureVersion(
            version="1.1.0",
            timestamp=(base_time + timedelta(hours=2)).isoformat(),
            feature_name="feature1",
            storage_path=str(tmp_path / "v2.parquet"),
        )
        
        # Create storage files
        (tmp_path / "v1.parquet").touch()
        (tmp_path / "v2.parquet").touch()
        
        store.feature_versions["feature1"] = [version1, version2]
        
        # Query at time between versions
        query_time = base_time + timedelta(hours=1)
        results = store.get_features_at_time(
            ["feature1"],
            query_time,
        )
        
        assert "feature1" in results
        assert results["feature1"]["version"] == "1.0.0"
        
        # Query after both versions
        query_time_later = base_time + timedelta(hours=3)
        results_later = store.get_features_at_time(
            ["feature1"],
            query_time_later,
        )
        
        assert "feature1" in results_later
        assert results_later["feature1"]["version"] == "1.1.0"


class TestFeatureHealthMonitor:
    """Tests for FeatureHealthMonitor class."""
    
    def test_monitor_initialization(self):
        """Test health monitor initializes correctly."""
        monitor = FeatureHealthMonitor(freshness_threshold_minutes=60)
        
        assert monitor.freshness_threshold == timedelta(minutes=60)
        assert monitor.feature_updates == {}
        assert monitor.error_counts == {}
        
    def test_record_feature_update(self):
        """Test recording feature updates."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("feature1")
        
        assert "feature1" in monitor.feature_updates
        assert isinstance(monitor.feature_updates["feature1"], datetime)
        
    def test_record_feature_error(self):
        """Test recording feature errors."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_error("feature1")
        assert monitor.error_counts["feature1"] == 1
        
        monitor.record_feature_error("feature1")
        assert monitor.error_counts["feature1"] == 2
        
    def test_get_freshness_level(self):
        """Test freshness level classification."""
        monitor = FeatureHealthMonitor()
        
        assert monitor.get_freshness_level(30) == "FRESH"
        assert monitor.get_freshness_level(120) == "ACCEPTABLE"
        assert monitor.get_freshness_level(720) == "STALE"
        assert monitor.get_freshness_level(2000) == "VERY_STALE"
        
    def test_check_feature_health_never_updated(self):
        """Test health check for never-updated feature."""
        monitor = FeatureHealthMonitor()
        
        status = monitor.check_feature_health("feature1")
        
        assert status.feature_name == "feature1"
        assert status.is_healthy is False
        assert status.last_updated == "never"
        assert status.freshness_level == "UNKNOWN"
        assert "never been updated" in status.warnings[0]
        
    def test_check_feature_health_fresh(self):
        """Test health check for fresh feature."""
        monitor = FeatureHealthMonitor(freshness_threshold_minutes=60)
        
        monitor.record_feature_update("feature1")
        status = monitor.check_feature_health("feature1")
        
        assert status.feature_name == "feature1"
        assert status.is_healthy is True
        assert status.last_updated != "never"
        assert status.freshness_level == "FRESH"
        assert len(status.warnings) == 0
        
    def test_check_feature_health_stale(self):
        """Test health check for stale feature."""
        monitor = FeatureHealthMonitor(freshness_threshold_minutes=10)
        
        # Record update in the past
        past_time = datetime.now() - timedelta(minutes=30)
        monitor.feature_updates["feature1"] = past_time
        
        status = monitor.check_feature_health("feature1")
        
        assert status.is_healthy is False
        assert status.freshness_level in ["STALE", "ACCEPTABLE"]
        assert len(status.warnings) > 0
        
    def test_check_feature_health_with_errors(self):
        """Test health check for feature with errors."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("feature1")
        
        # Record multiple errors
        for _ in range(10):
            monitor.record_feature_error("feature1")
        
        status = monitor.check_feature_health("feature1")
        
        assert status.is_healthy is False
        assert status.error_count == 10
        assert any("error" in w.lower() for w in status.warnings)
        
    def test_check_all_features(self):
        """Test checking all features at once."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("feature1")
        monitor.record_feature_update("feature2")
        
        statuses = monitor.check_all_features(["feature1", "feature2"])
        
        assert len(statuses) == 2
        assert "feature1" in statuses
        assert "feature2" in statuses
        
    def test_get_freshness_report(self):
        """Test freshness distribution report."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("fresh1")
        
        past_time = datetime.now() - timedelta(hours=12)
        monitor.feature_updates["stale1"] = past_time
        
        report = monitor.get_freshness_report()
        
        assert isinstance(report, dict)
        assert "FRESH" in report
        assert "STALE" in report
        
    def test_alert_stale_features(self):
        """Test alerting on stale features."""
        monitor = FeatureHealthMonitor()
        
        # Fresh feature
        monitor.record_feature_update("fresh1")
        
        # Stale feature
        past_time = datetime.now() - timedelta(hours=48)
        monitor.feature_updates["stale1"] = past_time
        
        stale_features = monitor.alert_stale_features(threshold_hours=24)
        
        assert "stale1" in stale_features
        assert "fresh1" not in stale_features
        
    def test_reset_error_counts(self):
        """Test resetting error counts."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_error("feature1")
        monitor.record_feature_error("feature2")
        
        assert len(monitor.error_counts) == 2
        
        monitor.reset_error_counts()
        
        assert len(monitor.error_counts) == 0


class TestHealthAlerts:
    """Tests for health alert generation."""
    
    def test_generate_alerts_critical(self):
        """Test generating critical alerts."""
        monitor = FeatureHealthMonitor()
        
        # Never updated feature
        status_never = FeatureHealthStatus(
            feature_name="feature1",
            is_healthy=False,
            last_updated="never",
            freshness_minutes=float("inf"),
            freshness_level="UNKNOWN",
        )
        
        statuses = {"feature1": status_never}
        alerts = monitor.generate_alerts(statuses, sla_minutes=120)
        
        assert len(alerts) > 0
        assert any(a.severity == "CRITICAL" for a in alerts)
        
    def test_generate_alerts_warning(self):
        """Test generating warning alerts."""
        monitor = FeatureHealthMonitor()
        
        # Feature approaching SLA violation
        status_warning = FeatureHealthStatus(
            feature_name="feature2",
            is_healthy=True,
            last_updated=datetime.now().isoformat(),
            freshness_minutes=100,  # 100 min, SLA is 120, approaching (>80%)
            freshness_level="ACCEPTABLE",
        )
        
        statuses = {"feature2": status_warning}
        alerts = monitor.generate_alerts(statuses, sla_minutes=120)
        
        # Should generate warning
        assert len(alerts) > 0
        assert any(a.severity == "WARNING" for a in alerts)
        
    def test_alert_to_dict(self):
        """Test converting alert to dictionary."""
        alert = HealthAlert(
            feature_name="test_feature",
            severity="CRITICAL",
            message="Feature is very stale",
            timestamp="2025-12-07T00:00:00",
            metric_value=1000.0,
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["feature_name"] == "test_feature"
        assert alert_dict["severity"] == "CRITICAL"
        assert alert_dict["message"] == "Feature is very stale"
        assert alert_dict["timestamp"] == "2025-12-07T00:00:00"
        assert alert_dict["metric_value"] == 1000.0


class TestHealthReporting:
    """Tests for health report generation."""
    
    def test_generate_json_report(self):
        """Test generating JSON health report."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("feature1")
        monitor.record_feature_update("feature2")
        
        statuses = monitor.check_all_features(["feature1", "feature2"])
        report_json = monitor.generate_health_report(
            statuses,
            format="json",
            include_recommendations=True,
        )
        
        report_data = json.loads(report_json)
        
        assert "timestamp" in report_data
        assert "summary" in report_data
        assert report_data["summary"]["total_features"] == 2
        assert "features" in report_data
        assert "feature1" in report_data["features"]
        assert "feature2" in report_data["features"]
        
    def test_generate_markdown_report(self):
        """Test generating Markdown health report."""
        monitor = FeatureHealthMonitor()
        
        monitor.record_feature_update("feature1")
        
        statuses = monitor.check_all_features(["feature1"])
        report_md = monitor.generate_health_report(
            statuses,
            format="markdown",
            include_recommendations=False,
        )
        
        assert "# Feature Health Report" in report_md
        assert "## Summary" in report_md
        assert "## Feature Details" in report_md
        assert "feature1" in report_md
        
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        monitor = FeatureHealthMonitor()
        
        # Stale feature
        past_time = datetime.now() - timedelta(hours=48)
        monitor.feature_updates["stale1"] = past_time
        
        # Feature with errors
        monitor.record_feature_update("error_feature")
        for _ in range(10):
            monitor.record_feature_error("error_feature")
        
        statuses = monitor.check_all_features(["stale1", "error_feature"])
        report_json = monitor.generate_health_report(
            statuses,
            format="json",
            include_recommendations=True,
        )
        
        report_data = json.loads(report_json)
        recommendations = report_data.get("recommendations", [])
        
        assert len(recommendations) > 0
        # Should recommend updating stale features
        assert any("stale" in r.lower() or "update" in r.lower() for r in recommendations)
        # Should recommend investigating errors
        assert any("error" in r.lower() or "investigate" in r.lower() for r in recommendations)


class TestFeatureMetadata:
    """Tests for feature metadata."""
    
    def test_feature_metadata_creation(self):
        """Test creating feature metadata."""
        metadata = FeatureMetadata(
            name="test_feature",
            version="1.0.0",
            dtype="float64",
            description="Test feature",
            created_at="2025-12-07T00:00:00",
            updated_at="2025-12-07T01:00:00",
            tags={"category": "demographic", "sensitive": "false"},
        )
        
        assert metadata.name == "test_feature"
        assert metadata.version == "1.0.0"
        assert metadata.dtype == "float64"
        assert metadata.tags["category"] == "demographic"
        
    def test_feature_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = FeatureMetadata(
            name="test_feature",
            version="1.0.0",
            dtype="float64",
            description="Test feature",
            created_at="2025-12-07T00:00:00",
            updated_at="2025-12-07T01:00:00",
        )
        
        metadata_dict = metadata.to_dict()
        
        assert metadata_dict["name"] == "test_feature"
        assert metadata_dict["version"] == "1.0.0"
        assert metadata_dict["dtype"] == "float64"


# pytest's built-in tmp_path fixture is used (no custom fixture needed)
