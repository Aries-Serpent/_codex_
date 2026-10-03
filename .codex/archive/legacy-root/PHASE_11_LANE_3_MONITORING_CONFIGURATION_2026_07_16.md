# PHASE 11 LANE 3: MONITORING INFRASTRUCTURE CONFIGURATION
## v0.2.0 Production Deployment - Monitoring Setup

**Created:** 2026-07-16T19:31:06Z  
**Authority:** performance-monitor-agent  
**Purpose:** Define monitoring dashboards, metrics, and alert rules for v0.2.0

---

## GRAFANA DASHBOARD CONFIGURATIONS

### Dashboard 1: System Health
**Dashboard ID:** `system-health-v0.2.0`  
**Refresh Rate:** 30 seconds  
**Retention:** 30 days

#### Panels Configuration

##### Panel 1.1: CPU Utilization
```json
{
  "title": "CPU Utilization",
  "targets": [
    {
      "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100",
      "legendFormat": "{{pod_name}}"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "max": 100,
      "threshold": "80,90"
    }
  ],
  "alert": {
    "name": "CPUUtilizationHigh",
    "condition": "avg() > 85",
    "duration": "5m"
  }
}
```

##### Panel 1.2: Memory Utilization
```json
{
  "title": "Memory Utilization",
  "targets": [
    {
      "expr": "(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100",
      "legendFormat": "{{pod_name}}"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "max": 100,
      "threshold": "85,92"
    }
  ],
  "alert": {
    "name": "MemoryUtilizationHigh",
    "condition": "avg() > 90",
    "duration": "5m"
  }
}
```

##### Panel 1.3: Disk Space Usage
```json
{
  "title": "Disk Space Available",
  "targets": [
    {
      "expr": "(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100",
      "legendFormat": "{{device}} ({{mountpoint}})"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "max": 100,
      "threshold": "30,10"
    }
  ],
  "alert": {
    "name": "DiskSpaceLow",
    "condition": "min() < 10",
    "duration": "1m"
  }
}
```

##### Panel 1.4: Network I/O
```json
{
  "title": "Network I/O",
  "targets": [
    {
      "expr": "rate(container_network_receive_bytes_total[5m])",
      "legendFormat": "RX {{pod_name}}"
    },
    {
      "expr": "rate(container_network_transmit_bytes_total[5m])",
      "legendFormat": "TX {{pod_name}}"
    }
  ],
  "yaxes": [
    {
      "format": "Bps"
    }
  ]
}
```

##### Panel 1.5: Load Average
```json
{
  "title": "Load Average",
  "targets": [
    {
      "expr": "node_load1",
      "legendFormat": "1m {{instance}}"
    },
    {
      "expr": "node_load5",
      "legendFormat": "5m {{instance}}"
    },
    {
      "expr": "node_load15",
      "legendFormat": "15m {{instance}}"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

---

### Dashboard 2: Application Metrics
**Dashboard ID:** `app-metrics-v0.2.0`  
**Refresh Rate:** 10 seconds  
**Retention:** 7 days

#### Panels Configuration

##### Panel 2.1: Error Rate
```json
{
  "title": "Error Rate",
  "targets": [
    {
      "expr": "(rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m])) * 100",
      "legendFormat": "5xx Errors"
    },
    {
      "expr": "(rate(http_requests_total{status=~'4..'}[5m]) / rate(http_requests_total[5m])) * 100",
      "legendFormat": "4xx Errors"
    },
    {
      "expr": "(rate(http_request_duration_seconds_bucket{le='+Inf',status='timeout'}[5m]) / rate(http_requests_total[5m])) * 100",
      "legendFormat": "Timeouts"
    }
  ],
  "yaxes": [
    {
      "format": "percent",
      "min": 0,
      "threshold": "0.2,0.5"
    }
  ],
  "alert": {
    "name": "ErrorRateHigh",
    "condition": "avg() > 0.5",
    "duration": "2m"
  }
}
```

##### Panel 2.2: Request Latency (p50, p95, p99)
```json
{
  "title": "Request Latency Percentiles",
  "targets": [
    {
      "expr": "histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m]))",
      "legendFormat": "p50"
    },
    {
      "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
      "legendFormat": "p95"
    },
    {
      "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
      "legendFormat": "p99"
    }
  ],
  "yaxes": [
    {
      "format": "ms",
      "threshold": "200,500,1000"
    }
  ],
  "alert": {
    "name": "LatencySpikeDetected",
    "condition": "p95 > 500 or p99 > 1000",
    "duration": "3m"
  }
}
```

##### Panel 2.3: Throughput (RPS)
```json
{
  "title": "Requests Per Second",
  "targets": [
    {
      "expr": "rate(http_requests_total[1m])",
      "legendFormat": "RPS {{instance}}"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

##### Panel 2.4: Request Duration Distribution
```json
{
  "title": "Request Duration Distribution",
  "targets": [
    {
      "expr": "http_request_duration_seconds_bucket",
      "format": "heatmap",
      "legendFormat": "{{le}}"
    }
  ]
}
```

##### Panel 2.5: Top Error Types (Table)
```json
{
  "title": "Top Error Types (Last Hour)",
  "targets": [
    {
      "expr": "topk(10, sum by (status, error_type) (rate(http_requests_total{status=~'[45]..'}[1h])))",
      "format": "table"
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": {},
        "indexByName": {},
        "renameByName": {
          "status": "HTTP Status",
          "error_type": "Error Type",
          "Value": "Count"
        }
      }
    }
  ]
}
```

##### Panel 2.6: Request Rate by Endpoint
```json
{
  "title": "Request Rate by Endpoint",
  "targets": [
    {
      "expr": "topk(15, sum by (endpoint) (rate(http_requests_total[5m])))",
      "legendFormat": "{{endpoint}}"
    }
  ],
  "type": "bargauge"
}
```

---

### Dashboard 3: Database Performance
**Dashboard ID:** `db-performance-v0.2.0`  
**Refresh Rate:** 30 seconds  
**Retention:** 7 days

#### Panels Configuration

##### Panel 3.1: Query Execution Times
```json
{
  "title": "Database Query Latency",
  "targets": [
    {
      "expr": "histogram_quantile(0.5, rate(db_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p50"
    },
    {
      "expr": "histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p95"
    },
    {
      "expr": "histogram_quantile(0.99, rate(db_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p99"
    }
  ],
  "yaxes": [
    {
      "format": "ms"
    }
  ]
}
```

##### Panel 3.2: Connection Pool Usage
```json
{
  "title": "Database Connection Pool",
  "targets": [
    {
      "expr": "db_connection_pool_size - db_connection_pool_available",
      "legendFormat": "Used Connections"
    },
    {
      "expr": "db_connection_pool_size",
      "legendFormat": "Pool Size"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ],
  "alert": {
    "name": "ConnectionPoolNearCapacity",
    "condition": "(used / pool_size) > 0.9",
    "duration": "2m"
  }
}
```

##### Panel 3.3: Active Connections
```json
{
  "title": "Active Database Connections",
  "targets": [
    {
      "expr": "db_active_connections",
      "legendFormat": "{{instance}}"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

##### Panel 3.4: Replication Lag
```json
{
  "title": "Replication Lag (if applicable)",
  "targets": [
    {
      "expr": "db_replication_lag_seconds",
      "legendFormat": "{{replica_name}}"
    }
  ],
  "yaxes": [
    {
      "format": "s"
    }
  ],
  "alert": {
    "name": "ReplicationLagHigh",
    "condition": "max() > 5",
    "duration": "2m"
  }
}
```

##### Panel 3.5: Slow Query Count
```json
{
  "title": "Slow Queries (>1s)",
  "targets": [
    {
      "expr": "rate(db_slow_queries_total[5m])",
      "legendFormat": "Slow Queries"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

---

### Dashboard 4: Business Metrics
**Dashboard ID:** `business-metrics-v0.2.0`  
**Refresh Rate:** 1 minute  
**Retention:** 30 days

#### Panels Configuration

##### Panel 4.1: Concurrent Users
```json
{
  "title": "Concurrent Users",
  "targets": [
    {
      "expr": "app_concurrent_users",
      "legendFormat": "Active Users"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

##### Panel 4.2: Transaction Volume
```json
{
  "title": "Transaction Volume",
  "targets": [
    {
      "expr": "rate(app_transactions_total[1m])",
      "legendFormat": "Transactions/min"
    }
  ],
  "yaxes": [
    {
      "format": "short"
    }
  ]
}
```

##### Panel 4.3: Feature Usage Distribution
```json
{
  "title": "Top 10 Feature Usage",
  "targets": [
    {
      "expr": "topk(10, sum by (feature_name) (rate(app_feature_usage_total[1h])))",
      "legendFormat": "{{feature_name}}"
    }
  ],
  "type": "piechart"
}
```

##### Panel 4.4: Session Duration
```json
{
  "title": "Average Session Duration",
  "targets": [
    {
      "expr": "app_session_duration_seconds",
      "legendFormat": "Duration"
    }
  ],
  "yaxes": [
    {
      "format": "s"
    }
  ]
}
```

---

## ALERT RULES CONFIGURATION

### AlertRule 1: ErrorRateExceeded
```yaml
alert: ErrorRateExceeded
expr: |
  (sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m]))) * 100 > 0.5
for: 2m
labels:
  severity: critical
  lane: 3
  phase: 11
annotations:
  summary: "Error rate exceeded 0.5%"
  description: "Current error rate: {{ $value }}%"
  action: "Page on-call engineer, create incident"
```

### AlertRule 2: LatencyPExceedsThreshold
```yaml
alert: LatencyPExceedsThreshold
expr: |
  histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
  or
  histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
for: 3m
labels:
  severity: high
  lane: 3
  phase: 11
annotations:
  summary: "Request latency spike detected"
  description: "p95: {{ $value }}s"
  action: "Alert on-call engineer via Slack"
```

### AlertRule 3: CPUSaturation
```yaml
alert: CPUSaturation
expr: |
  (rate(container_cpu_usage_seconds_total[5m]) * 100) > 85
for: 5m
labels:
  severity: high
  lane: 3
  phase: 11
annotations:
  summary: "CPU utilization exceeds 85%"
  description: "Current: {{ $value }}%"
  action: "Auto-scale up (if configured), alert team"
```

### AlertRule 4: MemorySaturation
```yaml
alert: MemorySaturation
expr: |
  (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 90
for: 5m
labels:
  severity: high
  lane: 3
  phase: 11
annotations:
  summary: "Memory utilization exceeds 90%"
  description: "Current: {{ $value }}%"
  action: "Investigate memory leak, consider restart"
```

### AlertRule 5: DBConnectionPoolNearCapacity
```yaml
alert: DBConnectionPoolNearCapacity
expr: |
  (db_connection_pool_size - db_connection_pool_available) / db_connection_pool_size > 0.9
for: 2m
labels:
  severity: warning
  lane: 3
  phase: 11
annotations:
  summary: "Database connection pool near capacity"
  description: "Pool usage: {{ $value | humanizePercentage }}"
  action: "Alert team, monitor for connection exhaustion"
```

### AlertRule 6: DiskSpaceCritical
```yaml
alert: DiskSpaceCritical
expr: |
  (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
for: 1m
labels:
  severity: critical
  lane: 3
  phase: 11
annotations:
  summary: "Disk space critically low"
  description: "Available: {{ $value }}%"
  action: "Page on-call, trigger cleanup procedures"
```

---

## PROMETHEUS SCRAPE CONFIGURATION

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_endpoints_name]
        regex: 'node-exporter'
        action: keep
```

---

## GRAFANA NOTIFICATION CHANNELS

### Channel 1: PagerDuty (Critical Alerts)
```json
{
  "name": "PagerDuty",
  "type": "pagerduty",
  "settings": {
    "integrationKey": "${PAGERDUTY_INTEGRATION_KEY}"
  },
  "conditions": {
    "severity": "critical"
  }
}
```

### Channel 2: Slack (All Alerts)
```json
{
  "name": "Slack #monitoring",
  "type": "slack",
  "settings": {
    "url": "${SLACK_WEBHOOK_URL}",
    "channel": "#monitoring"
  },
  "conditions": {
    "severity": "warning,high,critical"
  }
}
```

### Channel 3: Email (Summaries)
```json
{
  "name": "On-Call Email",
  "type": "email",
  "settings": {
    "addresses": "${ON_CALL_EMAIL_LIST}"
  },
  "conditions": {
    "severity": "high,critical"
  }
}
```

---

## MONITORING ACTIVATION CHECKLIST

**Pre-Observation (T-0 to T+5):**
- [ ] Prometheus collecting metrics from all scrapers
- [ ] Grafana dashboards visible and updating
- [ ] Alert rules loaded and tested (dry-run)
- [ ] Notification channels tested
- [ ] Baseline metrics captured (v0.2.0)
- [ ] On-call team briefed
- [ ] Escalation procedures reviewed

**During Observation (T+5 to T+120):**
- [ ] Dashboards updated every refresh cycle
- [ ] Metrics flowing continuously
- [ ] Alert rules armed and monitoring
- [ ] No false positives in dry-run tests
- [ ] Team monitoring dashboards actively
- [ ] Incident response team on standby

**Post-Observation (T+120+):**
- [ ] All metrics collected and archived
- [ ] Alert rules transitioned to 24/7 production
- [ ] Dashboards handed to ops team
- [ ] Baseline metrics documented
- [ ] Monitoring handoff completed

---

**Configuration Author:** performance-monitor-agent  
**Lane Owner:** performance-monitor-agent + workflow-health-monitor  
**Last Updated:** 2026-07-16T19:31:06Z
