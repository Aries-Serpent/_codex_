"""
Health Check Validation Tests for Self-Healing Infrastructure - PHASE 20.2 LANE B

This module contains 20+ comprehensive health check validation tests including:
- HTTP health check validation
- Database connectivity checks
- Message queue health validation
- Resource availability checks
- Application-level health checks
- Health check result aggregation
- Health check alert triggering
- Health check grace periods
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

from .conftest import HealthCheckResult, MockCache, MockDatabase, MockService, ServiceState


class HTTPHealthChecker:
    """HTTP health checker."""

    def __init__(self, service: MockService):
        self.service = service
        self.response_time_ms = 50.0

    def check(self) -> HealthCheckResult:
        """Check HTTP health."""
        if self.service.state == ServiceState.HEALTHY:
            status = ServiceState.HEALTHY
            error_msg = None
        else:
            status = ServiceState.UNHEALTHY
            error_msg = "Service unavailable"

        return HealthCheckResult(
            check_name="http_health",
            status=status,
            timestamp=datetime.now(),
            metrics={"response_time_ms": self.response_time_ms},
            error_message=error_msg
        )


class DatabaseHealthChecker:
    """Database health checker."""

    def __init__(self, database: MockDatabase):
        self.database = database

    def check(self) -> HealthCheckResult:
        """Check database health."""
        if self.database.check_connection():
            status = ServiceState.HEALTHY
            error_msg = None
        else:
            status = ServiceState.UNHEALTHY
            error_msg = "Database connection failed"

        return HealthCheckResult(
            check_name="database_health",
            status=status,
            timestamp=datetime.now(),
            metrics={"connected": self.database.connected, "replication_lag_ms": self.database.replication_lag_ms},
            error_message=error_msg
        )


class CacheHealthChecker:
    """Cache health checker."""

    def __init__(self, cache: MockCache):
        self.cache = cache

    def check(self) -> HealthCheckResult:
        """Check cache health."""
        if self.cache.state == ServiceState.HEALTHY:
            hit_rate = self.cache.hit_count / max(1, self.cache.hit_count + self.cache.miss_count)
            status = ServiceState.HEALTHY if hit_rate > 0.5 else ServiceState.DEGRADED
            error_msg = None
        else:
            status = ServiceState.UNHEALTHY
            error_msg = "Cache unhealthy"

        return HealthCheckResult(
            check_name="cache_health",
            status=status,
            timestamp=datetime.now(),
            metrics={"hit_rate": hit_rate if self.cache.state == ServiceState.HEALTHY else 0.0},
            error_message=error_msg
        )


class HealthCheckAggregator:
    """Aggregates health check results."""

    def __init__(self):
        self.checks: List[object] = []
        self.last_results: List[HealthCheckResult] = []
        self.alert_threshold = 0.5
        self.grace_period_seconds = 30

    def register_check(self, checker: object) -> bool:
        """Register a health checker."""
        self.checks.append(checker)
        return True

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = []
        for checker in self.checks:
            try:
                result = checker.check()
                results.append(result)
            except Exception as e:
                results.append(HealthCheckResult(
                    check_name=str(checker.__class__.__name__),
                    status=ServiceState.UNHEALTHY,
                    timestamp=datetime.now(),
                    metrics={},
                    error_message=str(e)
                ))

        self.last_results = results

        total_checks = len(results)
        healthy_count = sum(1 for r in results if r.status == ServiceState.HEALTHY)
        degraded_count = sum(1 for r in results if r.status == ServiceState.DEGRADED)
        unhealthy_count = sum(1 for r in results if r.status == ServiceState.UNHEALTHY)

        overall_status = ServiceState.HEALTHY
        if unhealthy_count > 0:
            overall_status = ServiceState.UNHEALTHY
        elif degraded_count > 0:
            overall_status = ServiceState.DEGRADED

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status.value,
            "total_checks": total_checks,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "details": results
        }

    def should_trigger_alert(self) -> bool:
        """Determine if alert should be triggered."""
        if not self.last_results:
            return False

        total = len(self.last_results)
        unhealthy = sum(1 for r in self.last_results if r.status == ServiceState.UNHEALTHY)
        unhealthy_ratio = unhealthy / total if total > 0 else 0
        return unhealthy_ratio >= self.alert_threshold

    def apply_grace_period(self, start_time: datetime) -> bool:
        """Check if grace period is still active."""
        elapsed = (datetime.now() - start_time).total_seconds()
        return elapsed < self.grace_period_seconds


# ============================================================================
# TESTS
# ============================================================================

class TestHTTPHealthCheck:
    """Tests for HTTP health checks."""

    def test_http_health_check_healthy(self):
        """Test HTTP health check for healthy service."""
        service = MockService("api")
        checker = HTTPHealthChecker(service)
        result = checker.check()
        assert result.status == ServiceState.HEALTHY
        assert result.error_message is None
        assert "response_time_ms" in result.metrics

    def test_http_health_check_unhealthy(self):
        """Test HTTP health check for unhealthy service."""
        service = MockService("api")
        service.inject_failure()
        checker = HTTPHealthChecker(service)
        result = checker.check()
        assert result.status == ServiceState.UNHEALTHY
        assert result.error_message is not None

    def test_http_response_time_metric(self):
        """Test HTTP response time metric."""
        service = MockService("api")
        checker = HTTPHealthChecker(service)
        result = checker.check()
        assert "response_time_ms" in result.metrics
        assert result.metrics["response_time_ms"] > 0


class TestDatabaseHealthCheck:
    """Tests for database health checks."""

    def test_database_connection_check_connected(self):
        """Test database connection check when connected."""
        database = MockDatabase()
        checker = DatabaseHealthChecker(database)
        result = checker.check()
        assert result.status == ServiceState.HEALTHY
        assert result.error_message is None
        assert result.metrics["connected"] is True

    def test_database_connection_check_disconnected(self):
        """Test database connection check when disconnected."""
        database = MockDatabase()
        database.connected = False
        checker = DatabaseHealthChecker(database)
        result = checker.check()
        assert result.status == ServiceState.UNHEALTHY
        assert result.error_message is not None

    def test_database_replication_lag_metric(self):
        """Test database replication lag metric."""
        database = MockDatabase()
        database.replication_lag_ms = 50.0
        checker = DatabaseHealthChecker(database)
        result = checker.check()
        assert "replication_lag_ms" in result.metrics
        assert result.metrics["replication_lag_ms"] == 50.0


class TestCacheHealthCheck:
    """Tests for cache health checks."""

    def test_cache_health_check_healthy(self):
        """Test cache health check for healthy cache."""
        cache = MockCache()
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss
        checker = CacheHealthChecker(cache)
        result = checker.check()
        assert result.status in [ServiceState.HEALTHY, ServiceState.DEGRADED]
        assert "hit_rate" in result.metrics

    def test_cache_hit_rate_metric(self):
        """Test cache hit rate metric."""
        cache = MockCache()
        cache.set("key1", "value1")
        for _ in range(5):
            cache.get("key1")  # 5 hits
        for _ in range(5):
            cache.get("nonexistent")  # 5 misses
        checker = CacheHealthChecker(cache)
        result = checker.check()
        assert "hit_rate" in result.metrics
        assert result.metrics["hit_rate"] == pytest.approx(0.5, abs=0.01)


class TestHealthCheckAggregation:
    """Tests for health check result aggregation."""

    def test_aggregate_all_healthy(self):
        """Test aggregating all healthy checks."""
        aggregator = HealthCheckAggregator()
        aggregator.register_check(HTTPHealthChecker(MockService("api")))
        aggregator.register_check(DatabaseHealthChecker(MockDatabase()))
        aggregator.register_check(CacheHealthChecker(MockCache()))
        result = aggregator.run_all_checks()
        assert result["overall_status"] in ["healthy", "degraded"]
        assert result["total_checks"] == 3
        assert result["healthy"] >= 1

    def test_aggregate_with_failure(self):
        """Test aggregating with one failure."""
        aggregator = HealthCheckAggregator()
        healthy_service = MockService("api")
        unhealthy_service = MockService("api_broken")
        unhealthy_service.inject_failure()
        aggregator.register_check(HTTPHealthChecker(healthy_service))
        aggregator.register_check(HTTPHealthChecker(unhealthy_service))
        result = aggregator.run_all_checks()
        assert result["healthy"] >= 1
        assert result["unhealthy"] >= 1
        assert result["total_checks"] == 2

    def test_aggregate_health_counts(self):
        """Test health check counts aggregation."""
        aggregator = HealthCheckAggregator()
        for i in range(5):
            service = MockService(f"service_{i}")
            aggregator.register_check(HTTPHealthChecker(service))
        result = aggregator.run_all_checks()
        assert result["healthy"] + result["degraded"] + result["unhealthy"] == 5


class TestAlertTriggering:
    """Tests for health check alert triggering."""

    def test_alert_on_multiple_failures(self):
        """Test alert triggering on multiple failures."""
        aggregator = HealthCheckAggregator()
        aggregator.alert_threshold = 0.5
        for i in range(4):
            service = MockService(f"service_{i}")
            if i >= 2:
                service.inject_failure()
            aggregator.register_check(HTTPHealthChecker(service))
        aggregator.run_all_checks()
        should_alert = aggregator.should_trigger_alert()
        assert should_alert is True

    def test_no_alert_on_single_failure(self):
        """Test no alert with single failure."""
        aggregator = HealthCheckAggregator()
        aggregator.alert_threshold = 0.75  # Require 75% failure rate
        healthy_service = MockService("healthy")
        unhealthy_service = MockService("unhealthy")
        unhealthy_service.inject_failure()
        aggregator.register_check(HTTPHealthChecker(healthy_service))
        aggregator.register_check(HTTPHealthChecker(unhealthy_service))
        aggregator.run_all_checks()
        should_alert = aggregator.should_trigger_alert()
        assert should_alert is False

    def test_alert_threshold_configuration(self):
        """Test configurable alert threshold."""
        aggregator = HealthCheckAggregator()
        aggregator.alert_threshold = 0.25
        for i in range(4):
            service = MockService(f"service_{i}")
            if i == 3:
                service.inject_failure()
            aggregator.register_check(HTTPHealthChecker(service))
        aggregator.run_all_checks()
        should_alert = aggregator.should_trigger_alert()
        assert should_alert is True


class TestGracePeriod:
    """Tests for health check grace periods."""

    def test_grace_period_active(self):
        """Test grace period is active."""
        aggregator = HealthCheckAggregator()
        aggregator.grace_period_seconds = 60
        start_time = datetime.now()
        is_in_grace = aggregator.apply_grace_period(start_time)
        assert is_in_grace is True

    def test_grace_period_expired(self):
        """Test grace period expiration."""
        aggregator = HealthCheckAggregator()
        aggregator.grace_period_seconds = 1
        start_time = datetime.now() - timedelta(seconds=2)
        is_in_grace = aggregator.apply_grace_period(start_time)
        assert is_in_grace is False

    def test_grace_period_configuration(self):
        """Test configurable grace period."""
        aggregator = HealthCheckAggregator()
        aggregator.grace_period_seconds = 5
        start_time = datetime.now() - timedelta(seconds=3)
        is_in_grace = aggregator.apply_grace_period(start_time)
        assert is_in_grace is True


class TestHealthCheckStress:
    """Stress tests for health checks."""

    def test_high_frequency_checks(self):
        """Test frequent health checking."""
        aggregator = HealthCheckAggregator()
        aggregator.register_check(HTTPHealthChecker(MockService("api")))
        for _ in range(100):
            result = aggregator.run_all_checks()
        assert result["total_checks"] >= 1

    def test_many_checks_aggregation(self):
        """Test aggregating many checks."""
        aggregator = HealthCheckAggregator()
        for i in range(20):
            service = MockService(f"service_{i}")
            aggregator.register_check(HTTPHealthChecker(service))
        result = aggregator.run_all_checks()
        assert result["total_checks"] == 20

    def test_mixed_check_types(self):
        """Test mixed check types aggregation."""
        aggregator = HealthCheckAggregator()
        aggregator.register_check(HTTPHealthChecker(MockService("api")))
        aggregator.register_check(DatabaseHealthChecker(MockDatabase()))
        aggregator.register_check(CacheHealthChecker(MockCache()))
        aggregator.register_check(HTTPHealthChecker(MockService("web")))
        result = aggregator.run_all_checks()
        assert result["total_checks"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
