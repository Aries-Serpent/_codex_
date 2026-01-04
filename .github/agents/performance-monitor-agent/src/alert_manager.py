"""
Alert Manager for Performance Agent
Manages real-time performance alerts
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random

RANDOM_SEED = 47

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class PerformanceAlert:
    """Performance alert"""
    timestamp: datetime
    severity: AlertSeverity
    metric_name: str
    message: str
    current_value: float
    threshold: float
    metadata: Dict[str, Any]

class AlertManager:
    """Manage performance alerts"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.alerts: List[PerformanceAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {
            "latency_p95": {"threshold": 100.0, "severity": AlertSeverity.WARNING},
            "latency_p99": {"threshold": 200.0, "severity": AlertSeverity.CRITICAL},
            "throughput": {"threshold": 1000.0, "severity": AlertSeverity.WARNING},
            "cpu_usage": {"threshold": 80.0, "severity": AlertSeverity.WARNING},
            "memory_usage": {"threshold": 8192.0, "severity": AlertSeverity.CRITICAL},
        }
        self.initialized = True
    
    def create_alert(
        self,
        metric_name: str,
        current_value: float,
        message: str,
        severity: Optional[AlertSeverity] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceAlert:
        """Create a new alert"""
        # Determine severity from rules if not provided
        if severity is None and metric_name in self.alert_rules:
            severity = self.alert_rules[metric_name]["severity"]
        elif severity is None:
            severity = AlertSeverity.INFO
        
        # Get threshold from rules
        threshold = self.alert_rules.get(metric_name, {}).get("threshold", 0.0)
        
        alert = PerformanceAlert(
            timestamp=datetime.now(),
            severity=severity,
            metric_name=metric_name,
            message=message,
            current_value=current_value,
            threshold=threshold,
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        return alert
    
    def check_metric(self, metric_name: str, value: float) -> Optional[PerformanceAlert]:
        """Check if metric exceeds threshold and create alert"""
        if metric_name not in self.alert_rules:
            return None
        
        rule = self.alert_rules[metric_name]
        threshold = rule["threshold"]
        
        # For throughput, lower than threshold is bad
        if "throughput" in metric_name.lower():
            if value < threshold:
                message = f"{metric_name} below threshold: {value:.2f} < {threshold:.2f}"
                return self.create_alert(metric_name, value, message, rule["severity"])
        else:  # For latency, cpu, memory: higher than threshold is bad
            if value > threshold:
                message = f"{metric_name} exceeds threshold: {value:.2f} > {threshold:.2f}"
                return self.create_alert(metric_name, value, message, rule["severity"])
        
        return None
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[PerformanceAlert]:
        """Get active alerts, optionally filtered by severity"""
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of alerts by severity"""
        summary = {
            "info": 0,
            "warning": 0,
            "critical": 0,
            "total": len(self.alerts)
        }
        
        for alert in self.alerts:
            summary[alert.severity.value] += 1
        
        return summary
    
    def clear_alerts(self, metric_name: Optional[str] = None) -> int:
        """Clear alerts, optionally filtered by metric name"""
        if metric_name:
            original_count = len(self.alerts)
            self.alerts = [a for a in self.alerts if a.metric_name != metric_name]
            return original_count - len(self.alerts)
        else:
            count = len(self.alerts)
            self.alerts = []
            return count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get alert manager metrics"""
        return {
            "seed": self.seed,
            "total_alerts": len(self.alerts),
            "alert_summary": self.get_alert_summary(),
            "alert_rules_count": len(self.alert_rules),
            "initialized": self.initialized
        }


def create_alert_manager(seed: int = RANDOM_SEED) -> AlertManager:
    """Factory function to create alert manager"""
    return AlertManager(seed=seed)
