"""
Tests for Phase 8.10 Production Deployment & Integration.

This test suite validates all 7 PRE-COMMITs:
1. Agent Marketplace Integration
2. Real-World Testing Infrastructure
3. Performance Benchmarking Suite
4. Monitoring & Observability
5. Documentation Portal
6. Security Hardening
7. Continuous Deployment Pipeline

Target: 105+ tests for Phase 8.10
Total accumulated target: 217+ tests (112 from 8.9 + 105 from 8.10)
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Any

import pytest

# Import Phase 8.10 components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase8_10_production_deployment import (
    AgentMarketplace,
    RealWorldTestingInfrastructure,
    PerformanceBenchmarkSuite,
    MonitoringObservability,
    DocumentationPortal,
    SecurityHardening,
    ContinuousDeploymentPipeline,
)

# Deterministic seed for Phase 8.10 tests
RANDOM_SEED_TEST_8_10 = 43


@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed before each test for determinism."""
    random.seed(RANDOM_SEED_TEST_8_10)


# ============================================================================
# PRE-COMMIT 1: Agent Marketplace Integration Tests (15 tests)
# ============================================================================

class TestAgentMarketplace:
    """Tests for Agent Marketplace Integration."""

    def test_marketplace_initialization(self):
        """Test marketplace initialization."""
        marketplace = AgentMarketplace()
        assert marketplace is not None
        metrics = marketplace.get_metrics()
        assert "total_agents" in metrics
        assert metrics["total_agents"] == 0

    def test_agent_registration(self):
        """Test agent registration."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent(
            name="test-agent",
            version="1.0.0",
            capabilities=["testing", "analysis"]
        )
        assert agent_id is not None
        metrics = marketplace.get_metrics()
        assert metrics["total_agents"] == 1

    def test_agent_discovery(self):
        """Test agent discovery by capabilities."""
        marketplace = AgentMarketplace()
        marketplace.register_agent("agent1", "1.0.0", ["testing"])
        marketplace.register_agent("agent2", "1.0.0", ["analysis"])
        
        agents = marketplace.discover_agents(capability="testing")
        assert len(agents) == 1
        assert agents[0]["name"] == "agent1"

    def test_version_compatibility_check(self):
        """Test version compatibility checking."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent("agent1", "1.2.3", [])
        
        is_compatible = marketplace.check_compatibility(agent_id, "1.2.0")
        assert is_compatible is True
        
        is_compatible = marketplace.check_compatibility(agent_id, "2.0.0")
        assert is_compatible is False

    def test_marketplace_metadata(self):
        """Test marketplace metadata creation."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent(
            "agent1", "1.0.0", ["testing"],
            description="Test agent",
            tags=["ci", "automation"]
        )
        
        metadata = marketplace.get_agent_metadata(agent_id)
        assert metadata["description"] == "Test agent"
        assert "ci" in metadata["tags"]

    def test_agent_deregistration(self):
        """Test agent deregistration."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent("agent1", "1.0.0", [])
        
        success = marketplace.deregister_agent(agent_id)
        assert success is True
        
        metrics = marketplace.get_metrics()
        assert metrics["total_agents"] == 0

    def test_multiple_versions(self):
        """Test multiple versions of same agent."""
        marketplace = AgentMarketplace()
        id1 = marketplace.register_agent("agent1", "1.0.0", [])
        id2 = marketplace.register_agent("agent1", "2.0.0", [])
        
        assert id1 != id2
        metrics = marketplace.get_metrics()
        assert metrics["total_agents"] == 2

    def test_capability_filtering(self):
        """Test filtering by multiple capabilities."""
        marketplace = AgentMarketplace()
        marketplace.register_agent("agent1", "1.0.0", ["testing", "analysis"])
        marketplace.register_agent("agent2", "1.0.0", ["testing"])
        
        agents = marketplace.discover_agents(capability="analysis")
        assert len(agents) == 1

    def test_empty_marketplace(self):
        """Test operations on empty marketplace."""
        marketplace = AgentMarketplace()
        agents = marketplace.discover_agents(capability="nonexistent")
        assert len(agents) == 0

    def test_agent_update(self):
        """Test updating agent metadata."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent("agent1", "1.0.0", ["testing"])
        
        success = marketplace.update_agent(agent_id, capabilities=["testing", "analysis"])
        assert success is True
        
        metadata = marketplace.get_agent_metadata(agent_id)
        assert "analysis" in metadata["capabilities"]

    def test_marketplace_search(self):
        """Test marketplace search functionality."""
        marketplace = AgentMarketplace()
        marketplace.register_agent("test-agent", "1.0.0", ["testing"])
        marketplace.register_agent("analysis-agent", "1.0.0", ["analysis"])
        
        results = marketplace.search("test")
        assert len(results) >= 1

    def test_agent_rating_system(self):
        """Test agent rating and reviews."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent("agent1", "1.0.0", [])
        
        marketplace.rate_agent(agent_id, rating=4.5)
        metadata = marketplace.get_agent_metadata(agent_id)
        assert "rating" in metadata

    def test_marketplace_pagination(self):
        """Test pagination of agent listings."""
        marketplace = AgentMarketplace()
        for i in range(25):
            marketplace.register_agent(f"agent{i}", "1.0.0", [])
        
        page1 = marketplace.list_agents(page=1, per_page=10)
        assert len(page1) == 10

    def test_agent_dependencies(self):
        """Test agent dependency tracking."""
        marketplace = AgentMarketplace()
        agent_id = marketplace.register_agent(
            "agent1", "1.0.0", [],
            dependencies=["dep1:1.0.0", "dep2:2.0.0"]
        )
        
        metadata = marketplace.get_agent_metadata(agent_id)
        assert len(metadata.get("dependencies", [])) == 2

    def test_marketplace_statistics(self):
        """Test marketplace statistics generation."""
        marketplace = AgentMarketplace()
        marketplace.register_agent("agent1", "1.0.0", ["testing"])
        marketplace.register_agent("agent2", "1.0.0", ["analysis"])
        
        stats = marketplace.get_statistics()
        assert "total_agents" in stats
        assert "capabilities_count" in stats


# ============================================================================
# PRE-COMMIT 2: Real-World Testing Infrastructure Tests (15 tests)
# ============================================================================

class TestRealWorldTestingInfrastructure:
    """Tests for Real-World Testing Infrastructure."""

    def test_infrastructure_initialization(self):
        """Test testing infrastructure initialization."""
        infra = RealWorldTestingInfrastructure()
        assert infra is not None

    def test_workload_generator(self):
        """Test synthetic workload generation."""
        infra = RealWorldTestingInfrastructure()
        workload = infra.generate_workload(size=100)
        assert len(workload) == 100

    def test_multi_repo_harness(self):
        """Test multi-repository test harness."""
        infra = RealWorldTestingInfrastructure()
        repos = ["repo1", "repo2", "repo3"]
        results = infra.run_multi_repo_tests(repos)
        assert len(results) == 3

    def test_ab_testing_setup(self):
        """Test A/B testing infrastructure."""
        infra = RealWorldTestingInfrastructure()
        experiment = infra.create_ab_test(
            name="test_experiment",
            variant_a="baseline",
            variant_b="new_feature"
        )
        assert experiment is not None

    def test_beta_testing_framework(self):
        """Test beta testing framework."""
        infra = RealWorldTestingInfrastructure()
        beta_id = infra.create_beta_test(
            name="beta_test_1",
            participants=10
        )
        assert beta_id is not None

    def test_load_generation(self):
        """Test load generation capabilities."""
        infra = RealWorldTestingInfrastructure()
        load = infra.generate_load(requests_per_second=100, duration=10)
        assert load["total_requests"] == 1000

    def test_chaos_engineering(self):
        """Test chaos engineering scenarios."""
        infra = RealWorldTestingInfrastructure()
        chaos = infra.inject_failure(failure_type="network_delay", intensity=0.5)
        assert chaos["injected"] is True

    def test_synthetic_data_generation(self):
        """Test synthetic data generation."""
        infra = RealWorldTestingInfrastructure()
        data = infra.generate_synthetic_data(schema={"field1": "string", "field2": "int"}, count=50)
        assert len(data) == 50

    def test_test_environment_provisioning(self):
        """Test test environment provisioning."""
        infra = RealWorldTestingInfrastructure()
        env_id = infra.provision_environment(config={"type": "staging"})
        assert env_id is not None

    def test_test_data_cleanup(self):
        """Test test data cleanup."""
        infra = RealWorldTestingInfrastructure()
        infra.generate_workload(size=100)
        cleanup_result = infra.cleanup_test_data()
        assert cleanup_result["cleaned"] is True

    def test_parallel_test_execution(self):
        """Test parallel test execution."""
        infra = RealWorldTestingInfrastructure()
        tests = [f"test_{i}" for i in range(20)]
        results = infra.run_parallel_tests(tests, workers=4)
        assert len(results) == 20

    def test_test_result_aggregation(self):
        """Test result aggregation."""
        infra = RealWorldTestingInfrastructure()
        results = [{"passed": True}, {"passed": False}, {"passed": True}]
        summary = infra.aggregate_results(results)
        assert summary["pass_rate"] == pytest.approx(0.666, 0.01)

    def test_flaky_test_detection(self):
        """Test flaky test detection."""
        infra = RealWorldTestingInfrastructure()
        test_runs = [True, False, True, False, True]
        is_flaky = infra.detect_flaky_test(test_runs)
        assert is_flaky is True

    def test_test_isolation(self):
        """Test test isolation mechanisms."""
        infra = RealWorldTestingInfrastructure()
        isolation = infra.create_isolated_environment()
        assert isolation["isolated"] is True

    def test_workload_replay(self):
        """Test workload replay functionality."""
        infra = RealWorldTestingInfrastructure()
        original = infra.generate_workload(size=50)
        replayed = infra.replay_workload(original)
        assert len(replayed) == len(original)


# ============================================================================
# PRE-COMMIT 3: Performance Benchmarking Suite Tests (15 tests)
# ============================================================================

class TestPerformanceBenchmarkSuite:
    """Tests for Performance Benchmarking Suite."""

    def test_benchmark_initialization(self):
        """Test benchmark suite initialization."""
        suite = PerformanceBenchmarkSuite()
        assert suite is not None

    def test_latency_measurement(self):
        """Test latency measurement."""
        suite = PerformanceBenchmarkSuite()
        latency = suite.measure_latency(lambda: time.sleep(0.01))
        assert latency > 0

    def test_throughput_measurement(self):
        """Test throughput measurement."""
        suite = PerformanceBenchmarkSuite()
        throughput = suite.measure_throughput(lambda: None, duration=1.0)
        assert throughput > 0

    def test_percentile_calculation(self):
        """Test latency percentile calculation."""
        suite = PerformanceBenchmarkSuite()
        latencies = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        p95 = suite.calculate_percentile(latencies, 95)
        assert p95 == 95.0

    def test_resource_monitoring(self):
        """Test resource usage monitoring."""
        suite = PerformanceBenchmarkSuite()
        resources = suite.monitor_resources(duration=0.1)
        assert "cpu_percent" in resources
        assert "memory_mb" in resources

    def test_regression_detection(self):
        """Test performance regression detection."""
        suite = PerformanceBenchmarkSuite()
        baseline = [100, 105, 98, 102]
        current = [150, 155, 148, 152]
        is_regression = suite.detect_regression(baseline, current, threshold=0.1)
        assert is_regression is True

    def test_benchmark_comparison(self):
        """Test benchmark comparison."""
        suite = PerformanceBenchmarkSuite()
        result1 = {"latency": 100, "throughput": 1000}
        result2 = {"latency": 110, "throughput": 900}
        comparison = suite.compare_benchmarks(result1, result2)
        assert "latency_change" in comparison

    def test_load_test(self):
        """Test load testing functionality."""
        suite = PerformanceBenchmarkSuite()
        results = suite.run_load_test(target_rps=100, duration=1.0)
        assert "average_latency" in results

    def test_stress_test(self):
        """Test stress testing."""
        suite = PerformanceBenchmarkSuite()
        breaking_point = suite.run_stress_test(increment=100, max_rps=1000)
        assert breaking_point > 0

    def test_benchmark_report_generation(self):
        """Test benchmark report generation."""
        suite = PerformanceBenchmarkSuite()
        suite.measure_latency(lambda: time.sleep(0.01))
        report = suite.generate_report()
        assert "summary" in report

    def test_concurrent_benchmark(self):
        """Test concurrent request benchmarking."""
        suite = PerformanceBenchmarkSuite()
        results = suite.benchmark_concurrent(lambda: None, concurrency=10, requests=100)
        assert results["total_requests"] == 100

    def test_memory_profiling(self):
        """Test memory profiling."""
        suite = PerformanceBenchmarkSuite()
        profile = suite.profile_memory(lambda: [i for i in range(1000)])
        assert "peak_memory" in profile

    def test_cache_performance(self):
        """Test cache performance measurement."""
        suite = PerformanceBenchmarkSuite()
        cache_stats = suite.measure_cache_performance(hit_rate=0.8, size=1000)
        assert cache_stats["hit_rate"] == 0.8

    def test_network_latency(self):
        """Test network latency measurement."""
        suite = PerformanceBenchmarkSuite()
        latency = suite.measure_network_latency(target="localhost")
        assert latency >= 0

    def test_benchmark_history(self):
        """Test benchmark history tracking."""
        suite = PerformanceBenchmarkSuite()
        suite.measure_latency(lambda: None)
        history = suite.get_history()
        assert len(history) > 0


# ============================================================================
# PRE-COMMIT 4: Monitoring & Observability Tests (15 tests)
# ============================================================================

class TestMonitoringObservability:
    """Tests for Monitoring & Observability."""

    def test_monitoring_initialization(self):
        """Test monitoring system initialization."""
        monitoring = MonitoringObservability()
        assert monitoring is not None

    def test_prometheus_metrics_export(self):
        """Test Prometheus metrics exporter."""
        monitoring = MonitoringObservability()
        metrics = monitoring.export_prometheus_metrics()
        assert metrics is not None

    def test_distributed_tracing(self):
        """Test distributed tracing."""
        monitoring = MonitoringObservability()
        trace_id = monitoring.start_trace(operation="test_operation")
        assert trace_id is not None
        monitoring.end_trace(trace_id)

    def test_span_creation(self):
        """Test span creation in tracing."""
        monitoring = MonitoringObservability()
        trace_id = monitoring.start_trace("parent")
        span_id = monitoring.create_span(trace_id, "child_operation")
        assert span_id is not None

    def test_log_aggregation(self):
        """Test log aggregation."""
        monitoring = MonitoringObservability()
        monitoring.log("INFO", "Test message")
        logs = monitoring.get_aggregated_logs()
        assert len(logs) > 0

    def test_alert_creation(self):
        """Test alert creation."""
        monitoring = MonitoringObservability()
        alert_id = monitoring.create_alert(
            name="high_latency",
            condition="latency > 100",
            severity="warning"
        )
        assert alert_id is not None

    def test_metric_collection(self):
        """Test metric collection."""
        monitoring = MonitoringObservability()
        monitoring.collect_metric("request_count", 100)
        metrics = monitoring.get_metrics()
        assert "request_count" in metrics

    def test_health_check(self):
        """Test health check endpoint."""
        monitoring = MonitoringObservability()
        health = monitoring.health_check()
        assert health["status"] in ["healthy", "degraded", "unhealthy"]

    def test_dashboard_data(self):
        """Test dashboard data generation."""
        monitoring = MonitoringObservability()
        dashboard_data = monitoring.get_dashboard_data()
        assert "metrics" in dashboard_data

    def test_error_tracking(self):
        """Test error tracking."""
        monitoring = MonitoringObservability()
        monitoring.track_error(error_type="ValueError", message="Test error")
        errors = monitoring.get_error_summary()
        assert len(errors) > 0

    def test_custom_metric_registration(self):
        """Test custom metric registration."""
        monitoring = MonitoringObservability()
        success = monitoring.register_custom_metric(
            name="custom_metric",
            metric_type="gauge"
        )
        assert success is True

    def test_trace_context_propagation(self):
        """Test trace context propagation."""
        monitoring = MonitoringObservability()
        trace_id = monitoring.start_trace("operation1")
        context = monitoring.get_trace_context(trace_id)
        assert "trace_id" in context

    def test_sampling_configuration(self):
        """Test sampling configuration."""
        monitoring = MonitoringObservability()
        monitoring.configure_sampling(rate=0.1)
        config = monitoring.get_sampling_config()
        assert config["rate"] == 0.1

    def test_metric_aggregation(self):
        """Test metric aggregation."""
        monitoring = MonitoringObservability()
        for i in range(10):
            monitoring.collect_metric("test_metric", i)
        aggregated = monitoring.aggregate_metric("test_metric", aggregation="avg")
        assert aggregated == 4.5

    def test_alerting_rules(self):
        """Test alerting rules engine."""
        monitoring = MonitoringObservability()
        monitoring.create_alert("test_alert", "metric > 100", "critical")
        monitoring.collect_metric("metric", 150)
        alerts = monitoring.check_alerts()
        assert len(alerts) > 0


# ============================================================================
# PRE-COMMIT 5: Documentation Portal Tests (15 tests)
# ============================================================================

class TestDocumentationPortal:
    """Tests for Documentation Portal."""

    def test_portal_initialization(self):
        """Test documentation portal initialization."""
        portal = DocumentationPortal()
        assert portal is not None

    def test_api_documentation_generation(self):
        """Test API documentation generation."""
        portal = DocumentationPortal()
        def sample_function(x: int) -> int:
            """Sample function."""
            return x * 2
        
        docs = portal.generate_api_docs(sample_function)
        assert "parameters" in docs

    def test_user_guide_creation(self):
        """Test user guide creation."""
        portal = DocumentationPortal()
        guide_id = portal.create_user_guide(
            title="Getting Started",
            content="# Getting Started\n\nWelcome!"
        )
        assert guide_id is not None

    def test_tutorial_management(self):
        """Test tutorial management."""
        portal = DocumentationPortal()
        tutorial_id = portal.add_tutorial(
            name="Basic Tutorial",
            steps=["Step 1", "Step 2", "Step 3"]
        )
        assert tutorial_id is not None

    def test_documentation_search(self):
        """Test documentation search."""
        portal = DocumentationPortal()
        portal.create_user_guide("Guide 1", "Content about testing")
        results = portal.search("testing")
        assert len(results) > 0

    def test_version_management(self):
        """Test documentation versioning."""
        portal = DocumentationPortal()
        guide_id = portal.create_user_guide("Guide", "Version 1")
        version = portal.create_version(guide_id, content="Version 2")
        assert version is not None

    def test_markdown_rendering(self):
        """Test markdown rendering."""
        portal = DocumentationPortal()
        markdown = "# Header\n\n**Bold text**"
        html = portal.render_markdown(markdown)
        assert "<h1>" in html

    def test_code_example_embedding(self):
        """Test code example embedding."""
        portal = DocumentationPortal()
        example = portal.create_code_example(
            language="python",
            code="print('Hello, World!')"
        )
        assert example["language"] == "python"

    def test_troubleshooting_guide(self):
        """Test troubleshooting guide creation."""
        portal = DocumentationPortal()
        guide_id = portal.add_troubleshooting_guide(
            issue="Error XYZ",
            solution="Solution steps..."
        )
        assert guide_id is not None

    def test_documentation_navigation(self):
        """Test documentation navigation structure."""
        portal = DocumentationPortal()
        portal.create_user_guide("Guide 1", "Content 1")
        portal.create_user_guide("Guide 2", "Content 2")
        nav = portal.get_navigation()
        assert len(nav) >= 2

    def test_doc_validation(self):
        """Test documentation validation."""
        portal = DocumentationPortal()
        guide_id = portal.create_user_guide("Test", "# Header\n\nContent")
        is_valid = portal.validate_documentation(guide_id)
        assert is_valid is True

    def test_api_reference_indexing(self):
        """Test API reference indexing."""
        portal = DocumentationPortal()
        portal.index_api_reference(module_name="test_module", functions=["func1", "func2"])
        index = portal.get_api_index()
        assert "test_module" in index

    def test_documentation_export(self):
        """Test documentation export."""
        portal = DocumentationPortal()
        portal.create_user_guide("Guide", "Content")
        export = portal.export_documentation(format="pdf")
        assert export is not None

    def test_interactive_examples(self):
        """Test interactive code examples."""
        portal = DocumentationPortal()
        example_id = portal.create_interactive_example(
            code="x = 5\nprint(x)",
            editable=True
        )
        assert example_id is not None

    def test_documentation_analytics(self):
        """Test documentation analytics."""
        portal = DocumentationPortal()
        guide_id = portal.create_user_guide("Guide", "Content")
        portal.track_view(guide_id)
        analytics = portal.get_analytics(guide_id)
        assert analytics["views"] > 0


# ============================================================================
# PRE-COMMIT 6: Security Hardening Tests (15 tests)
# ============================================================================

class TestSecurityHardening:
    """Tests for Security Hardening."""

    def test_security_initialization(self):
        """Test security system initialization."""
        security = SecurityHardening()
        assert security is not None

    def test_input_validation(self):
        """Test input validation."""
        security = SecurityHardening()
        is_valid = security.validate_input("test_input", pattern=r"^[a-z_]+$")
        assert is_valid is True

    def test_input_sanitization(self):
        """Test input sanitization."""
        security = SecurityHardening()
        sanitized = security.sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in sanitized

    def test_rate_limiting(self):
        """Test rate limiting."""
        security = SecurityHardening()
        client_id = "client123"
        
        # First request should succeed
        allowed = security.check_rate_limit(client_id, limit=5, window=60)
        assert allowed is True

    def test_throttling(self):
        """Test request throttling."""
        security = SecurityHardening()
        for i in range(10):
            security.record_request("client1")
        
        is_throttled = security.is_throttled("client1", threshold=5)
        assert is_throttled is True

    def test_audit_logging(self):
        """Test security audit logging."""
        security = SecurityHardening()
        security.log_security_event(
            event_type="authentication",
            user="test_user",
            action="login"
        )
        logs = security.get_audit_logs()
        assert len(logs) > 0

    def test_secrets_management(self):
        """Test secrets management integration."""
        security = SecurityHardening()
        secret_id = security.store_secret(key="api_key", value="secret_value")
        assert secret_id is not None

    def test_rbac_authorization(self):
        """Test RBAC authorization."""
        security = SecurityHardening()
        security.assign_role(user="user1", role="admin")
        
        has_permission = security.check_permission(user="user1", permission="write")
        assert has_permission is True

    def test_permission_management(self):
        """Test permission management."""
        security = SecurityHardening()
        security.create_permission(name="read_data", resource="database")
        permissions = security.list_permissions()
        assert "read_data" in [p["name"] for p in permissions]

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        security = SecurityHardening()
        query = "SELECT * FROM users WHERE id = '1' OR '1'='1'"
        is_safe = security.check_sql_safety(query)
        assert is_safe is False

    def test_xss_prevention(self):
        """Test XSS prevention."""
        security = SecurityHardening()
        user_input = "<img src=x onerror=alert('xss')>"
        sanitized = security.prevent_xss(user_input)
        assert "onerror" not in sanitized

    def test_csrf_token_generation(self):
        """Test CSRF token generation."""
        security = SecurityHardening()
        token = security.generate_csrf_token(session_id="session123")
        assert len(token) > 0

    def test_password_hashing(self):
        """Test password hashing."""
        security = SecurityHardening()
        hashed = security.hash_password("password123")
        assert hashed != "password123"
        
        is_valid = security.verify_password("password123", hashed)
        assert is_valid is True

    def test_encryption(self):
        """Test data encryption."""
        security = SecurityHardening()
        plaintext = "sensitive data"
        encrypted = security.encrypt(plaintext)
        assert encrypted != plaintext
        
        decrypted = security.decrypt(encrypted)
        assert decrypted == plaintext

    def test_security_headers(self):
        """Test security headers generation."""
        security = SecurityHardening()
        headers = security.generate_security_headers()
        assert "X-Content-Type-Options" in headers


# ============================================================================
# PRE-COMMIT 7: Continuous Deployment Pipeline Tests (15 tests)
# ============================================================================

class TestContinuousDeploymentPipeline:
    """Tests for Continuous Deployment Pipeline."""

    def test_pipeline_initialization(self):
        """Test CD pipeline initialization."""
        pipeline = ContinuousDeploymentPipeline()
        assert pipeline is not None

    def test_gitops_workflow(self):
        """Test GitOps workflow."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.deploy_via_gitops(
            repo="test-repo",
            branch="main",
            environment="staging"
        )
        assert deployment_id is not None

    def test_canary_deployment(self):
        """Test canary deployment strategy."""
        pipeline = ContinuousDeploymentPipeline()
        canary_id = pipeline.create_canary_deployment(
            version="v2.0.0",
            traffic_percentage=10
        )
        assert canary_id is not None

    def test_rollback_automation(self):
        """Test rollback automation."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.deploy_via_gitops("repo", "main", "staging")
        
        rollback_success = pipeline.rollback(deployment_id)
        assert rollback_success is True

    def test_health_checks(self):
        """Test health checks."""
        pipeline = ContinuousDeploymentPipeline()
        health = pipeline.run_health_check(endpoint="/health")
        assert health["status"] in ["healthy", "unhealthy"]

    def test_readiness_probes(self):
        """Test readiness probes."""
        pipeline = ContinuousDeploymentPipeline()
        is_ready = pipeline.check_readiness(service="test-service")
        assert isinstance(is_ready, bool)

    def test_deployment_verification(self):
        """Test deployment verification."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.deploy_via_gitops("repo", "main", "staging")
        
        is_verified = pipeline.verify_deployment(deployment_id)
        assert isinstance(is_verified, bool)

    def test_blue_green_deployment(self):
        """Test blue-green deployment."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.create_blue_green_deployment(
            blue_version="v1.0.0",
            green_version="v2.0.0"
        )
        assert deployment_id is not None

    def test_traffic_shifting(self):
        """Test traffic shifting."""
        pipeline = ContinuousDeploymentPipeline()
        canary_id = pipeline.create_canary_deployment("v2.0.0", 10)
        
        success = pipeline.shift_traffic(canary_id, new_percentage=50)
        assert success is True

    def test_deployment_approval(self):
        """Test deployment approval workflow."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.deploy_via_gitops("repo", "main", "production")
        
        pipeline.request_approval(deployment_id)
        status = pipeline.get_approval_status(deployment_id)
        assert status in ["pending", "approved", "rejected"]

    def test_deployment_history(self):
        """Test deployment history tracking."""
        pipeline = ContinuousDeploymentPipeline()
        pipeline.deploy_via_gitops("repo", "main", "staging")
        
        history = pipeline.get_deployment_history()
        assert len(history) > 0

    def test_environment_promotion(self):
        """Test environment promotion."""
        pipeline = ContinuousDeploymentPipeline()
        deployment_id = pipeline.deploy_via_gitops("repo", "main", "staging")
        
        promoted = pipeline.promote_to_production(deployment_id)
        assert promoted is not None

    def test_deployment_notifications(self):
        """Test deployment notifications."""
        pipeline = ContinuousDeploymentPipeline()
        success = pipeline.send_notification(
            channel="slack",
            message="Deployment completed",
            deployment_id="deploy123"
        )
        assert success is True

    def test_deployment_metrics(self):
        """Test deployment metrics collection."""
        pipeline = ContinuousDeploymentPipeline()
        pipeline.deploy_via_gitops("repo", "main", "staging")
        
        metrics = pipeline.get_deployment_metrics()
        assert "total_deployments" in metrics

    def test_progressive_rollout(self):
        """Test progressive rollout strategy."""
        pipeline = ContinuousDeploymentPipeline()
        rollout_id = pipeline.create_progressive_rollout(
            version="v2.0.0",
            stages=[10, 25, 50, 100]
        )
        assert rollout_id is not None


# ============================================================================
# Integration Tests (10 tests)
# ============================================================================

class TestPhase810Integration:
    """Integration tests across Phase 8.10 components."""

    def test_marketplace_with_monitoring(self):
        """Test marketplace integration with monitoring."""
        marketplace = AgentMarketplace()
        monitoring = MonitoringObservability()
        
        agent_id = marketplace.register_agent("test-agent", "1.0.0", [])
        monitoring.collect_metric("agent_registrations", 1)
        
        metrics = monitoring.get_metrics()
        assert "agent_registrations" in metrics

    def test_benchmarking_with_monitoring(self):
        """Test benchmarking with monitoring integration."""
        suite = PerformanceBenchmarkSuite()
        monitoring = MonitoringObservability()
        
        trace_id = monitoring.start_trace("benchmark")
        latency = suite.measure_latency(lambda: None)
        monitoring.end_trace(trace_id)
        
        assert latency >= 0

    def test_security_with_deployment(self):
        """Test security integration with deployment."""
        security = SecurityHardening()
        pipeline = ContinuousDeploymentPipeline()
        
        # Validate deployment configuration
        is_valid = security.validate_input("staging", pattern=r"^[a-z]+$")
        assert is_valid is True
        
        if is_valid:
            deployment_id = pipeline.deploy_via_gitops("repo", "main", "staging")
            assert deployment_id is not None

    def test_documentation_with_marketplace(self):
        """Test documentation portal integration with marketplace."""
        portal = DocumentationPortal()
        marketplace = AgentMarketplace()
        
        agent_id = marketplace.register_agent("test-agent", "1.0.0", [])
        guide_id = portal.create_user_guide(
            f"Agent {agent_id} Documentation",
            "# Getting Started\n\nAgent documentation..."
        )
        assert guide_id is not None

    def test_testing_infrastructure_with_security(self):
        """Test testing infrastructure with security."""
        infra = RealWorldTestingInfrastructure()
        security = SecurityHardening()
        
        # Generate secure test data
        workload = infra.generate_workload(size=10)
        for item in workload:
            sanitized = security.sanitize_input(str(item))
            assert sanitized is not None

    def test_full_deployment_workflow(self):
        """Test full deployment workflow with all components."""
        marketplace = AgentMarketplace()
        security = SecurityHardening()
        monitoring = MonitoringObservability()
        pipeline = ContinuousDeploymentPipeline()
        
        # Register agent
        agent_id = marketplace.register_agent("prod-agent", "1.0.0", [])
        
        # Security check
        security.log_security_event("deployment", "system", "starting")
        
        # Monitor deployment
        trace_id = monitoring.start_trace("deployment")
        
        # Deploy
        deployment_id = pipeline.deploy_via_gitops("repo", "main", "production")
        
        monitoring.end_trace(trace_id)
        
        assert deployment_id is not None

    def test_performance_monitoring_integration(self):
        """Test performance benchmarking with monitoring."""
        suite = PerformanceBenchmarkSuite()
        monitoring = MonitoringObservability()
        
        # Run benchmark and collect metrics
        latency = suite.measure_latency(lambda: time.sleep(0.01))
        monitoring.collect_metric("benchmark_latency", latency)
        
        metrics = monitoring.get_metrics()
        assert "benchmark_latency" in metrics

    def test_security_audit_with_documentation(self):
        """Test security audit logging with documentation."""
        security = SecurityHardening()
        portal = DocumentationPortal()
        
        # Log security event
        security.log_security_event("audit", "admin", "view_docs")
        
        # Document security policies
        guide_id = portal.create_user_guide(
            "Security Policies",
            "# Security Policies\n\nAudit logging enabled."
        )
        assert guide_id is not None

    def test_canary_deployment_with_monitoring(self):
        """Test canary deployment with health monitoring."""
        pipeline = ContinuousDeploymentPipeline()
        monitoring = MonitoringObservability()
        
        # Create canary deployment
        canary_id = pipeline.create_canary_deployment("v2.0.0", 10)
        
        # Monitor health
        health = pipeline.run_health_check("/health")
        monitoring.collect_metric("canary_health", 1 if health["status"] == "healthy" else 0)
        
        assert canary_id is not None

    def test_end_to_end_production_flow(self):
        """Test end-to-end production deployment flow."""
        marketplace = AgentMarketplace()
        infra = RealWorldTestingInfrastructure()
        suite = PerformanceBenchmarkSuite()
        monitoring = MonitoringObservability()
        portal = DocumentationPortal()
        security = SecurityHardening()
        pipeline = ContinuousDeploymentPipeline()
        
        # 1. Register agent
        agent_id = marketplace.register_agent("production-agent", "1.0.0", ["production"])
        
        # 2. Run tests
        workload = infra.generate_workload(size=50)
        
        # 3. Benchmark performance
        latency = suite.measure_latency(lambda: None)
        
        # 4. Security validation
        security.log_security_event("validation", "system", "passed")
        
        # 5. Create documentation
        portal.create_user_guide("Production Guide", "# Production\n\nReady to deploy.")
        
        # 6. Start monitoring
        trace_id = monitoring.start_trace("production_deployment")
        
        # 7. Deploy with canary
        canary_id = pipeline.create_canary_deployment("v1.0.0", 10)
        
        # 8. Verify and promote
        is_verified = pipeline.verify_deployment(canary_id)
        
        monitoring.end_trace(trace_id)
        
        assert is_verified is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
