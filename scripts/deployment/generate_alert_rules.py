#!/usr/bin/env python3
"""
Generate alert rules for critical metrics monitoring.
This script generates Prometheus alert rules and recording rules
for comprehensive monitoring coverage.
"""

import json
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any


def generate_alert_rules() -> Dict[str, Any]:
    """Generate Prometheus alert rules."""
    return {
        "groups": [
            {
                "name": "application_alerts",
                "interval": "30s",
                "rules": [
                    {
                        "alert": "HighErrorRate",
                        "expr": 'rate(http_requests_total{status=~"5.."}[5m]) > 0.05',
                        "for": "5m",
                        "labels": {"severity": "critical", "component": "application"},
                        "annotations": {
                            "summary": "High error rate detected",
                            "description": "Error rate is {{ $value | humanizePercentage }} for {{ $labels.service }}",
                        },
                    },
                    {
                        "alert": "HighLatency",
                        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "application"},
                        "annotations": {
                            "summary": "High latency detected",
                            "description": "P95 latency is {{ $value }}s for {{ $labels.service }}",
                        },
                    },
                    {
                        "alert": "ServiceDown",
                        "expr": "up{job='kubernetes-pods'} == 0",
                        "for": "1m",
                        "labels": {"severity": "critical", "component": "application"},
                        "annotations": {
                            "summary": "Service is down",
                            "description": "Service {{ $labels.kubernetes_pod_name }} in {{ $labels.kubernetes_namespace }} is down",
                        },
                    },
                ],
            },
            {
                "name": "resource_alerts",
                "interval": "30s",
                "rules": [
                    {
                        "alert": "HighCPUUsage",
                        "expr": "rate(container_cpu_usage_seconds_total[5m]) > 0.85",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "infrastructure"},
                        "annotations": {
                            "summary": "High CPU usage",
                            "description": "Container {{ $labels.container_name }} CPU usage is {{ $value | humanizePercentage }}",
                        },
                    },
                    {
                        "alert": "HighMemoryUsage",
                        "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "infrastructure"},
                        "annotations": {
                            "summary": "High memory usage",
                            "description": "Container {{ $labels.container_name }} memory usage is {{ $value | humanizePercentage }}",
                        },
                    },
                    {
                        "alert": "DiskSpaceRunningOut",
                        "expr": "(node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.15",
                        "for": "5m",
                        "labels": {"severity": "critical", "component": "infrastructure"},
                        "annotations": {
                            "summary": "Disk space running out",
                            "description": "Disk {{ $labels.device }} on {{ $labels.node }} has only {{ $value | humanizePercentage }} free space",
                        },
                    },
                    {
                        "alert": "HighNetworkTraffic",
                        "expr": "rate(node_network_transmit_bytes_total[5m]) > 100000000",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "infrastructure"},
                        "annotations": {
                            "summary": "High network traffic",
                            "description": "Network traffic on {{ $labels.device }} is {{ $value | humanize }}B/s",
                        },
                    },
                ],
            },
            {
                "name": "kubernetes_alerts",
                "interval": "30s",
                "rules": [
                    {
                        "alert": "PodCrashLooping",
                        "expr": "rate(kube_pod_container_status_restarts_total[15m]) > 0.1",
                        "for": "5m",
                        "labels": {"severity": "critical", "component": "kubernetes"},
                        "annotations": {
                            "summary": "Pod crash looping",
                            "description": "Pod {{ $labels.pod }} in {{ $labels.namespace }} is crash looping",
                        },
                    },
                    {
                        "alert": "NodeNotReady",
                        "expr": "kube_node_status_condition{condition='Ready',status='true'} == 0",
                        "for": "5m",
                        "labels": {"severity": "critical", "component": "kubernetes"},
                        "annotations": {
                            "summary": "Node not ready",
                            "description": "Node {{ $labels.node }} is not in Ready state",
                        },
                    },
                    {
                        "alert": "PVCAlmostFull",
                        "expr": "(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) > 0.85",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "kubernetes"},
                        "annotations": {
                            "summary": "PVC almost full",
                            "description": "PVC {{ $labels.persistentvolumeclaim }} is {{ $value | humanizePercentage }} full",
                        },
                    },
                    {
                        "alert": "StatefulSetReplicasMismatch",
                        "expr": "kube_statefulset_status_replicas_ready != kube_statefulset_status_replicas",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "kubernetes"},
                        "annotations": {
                            "summary": "StatefulSet replicas mismatch",
                            "description": "StatefulSet {{ $labels.statefulset }} has {{ $value }} replicas not ready",
                        },
                    },
                ],
            },
            {
                "name": "alertmanager_alerts",
                "interval": "30s",
                "rules": [
                    {
                        "alert": "AlertmanagerConfigReloadFailed",
                        "expr": "alertmanager_config_last_reload_successful == 0",
                        "for": "5m",
                        "labels": {"severity": "critical", "component": "monitoring"},
                        "annotations": {
                            "summary": "AlertManager config reload failed",
                            "description": "AlertManager failed to reload configuration",
                        },
                    },
                    {
                        "alert": "AlertmanagerFilingNotifications",
                        "expr": "rate(alertmanager_notifications_failed_total[5m]) > 0.01",
                        "for": "5m",
                        "labels": {"severity": "warning", "component": "monitoring"},
                        "annotations": {
                            "summary": "AlertManager filing notifications",
                            "description": "AlertManager is failing to send {{ $value | humanizePercentage }} of notifications",
                        },
                    },
                ],
            },
        ]
    }


def generate_recording_rules() -> Dict[str, Any]:
    """Generate Prometheus recording rules for performance."""
    return {
        "groups": [
            {
                "name": "http_requests",
                "interval": "30s",
                "rules": [
                    {
                        "record": "http:requests:rate1m",
                        "expr": "rate(http_requests_total[1m])",
                    },
                    {
                        "record": "http:requests:rate5m",
                        "expr": "rate(http_requests_total[5m])",
                    },
                    {
                        "record": "http:errors:rate5m",
                        "expr": 'rate(http_requests_total{status=~"5.."}[5m])',
                    },
                    {
                        "record": "http:latency:p50",
                        "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
                    },
                    {
                        "record": "http:latency:p95",
                        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                    },
                    {
                        "record": "http:latency:p99",
                        "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
                    },
                ],
            },
            {
                "name": "cpu_memory",
                "interval": "30s",
                "rules": [
                    {
                        "record": "node:cpu:usage",
                        "expr": "1 - rate(node_cpu_seconds_total{mode='idle'}[5m])",
                    },
                    {
                        "record": "node:memory:usage",
                        "expr": "1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)",
                    },
                    {
                        "record": "container:cpu:usage",
                        "expr": "rate(container_cpu_usage_seconds_total[5m])",
                    },
                    {
                        "record": "container:memory:usage",
                        "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes",
                    },
                ],
            },
            {
                "name": "disk_network",
                "interval": "30s",
                "rules": [
                    {
                        "record": "node:disk:usage",
                        "expr": "1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)",
                    },
                    {
                        "record": "node:disk:iops_read",
                        "expr": "rate(node_disk_reads_completed_total[5m])",
                    },
                    {
                        "record": "node:disk:iops_write",
                        "expr": "rate(node_disk_writes_completed_total[5m])",
                    },
                    {
                        "record": "node:network:in",
                        "expr": "rate(node_network_receive_bytes_total[5m])",
                    },
                    {
                        "record": "node:network:out",
                        "expr": "rate(node_network_transmit_bytes_total[5m])",
                    },
                ],
            },
        ]
    }


def generate_alertmanager_config() -> Dict[str, Any]:
    """Generate AlertManager configuration."""
    return {
        "global": {
            "resolve_timeout": "5m",
            "slack_api_url": "",  # Set to Slack webhook
            "pagerduty_url": "https://events.pagerduty.com/v2/enqueue",
        },
        "templates": ["/etc/alertmanager/templates/*.tmpl"],
        "route": {
            "receiver": "default",
            "group_by": ["alertname", "cluster", "service"],
            "group_wait": "10s",
            "group_interval": "10s",
            "repeat_interval": "12h",
            "routes": [
                {
                    "match": {"severity": "critical"},
                    "receiver": "pagerduty",
                    "continue": True,
                    "group_wait": "0s",
                    "repeat_interval": "4h",
                },
                {
                    "match": {"severity": "warning"},
                    "receiver": "slack-warnings",
                    "group_wait": "30s",
                    "repeat_interval": "24h",
                },
                {
                    "match": {"severity": "info"},
                    "receiver": "default",
                    "repeat_interval": "7d",
                },
            ],
        },
        "receivers": [
            {
                "name": "default",
                "email_configs": [
                    {
                        "to": "alerts@example.com",
                        "from": "alertmanager@example.com",
                        "smarthost": "smtp.example.com:587",
                        "auth_username": "alertmanager@example.com",
                        "auth_password": "password",
                    }
                ],
            },
            {
                "name": "slack-warnings",
                "slack_configs": [
                    {
                        "channel": "#alerts-warning",
                        "title": "Alert: {{ .GroupLabels.alertname }}",
                        "text": "{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}",
                    }
                ],
            },
            {
                "name": "pagerduty",
                "pagerduty_configs": [
                    {
                        "service_key": "YOUR_PAGERDUTY_SERVICE_KEY",
                        "description": "{{ .GroupLabels.alertname }}",
                        "details": {
                            "severity": "{{ .GroupLabels.severity }}",
                            "cluster": "{{ .GroupLabels.cluster }}",
                        },
                    }
                ],
            },
        ],
        "inhibit_rules": [
            {
                "source_match": {"severity": "warning"},
                "target_match": {"severity": "info"},
                "equal": ["alertname", "cluster", "service"],
            },
            {
                "source_match": {"severity": "critical"},
                "target_match": {"severity": "warning"},
                "equal": ["alertname", "cluster", "service"],
            },
        ],
    }


def main():
    """Main function."""
    # Create output directories
    prometheus_dir = Path(__file__).parent.parent.parent / "manifests" / "monitoring" / "prometheus"
    alertmanager_dir = Path(__file__).parent.parent.parent / "manifests" / "monitoring" / "alertmanager"
    prometheus_dir.mkdir(parents=True, exist_ok=True)
    alertmanager_dir.mkdir(parents=True, exist_ok=True)

    # Generate and write alert rules
    alert_rules = generate_alert_rules()
    alert_rules_file = prometheus_dir / "alert-rules.yaml"
    with open(alert_rules_file, "w") as f:
        yaml.dump(alert_rules, f, default_flow_style=False)
    print(f"✅ Generated: {alert_rules_file.relative_to(Path.cwd())}")

    # Generate and write recording rules
    recording_rules = generate_recording_rules()
    
    # Merge with alert rules for output
    merged_rules = {
        "groups": alert_rules["groups"] + recording_rules["groups"]
    }
    
    with open(alert_rules_file, "w") as f:
        yaml.dump(merged_rules, f, default_flow_style=False)
    print(f"✅ Updated: {alert_rules_file.relative_to(Path.cwd())} (with recording rules)")

    # Generate and write AlertManager config
    alertmanager_config = generate_alertmanager_config()
    alertmanager_config_file = alertmanager_dir / "alertmanager-config.yaml"
    with open(alertmanager_config_file, "w") as f:
        yaml.dump({"alertmanager": alertmanager_config}, f, default_flow_style=False)
    print(f"✅ Generated: {alertmanager_config_file.relative_to(Path.cwd())}")

    # Generate summary
    summary = {
        "alert_rules": len(alert_rules["groups"]),
        "alert_rules_count": sum(len(group["rules"]) for group in alert_rules["groups"]),
        "recording_rules": len(recording_rules["groups"]),
        "recording_rules_count": sum(len(group["rules"]) for group in recording_rules["groups"]),
        "alert_groups": [group["name"] for group in alert_rules["groups"]],
        "recording_groups": [group["name"] for group in recording_rules["groups"]],
        "alert_severities": ["critical", "warning", "info"],
        "notification_channels": ["email", "slack", "pagerduty"],
    }

    summary_file = prometheus_dir / "alert-rules-summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Generated summary: {summary_file.relative_to(Path.cwd())}")

    print(f"\n📊 Summary:")
    print(f"  - Alert Rule Groups: {summary['alert_rules']}")
    print(f"  - Alert Rules: {summary['alert_rules_count']}")
    print(f"  - Recording Rule Groups: {summary['recording_rules']}")
    print(f"  - Recording Rules: {summary['recording_rules_count']}")
    print(f"  - Notification Channels: {len(summary['notification_channels'])}")
    print(f"  - Alert Severities: {', '.join(summary['alert_severities'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
