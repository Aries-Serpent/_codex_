"""
Coherence Monitor - Real-time monitoring and alerting for quantum features.

Monitors quantum feature metrics, detects degradation, and triggers
automatic rollbacks when coherence falls below acceptable thresholds.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository
)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertThreshold:
    """Configuration for alert thresholds."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str  # 'less_than', 'greater_than'
    
    def check(self, value: float) -> Optional[AlertLevel]:
        """
        Check if value triggers an alert.
        
        Args:
            value: Metric value to check
            
        Returns:
            AlertLevel if threshold exceeded, None otherwise
        """
        if self.comparison == 'less_than':
            if value < self.critical_threshold:
                return AlertLevel.CRITICAL
            elif value < self.warning_threshold:
                return AlertLevel.WARNING
        elif self.comparison == 'greater_than':
            if value > self.critical_threshold:
                return AlertLevel.CRITICAL
            elif value > self.warning_threshold:
                return AlertLevel.WARNING
        
        return None


@dataclass
class Alert:
    """Represents a monitoring alert."""
    feature: str
    metric_name: str
    level: AlertLevel
    current_value: float
    threshold_value: float
    timestamp: datetime
    message: str


class CoherenceMonitor:
    """
    Monitors quantum feature coherence and system health.
    
    Tracks metrics in real-time, detects degradation patterns,
    and triggers automatic rollbacks when coherence falls below
    acceptable levels.
    
    Default Alert Thresholds (from Phase 7 spec):
    - coherence_avg < 0.3 → CRITICAL
    - error_rate > 0.05 → WARNING
    - latency_p99 > 2000ms → WARNING
    - accuracy < 0.90 → CRITICAL
    """
    
    def __init__(
        self,
        config: QuantumConfig,
        repository: QuantumMetricRepository,
        alert_callback: Optional[Callable[[Alert], None]] = None
    ):
        """
        Initialize coherence monitor.
        
        Args:
            config: Quantum configuration
            repository: Database repository for metrics
            alert_callback: Optional callback function for alerts
        """
        self.config = config
        self.repository = repository
        self.alert_callback = alert_callback
        
        # Default thresholds from Phase 7 spec
        self.thresholds = [
            AlertThreshold(
                metric_name='coherence',
                warning_threshold=0.5,
                critical_threshold=0.3,
                comparison='less_than'
            ),
            AlertThreshold(
                metric_name='error_rate',
                warning_threshold=0.05,
                critical_threshold=0.10,
                comparison='greater_than'
            ),
            AlertThreshold(
                metric_name='latency_p99',
                warning_threshold=2000.0,
                critical_threshold=5000.0,
                comparison='greater_than'
            ),
            AlertThreshold(
                metric_name='accuracy',
                warning_threshold=0.90,
                critical_threshold=0.85,
                comparison='less_than'
            ),
        ]
        
        self._active_alerts: List[Alert] = []
        self._rollback_triggered = False
    
    def record_metric(
        self,
        feature: str,
        metric_name: str,
        metric_value: float,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> QuantumMetric:
        """
        Record a metric and check for alerts.
        
        Args:
            feature: Feature name
            metric_name: Metric name
            metric_value: Metric value
            agent_id: Optional agent identifier
            metadata: Optional metadata
            
        Returns:
            Created QuantumMetric instance
        """
        # Create and persist metric
        metric = QuantumMetric(
            feature=feature,
            metric_name=metric_name,
            metric_value=metric_value,
            agent_id=agent_id,
            metadata=metadata
        )
        
        saved_metric = self.repository.create(metric)
        
        # Check thresholds
        self._check_thresholds(feature, metric_name, metric_value)
        
        return saved_metric
    
    def _check_thresholds(
        self,
        feature: str,
        metric_name: str,
        value: float
    ) -> None:
        """
        Check if metric value triggers any alerts.
        
        Args:
            feature: Feature name
            metric_name: Metric name
            value: Metric value
        """
        for threshold in self.thresholds:
            if threshold.metric_name == metric_name:
                alert_level = threshold.check(value)
                
                if alert_level:
                    alert = Alert(
                        feature=feature,
                        metric_name=metric_name,
                        level=alert_level,
                        current_value=value,
                        threshold_value=(
                            threshold.critical_threshold
                            if alert_level == AlertLevel.CRITICAL
                            else threshold.warning_threshold
                        ),
                        timestamp=datetime.utcnow(),
                        message=self._format_alert_message(
                            feature, metric_name, value, alert_level, threshold
                        )
                    )
                    
                    self._trigger_alert(alert)
    
    def _format_alert_message(
        self,
        feature: str,
        metric_name: str,
        value: float,
        level: AlertLevel,
        threshold: AlertThreshold
    ) -> str:
        """Format alert message."""
        threshold_val = (
            threshold.critical_threshold
            if level == AlertLevel.CRITICAL
            else threshold.warning_threshold
        )
        
        return (
            f"[{level.value.upper()}] {feature}/{metric_name}: "
            f"{value:.3f} {threshold.comparison.replace('_', ' ')} {threshold_val:.3f}"
        )
    
    def _trigger_alert(self, alert: Alert) -> None:
        """
        Trigger an alert and potentially initiate rollback.
        
        Args:
            alert: Alert to trigger
        """
        self._active_alerts.append(alert)
        
        # Call alert callback if provided
        if self.alert_callback:
            self.alert_callback(alert)
        
        # Trigger automatic rollback on critical alerts
        if alert.level == AlertLevel.CRITICAL and not self._rollback_triggered:
            self._initiate_rollback(alert)
    
    def _initiate_rollback(self, alert: Alert) -> None:
        """
        Initiate automatic rollback of quantum features.
        
        Args:
            alert: Alert that triggered rollback
        """
        self._rollback_triggered = True
        
        # Log rollback event
        self.record_metric(
            feature=alert.feature,
            metric_name='rollback_triggered',
            metric_value=1.0,
            metadata={
                'reason': alert.message,
                'alert_level': alert.level.value,
                'trigger_metric': alert.metric_name,
                'trigger_value': alert.current_value
            }
        )
    
    def get_feature_health(
        self,
        feature: str,
        hours: int = 24
    ) -> Dict[str, any]:
        """
        Get health status for a quantum feature.
        
        Args:
            feature: Feature name
            hours: Time window in hours
            
        Returns:
            Dictionary with health metrics
        """
        stats = self.repository.get_coherence_stats(feature, hours)
        
        # Get recent metrics for other health indicators
        recent_metrics = self.repository.find_by_feature(feature, limit=100)
        
        error_rates = [
            m.metric_value for m in recent_metrics
            if m.metric_name == 'error_rate'
        ]
        
        latencies = [
            m.metric_value for m in recent_metrics
            if m.metric_name == 'latency_p99'
        ]
        
        return {
            'feature': feature,
            'coherence': {
                'avg': stats.get('avg_coherence'),
                'min': stats.get('min_coherence'),
                'max': stats.get('max_coherence'),
                'samples': stats.get('sample_count', 0),
            },
            'error_rate': {
                'current': error_rates[0] if error_rates else None,
                'avg': sum(error_rates) / len(error_rates) if error_rates else None,
            },
            'latency': {
                'current_p99': latencies[0] if latencies else None,
                'avg_p99': sum(latencies) / len(latencies) if latencies else None,
            },
            'health_status': self._assess_health_status(feature, stats, error_rates),
            'active_alerts': [
                a for a in self._active_alerts
                if a.feature == feature
            ],
        }
    
    def _assess_health_status(
        self,
        feature: str,
        coherence_stats: Dict,
        error_rates: List[float]
    ) -> str:
        """
        Assess overall health status of a feature.
        
        Args:
            feature: Feature name
            coherence_stats: Coherence statistics
            error_rates: Recent error rates
            
        Returns:
            Health status: 'healthy', 'degraded', or 'critical'
        """
        avg_coherence = coherence_stats.get('avg_coherence')
        
        # Check for critical conditions
        if avg_coherence is not None and avg_coherence < 0.3:
            return 'critical'
        
        if error_rates and max(error_rates) > 0.10:
            return 'critical'
        
        # Check for degraded conditions
        if avg_coherence is not None and avg_coherence < 0.5:
            return 'degraded'
        
        if error_rates and max(error_rates) > 0.05:
            return 'degraded'
        
        return 'healthy'
    
    def get_all_features_health(self) -> Dict[str, Dict]:
        """
        Get health status for all quantum features.
        
        Returns:
            Dictionary mapping feature names to health data
        """
        features = ['superposition', 'entanglement', 'uncertainty', 'wave_collapse']
        
        return {
            feature: self.get_feature_health(feature)
            for feature in features
            if self.config.is_enabled(feature)
        }
    
    def get_active_alerts(
        self,
        feature: Optional[str] = None,
        level: Optional[AlertLevel] = None
    ) -> List[Alert]:
        """
        Get currently active alerts.
        
        Args:
            feature: Optional feature name filter
            level: Optional alert level filter
            
        Returns:
            List of active alerts
        """
        alerts = self._active_alerts
        
        if feature:
            alerts = [a for a in alerts if a.feature == feature]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return alerts
    
    def clear_alerts(
        self,
        feature: Optional[str] = None,
        older_than_hours: Optional[int] = None
    ) -> int:
        """
        Clear resolved or old alerts.
        
        Args:
            feature: Optional feature name to clear alerts for
            older_than_hours: Clear alerts older than N hours
            
        Returns:
            Number of alerts cleared
        """
        initial_count = len(self._active_alerts)
        
        if older_than_hours:
            cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
            self._active_alerts = [
                a for a in self._active_alerts
                if a.timestamp > cutoff
            ]
        
        if feature:
            self._active_alerts = [
                a for a in self._active_alerts
                if a.feature != feature
            ]
        
        if not older_than_hours and not feature:
            self._active_alerts = []
        
        return initial_count - len(self._active_alerts)
    
    def reset_rollback_flag(self) -> None:
        """Reset the rollback triggered flag."""
        self._rollback_triggered = False
    
    @property
    def is_rollback_triggered(self) -> bool:
        """Check if automatic rollback has been triggered."""
        return self._rollback_triggered
