# Iteration 7: Advanced Monitoring Dashboards - Complete Prompt Set

**Iteration**: 7 of 7 (Advanced Validation Series - FINAL)  
**Priority**: P2 (Medium)  
**Duration**: 2-3 hours  
**Dependencies**: Iterations 1-6 complete  
**Environment**: Grafana + Prometheus stack

---

## Executive Summary

Create production-grade monitoring dashboards for the RAG system with real-time metrics, alerting, and observability across all deployment regions. Implement comprehensive visualization for performance, health, cost, and user experience metrics.

---

## Prerequisites Checklist

- [x] Iterations 1-6 complete (multi-region deployed)
- [ ] Grafana 9.0+ installed and accessible
- [ ] Prometheus configured and scraping metrics
- [ ] CloudWatch access (if using AWS)
- [ ] Alert manager configured
- [ ] Slack/PagerDuty webhooks (for alerts)

---

## Prompt for GitHub Copilot Agent

```
@copilot Execute Iteration 7 (Advanced Monitoring Dashboards) for RAG Production Readiness - FINAL

## Context
Branch: copilot/sub-pr-2750
Status: Iterations 1-6 complete, multi-region deployed, load tested
Goal: Create comprehensive monitoring dashboards for production observability

## Dashboard Objectives

1. **Executive Dashboard**: High-level KPIs for stakeholders
2. **Operations Dashboard**: Real-time system health for SRE team
3. **Performance Dashboard**: Detailed metrics for optimization
4. **Cost Dashboard**: Resource utilization and cost tracking
5. **User Experience Dashboard**: End-user metrics and satisfaction

## Implementation Tasks

### Task 1: Create Executive Dashboard

Create `deploy/grafana/dashboards/01-executive-overview.json`:

```json
{
  "dashboard": {
    "title": "RAG Executive Overview",
    "tags": ["rag", "executive", "kpi"],
    "timezone": "utc",
    "refresh": "30s",
    
    "panels": [
      {
        "id": 1,
        "title": "Total Queries (24h)",
        "type": "stat",
        "targets": [{
          "expr": "sum(increase(rag_queries_total[24h]))",
          "legendFormat": "Total Queries"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "thresholds": {
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 1000000, "color": "yellow"},
                {"value": 5000000, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      
      {
        "id": 2,
        "title": "Query Success Rate",
        "type": "gauge",
        "targets": [{
          "expr": "(sum(rate(rag_queries_total{status=\"success\"}[5m])) / sum(rate(rag_queries_total[5m]))) * 100",
          "legendFormat": "Success Rate"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 95, "color": "yellow"},
                {"value": 99, "color": "green"}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      
      {
        "id": 3,
        "title": "Global P99 Latency",
        "type": "gauge",
        "targets": [{
          "expr": "histogram_quantile(0.99, sum(rate(rag_query_latency_ms_bucket[5m])) by (le))",
          "legendFormat": "P99"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "min": 0,
            "max": 500,
            "thresholds": {
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 100, "color": "yellow"},
                {"value": 200, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      
      {
        "id": 4,
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [{
          "expr": "rag_cache_hit_rate * 100",
          "legendFormat": "Hit Rate"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 70, "color": "yellow"},
                {"value": 90, "color": "green"}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
      },
      
      {
        "id": 5,
        "title": "Query Volume by Region",
        "type": "timeseries",
        "targets": [{
          "expr": "sum(rate(rag_queries_total[5m])) by (region)",
          "legendFormat": "{{region}}"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "qps",
            "custom": {"lineWidth": 2, "fillOpacity": 10}
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      
      {
        "id": 6,
        "title": "System Health Score",
        "type": "timeseries",
        "targets": [{
          "expr": "(rag_cache_hit_rate * 0.3 + (rag_queries_total{status=\"success\"} / rag_queries_total) * 0.4 + (1 - (rag_query_latency_ms_p99 / 500)) * 0.3) * 100",
          "legendFormat": "Health Score"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "custom": {"lineWidth": 3, "fillOpacity": 20}
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      
      {
        "id": 7,
        "title": "Regional Status",
        "type": "table",
        "targets": [{
          "expr": "rag_region_status",
          "format": "table",
          "instant": true
        }],
        "transformations": [{
          "id": "organize",
          "options": {
            "excludeByName": {},
            "indexByName": {"region": 0, "status": 1, "queries_24h": 2, "latency_p99": 3},
            "renameByName": {
              "region": "Region",
              "status": "Status",
              "queries_24h": "Queries (24h)",
              "latency_p99": "P99 Latency"
            }
          }
        }],
        "gridPos": {"h": 6, "w": 24, "x": 0, "y": 12}
      }
    ]
  }
}
```

### Task 2: Create Operations Dashboard

Create Python script to generate comprehensive ops dashboard:

```python
#!/usr/bin/env python3
"""
Generate Operations Dashboard for RAG System
Provides detailed real-time metrics for SRE team.
"""

import json
from typing import Dict, List, Any


def create_panel(
    panel_id: int,
    title: str,
    panel_type: str,
    targets: List[Dict],
    grid_pos: Dict[str, int],
    **kwargs
) -> Dict[str, Any]:
    """Create a Grafana panel configuration."""
    panel = {
        "id": panel_id,
        "title": title,
        "type": panel_type,
        "targets": targets,
        "gridPos": grid_pos
    }
    panel.update(kwargs)
    return panel


def generate_operations_dashboard() -> Dict[str, Any]:
    """Generate complete operations dashboard."""
    
    panels = []
    panel_id = 1
    
    # Row 1: Critical Metrics
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Query Throughput (QPS)",
        "timeseries",
        [{
            "expr": "sum(rate(rag_queries_total[1m])) by (region, tenant_id)",
            "legendFormat": "{{region}}/{{tenant_id}}"
        }],
        {"h": 8, "w": 12, "x": 0, "y": 0},
        fieldConfig={
            "defaults": {
                "unit": "qps",
                "custom": {"lineWidth": 2, "fillOpacity": 10}
            }
        }
    ))
    
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Error Rate",
        "timeseries",
        [{
            "expr": "sum(rate(rag_errors_total[5m])) by (error_type)",
            "legendFormat": "{{error_type}}"
        }],
        {"h": 8, "w": 12, "x": 12, "y": 0},
        fieldConfig={
            "defaults": {
                "unit": "errors/s",
                "custom": {"lineWidth": 2}
            }
        }
    ))
    
    # Row 2: Latency Distribution
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Latency Percentiles",
        "timeseries",
        [
            {
                "expr": "histogram_quantile(0.50, sum(rate(rag_query_latency_ms_bucket[5m])) by (le))",
                "legendFormat": "P50"
            },
            {
                "expr": "histogram_quantile(0.95, sum(rate(rag_query_latency_ms_bucket[5m])) by (le))",
                "legendFormat": "P95"
            },
            {
                "expr": "histogram_quantile(0.99, sum(rate(rag_query_latency_ms_bucket[5m])) by (le))",
                "legendFormat": "P99"
            },
            {
                "expr": "histogram_quantile(0.999, sum(rate(rag_query_latency_ms_bucket[5m])) by (le))",
                "legendFormat": "P99.9"
            }
        ],
        {"h": 8, "w": 24, "x": 0, "y": 8},
        fieldConfig={
            "defaults": {
                "unit": "ms",
                "custom": {"lineWidth": 2}
            }
        }
    ))
    
    # Row 3: Cache Performance
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Cache Hit Rate by Tenant",
        "timeseries",
        [{
            "expr": "rag_cache_hit_rate by (tenant_id)",
            "legendFormat": "{{tenant_id}}"
        }],
        {"h": 8, "w": 12, "x": 0, "y": 16},
        fieldConfig={
            "defaults": {
                "unit": "percentunit",
                "min": 0,
                "max": 1
            }
        }
    ))
    
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Cache Memory Usage",
        "timeseries",
        [{
            "expr": "rag_cache_size_bytes / 1024 / 1024",
            "legendFormat": "Cache Size"
        }],
        {"h": 8, "w": 12, "x": 12, "y": 16},
        fieldConfig={
            "defaults": {
                "unit": "MB"
            }
        }
    ))
    
    # Row 4: Resource Utilization
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "CPU Usage by Region",
        "timeseries",
        [{
            "expr": "100 - (avg by (region) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{region}}"
        }],
        {"h": 8, "w": 8, "x": 0, "y": 24},
        fieldConfig={
            "defaults": {
                "unit": "percent",
                "min": 0,
                "max": 100
            }
        }
    ))
    
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Memory Usage",
        "timeseries",
        [{
            "expr": "rag_memory_usage_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{region}}"
        }],
        {"h": 8, "w": 8, "x": 8, "y": 24},
        fieldConfig={
            "defaults": {
                "unit": "GB"
            }
        }
    ))
    
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Disk I/O",
        "timeseries",
        [{
            "expr": "rate(node_disk_read_bytes_total[5m]) / 1024 / 1024",
            "legendFormat": "Read {{region}}"
        },
        {
            "expr": "rate(node_disk_written_bytes_total[5m]) / 1024 / 1024",
            "legendFormat": "Write {{region}}"
        }],
        {"h": 8, "w": 8, "x": 16, "y": 24},
        fieldConfig={
            "defaults": {
                "unit": "MB/s"
            }
        }
    ))
    
    # Row 5: Index Operations
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Index Operations",
        "timeseries",
        [{
            "expr": "sum(rate(rag_index_operations_total[5m])) by (operation)",
            "legendFormat": "{{operation}}"
        }],
        {"h": 8, "w": 12, "x": 0, "y": 32},
        fieldConfig={
            "defaults": {
                "unit": "ops/s"
            }
        }
    ))
    
    panels.append(create_panel(
        panel_id := panel_id + 1,
        "Index Sync Lag",
        "timeseries",
        [{
            "expr": "rag_index_sync_lag_seconds by (source_region, target_region)",
            "legendFormat": "{{source_region}} → {{target_region}}"
        }],
        {"h": 8, "w": 12, "x": 12, "y": 32},
        fieldConfig={
            "defaults": {
                "unit": "s"
            }
        }
    ))
    
    dashboard = {
        "dashboard": {
            "title": "RAG Operations Dashboard",
            "tags": ["rag", "operations", "sre"],
            "timezone": "utc",
            "refresh": "10s",
            "panels": panels,
            "templating": {
                "list": [
                    {
                        "name": "region",
                        "type": "query",
                        "query": "label_values(rag_queries_total, region)",
                        "multi": True,
                        "includeAll": True
                    },
                    {
                        "name": "tenant",
                        "type": "query",
                        "query": "label_values(rag_queries_total{region=\"$region\"}, tenant_id)",
                        "multi": True,
                        "includeAll": True
                    }
                ]
            },
            "annotations": {
                "list": [
                    {
                        "name": "Deployments",
                        "datasource": "Prometheus",
                        "expr": "changes(rag_deployment_version[1m]) > 0",
                        "titleFormat": "Deployment",
                        "textFormat": "Version {{version}}"
                    }
                ]
            }
        }
    }
    
    return dashboard


if __name__ == "__main__":
    dashboard = generate_operations_dashboard()
    
    with open("deploy/grafana/dashboards/02-operations.json", "w") as f:
        json.dump(dashboard, f, indent=2)
    
    print("✅ Operations dashboard generated")
    print("   File: deploy/grafana/dashboards/02-operations.json")
    print(f"   Panels: {len(dashboard['dashboard']['panels'])}")
```

### Task 3: Create Alert Rules

Create `deploy/prometheus/alerts/rag-alerts.yml`:

```yaml
groups:
  - name: rag_critical
    interval: 30s
    rules:
      - alert: RAGHighErrorRate
        expr: |
          sum(rate(rag_errors_total[5m])) / sum(rate(rag_queries_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
          team: rag-sre
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
          runbook: "https://docs.example.com/runbooks/high-error-rate"
      
      - alert: RAGHighLatency
        expr: |
          histogram_quantile(0.99, sum(rate(rag_query_latency_ms_bucket[5m])) by (le, region)) > 500
        for: 10m
        labels:
          severity: warning
          team: rag-sre
        annotations:
          summary: "High P99 latency in {{$labels.region}}"
          description: "P99 latency is {{ $value }}ms (threshold: 500ms)"
          runbook: "https://docs.example.com/runbooks/high-latency"
      
      - alert: RAGRegionDown
        expr: |
          up{job="rag-api"} == 0
        for: 2m
        labels:
          severity: critical
          team: rag-sre
          pagerduty: "yes"
        annotations:
          summary: "RAG region {{$labels.region}} is down"
          description: "Health checks failing for {{$labels.instance}}"
          runbook: "https://docs.example.com/runbooks/region-down"
      
      - alert: RAGCacheLowHitRate
        expr: |
          rag_cache_hit_rate < 0.5
        for: 15m
        labels:
          severity: warning
          team: rag-dev
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }} (target: 70%)"
          runbook: "https://docs.example.com/runbooks/low-cache-hit-rate"
      
      - alert: RAGIndexSyncLag
        expr: |
          rag_index_sync_lag_seconds > 600
        for: 10m
        labels:
          severity: warning
          team: rag-sre
        annotations:
          summary: "Index sync lagging"
          description: "Sync lag is {{ $value }}s between {{$labels.source_region}} and {{$labels.target_region}}"
          runbook: "https://docs.example.com/runbooks/index-sync-lag"
      
      - alert: RAGMemoryHigh
        expr: |
          rag_memory_usage_bytes / rag_memory_limit_bytes > 0.85
        for: 5m
        labels:
          severity: warning
          team: rag-sre
        annotations:
          summary: "High memory usage in {{$labels.region}}"
          description: "Memory usage is {{ $value | humanizePercentage }} of limit"
          runbook: "https://docs.example.com/runbooks/high-memory"

  - name: rag_slo
    interval: 1m
    rules:
      - record: rag:slo:availability_30d
        expr: |
          1 - (
            sum(rate(rag_queries_total{status="error"}[30d])) /
            sum(rate(rag_queries_total[30d]))
          )
      
      - record: rag:slo:latency_p99_30d
        expr: |
          histogram_quantile(0.99,
            sum(rate(rag_query_latency_ms_bucket[30d])) by (le)
          )
      
      - alert: RAGSLOAvailabilityBreach
        expr: rag:slo:availability_30d < 0.999
        for: 1h
        labels:
          severity: critical
          team: rag-leadership
        annotations:
          summary: "SLO breach: availability"
          description: "30-day availability is {{ $value | humanizePercentage }} (SLO: 99.9%)"
          
      - alert: RAGSLOLatencyBreach
        expr: rag:slo:latency_p99_30d > 200
        for: 1h
        labels:
          severity: warning
          team: rag-leadership
        annotations:
          summary: "SLO breach: latency"
          description: "30-day P99 latency is {{ $value }}ms (SLO: 200ms)"
```

### Task 4: Create Cost Dashboard

```python
# Generate cost tracking dashboard
# Integrates with AWS Cost Explorer or CloudWatch billing metrics
# (Script similar to operations dashboard generator)
```

### Task 5: Deploy Dashboards

```bash
#!/bin/bash
# scripts/deploy-dashboards.sh

GRAFANA_URL="http://grafana:3000"
GRAFANA_API_KEY="${GRAFANA_API_KEY}"

echo "Deploying Grafana dashboards..."

for dashboard in deploy/grafana/dashboards/*.json; do
    echo "  Uploading $(basename $dashboard)..."
    
    curl -X POST \
        -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
        -H "Content-Type: application/json" \
        -d @"$dashboard" \
        "${GRAFANA_URL}/api/dashboards/db"
    
    echo "  ✅ Deployed"
done

echo "Configuring alert rules..."
kubectl apply -f deploy/prometheus/alerts/rag-alerts.yml

echo "✅ All dashboards and alerts deployed"
```

## Success Criteria

- ✅ 5 comprehensive dashboards created
- ✅ 10+ alert rules configured
- ✅ SLO tracking implemented
- ✅ Real-time metrics (<30s refresh)
- ✅ Multi-region visibility
- ✅ Cost tracking enabled
- ✅ Runbooks linked from alerts
- ✅ Team notifications configured

## Deliverables

1. Executive dashboard (high-level KPIs)
2. Operations dashboard (detailed metrics)
3. Performance dashboard (optimization)
4. Cost dashboard (resource tracking)
5. UX dashboard (user experience)
6. Alert rules configuration
7. Runbook documentation
8. Deployment scripts

Execute all tasks and create production-ready monitoring infrastructure.
```

---

## Execution Checklist

- [ ] Executive dashboard created and deployed
- [ ] Operations dashboard created and deployed
- [ ] Performance dashboard created
- [ ] Cost dashboard created
- [ ] UX dashboard created
- [ ] Alert rules configured
- [ ] Runbooks written
- [ ] Notifications tested
- [ ] SLO tracking enabled
- [ ] Team training completed

---

## Timeline

- Dashboard design: 1 hour
- Implementation: 3 hours
- Testing & validation: 1 hour
- Documentation: 1 hour
- **Total**: ~6 hours

---

**Prompt Created**: 2026-01-08 21:00 UTC  
**Ready for**: DevOps/SRE team execution  
**Expected Outcome**: Complete observability stack for RAG system
