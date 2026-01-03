"""
Tests for Production Deployment Module (Phase 8.5).

Comprehensive test suite covering:
- Health checks
- Monitoring integration
- Deployment configuration
- Production test suite
"""
import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_deployment import (
    # Health checks
    HealthStatus,
    HealthCheckResult,
    HealthCheck,
    MemoryHealthCheck,
    DatabaseHealthCheck,
    LearningEngineHealthCheck,
    HealthCheckEndpoint,
    # Monitoring
    MetricValue,
    MetricsCollector,
    LogLevel,
    LogEntry,
    LogAggregator,
    MonitoringIntegration,
    # Deployment
    ContainerConfig,
    KubernetesConfig,
    DeploymentConfiguration,
    # Tests
    ProductionTest,
    HealthEndpointTest,
    LearningEngineTest,
    ProductionTestSuite,
)


# =============================================================================
# HEALTH CHECK TESTS
# =============================================================================


class TestHealthStatus:
    """Tests for HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test health status values exist."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheckResult:
    """Tests for HealthCheckResult."""
    
    def test_create_result(self):
        """Test creating health check result."""
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="All good",
        )
        
        assert result.component == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.timestamp != ""
    
    def test_result_with_details(self):
        """Test result with details."""
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.DEGRADED,
            details={'metric': 42},
        )
        
        assert result.details['metric'] == 42


class TestMemoryHealthCheck:
    """Tests for MemoryHealthCheck."""
    
    def test_create_check(self):
        """Test creating memory health check."""
        check = MemoryHealthCheck()
        assert check.name == "memory"
    
    def test_run_check(self):
        """Test running memory check."""
        check = MemoryHealthCheck()
        result = check.check()
        
        assert result.component == "memory"
        assert result.status in list(HealthStatus)
        assert result.latency_ms >= 0


class TestDatabaseHealthCheck:
    """Tests for DatabaseHealthCheck."""
    
    def test_create_check(self):
        """Test creating database health check."""
        check = DatabaseHealthCheck()
        assert check.name == "database"
    
    def test_run_check_memory_db(self):
        """Test running check with in-memory database."""
        check = DatabaseHealthCheck(":memory:")
        result = check.check()
        
        assert result.status == HealthStatus.HEALTHY
    
    def test_run_check_invalid_db(self):
        """Test running check with invalid database."""
        check = DatabaseHealthCheck("/nonexistent/path/db.sqlite")
        result = check.check()
        
        # Should fail but not crash
        assert result.status in list(HealthStatus)


class TestLearningEngineHealthCheck:
    """Tests for LearningEngineHealthCheck."""
    
    def test_no_engine(self):
        """Test check with no engine."""
        check = LearningEngineHealthCheck()
        result = check.check()
        
        assert result.status == HealthStatus.UNKNOWN
    
    def test_valid_engine(self):
        """Test check with valid engine mock."""
        class MockEngine:
            def select_action(self): pass
            def update(self): pass
        
        check = LearningEngineHealthCheck(MockEngine())
        result = check.check()
        
        assert result.status == HealthStatus.HEALTHY


class TestHealthCheckEndpoint:
    """Tests for HealthCheckEndpoint."""
    
    def test_create_endpoint(self):
        """Test creating endpoint."""
        endpoint = HealthCheckEndpoint()
        assert endpoint is not None
    
    def test_register_check(self):
        """Test registering check."""
        endpoint = HealthCheckEndpoint()
        check = MemoryHealthCheck()
        
        endpoint.register(check)
        
        assert len(endpoint.checks) == 1
    
    def test_run_checks(self):
        """Test running all checks."""
        endpoint = HealthCheckEndpoint()
        endpoint.register(MemoryHealthCheck())
        endpoint.register(DatabaseHealthCheck(":memory:"))
        
        results = endpoint.run_checks()
        
        assert "memory" in results
        assert "database" in results
    
    def test_get_overall_status(self):
        """Test getting overall status."""
        endpoint = HealthCheckEndpoint()
        endpoint.register(DatabaseHealthCheck(":memory:"))
        
        endpoint.run_checks()
        status = endpoint.get_overall_status()
        
        assert status == HealthStatus.HEALTHY
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        endpoint = HealthCheckEndpoint()
        endpoint.register(MemoryHealthCheck())
        endpoint.run_checks()
        
        result = endpoint.to_dict()
        
        assert 'status' in result
        assert 'checks' in result


# =============================================================================
# MONITORING TESTS
# =============================================================================


class TestMetricValue:
    """Tests for MetricValue."""
    
    def test_create_metric(self):
        """Test creating metric value."""
        metric = MetricValue(
            name="test_metric",
            value=42.0,
            labels={'env': 'test'},
        )
        
        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.timestamp != ""


class TestMetricsCollector:
    """Tests for MetricsCollector."""
    
    def test_create_collector(self):
        """Test creating collector."""
        collector = MetricsCollector()
        assert collector is not None
    
    def test_increment_counter(self):
        """Test incrementing counter."""
        collector = MetricsCollector()
        
        collector.increment("requests_total")
        collector.increment("requests_total")
        
        assert collector.get_counter("requests_total") == 2
    
    def test_increment_with_labels(self):
        """Test incrementing with labels."""
        collector = MetricsCollector()
        
        collector.increment("requests", labels={'method': 'GET'})
        collector.increment("requests", labels={'method': 'POST'})
        
        assert collector.get_counter("requests", {'method': 'GET'}) == 1
        assert collector.get_counter("requests", {'method': 'POST'}) == 1
    
    def test_gauge(self):
        """Test setting gauge."""
        collector = MetricsCollector()
        
        collector.gauge("memory_mb", 256.0)
        
        assert collector.get_gauge("memory_mb") == 256.0
    
    def test_get_all_metrics(self):
        """Test getting all metrics."""
        collector = MetricsCollector()
        collector.increment("counter1")
        collector.gauge("gauge1", 10.0)
        
        metrics = collector.get_all_metrics()
        
        assert 'counters' in metrics
        assert 'gauges' in metrics


class TestLogEntry:
    """Tests for LogEntry."""
    
    def test_create_entry(self):
        """Test creating log entry."""
        entry = LogEntry(
            level=LogLevel.INFO,
            message="Test message",
        )
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        entry = LogEntry(
            level=LogLevel.ERROR,
            message="Error occurred",
            extra={'code': 500},
        )
        
        d = entry.to_dict()
        
        assert d['level'] == 'error'
        assert d['code'] == 500


class TestLogAggregator:
    """Tests for LogAggregator."""
    
    def test_create_aggregator(self):
        """Test creating aggregator."""
        aggregator = LogAggregator()
        assert aggregator.max_entries == 1000
    
    def test_log_levels(self):
        """Test logging at different levels."""
        aggregator = LogAggregator()
        
        aggregator.debug("Debug")
        aggregator.info("Info")
        aggregator.warning("Warning")
        aggregator.error("Error")
        aggregator.critical("Critical")
        
        assert len(aggregator.entries) == 5
    
    def test_get_entries_by_level(self):
        """Test getting entries by level."""
        aggregator = LogAggregator()
        aggregator.info("Info 1")
        aggregator.info("Info 2")
        aggregator.error("Error 1")
        
        info_entries = aggregator.get_entries(LogLevel.INFO)
        
        assert len(info_entries) == 2
    
    def test_max_entries(self):
        """Test max entries limit."""
        aggregator = LogAggregator(max_entries=5)
        
        for i in range(10):
            aggregator.info(f"Message {i}")
        
        assert len(aggregator.entries) == 5


class TestMonitoringIntegration:
    """Tests for MonitoringIntegration."""
    
    def test_create_integration(self):
        """Test creating monitoring integration."""
        monitoring = MonitoringIntegration()
        
        assert monitoring.health is not None
        assert monitoring.metrics is not None
        assert monitoring.logs is not None
    
    def test_record_action(self):
        """Test recording action."""
        monitoring = MonitoringIntegration()
        
        monitoring.record_action("test_action", success=True, latency_ms=50.0)
        
        # Should have metrics and logs
        assert len(monitoring.logs.entries) > 0
    
    def test_record_learning_update(self):
        """Test recording learning update."""
        monitoring = MonitoringIntegration()
        
        monitoring.record_learning_update("test_domain", q_value_delta=0.5)
        
        assert monitoring.metrics.get_counter(
            "cognitive_brain_learning_updates_total",
            {'domain': 'test_domain'},
        ) == 1
    
    def test_get_status(self):
        """Test getting full status."""
        monitoring = MonitoringIntegration()
        
        status = monitoring.get_status()
        
        assert 'health' in status
        assert 'metrics' in status
        assert 'logs' in status


# =============================================================================
# DEPLOYMENT CONFIGURATION TESTS
# =============================================================================


class TestContainerConfig:
    """Tests for ContainerConfig."""
    
    def test_default_config(self):
        """Test default container config."""
        config = ContainerConfig()
        
        assert config.image == "cognitive-brain"
        assert config.tag == "latest"
        assert 8080 in config.ports
    
    def test_custom_config(self):
        """Test custom container config."""
        config = ContainerConfig(
            image="my-image",
            tag="v1.0.0",
            ports={9090: 9090},
        )
        
        assert config.image == "my-image"
        assert config.tag == "v1.0.0"


class TestKubernetesConfig:
    """Tests for KubernetesConfig."""
    
    def test_default_config(self):
        """Test default Kubernetes config."""
        config = KubernetesConfig()
        
        assert config.name == "cognitive-brain"
        assert config.namespace == "default"
        assert config.replicas == 1
    
    def test_custom_config(self):
        """Test custom Kubernetes config."""
        config = KubernetesConfig(
            name="my-deployment",
            replicas=3,
        )
        
        assert config.name == "my-deployment"
        assert config.replicas == 3


class TestDeploymentConfiguration:
    """Tests for DeploymentConfiguration."""
    
    def test_create_configuration(self):
        """Test creating deployment configuration."""
        config = DeploymentConfiguration()
        
        assert config.container is not None
        assert config.k8s is not None
    
    def test_generate_dockerfile(self):
        """Test generating Dockerfile."""
        config = DeploymentConfiguration()
        
        dockerfile = config.generate_dockerfile()
        
        assert "FROM python:3.11-slim" in dockerfile
        assert "HEALTHCHECK" in dockerfile
    
    def test_generate_k8s_deployment(self):
        """Test generating Kubernetes deployment."""
        config = DeploymentConfiguration()
        
        deployment = config.generate_k8s_deployment()
        
        assert deployment['kind'] == 'Deployment'
        assert 'spec' in deployment
        assert deployment['spec']['replicas'] == 1
    
    def test_generate_k8s_service(self):
        """Test generating Kubernetes service."""
        config = DeploymentConfiguration()
        
        service = config.generate_k8s_service()
        
        assert service['kind'] == 'Service'
        assert 'spec' in service


# =============================================================================
# PRODUCTION TEST SUITE TESTS
# =============================================================================


class TestHealthEndpointTest:
    """Tests for HealthEndpointTest."""
    
    def test_run_healthy(self):
        """Test running with healthy endpoint."""
        endpoint = HealthCheckEndpoint()
        endpoint.register(DatabaseHealthCheck(":memory:"))
        
        test = HealthEndpointTest(endpoint)
        passed, message = test.run()
        
        assert passed is True
        assert "operational" in message


class TestLearningEngineTest:
    """Tests for LearningEngineTest."""
    
    def test_no_engine(self):
        """Test with no engine configured."""
        test = LearningEngineTest()
        passed, message = test.run()
        
        assert passed is False
    
    def test_valid_engine(self):
        """Test with valid engine."""
        class MockEngine:
            def select_action(self): pass
            def update(self): pass
        
        test = LearningEngineTest(MockEngine())
        passed, message = test.run()
        
        assert passed is True


class TestProductionTestSuite:
    """Tests for ProductionTestSuite."""
    
    def test_create_suite(self):
        """Test creating test suite."""
        suite = ProductionTestSuite()
        assert suite is not None
    
    def test_register_and_run(self):
        """Test registering and running tests."""
        suite = ProductionTestSuite()
        
        endpoint = HealthCheckEndpoint()
        endpoint.register(DatabaseHealthCheck(":memory:"))
        
        suite.register(HealthEndpointTest(endpoint))
        
        all_passed = suite.run_all()
        
        assert all_passed is True
    
    def test_get_summary(self):
        """Test getting test summary."""
        suite = ProductionTestSuite()
        
        endpoint = HealthCheckEndpoint()
        suite.register(HealthEndpointTest(endpoint))
        
        suite.run_all()
        summary = suite.get_summary()
        
        assert 'total' in summary
        assert 'passed' in summary
        assert 'failed' in summary
