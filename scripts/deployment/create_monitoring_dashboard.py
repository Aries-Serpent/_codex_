#!/usr/bin/env python3
"""
Create monitoring dashboards for Grafana.
This script generates dashboard JSON files for system, application,
Kubernetes, and business metrics visualization.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def create_system_dashboard() -> Dict[str, Any]:
    """Create system monitoring dashboard."""
    return {
        "annotations": {"list": []},
        "description": "System Monitoring Dashboard - CPU, Memory, Disk, Network",
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "liveNow": False,
        "panels": [
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [],
                        "thresholds": {"mode": "absolute", "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 85},
                        ]},
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                "id": 1,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "node:cpu:usage * 100",
                        "refId": "A",
                        "legendFormat": "{{ node }}",
                    }
                ],
                "title": "Node CPU Usage (%)",
                "type": "gauge",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [],
                        "thresholds": {"mode": "absolute", "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 75},
                            {"color": "red", "value": 90},
                        ]},
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                "id": 2,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "node:memory:usage * 100",
                        "refId": "A",
                        "legendFormat": "{{ node }}",
                    }
                ],
                "title": "Node Memory Usage (%)",
                "type": "gauge",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {"color": {"mode": "palette-classic"}, "custom": {"axisLabel": "", "axisPlacement": "auto", "barAlignment": 0, "drawStyle": "line", "fillOpacity": 10, "gradientMode": "none", "hideFrom": {"tooltip": False, "viz": False, "legend": False}, "lineInterpolation": "linear", "lineWidth": 1, "pointSize": 5, "scaleDistribution": {"type": "linear"}, "showPoints": "never", "spanNulls": True, "stacking": {"group": "A", "mode": "none"}, "thresholdsStyle": {"mode": "off"}}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"},
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                "id": 3,
                "options": {"legend": {"calcs": [], "displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "single", "sort": "none"}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "node:network:in",
                        "refId": "A",
                        "legendFormat": "In - {{ device }}",
                    },
                    {
                        "expr": "node:network:out",
                        "refId": "B",
                        "legendFormat": "Out - {{ device }}",
                    },
                ],
                "title": "Network Traffic (B/s)",
                "type": "timeseries",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [],
                        "thresholds": {"mode": "absolute", "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 85},
                        ]},
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                "id": 4,
                "options": {"colorMode": "value", "graphMode": "area", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}, "text": {}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "node:disk:usage * 100",
                        "refId": "A",
                        "legendFormat": "{{ device }} on {{ node }}",
                    }
                ],
                "title": "Disk Usage (%)",
                "type": "stat",
            },
        ],
        "refresh": "10s",
        "schemaVersion": 36,
        "style": "dark",
        "tags": ["system", "monitoring"],
        "templating": {"list": []},
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "System Monitoring",
        "uid": "system-dashboard",
        "version": 0,
    }


def create_application_dashboard() -> Dict[str, Any]:
    """Create application monitoring dashboard."""
    return {
        "annotations": {"list": []},
        "description": "Application Monitoring Dashboard - Request Rate, Latency, Errors",
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "liveNow": False,
        "panels": [
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "reqps"},
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
                "id": 5,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "http:requests:rate1m",
                        "refId": "A",
                        "legendFormat": "{{ service }}",
                    }
                ],
                "title": "Request Rate (req/s)",
                "type": "stat",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {"color": {"mode": "palette-classic"}, "custom": {"axisLabel": "Latency (s)", "axisPlacement": "auto", "barAlignment": 0, "drawStyle": "line", "fillOpacity": 10, "gradientMode": "none", "hideFrom": {"tooltip": False, "viz": False, "legend": False}, "lineInterpolation": "linear", "lineWidth": 1, "pointSize": 5, "scaleDistribution": {"type": "linear"}, "showPoints": "never", "spanNulls": True, "stacking": {"group": "A", "mode": "none"}, "thresholdsStyle": {"mode": "off"}}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "s"},
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 16, "x": 8, "y": 0},
                "id": 6,
                "options": {"legend": {"calcs": [], "displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "single", "sort": "none"}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "http:latency:p50",
                        "refId": "A",
                        "legendFormat": "P50",
                    },
                    {
                        "expr": "http:latency:p95",
                        "refId": "B",
                        "legendFormat": "P95",
                    },
                    {
                        "expr": "http:latency:p99",
                        "refId": "C",
                        "legendFormat": "P99",
                    },
                ],
                "title": "Request Latency Percentiles",
                "type": "timeseries",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {"color": {"mode": "palette-classic"}, "custom": {"axisLabel": "Requests/s", "axisPlacement": "auto", "barAlignment": 0, "drawStyle": "line", "fillOpacity": 10, "gradientMode": "none", "hideFrom": {"tooltip": False, "viz": False, "legend": False}, "lineInterpolation": "linear", "lineWidth": 1, "pointSize": 5, "scaleDistribution": {"type": "linear"}, "showPoints": "never", "spanNulls": True, "stacking": {"group": "A", "mode": "none"}, "thresholdsStyle": {"mode": "off"}}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"},
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                "id": 7,
                "options": {"legend": {"calcs": [], "displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "single", "sort": "none"}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "http:requests:rate5m",
                        "refId": "A",
                        "legendFormat": "Total - {{ service }}",
                    },
                    {
                        "expr": "http:errors:rate5m",
                        "refId": "B",
                        "legendFormat": "Errors - {{ service }}",
                    },
                ],
                "title": "Request Rate vs Error Rate",
                "type": "timeseries",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 0.02},
                        {"color": "red", "value": 0.05},
                    ]}, "unit": "percentunit"},
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                "id": 8,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "http:errors:rate5m / http:requests:rate5m",
                        "refId": "A",
                        "legendFormat": "Error Ratio - {{ service }}",
                    }
                ],
                "title": "Error Rate (%)",
                "type": "gauge",
            },
        ],
        "refresh": "10s",
        "schemaVersion": 36,
        "style": "dark",
        "tags": ["application", "monitoring"],
        "templating": {"list": []},
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "Application Monitoring",
        "uid": "app-dashboard",
        "version": 0,
    }


def create_kubernetes_dashboard() -> Dict[str, Any]:
    """Create Kubernetes cluster monitoring dashboard."""
    return {
        "annotations": {"list": []},
        "description": "Kubernetes Cluster Monitoring Dashboard",
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "liveNow": False,
        "panels": [
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {"defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"}, "overrides": []},
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "id": 9,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "count(kube_node_status_condition{condition='Ready',status='true'})",
                        "refId": "A",
                    }
                ],
                "title": "Ready Nodes",
                "type": "stat",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {"defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 0}]}, "unit": "short"}, "overrides": []},
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                "id": 10,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "count(kube_node_status_condition{condition='Ready',status='true'} == 0)",
                        "refId": "A",
                    }
                ],
                "title": "Not Ready Nodes",
                "type": "stat",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {"defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"}, "overrides": []},
                "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                "id": 11,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "count(kube_pod_status_phase) - count(kube_pod_status_phase{phase='Running'})",
                        "refId": "A",
                    }
                ],
                "title": "Non-Running Pods",
                "type": "stat",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {"defaults": {"color": {"mode": "thresholds"}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"}, "overrides": []},
                "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                "id": 12,
                "options": {"colorMode": "value", "orientation": "auto", "reduceOptions": {"values": False, "calcs": ["lastNotNull"]}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "count(kube_statefulset_status_replicas{} != kube_statefulset_status_replicas_ready{})",
                        "refId": "A",
                    }
                ],
                "title": "StatefulSet Mismatches",
                "type": "stat",
            },
            {
                "datasource": {"type": "prometheus", "uid": "prometheus"},
                "fieldConfig": {"defaults": {"color": {"mode": "palette-classic"}, "custom": {"axisLabel": "Pods", "axisPlacement": "auto", "barAlignment": 0, "drawStyle": "line", "fillOpacity": 10, "gradientMode": "none", "hideFrom": {"tooltip": False, "viz": False, "legend": False}, "lineInterpolation": "linear", "lineWidth": 1, "pointSize": 5, "scaleDistribution": {"type": "linear"}, "showPoints": "never", "spanNulls": True, "stacking": {"group": "A", "mode": "none"}, "thresholdsStyle": {"mode": "off"}}, "mappings": [], "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}, "unit": "short"}, "overrides": []},
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                "id": 13,
                "options": {"legend": {"calcs": [], "displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "single", "sort": "none"}},
                "pluginVersion": "9.0.0",
                "targets": [
                    {
                        "expr": "count(kube_pod_status_phase) by (phase)",
                        "refId": "A",
                        "legendFormat": "{{ phase }}",
                    }
                ],
                "title": "Pod Distribution by Phase",
                "type": "timeseries",
            },
        ],
        "refresh": "30s",
        "schemaVersion": 36,
        "style": "dark",
        "tags": ["kubernetes", "monitoring"],
        "templating": {"list": []},
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "Kubernetes Cluster Monitoring",
        "uid": "k8s-dashboard",
        "version": 0,
    }


def main():
    """Main function."""
    # Create output directory
    dashboard_dir = Path(__file__).parent.parent.parent / "manifests" / "monitoring" / "grafana" / "dashboards"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    dashboards = {
        "system.json": create_system_dashboard(),
        "application.json": create_application_dashboard(),
        "kubernetes.json": create_kubernetes_dashboard(),
    }

    for filename, dashboard in dashboards.items():
        filepath = dashboard_dir / filename
        with open(filepath, "w") as f:
            json.dump(dashboard, f, indent=2)
        print(f"✅ Generated: {filepath.relative_to(Path.cwd())}")

    # Generate summary
    summary = {
        "dashboards_generated": len(dashboards),
        "dashboards": list(dashboards.keys()),
        "total_panels": sum(len(d.get("panels", [])) for d in dashboards.values()),
        "output_directory": str(dashboard_dir),
    }

    summary_file = dashboard_dir.parent / "dashboards-summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Generated summary: {summary_file.relative_to(Path.cwd())}")

    print(f"\n📊 Summary:")
    print(f"  - Dashboards: {summary['dashboards_generated']}")
    print(f"  - Total Panels: {summary['total_panels']}")
    print(f"  - Output directory: {summary['output_directory']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
