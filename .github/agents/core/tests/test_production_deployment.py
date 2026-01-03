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
    # Phase 8.5 Full Implementation
    ProcessHealthCheck,
    NetworkHealthCheck,
    NodeInfo,
    DistributedDeployment,
    StructuredLog,
    LoggingAggregator,
    PrometheusExporter,
    HardeningItem,
    ProductionHardeningChecklist,
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


# =============================================================================
# PHASE 8.5 FULL IMPLEMENTATION TESTS
# =============================================================================


class TestProcessHealthCheck:
    """Tests for ProcessHealthCheck."""
    
    def test_name(self):
        """Test check name."""
        check = ProcessHealthCheck()
        assert check.name == "process"
    
    def test_run_check(self):
        """Test running process check."""
        check = ProcessHealthCheck()
        result = check.check()
        
        assert result.component == "process"
        assert result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNKNOWN]
        assert 'pid' in result.details
    
    def test_custom_thresholds(self):
        """Test custom thresholds."""
        check = ProcessHealthCheck(cpu_threshold=50.0, memory_threshold_mb=512.0)
        result = check.check()
        
        assert result is not None


class TestNetworkHealthCheck:
    """Tests for NetworkHealthCheck."""
    
    def test_name(self):
        """Test check name."""
        check = NetworkHealthCheck()
        assert check.name == "network"
    
    def test_run_check(self):
        """Test running network check."""
        check = NetworkHealthCheck()
        result = check.check()
        
        assert result.component == "network"
        assert 'network_available' in result.details


class TestNodeInfo:
    """Tests for NodeInfo."""
    
    def test_create_node(self):
        """Test creating node info."""
        node = NodeInfo(node_id="node-1", host="192.168.1.1", port=8080)
        
        assert node.node_id == "node-1"
        assert node.host == "192.168.1.1"
        assert node.last_heartbeat != ""
    
    def test_default_values(self):
        """Test default values."""
        node = NodeInfo(node_id="node-2")
        
        assert node.host == "localhost"
        assert node.port == 8080
        assert node.role == "worker"


class TestDistributedDeployment:
    """Tests for DistributedDeployment."""
    
    def test_create_deployment(self):
        """Test creating deployment."""
        deployment = DistributedDeployment()
        
        assert deployment.replication_factor == 3
        assert deployment.leader_id is None
    
    def test_register_node(self):
        """Test registering nodes."""
        deployment = DistributedDeployment()
        node = NodeInfo(node_id="node-1")
        
        deployment.register_node(node)
        
        assert "node-1" in deployment.nodes
        assert deployment.leader_id == "node-1"  # First node becomes leader
    
    def test_leader_election(self):
        """Test simple leader election."""
        deployment = DistributedDeployment()
        
        deployment.register_node(NodeInfo(node_id="node-1"))
        deployment.register_node(NodeInfo(node_id="node-2"))
        
        # First node should be leader
        assert deployment.leader_id == "node-1"
        assert deployment.nodes["node-1"].role == "primary"
    
    def test_unregister_leader(self):
        """Test unregistering leader promotes new leader."""
        deployment = DistributedDeployment()
        
        deployment.register_node(NodeInfo(node_id="node-1"))
        deployment.register_node(NodeInfo(node_id="node-2"))
        
        deployment.unregister_node("node-1")
        
        assert deployment.leader_id == "node-2"
    
    def test_heartbeat(self):
        """Test heartbeat update."""
        deployment = DistributedDeployment()
        node = NodeInfo(node_id="node-1")
        
        deployment.register_node(node)
        deployment.update_heartbeat("node-1")
        
        assert deployment.nodes["node-1"].status == "healthy"
    
    def test_get_healthy_nodes(self):
        """Test getting healthy nodes."""
        deployment = DistributedDeployment()
        
        deployment.register_node(NodeInfo(node_id="node-1"))
        deployment.update_heartbeat("node-1")
        
        healthy = deployment.get_healthy_nodes()
        
        assert len(healthy) == 1
    
    def test_cluster_status(self):
        """Test getting cluster status."""
        deployment = DistributedDeployment(replication_factor=2)
        
        deployment.register_node(NodeInfo(node_id="node-1"))
        deployment.register_node(NodeInfo(node_id="node-2"))
        deployment.update_heartbeat("node-1")
        deployment.update_heartbeat("node-2")
        
        status = deployment.get_cluster_status()
        
        assert status['total_nodes'] == 2
        assert status['healthy_nodes'] == 2
        assert status['status'] == 'healthy'
    
    def test_generate_statefulset(self):
        """Test generating StatefulSet manifest."""
        deployment = DistributedDeployment(replication_factor=3)
        k8s_config = KubernetesConfig(name="test-app")
        
        manifest = deployment.generate_k8s_statefulset(k8s_config)
        
        assert manifest['kind'] == 'StatefulSet'
        assert manifest['spec']['replicas'] == 3


class TestStructuredLog:
    """Tests for StructuredLog."""
    
    def test_create_log(self):
        """Test creating structured log."""
        log = StructuredLog(
            timestamp="2026-01-03T00:00:00Z",
            level="info",
            message="Test message",
        )
        
        assert log.level == "info"
        assert log.message == "Test message"
    
    def test_to_json(self):
        """Test JSON serialization."""
        log = StructuredLog(
            timestamp="2026-01-03T00:00:00Z",
            level="error",
            message="Error occurred",
        )
        
        json_str = log.to_json()
        
        assert "error" in json_str
        assert "Error occurred" in json_str
    
    def test_to_logfmt(self):
        """Test logfmt serialization."""
        log = StructuredLog(
            timestamp="2026-01-03T00:00:00Z",
            level="info",
            message="Test",
        )
        
        logfmt = log.to_logfmt()
        
        assert "level=info" in logfmt
        assert 'msg="Test"' in logfmt


class TestLoggingAggregator:
    """Tests for LoggingAggregator."""
    
    def test_create_aggregator(self):
        """Test creating aggregator."""
        aggregator = LoggingAggregator()
        
        assert aggregator.service_name == "cognitive-brain"
    
    def test_log_levels(self):
        """Test logging at different levels."""
        aggregator = LoggingAggregator()
        
        aggregator.debug("Debug message")
        aggregator.info("Info message")
        aggregator.warning("Warning message")
        aggregator.error("Error message")
        aggregator.critical("Critical message")
        
        assert len(aggregator.logs) == 5
    
    def test_trace_context(self):
        """Test trace context."""
        aggregator = LoggingAggregator()
        
        aggregator.set_trace_context("trace-123", "span-456")
        entry = aggregator.info("Traced log")
        
        assert entry.trace_id == "trace-123"
        assert entry.span_id == "span-456"
        
        aggregator.clear_trace_context()
        entry2 = aggregator.info("Untraced log")
        assert entry2.trace_id == ""
    
    def test_export_json(self):
        """Test JSON export."""
        aggregator = LoggingAggregator()
        aggregator.info("Test log", labels={'env': 'test'})
        
        json_output = aggregator.export_json()
        
        assert "Test log" in json_output
    
    def test_export_json_with_filter(self):
        """Test JSON export with label filter."""
        aggregator = LoggingAggregator()
        aggregator.info("Log 1", labels={'env': 'prod'})
        aggregator.info("Log 2", labels={'env': 'test'})
        
        filtered = aggregator.export_json({'env': 'prod'})
        
        assert "Log 1" in filtered
        assert "Log 2" not in filtered
    
    def test_statistics(self):
        """Test log statistics."""
        aggregator = LoggingAggregator()
        aggregator.info("Info 1")
        aggregator.error("Error 1")
        
        stats = aggregator.get_statistics()
        
        assert stats['total_logs'] == 2
        assert 'info' in stats['levels']
        assert 'error' in stats['levels']


class TestPrometheusExporter:
    """Tests for PrometheusExporter."""
    
    def test_create_exporter(self):
        """Test creating exporter."""
        exporter = PrometheusExporter()
        
        assert exporter.prefix == "cognitive_brain"
    
    def test_register_counter(self):
        """Test registering counter."""
        exporter = PrometheusExporter()
        exporter.register_counter("requests", "Total requests")
        
        assert "cognitive_brain_requests" in exporter.counters
    
    def test_increment_counter(self):
        """Test incrementing counter."""
        exporter = PrometheusExporter()
        
        exporter.inc_counter("requests")
        exporter.inc_counter("requests", 2)
        
        assert exporter.counters["cognitive_brain_requests"][""] == 3
    
    def test_counter_with_labels(self):
        """Test counter with labels."""
        exporter = PrometheusExporter()
        
        exporter.inc_counter("requests", labels={'method': 'GET'})
        exporter.inc_counter("requests", labels={'method': 'POST'})
        
        assert exporter.counters["cognitive_brain_requests"]['{method="GET"}'] == 1
        assert exporter.counters["cognitive_brain_requests"]['{method="POST"}'] == 1
    
    def test_gauge(self):
        """Test gauge metric."""
        exporter = PrometheusExporter()
        
        exporter.set_gauge("temperature", 42.5)
        exporter.set_gauge("temperature", 43.0)  # Should overwrite
        
        assert exporter.gauges["cognitive_brain_temperature"][""] == 43.0
    
    def test_histogram(self):
        """Test histogram metric."""
        exporter = PrometheusExporter()
        
        exporter.observe_histogram("latency", 0.05)
        exporter.observe_histogram("latency", 0.1)
        exporter.observe_histogram("latency", 0.2)
        
        assert len(exporter.histograms["cognitive_brain_latency"]) == 3
    
    def test_export(self):
        """Test Prometheus format export."""
        exporter = PrometheusExporter()
        
        exporter.inc_counter("requests")
        exporter.set_gauge("temperature", 42)
        
        output = exporter.export()
        
        assert "cognitive_brain_requests" in output
        assert "cognitive_brain_temperature" in output
        assert "# HELP" in output
        assert "# TYPE" in output


class TestHardeningChecklist:
    """Tests for ProductionHardeningChecklist."""
    
    def test_create_checklist(self):
        """Test creating checklist."""
        checklist = ProductionHardeningChecklist()
        
        assert len(checklist.items) > 0
    
    def test_default_items(self):
        """Test default items exist."""
        checklist = ProductionHardeningChecklist()
        
        item_names = [item.name for item in checklist.items]
        
        assert "no_debug_mode" in item_names
        assert "health_checks" in item_names
        assert "metrics_endpoint" in item_names
    
    def test_add_item(self):
        """Test adding custom item."""
        checklist = ProductionHardeningChecklist()
        initial_count = len(checklist.items)
        
        checklist.add_item(HardeningItem(
            category="custom",
            name="custom_check",
            description="Custom check",
        ))
        
        assert len(checklist.items) == initial_count + 1
    
    def test_check_item(self):
        """Test marking item as checked."""
        checklist = ProductionHardeningChecklist()
        
        checklist.check_item("no_debug_mode", True, "Debug is off")
        
        item = next(i for i in checklist.items if i.name == "no_debug_mode")
        assert item.passed is True
        assert item.message == "Debug is off"
    
    def test_get_summary(self):
        """Test getting summary."""
        checklist = ProductionHardeningChecklist()
        
        # Mark some items as passed
        checklist.check_item("no_debug_mode", True)
        checklist.check_item("health_checks", True)
        
        summary = checklist.get_summary()
        
        assert 'total_items' in summary
        assert 'passed' in summary
        assert 'failed_critical' in summary
        assert 'by_category' in summary
    
    def test_production_ready(self):
        """Test production ready check."""
        checklist = ProductionHardeningChecklist()
        
        # Mark all critical items
        for item in checklist.items:
            if item.severity == 'critical':
                checklist.check_item(item.name, True)
        
        summary = checklist.get_summary()
        
        assert summary['production_ready'] is True
    
    def test_to_markdown(self):
        """Test Markdown export."""
        checklist = ProductionHardeningChecklist()
        checklist.check_item("no_debug_mode", True)
        
        markdown = checklist.to_markdown()
        
        assert "# Production Hardening Checklist" in markdown
        assert "✅" in markdown
