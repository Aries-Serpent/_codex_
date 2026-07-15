#!/usr/bin/env python3
"""
MONITORING CONFIGURATION FOR CASCADE DETECTION
───────────────────────────────────────────────

CloudWatch/Prometheus metrics emitted by cascade detection system.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CascadeMetrics:
    """Metrics configuration for cascade detection."""

    # Error counters
    error_count_per_hour: int  # Current error count in last hour
    error_count_per_minute: int  # Current error count in last minute
    error_count_per_day: int  # Current error count in last day

    # Circuit breaker state
    breaker_state_armed: bool  # Circuit breaker in ARMED state
    breaker_state_closed: bool  # Circuit breaker in CLOSED state
    breaker_state_open: bool  # Circuit breaker in OPEN state
    breaker_state_half_open: bool  # Circuit breaker in HALF_OPEN state

    # Cascade waves
    cascade_wave_1_detected: bool  # Wave 1 (3+ errors)
    cascade_wave_2_detected: bool  # Wave 2 (10+ errors)
    cascade_wave_3_detected: bool  # Wave 3 (26+ errors)

    # Recovery metrics
    recovery_attempts: int  # Number of recovery attempts
    time_in_open_state_seconds: Optional[int]  # Duration in OPEN state

    # Rate limiting
    rate_limit_triggered: bool  # >5 errors/hour
    emergency_limit_triggered: bool  # >2 errors/minute


METRIC_DEFINITIONS = {
    # CloudWatch-style definitions
    "CascadeDetection": {
        "Namespace": "Copilot/CascadeDetection",
        "Metrics": {
            "ErrorCountPerHour": {
                "Unit": "Count",
                "Type": "gauge",
                "Description": "Error comments posted in the last hour",
                "Thresholds": {
                    "warning": 3,  # Wave 1
                    "alert": 10,  # Wave 2
                    "critical": 26,  # Wave 3
                },
            },
            "ErrorCountPerMinute": {
                "Unit": "Count",
                "Type": "gauge",
                "Description": "Error comments posted in the last minute",
                "Thresholds": {
                    "emergency": 2,
                },
            },
            "CircuitBreakerState": {
                "Unit": "None",
                "Type": "enum",
                "Description": "Current circuit breaker state",
                "Values": ["armed", "closed", "open", "half_open"],
            },
            "CascadeWave": {
                "Unit": "None",
                "Type": "enum",
                "Description": "Highest cascade wave detected",
                "Values": ["none", "wave_1", "wave_2", "wave_3"],
            },
            "RecoveryAttempts": {
                "Unit": "Count",
                "Type": "gauge",
                "Description": "Number of failed recovery attempts",
            },
            "TimeInOpenState": {
                "Unit": "Seconds",
                "Type": "gauge",
                "Description": "Duration circuit breaker has been in OPEN state",
            },
        },
    },
}

ALERT_RULES = {
    # Prometheus-style alert rules
    "CascadeDetection": [
        {
            "alert": "CascadeWave1Detected",
            "expr": "highest_wave == 'wave_1'",
            "for": "1m",
            "severity": "warning",
            "description": "3+ errors detected in last 60 seconds",
        },
        {
            "alert": "CascadeWave2Detected",
            "expr": "highest_wave == 'wave_2'",
            "for": "1m",
            "severity": "critical",
            "description": "10+ errors detected in last 60 seconds",
        },
        {
            "alert": "CascadeWave3Detected",
            "expr": "highest_wave == 'wave_3'",
            "for": "1m",
            "severity": "critical",
            "description": "26+ errors detected in last 60 seconds - ESCALATE",
        },
        {
            "alert": "CircuitBreakerOpen",
            "expr": "breaker_state == 'open'",
            "for": "2m",
            "severity": "critical",
            "description": "Circuit breaker in OPEN state - comment posting paused",
        },
        {
            "alert": "RecoveryFailures",
            "expr": "breaker_recovery_attempts > 3",
            "for": "5m",
            "severity": "critical",
            "description": "Recovery attempts exceeded threshold - escalate",
        },
        {
            "alert": "RateLimitTriggered",
            "expr": "error_count_per_hour > 5",
            "for": "1m",
            "severity": "warning",
            "description": "Error rate limit exceeded (>5 errors/hour)",
        },
        {
            "alert": "EmergencyLimitTriggered",
            "expr": "error_count > 2",
            "for": "30s",
            "severity": "critical",
            "description": "Emergency error limit exceeded (>2 errors/minute)",
        },
    ],
}

DASHBOARD_CONFIG = {
    # Grafana dashboard configuration
    "title": "Copilot Cascade Detection Dashboard",
    "tags": ["cascade-detection", "copilot", "incident-response"],
    "timezone": "UTC",
    "panels": [
        {
            "id": 1,
            "title": "Error Count (Last Hour)",
            "type": "graph",
            "targets": [
                {
                    "expr": "cascade_error_count_per_hour",
                    "legendFormat": "Errors/hour",
                }
            ],
            "thresholds": [
                {"value": 3, "color": "orange", "label": "Wave 1"},
                {"value": 10, "color": "red", "label": "Wave 2"},
                {"value": 26, "color": "darkred", "label": "Wave 3"},
            ],
        },
        {
            "id": 2,
            "title": "Circuit Breaker State",
            "type": "stat",
            "targets": [
                {
                    "expr": "cascade_breaker_state",
                    "legendFormat": "{{ state }}",
                }
            ],
            "mappings": {
                "0": "ARMED",
                "1": "CLOSED",
                "2": "OPEN",
                "3": "HALF_OPEN",
            },
        },
        {
            "id": 3,
            "title": "Cascade Wave Detection",
            "type": "stat",
            "targets": [
                {
                    "expr": "cascade_highest_wave",
                    "legendFormat": "{{ wave }}",
                }
            ],
        },
        {
            "id": 4,
            "title": "Recovery Attempts",
            "type": "graph",
            "targets": [
                {
                    "expr": "cascade_recovery_attempts",
                    "legendFormat": "Attempts",
                }
            ],
            "thresholds": [
                {"value": 3, "color": "orange", "label": "Escalation threshold"}
            ],
        },
        {
            "id": 5,
            "title": "Time in OPEN State",
            "type": "graph",
            "targets": [
                {
                    "expr": "cascade_time_in_open_state_seconds",
                    "legendFormat": "Seconds",
                }
            ],
        },
        {
            "id": 6,
            "title": "Error Rate (Last Minute)",
            "type": "graph",
            "targets": [
                {
                    "expr": "cascade_error_count_per_minute",
                    "legendFormat": "Errors/minute",
                }
            ],
            "thresholds": [
                {"value": 2, "color": "red", "label": "Emergency"},
            ],
        },
    ],
}

if __name__ == "__main__":
    import json

    print("=== Cascade Detection Monitoring Configuration ===\n")

    print("Metric Definitions:")
    print(json.dumps(METRIC_DEFINITIONS, indent=2))

    print("\nAlert Rules:")
    print(json.dumps(ALERT_RULES, indent=2))

    print("\nDashboard Config:")
    print(json.dumps(DASHBOARD_CONFIG, indent=2))
