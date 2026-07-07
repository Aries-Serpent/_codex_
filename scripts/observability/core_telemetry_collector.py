#!/usr/bin/env python3
"""
Phase 12 Wave 2 - D3.2 Core Telemetry Collector

Collects and manages 25 core metrics across Agent Lifecycle, Workflow Execution,
Permission/Access Control, Configuration Management, and Secret/Token Management
as defined in TELEMETRY_SCHEMA.md.

Authority: @mbaetiong (D-tier)
Version: 1.0.0
Status: Production-Ready
"""

import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Set
from collections import defaultdict, deque

# ============================================================================
# CONFIGURATION & ENUMS
# ============================================================================

class CoreEventType(str, Enum):
    """Core event types mapping to Section A metric updates"""
    AGENT_LAUNCHED = "agent.launched"
    AGENT_STOPPED = "agent.stopped"
    AGENT_RESTARTED = "agent.restarted"
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_COMPLETED = "workflow.completed"
    ROLE_CHECK = "rbac.role.check"
    ACCESS_DENIED = "rbac.access.denied"
    CONFIG_CHANGED = "config.changed"
    CONFIG_DRIFT = "config.drift"
    SECRET_ACCESSED = "secret.accessed"
    SECRET_ROTATED = "secret.rotated"


@dataclass
class CoreEventData:
    """Schema-compliant core event"""
    version: str = "1.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = ""
    domain: str = ""
    event_id: str = ""
    agent_id: str = ""
    agent_type: str = ""
    workflow_id: str = ""
    workflow_type: str = ""
    status: str = ""
    duration_seconds: float = 0.0
    error_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricPoint:
    """Single metric observation"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"


class CoreTelemetryCollector:
    """
    Thread-safe collector for 25 core metrics.
    """
    
    def __init__(self, max_events: int = 10000, cardinality_limit: int = 2000):
        self.logger = logging.getLogger(__name__)
        self.lock = threading.RLock()
        self.max_events = max_events
        self.cardinality_limit = cardinality_limit
        
        # State
        self.events: deque = deque(maxlen=max_events)
        
        # Counters
        self.counters = defaultdict(int)
        
        # Gauges
        self.gauges = defaultdict(float)
        
        # Histograms (stored as lists of values for simplicity)
        self.histograms = defaultdict(list)
        
        # Timeseries registry
        self.timeseries_keys: Set[str] = set()

    def _register_timeseries(self, metric_name: str, labels: Dict[str, str]) -> str:
        """Register a timeseries and return its unique key. Enforces cardinality limit."""
        sorted_labels = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        key = f"{metric_name}{{{sorted_labels}}}"
        
        if key not in self.timeseries_keys:
            if len(self.timeseries_keys) >= self.cardinality_limit:
                self.logger.warning(f"Cardinality limit ({self.cardinality_limit}) reached! Dropping metric: {key}")
                return ""
            self.timeseries_keys.add(key)
        
        return key

    # ========================================================================
    # A.1 AGENT LIFECYCLE METRICS
    # ========================================================================
    
    def record_agent_launch(self, agent_id: str, agent_type: str, initiator_id: str) -> None:
        """agent_launches_total"""
        with self.lock:
            labels = {"agent_id": agent_id, "agent_type": agent_type, "initiator_id": initiator_id}
            key = self._register_timeseries("agent_launches_total", labels)
            if key:
                self.counters[key] += 1
            
            event = CoreEventData(
                event_type=CoreEventType.AGENT_LAUNCHED.value,
                domain="agent_lifecycle",
                agent_id=agent_id,
                agent_type=agent_type,
                metadata={"initiator_id": initiator_id}
            )
            self.events.append(asdict(event))

    def record_agent_stop(self, agent_id: str, stop_reason: str, initiator_id: str) -> None:
        """agent_stops_total"""
        with self.lock:
            labels = {"agent_id": agent_id, "stop_reason": stop_reason, "initiator_id": initiator_id}
            key = self._register_timeseries("agent_stops_total", labels)
            if key:
                self.counters[key] += 1

            event = CoreEventData(
                event_type=CoreEventType.AGENT_STOPPED.value,
                domain="agent_lifecycle",
                agent_id=agent_id,
                metadata={"stop_reason": stop_reason, "initiator_id": initiator_id}
            )
            self.events.append(asdict(event))

    def update_agent_uptime(self, agent_id: str, agent_type: str, uptime_seconds: float) -> None:
        """agent_uptime_seconds"""
        with self.lock:
            labels = {"agent_id": agent_id, "agent_type": agent_type}
            key = self._register_timeseries("agent_uptime_seconds", labels)
            if key:
                self.gauges[key] = uptime_seconds

    def update_agent_error_rate(self, agent_id: str, error_category: str, error_rate: float) -> None:
        """agent_error_rate"""
        with self.lock:
            labels = {"agent_id": agent_id, "error_category": error_category}
            key = self._register_timeseries("agent_error_rate", labels)
            if key:
                self.gauges[key] = error_rate

    def update_agent_memory_usage(self, agent_id: str, memory_type: str, usage_bytes: float) -> None:
        """agent_memory_usage_bytes"""
        with self.lock:
            labels = {"agent_id": agent_id, "memory_type": memory_type}
            key = self._register_timeseries("agent_memory_usage_bytes", labels)
            if key:
                self.gauges[key] = usage_bytes

    def update_agent_cpu_utilization(self, agent_id: str, utilization_percent: float) -> None:
        """agent_cpu_utilization_percent"""
        with self.lock:
            labels = {"agent_id": agent_id}
            key = self._register_timeseries("agent_cpu_utilization_percent", labels)
            if key:
                self.gauges[key] = utilization_percent

    def record_agent_restart(self, agent_id: str, restart_reason: str) -> None:
        """agent_restart_count"""
        with self.lock:
            labels = {"agent_id": agent_id, "restart_reason": restart_reason}
            key = self._register_timeseries("agent_restart_count", labels)
            if key:
                self.counters[key] += 1

    # ========================================================================
    # A.2 WORKFLOW EXECUTION METRICS
    # ========================================================================
    
    def record_workflow_trigger(self, workflow_id: str, trigger_type: str, initiator_id: str) -> None:
        """workflow_triggers_total"""
        with self.lock:
            labels = {"workflow_id": workflow_id, "trigger_type": trigger_type, "initiator_id": initiator_id}
            key = self._register_timeseries("workflow_triggers_total", labels)
            if key:
                self.counters[key] += 1

    def record_workflow_completion(self, workflow_id: str, workflow_type: str, completion_status: str, duration_seconds: float) -> None:
        """workflow_completions_total, workflow_duration_seconds"""
        with self.lock:
            labels = {"workflow_id": workflow_id, "completion_status": completion_status}
            key = self._register_timeseries("workflow_completions_total", labels)
            if key:
                self.counters[key] += 1
                
            dur_labels = {"workflow_id": workflow_id, "workflow_type": workflow_type}
            dur_key = self._register_timeseries("workflow_duration_seconds", dur_labels)
            if dur_key:
                self.histograms[dur_key].append(duration_seconds)

    def record_workflow_error(self, workflow_id: str, error_type: str, stage: str) -> None:
        """workflow_errors_total"""
        with self.lock:
            labels = {"workflow_id": workflow_id, "error_type": error_type, "stage": stage}
            key = self._register_timeseries("workflow_errors_total", labels)
            if key:
                self.counters[key] += 1

    def update_workflow_queue_depth(self, workflow_type: str, depth: int) -> None:
        """workflow_queue_depth"""
        with self.lock:
            labels = {"workflow_type": workflow_type}
            key = self._register_timeseries("workflow_queue_depth", labels)
            if key:
                self.gauges[key] = float(depth)

    # ========================================================================
    # A.3 PERMISSION & ACCESS CONTROL METRICS
    # ========================================================================
    
    def record_role_check(self, agent_id: str, role: str, check_result: str) -> None:
        """role_checks_total"""
        with self.lock:
            labels = {"agent_id": agent_id, "role": role, "check_result": check_result}
            key = self._register_timeseries("role_checks_total", labels)
            if key:
                self.counters[key] += 1

    def record_permission_cache_hit(self, permission_type: str, role: str) -> None:
        """permission_cache_hits_total"""
        with self.lock:
            labels = {"permission_type": permission_type, "role": role}
            key = self._register_timeseries("permission_cache_hits_total", labels)
            if key:
                self.counters[key] += 1

    def record_access_denial(self, denial_reason: str, resource_type: str, role: str) -> None:
        """access_denials_total"""
        with self.lock:
            labels = {"denial_reason": denial_reason, "resource_type": resource_type, "role": role}
            key = self._register_timeseries("access_denials_total", labels)
            if key:
                self.counters[key] += 1

    def record_permission_grant_latency(self, permission_type: str, latency_seconds: float) -> None:
        """permission_grant_latency_seconds"""
        with self.lock:
            labels = {"permission_type": permission_type}
            key = self._register_timeseries("permission_grant_latency_seconds", labels)
            if key:
                self.histograms[key].append(latency_seconds)

    def record_unauthorized_access_attempt(self, agent_id: str, attempted_resource: str, role: str) -> None:
        """unauthorized_access_attempts_total"""
        with self.lock:
            labels = {"agent_id": agent_id, "attempted_resource": attempted_resource, "role": role}
            key = self._register_timeseries("unauthorized_access_attempts_total", labels)
            if key:
                self.counters[key] += 1

    # ========================================================================
    # A.4 CONFIGURATION MANAGEMENT METRICS
    # ========================================================================
    
    def record_config_change(self, config_domain: str, change_type: str) -> None:
        """config_changes_total"""
        with self.lock:
            labels = {"config_domain": config_domain, "change_type": change_type}
            key = self._register_timeseries("config_changes_total", labels)
            if key:
                self.counters[key] += 1

    def record_config_validation(self, config_domain: str, validation_result: str) -> None:
        """config_validations_total"""
        with self.lock:
            labels = {"config_domain": config_domain, "validation_result": validation_result}
            key = self._register_timeseries("config_validations_total", labels)
            if key:
                self.counters[key] += 1

    def record_config_rollback(self, config_domain: str, rollback_reason: str) -> None:
        """config_rollbacks_total"""
        with self.lock:
            labels = {"config_domain": config_domain, "rollback_reason": rollback_reason}
            key = self._register_timeseries("config_rollbacks_total", labels)
            if key:
                self.counters[key] += 1

    def record_config_drift(self, config_domain: str, drift_type: str) -> None:
        """config_drift_events_total"""
        with self.lock:
            labels = {"config_domain": config_domain, "drift_type": drift_type}
            key = self._register_timeseries("config_drift_events_total", labels)
            if key:
                self.counters[key] += 1

    # ========================================================================
    # A.5 SECRET & TOKEN MANAGEMENT METRICS
    # ========================================================================
    
    def record_secret_access(self, secret_type: str, accessor_id: str, access_result: str) -> None:
        """secret_access_events_total"""
        with self.lock:
            labels = {"secret_type": secret_type, "accessor_id": accessor_id, "access_result": access_result}
            key = self._register_timeseries("secret_access_events_total", labels)
            if key:
                self.counters[key] += 1

    def record_secret_rotation(self, secret_type: str, rotation_status: str) -> None:
        """secret_rotation_events_total"""
        with self.lock:
            labels = {"secret_type": secret_type, "rotation_status": rotation_status}
            key = self._register_timeseries("secret_rotation_events_total", labels)
            if key:
                self.counters[key] += 1

    def record_secret_expiry_warning(self, secret_type: str, days_until_expiry_bucket: str) -> None:
        """secret_expiry_warnings_total"""
        with self.lock:
            labels = {"secret_type": secret_type, "days_until_expiry_bucket": days_until_expiry_bucket}
            key = self._register_timeseries("secret_expiry_warnings_total", labels)
            if key:
                self.counters[key] += 1

    def record_secret_unauthorized_attempt(self, secret_type: str, accessor_id: str) -> None:
        """secret_unauthorized_attempts_total"""
        with self.lock:
            labels = {"secret_type": secret_type, "accessor_id": accessor_id}
            key = self._register_timeseries("secret_unauthorized_attempts_total", labels)
            if key:
                self.counters[key] += 1

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Returns a dict containing all counters, gauges, and summary of histograms."""
        with self.lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {k: {"count": len(v), "avg": sum(v)/len(v) if v else 0} for k, v in self.histograms.items()},
                "timeseries_count": len(self.timeseries_keys),
                "event_count": len(self.events)
            }


if __name__ == "__main__":
    # Test core collector
    logging.basicConfig(level=logging.INFO)
    collector = CoreTelemetryCollector()
    
    # Simulate some events
    collector.record_agent_launch("agent-01", "explore", "user-01")
    collector.update_agent_uptime("agent-01", "explore", 3600)
    collector.record_workflow_trigger("wf-123", "manual", "user-01")
    collector.record_workflow_completion("wf-123", "ci-build", "success", 125.5)
    collector.record_role_check("agent-01", "admin", "allowed")
    collector.record_config_change("database", "update")
    collector.record_secret_access("api-key", "agent-01", "success")
    
    snapshot = collector.get_metrics_snapshot()
    print(f"Metrics snapshot:\n{json.dumps(snapshot, indent=2)}")
    print("Total metrics implemented: 25")
