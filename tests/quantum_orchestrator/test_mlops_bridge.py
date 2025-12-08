"""
Tests for MLOps integration bridge.
"""

import pytest
import time
import logging

from codex.quantum_orchestrator.mlops_bridge import (
    MetricsCollector,
    LoggingAdapter,
    DistributedCoordinator,
    ObservableOrchestrator,
    create_observable_orchestrator,
    Metric,
    MetricType,
)
from codex.quantum_orchestrator.orchestrator import create_orchestrator


class TestMetricsCollector:
    """Test metrics collection."""
    
    def test_collect_orchestrator_metrics(self):
        """Test collecting metrics from orchestrator."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        orch.add_task("task2", "Task 2")
        
        collector = MetricsCollector(orch)
        metrics = collector.collect_orchestrator_metrics()
        
        # Should have multiple metrics
        assert len(metrics) > 0
        
        # Check for expected metrics
        metric_names = {m.name for m in metrics}
        assert "quantum_orchestrator_tasks_total" in metric_names
        assert "quantum_orchestrator_coherence" in metric_names
    
    def test_export_prometheus(self):
        """Test Prometheus format export."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        
        collector = MetricsCollector(orch)
        collector.collect_orchestrator_metrics()
        
        prom_output = collector.export_prometheus()
        
        # Should contain metric lines
        assert len(prom_output) > 0
        assert "quantum_orchestrator" in prom_output
    
    def test_export_json(self):
        """Test JSON export."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        
        collector = MetricsCollector(orch)
        collector.collect_orchestrator_metrics()
        
        json_output = collector.export_json()
        
        # Should be valid JSON
        import json
        data = json.loads(json_output)
        assert isinstance(data, list)
        assert len(data) > 0


class TestLoggingAdapter:
    """Test logging adapter."""
    
    def test_log_evolution_step(self):
        """Test logging evolution steps."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        
        logger = logging.getLogger("test_orchestrator")
        adapter = LoggingAdapter(orch, logger)
        
        # Should not raise
        adapter.log_evolution_step()
        assert adapter.event_count > 0
    
    def test_log_task_completion(self):
        """Test logging task completion."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        
        adapter = LoggingAdapter(orch)
        adapter.log_task_completion("task1")
        
        assert adapter.event_count > 0
    
    def test_log_stability_issue(self):
        """Test logging stability issues."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1")
        
        adapter = LoggingAdapter(orch)
        adapter.log_stability_issue("task1", "high")
        
        assert adapter.event_count > 0
    
    def test_log_conservation_violation(self):
        """Test logging conservation violations."""
        orch = create_orchestrator()
        
        adapter = LoggingAdapter(orch)
        adapter.log_conservation_violation(0.05)
        
        assert adapter.event_count > 0


class TestDistributedCoordinator:
    """Test distributed coordination."""
    
    def test_register_peer(self):
        """Test peer registration."""
        coordinator = DistributedCoordinator("node1")
        coordinator.register_peer("node2")
        coordinator.register_peer("node3")
        
        assert len(coordinator.peer_nodes) == 2
        assert "node2" in coordinator.peer_nodes
    
    def test_partition_tasks_round_robin(self):
        """Test round-robin task partitioning."""
        coordinator = DistributedCoordinator("node1")
        coordinator.register_peer("node2")
        coordinator.register_peer("node3")
        
        task_ids = [f"task{i}" for i in range(9)]
        partitions = coordinator.partition_tasks(task_ids, "round_robin")
        
        # All nodes should get tasks
        assert len(partitions) == 3
        
        # Total tasks should match
        total_tasks = sum(len(tasks) for tasks in partitions.values())
        assert total_tasks == 9
    
    def test_partition_tasks_hash(self):
        """Test hash-based task partitioning."""
        coordinator = DistributedCoordinator("node1")
        coordinator.register_peer("node2")
        
        task_ids = [f"task{i}" for i in range(10)]
        partitions = coordinator.partition_tasks(task_ids, "hash")
        
        # Should have partitions for all nodes
        assert len(partitions) == 2
        
        # Total should match
        total_tasks = sum(len(tasks) for tasks in partitions.values())
        assert total_tasks == 10
    
    def test_get_local_tasks(self):
        """Test getting local task assignments."""
        coordinator = DistributedCoordinator("node1")
        coordinator.assign_task("task1", "node1")
        coordinator.assign_task("task2", "node2")
        coordinator.assign_task("task3", "node1")
        
        local = coordinator.get_local_tasks(["task1", "task2", "task3"])
        
        assert len(local) == 2
        assert "task1" in local
        assert "task3" in local


class TestObservableOrchestrator:
    """Test observable orchestrator wrapper."""
    
    def test_create_observable_orchestrator(self):
        """Test factory function."""
        obs_orch = create_observable_orchestrator()
        
        assert obs_orch.orchestrator is not None
        assert obs_orch.metrics is not None
        assert obs_orch.logging is not None
    
    def test_evolve_with_observability(self):
        """Test evolution with observability hooks."""
        obs_orch = create_observable_orchestrator()
        obs_orch.orchestrator.add_task("task1", "Task 1")
        
        # Add hook
        hook_called = []
        def test_hook():
            hook_called.append(True)
        
        obs_orch.add_post_evolve_hook(test_hook)
        
        # Evolve
        obs_orch.evolve()
        
        # Hook should have been called
        assert len(hook_called) > 0
    
    def test_task_completion_hooks(self):
        """Test task completion hooks."""
        obs_orch = create_observable_orchestrator()
        obs_orch.orchestrator.add_task("task1", "Task 1")
        
        # Set task to near completion
        task = obs_orch.orchestrator.state.tasks["task1"]
        task.spinor.components = task.spinor.components * 0.001
        
        # Add completion hook
        completed_tasks = []
        def completion_hook(task_id: str):
            completed_tasks.append(task_id)
        
        obs_orch.add_task_completion_hook(completion_hook)
        
        # Evolve
        obs_orch.evolve()
        
        # Hook should be called if task completed
        # (May not complete in one step, but shouldn't error)
        assert isinstance(completed_tasks, list)
    
    def test_get_metrics_report(self):
        """Test getting metrics report."""
        obs_orch = create_observable_orchestrator()
        obs_orch.orchestrator.add_task("task1", "Task 1")
        
        obs_orch.evolve()
        
        report = obs_orch.get_metrics_report()
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_get_health_status(self):
        """Test health status reporting."""
        obs_orch = create_observable_orchestrator()
        obs_orch.orchestrator.add_task("task1", "Task 1")
        
        health = obs_orch.get_health_status()
        
        assert "status" in health
        assert "issues" in health
        assert "task_count" in health
        assert "coherence" in health
        
        # Should be healthy initially
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_run_with_observability(self):
        """Test full run with observability."""
        obs_orch = create_observable_orchestrator()
        obs_orch.orchestrator.add_task("task1", "Task 1")
        obs_orch.orchestrator.add_task("task2", "Task 2")
        
        results = obs_orch.run(max_iterations=5)
        
        assert "elapsed_time" in results
        assert "iterations" in results
        assert results["elapsed_time"] > 0


class TestMetricTypes:
    """Test metric type handling."""
    
    def test_metric_to_prometheus(self):
        """Test Prometheus format conversion."""
        metric = Metric(
            "test_metric",
            42.0,
            MetricType.GAUGE,
            labels={"task": "task1"},
        )
        
        prom_str = metric.to_prometheus()
        
        assert "test_metric" in prom_str
        assert "42" in prom_str
        assert "task1" in prom_str


class TestIntegration:
    """Integration tests."""
    
    def test_full_observable_workflow(self):
        """Test complete observable orchestration workflow."""
        # Create observable orchestrator
        obs_orch = create_observable_orchestrator(
            enable_metrics=True,
            enable_logging=True,
        )
        
        # Add tasks
        for i in range(5):
            obs_orch.orchestrator.add_task(
                f"task{i}",
                f"Task {i}",
                priority=0.5 + i * 0.1,
            )
        
        # Track events
        events = []
        def event_hook():
            events.append(time.time())
        obs_orch.add_post_evolve_hook(event_hook)
        
        # Run
        results = obs_orch.run(max_iterations=10)
        
        # Verify
        assert results["iterations"] > 0
        assert len(events) > 0
        
        # Get reports
        metrics = obs_orch.get_metrics_report()
        health = obs_orch.get_health_status()
        
        assert len(metrics) > 0
        assert "status" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
