"""
Performance Monitor Agent - Main Module
Integrates all performance monitoring capabilities with Cognitive Brain PDA Loop
"""
import os
import random
from typing import Any, Dict, List, Optional

try:
    from .alert_manager import AlertManager, AlertSeverity, create_alert_manager
    from .latency_monitor import LatencyMonitor, create_monitor
    from .regression_detector import RegressionDetector, create_detector
    from .resource_predictor import ResourcePredictor, create_predictor
    from .throughput_optimizer import ThroughputOptimizer, create_optimizer
except ImportError:
    # Fallback for direct execution
    from alert_manager import AlertManager, AlertSeverity, create_alert_manager
    from latency_monitor import LatencyMonitor, create_monitor
    from regression_detector import RegressionDetector, create_detector
    from resource_predictor import ResourcePredictor, create_predictor
    from throughput_optimizer import ThroughputOptimizer, create_optimizer

RANDOM_SEED = 47  # Performance Monitor Agent seed

class PerformanceMonitorAgent:
    """
    Performance Monitor Agent - V10 Custom Agent

    Capabilities:
    1. Latency monitoring (p95 < 100ms)
    2. Throughput optimization (>1000 req/s)
    3. Resource usage prediction
    4. Performance regression detection
    5. Real-time alerting

    Integration: Cognitive Brain V10 PDA Loop + AfterMath
    """

    def __init__(self, seed: Optional[int] = None):
        # Load seed from environment variable or use default
        if seed is None:
            seed = int(os.getenv('PERF_MONITOR_SEED', str(RANDOM_SEED)))

        self.seed = seed
        self._rng = random.Random(seed)

        # Initialize all components
        self.latency_monitor = create_monitor(seed)
        self.throughput_optimizer = create_optimizer(seed)
        self.resource_predictor = create_predictor(seed)
        self.regression_detector = create_detector(seed)
        self.alert_manager = create_alert_manager(seed)

        # PDA Loop state
        self.pda_state = {
            "perception": [],
            "decision": [],
            "action": [],
            "aftermath": []
        }

        # Performance metrics
        self.performance_metrics = {
            "latency_p95": 0.0,
            "throughput_rps": 0.0,
            "alerts_generated": 0,
            "regressions_detected": 0
        }

        self.initialized = True

    # PDA Loop Implementation

    def perceive(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Perception Phase: Gather performance metrics and analyze patterns
        """
        perception = {
            "timestamp": self._get_timestamp(),
            "context": context,
            "latency_metrics": self.latency_monitor.get_metrics(),
            "throughput_metrics": self.throughput_optimizer.get_metrics(),
            "resource_predictions": self.resource_predictor.get_metrics(),
            "regression_status": self.regression_detector.get_metrics(),
            "alert_status": self.alert_manager.get_metrics()
        }

        self.pda_state["perception"].append(perception)
        return perception

    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """
        Decision Phase: Determine actions based on performance analysis
        """
        decision = {
            "timestamp": self._get_timestamp(),
            "action_type": "monitor",
            "confidence": 0.9,
            "reasoning": [],
            "recommendations": []
        }

        # Check latency thresholds
        latency_metrics = perception.get("latency_metrics", {})
        percentiles = latency_metrics.get("percentiles", {})
        if percentiles.get("p95", 0) > 100.0:
            decision["reasoning"].append("p95 latency exceeds 100ms threshold")
            decision["recommendations"].append("Optimize slow endpoints")
            decision["action_type"] = "optimize_latency"

        # Check throughput
        throughput_metrics = perception.get("throughput_metrics", {})
        if throughput_metrics.get("average_throughput", 0) < 1000.0:
            decision["reasoning"].append("Throughput below 1000 req/s target")
            decision["recommendations"].append("Scale horizontally")
            decision["action_type"] = "optimize_throughput"

        # Check for regressions
        regression_status = perception.get("regression_status", {})
        if regression_status.get("detected_regressions", 0) > 0:
            decision["reasoning"].append("Performance regression detected")
            decision["recommendations"].append("Investigate recent changes")
            decision["action_type"] = "investigate_regression"

        self.pda_state["decision"].append(decision)
        return decision

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Action Phase: Execute performance monitoring and optimization
        """
        result = {
            "timestamp": self._get_timestamp(),
            "action": decision["action_type"],
            "status": "success",
            "outputs": [],
            "metrics_updated": True
        }

        action_type = decision["action_type"]

        if action_type == "optimize_latency":
            # Trigger latency optimization
            result["outputs"].append("Latency optimization triggered")
            anomalies = self.latency_monitor.detect_anomalies()
            if anomalies:
                result["outputs"].append(f"Detected {len(anomalies)} anomalous requests")

        elif action_type == "optimize_throughput":
            # Trigger throughput optimization
            result["outputs"].append("Throughput optimization triggered")
            _ = self.throughput_optimizer.identify_bottlenecks()  # Analyze bottlenecks
            optimizations = self.throughput_optimizer.suggest_optimizations()
            result["outputs"].extend(optimizations)

        elif action_type == "investigate_regression":
            # Investigate performance regression
            result["outputs"].append("Regression investigation started")
            regressions = self.regression_detector.check_all_metrics()
            for reg in regressions:
                result["outputs"].append(
                    f"Regression in {reg['metric']}: {reg['degradation_percent']:.1f}% degradation"
                )

        else:  # Default monitoring
            result["outputs"].append("Continuous monitoring active")

        self.pda_state["action"].append(result)
        return result

    def aftermath(self, action_result: dict[str, Any]) -> dict[str, Any]:
        """
        AfterMath Phase: Learn from action outcomes and improve
        """
        aftermath = {
            "timestamp": self._get_timestamp(),
            "success": action_result["status"] == "success",
            "lessons_learned": [],
            "improvements_applied": [],
            "updated_beliefs": {}
        }

        # Extract lessons
        if action_result["status"] == "success":
            aftermath["lessons_learned"].append("Performance monitoring cycle completed successfully")

            # Update performance metrics
            self.performance_metrics["alerts_generated"] = self.alert_manager.get_metrics()["total_alerts"]
            self.performance_metrics["regressions_detected"] = self.regression_detector.get_metrics()["detected_regressions"]

            aftermath["improvements_applied"].append("Updated performance baselines")

        # Update beliefs based on outcomes
        aftermath["updated_beliefs"] = {
            "monitoring_effective": action_result["status"] == "success",
            "patterns_detected": len(action_result.get("outputs", [])) > 0
        }

        self.pda_state["aftermath"].append(aftermath)
        return aftermath

    # Public API Methods

    def monitor_latency(self, endpoint: str, latency_ms: float, status_code: int = 200) -> None:
        """Record latency measurement"""
        self.latency_monitor.record_latency(endpoint, latency_ms, status_code)

        # Check for alerts
        self.alert_manager.check_metric("latency_p95", latency_ms)

    def monitor_throughput(self, rps: float, connections: int, queue_depth: int) -> None:
        """Record throughput measurement"""
        self.throughput_optimizer.record_throughput(rps, connections, queue_depth)

        # Check for alerts
        self.alert_manager.check_metric("throughput", rps)

    def monitor_resources(self, cpu: float, memory_mb: float, disk_mbps: float, network_mbps: float) -> None:
        """Record resource usage"""
        self.resource_predictor.record_usage(cpu, memory_mb, disk_mbps, network_mbps)

        # Check for alerts
        self.alert_manager.check_metric("cpu_usage", cpu)
        self.alert_manager.check_metric("memory_usage", memory_mb)

    def set_performance_baseline(self, metric_name: str, value: float, commit_sha: str = "baseline") -> None:
        """Set performance baseline for regression detection"""
        self.regression_detector.set_baseline(metric_name, value, commit_sha)

    def measure_performance(self, metric_name: str, value: float, commit_sha: str = "current") -> None:
        """Measure performance metric"""
        self.regression_detector.measure(metric_name, value, commit_sha)

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive agent metrics"""
        return {
            "agent_name": "performance-monitor",
            "seed": self.seed,
            "pda_cycles": {
                "perceptions": len(self.pda_state["perception"]),
                "decisions": len(self.pda_state["decision"]),
                "actions": len(self.pda_state["action"]),
                "aftermaths": len(self.pda_state["aftermath"])
            },
            "components": {
                "latency_monitor": self.latency_monitor.get_metrics(),
                "throughput_optimizer": self.throughput_optimizer.get_metrics(),
                "resource_predictor": self.resource_predictor.get_metrics(),
                "regression_detector": self.regression_detector.get_metrics(),
                "alert_manager": self.alert_manager.get_metrics()
            },
            "performance_metrics": self.performance_metrics,
            "initialized": self.initialized
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def create_agent(seed: Optional[int] = None) -> PerformanceMonitorAgent:
    """Factory function to create Performance Monitor Agent"""
    return PerformanceMonitorAgent(seed=seed)
