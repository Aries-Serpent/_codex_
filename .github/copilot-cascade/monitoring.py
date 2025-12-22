"""
Performance Monitoring for Cascade Delegation Operations.

Provides real-time monitoring, metrics collection, and dashboard data
for cascade system performance analysis.
"""

import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CascadeMetrics:
    """Container for cascade metrics."""

    total_cascades: int = 0
    successful_cascades: int = 0
    failed_cascades: int = 0
    total_tokens: int = 0
    total_time: float = 0.0
    model_usage: Dict[str, int] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)


class CascadeMonitor:
    """Monitors cascade delegation performance and provides analytics."""

    def __init__(self, log_dir: str = ".github/copilot-cascade/logs"):
        """
        Initialize cascade monitor.

        Args:
            log_dir: Directory for storing log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = CascadeMetrics()
        self._start_time = time.time()

        # Load existing metrics if available
        self._load_metrics()

        logger.info(f"Cascade monitor initialized. Log directory: {self.log_dir}")

    def record_cascade(self, results: Dict[str, Any]):
        """
        Record cascade execution metrics.

        Args:
            results: Results dictionary from cascade execution
        """
        self.metrics.total_cascades += 1

        # Determine success
        verification = results.get("verification", {})
        status = verification.get("status", "unknown")

        if status in ["verified", "success"]:
            self.metrics.successful_cascades += 1
        else:
            self.metrics.failed_cascades += 1

        # Track tokens and time
        self.metrics.total_tokens += results.get("total_tokens", 0)
        self.metrics.total_time += results.get("total_time", 0.0)

        # Track model usage
        for subtask in results.get("subtasks", []):
            model = subtask.get("model", "unknown")
            self.metrics.model_usage[model] = self.metrics.model_usage.get(model, 0) + 1

        # Track errors
        for subtask in results.get("subtasks", []):
            if subtask.get("error"):
                error_type = self._classify_error(subtask["error"])
                self.metrics.error_types[error_type] = (
                    self.metrics.error_types.get(error_type, 0) + 1
                )

        # Add to history
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": results.get("task_id", "unknown"),
            "tokens": results.get("total_tokens", 0),
            "time": results.get("total_time", 0.0),
            "success": status in ["verified", "success"],
            "subtasks_count": len(results.get("subtasks", [])),
            "confidence": verification.get("confidence", 0.0),
        }

        self.metrics.performance_history.append(history_entry)

        # Keep only last 100 entries
        if len(self.metrics.performance_history) > 100:
            self.metrics.performance_history = self.metrics.performance_history[-100:]

        # Save metrics
        self._save_metrics()

        logger.info(
            f"Recorded cascade: {results.get('task_id')} (success={history_entry['success']})"
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for monitoring dashboard.

        Returns:
            Dashboard data dictionary
        """
        # Calculate success rate
        total = max(self.metrics.total_cascades, 1)
        success_rate = (self.metrics.successful_cascades / total) * 100

        # Calculate averages
        avg_tokens = self.metrics.total_tokens / total
        avg_time = self.metrics.total_time / total

        # Recent performance (last 10)
        recent = self.metrics.performance_history[-10:] if self.metrics.performance_history else []
        recent_success_rate = 0.0
        if recent:
            recent_success_rate = (sum(1 for r in recent if r["success"]) / len(recent)) * 100

        # Calculate trends
        trends = self._calculate_trends()

        # Estimate cost
        total_cost = self._estimate_cost()

        return {
            "summary": {
                "total_cascades": self.metrics.total_cascades,
                "success_rate": round(success_rate, 1),
                "average_tokens": round(avg_tokens),
                "average_time": round(avg_time, 2),
                "total_cost": total_cost,
                "uptime_hours": round((time.time() - self._start_time) / 3600, 2),
            },
            "model_distribution": self.metrics.model_usage,
            "error_distribution": self.metrics.error_types,
            "recent_performance": {
                "success_rate": round(recent_success_rate, 1),
                "cascades": recent,
            },
            "trends": trends,
            "health": self._calculate_health_status(success_rate),
        }

    def get_detailed_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics for analysis."""
        if not self.metrics.performance_history:
            return {"status": "no_data"}

        # Extract metrics
        tokens = [h["tokens"] for h in self.metrics.performance_history]
        times = [h["time"] for h in self.metrics.performance_history]
        successes = [h["success"] for h in self.metrics.performance_history]

        return {
            "tokens": {
                "mean": statistics.mean(tokens) if tokens else 0,
                "median": statistics.median(tokens) if tokens else 0,
                "stdev": statistics.stdev(tokens) if len(tokens) > 1 else 0,
                "min": min(tokens) if tokens else 0,
                "max": max(tokens) if tokens else 0,
            },
            "time": {
                "mean": statistics.mean(times) if times else 0,
                "median": statistics.median(times) if times else 0,
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "min": min(times) if times else 0,
                "max": max(times) if times else 0,
            },
            "success_rate": (sum(successes) / len(successes) * 100) if successes else 0,
            "total_samples": len(self.metrics.performance_history),
        }

    def _classify_error(self, error: str) -> str:
        """Classify error type from error message."""
        error_lower = error.lower()

        if "timeout" in error_lower:
            return "timeout"
        elif "auth" in error_lower or "permission" in error_lower:
            return "authentication"
        elif "not found" in error_lower or "404" in error_lower:
            return "not_found"
        elif "rate" in error_lower or "limit" in error_lower:
            return "rate_limit"
        elif "connection" in error_lower or "network" in error_lower:
            return "network"
        elif "memory" in error_lower or "oom" in error_lower:
            return "memory"
        else:
            return "other"

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate performance trends."""
        history = self.metrics.performance_history

        if len(history) < 10:
            return {"status": "insufficient_data"}

        # Compare last 10 vs previous 10
        recent_10 = history[-10:]
        prev_10 = history[-20:-10] if len(history) >= 20 else []

        if not prev_10:
            return {"status": "insufficient_data"}

        # Calculate averages
        recent_avg_tokens = statistics.mean(r["tokens"] for r in recent_10)
        prev_avg_tokens = statistics.mean(r["tokens"] for r in prev_10)

        recent_avg_time = statistics.mean(r["time"] for r in recent_10)
        prev_avg_time = statistics.mean(r["time"] for r in prev_10)

        recent_success = sum(1 for r in recent_10 if r["success"]) / len(recent_10)
        prev_success = sum(1 for r in prev_10 if r["success"]) / len(prev_10)

        # Calculate trend directions
        token_change = (
            ((recent_avg_tokens - prev_avg_tokens) / prev_avg_tokens * 100)
            if prev_avg_tokens > 0
            else 0
        )
        time_change = (
            ((recent_avg_time - prev_avg_time) / prev_avg_time * 100) if prev_avg_time > 0 else 0
        )
        success_change = (recent_success - prev_success) * 100

        return {
            "status": "available",
            "token_trend": "improving" if token_change < 0 else "degrading",
            "time_trend": "improving" if time_change < 0 else "degrading",
            "success_trend": "improving" if success_change > 0 else "degrading",
            "token_change_percent": round(token_change, 1),
            "time_change_percent": round(time_change, 1),
            "success_change_percent": round(success_change, 1),
        }

    def _estimate_cost(self) -> float:
        """Estimate total cost based on model usage and tokens."""
        # Cost per 1K tokens (approximate)
        cost_per_1k = {
            "gpt-4o-mini": 0.00015,  # $0.15 per 1M tokens
            "claude-3-5-sonnet-20241022": 0.003,  # $3 per 1M tokens
            "gpt-5": 0.005,  # Estimated
            "default": 0.002,
        }

        total_cost = 0.0

        # Estimate based on model usage
        for model, count in self.metrics.model_usage.items():
            # Rough estimate: 1000 tokens per task
            estimated_tokens = count * 1000
            rate = cost_per_1k.get(model, cost_per_1k["default"])
            total_cost += (estimated_tokens / 1000) * rate

        return round(total_cost, 4)

    def _calculate_health_status(self, success_rate: float) -> Dict[str, Any]:
        """Calculate overall system health status."""
        if success_rate >= 90:
            status = "healthy"
            color = "green"
        elif success_rate >= 70:
            status = "warning"
            color = "yellow"
        else:
            status = "critical"
            color = "red"

        return {
            "status": status,
            "color": color,
            "success_rate": round(success_rate, 1),
            "message": self._get_health_message(status, success_rate),
        }

    def _get_health_message(self, status: str, success_rate: float) -> str:
        """Get health status message."""
        if status == "healthy":
            return f"System operating normally ({success_rate:.1f}% success rate)"
        elif status == "warning":
            return f"Performance degraded ({success_rate:.1f}% success rate) - investigate errors"
        else:
            return f"Critical issues detected ({success_rate:.1f}% success rate) - immediate attention required"

    def _save_metrics(self):
        """Save metrics to file."""
        try:
            metrics_file = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"

            # Convert to dict for JSON serialization
            metrics_dict = {
                "total_cascades": self.metrics.total_cascades,
                "successful_cascades": self.metrics.successful_cascades,
                "failed_cascades": self.metrics.failed_cascades,
                "total_tokens": self.metrics.total_tokens,
                "total_time": self.metrics.total_time,
                "model_usage": self.metrics.model_usage,
                "error_types": self.metrics.error_types,
                "performance_history": self.metrics.performance_history,
            }

            with open(metrics_file, "w") as f:
                json.dump(metrics_dict, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _load_metrics(self):
        """Load metrics from file if exists."""
        try:
            metrics_file = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"

            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    data = json.load(f)

                self.metrics = CascadeMetrics(
                    total_cascades=data.get("total_cascades", 0),
                    successful_cascades=data.get("successful_cascades", 0),
                    failed_cascades=data.get("failed_cascades", 0),
                    total_tokens=data.get("total_tokens", 0),
                    total_time=data.get("total_time", 0.0),
                    model_usage=data.get("model_usage", {}),
                    error_types=data.get("error_types", {}),
                    performance_history=data.get("performance_history", []),
                )

                logger.info(f"Loaded existing metrics: {self.metrics.total_cascades} cascades")

        except Exception as e:
            logger.warning(f"Could not load existing metrics: {e}")

    def export_report(self, filename: Optional[str] = None) -> str:
        """
        Export detailed report to file.

        Args:
            filename: Output filename. If None, auto-generated.

        Returns:
            Path to exported report
        """
        if filename is None:
            filename = f"cascade_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report_path = self.log_dir / filename

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dashboard_data": self.get_dashboard_data(),
            "detailed_statistics": self.get_detailed_statistics(),
            "raw_metrics": {
                "total_cascades": self.metrics.total_cascades,
                "successful_cascades": self.metrics.successful_cascades,
                "failed_cascades": self.metrics.failed_cascades,
                "total_tokens": self.metrics.total_tokens,
                "total_time": self.metrics.total_time,
            },
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Exported report to {report_path}")
        return str(report_path)


# Singleton instance
_monitor_instance: Optional[CascadeMonitor] = None


def get_monitor() -> CascadeMonitor:
    """Get or create monitor singleton."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = CascadeMonitor()
    return _monitor_instance


def record_cascade(results: Dict[str, Any]):
    """Convenience function to record cascade (uses singleton)."""
    monitor = get_monitor()
    monitor.record_cascade(results)


def get_dashboard_data() -> Dict[str, Any]:
    """Convenience function to get dashboard data (uses singleton)."""
    monitor = get_monitor()
    return monitor.get_dashboard_data()
