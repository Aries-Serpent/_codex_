# Production Monitoring Guide

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainer**: SRE Team  
**Primary Tools**: Prometheus, Grafana, Elasticsearch, PagerDuty  

---

## Executive Summary

This guide provides comprehensive procedures for monitoring production systems, interpreting metrics, configuring alerts, and responding to monitoring insights. It covers Prometheus/Grafana setup, alert thresholds, dashboard usage, and log aggregation patterns.

**Monitoring SLA Targets**:
- Alert detection latency: < 1 minute
- Dashboard response time: < 2 seconds
- Log ingestion delay: < 30 seconds
- Metric retention: 15 days raw, 90 days aggregated

---

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────┐
│           Production Monitoring Stack                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Applications & Infrastructure                      │
│  ├─ Prometheus Exporters                           │
│  ├─ Application Metrics (StatsD/OpenTelemetry)    │
│  ├─ System Metrics (node_exporter, kube-state-exp)│
│  └─ Log Collectors (Fluent Bit, Filebeat)         │
│                 │                                  │
│         ┌───────┴───────┬──────────┐              │
│         │               │          │              │
│     Prometheus      Elasticsearch  │              │
│     (Time Series)   (Log Storage)  │              │
│         │               │          │              │
│         └───────┬───────┴──────────┘              │
│                 │                                │
│         ┌───────┴────────┐                       │
│         │                │                       │
│      Grafana         Kibana/ELK                  │
│    (Dashboards)     (Log Search)                 │
│         │                │                       │
│         └───────┬────────┘                       │
│                 │                                │
│          PagerDuty/AlertManager                  │
│         (Alert Routing & Escalation)             │
│                                                  │
└─────────────────────────────────────────────────────┘
```

---

## Prometheus Configuration

### 1.1 Scrape Configuration

**Application Metrics Collection**:

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    environment: 'prod'

scrape_configs:
  # Application metrics
  - job_name: 'codex-api'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: codex-api
      - source_labels: [__meta_kubernetes_pod_port_name]
        action: keep
        regex: metrics
    scrape_interval: 30s
    scrape_timeout: 10s

  # Node metrics
  - job_name: 'kubernetes-nodes'
    scheme: https
    kubernetes_sd_configs:
      - role: node
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Database metrics
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
    relabel_configs:
      - source_labels: [__scheme__, __address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: postgres-exporter:9187

  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 1.2 Alert Rules Configuration

**Alerting Rules**:

```yaml
# prometheus-alerts.yaml
groups:
  - name: application
    interval: 30s
    rules:
      - alert: APIHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
          service: api
        annotations:
          summary: "High error rate detected"
          description: "Error rate {{ $value | humanizePercentage }} for {{ $labels.handler }}"

      - alert: APIHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: high
          service: api
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.05
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"

      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: high
          service: database
        annotations:
          summary: "Database connection pool {{ $value | humanizePercentage }} full"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Low disk space on {{ $labels.device }}"
          description: "Only {{ $value | humanizePercentage }} available"

      - alert: MemoryUtilizationHigh
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.85
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "High memory utilization: {{ $value | humanizePercentage }}"

      - alert: CPUUtilizationHigh
        expr: rate(node_cpu_seconds_total{mode="idle"}[5m]) < 0.2
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "High CPU utilization"
```

---

## Grafana Dashboard Setup

### 2.1 Dashboard Categories

**Dashboard Organization**:

```
Production Dashboards
├─ Overview Dashboard
│  ├─ System health status
│  ├─ Active alerts
│  └─ Key metrics at a glance
│
├─ Application Performance
│  ├─ Request rate by endpoint
│  ├─ Response time percentiles
│  ├─ Error rate by status code
│  └─ Throughput and latency trends
│
├─ Infrastructure
│  ├─ Node CPU/Memory utilization
│  ├─ Network I/O
│  ├─ Disk usage and I/O
│  └─ Container resource usage
│
├─ Database
│  ├─ Connection pool status
│  ├─ Query execution time
│  ├─ Slow query analysis
│  └─ Replication lag
│
├─ Cache (Redis)
│  ├─ Hit/miss ratio
│  ├─ Memory usage
│  ├─ Eviction rate
│  └─ Connection count
│
└─ Custom Application Metrics
   ├─ Business metrics
   ├─ Feature usage
   └─ Custom timers
```

### 2.2 Key Dashboard Panels

**Overview Dashboard**:

```
Panel 1: System Status (Stat Panel)
- Query: sum(rate(http_requests_total[5m]))
- Display: Current request rate
- Threshold: Green < 500 req/s, Yellow 500-1000, Red > 1000

Panel 2: Error Rate (Gauge)
- Query: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
- Display: Percentage
- Threshold: Green < 0.1%, Yellow 0.1-1%, Red > 1%

Panel 3: Response Time (Stat)
- Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
- Display: 200ms, 300ms (p99), etc.
- Threshold: Green < 200ms, Yellow 200-500ms, Red > 500ms

Panel 4: Alert Count (Stat)
- Query: count(ALERTS{alertstate="firing"})
- Display: Number of active alerts
- Link: Click to see alert details

Panel 5: Pod Status (Table)
- Query: kube_pod_status_phase{namespace="production"}
- Display: Running/Pending/Failed count
- Alert: Any pod in Failed phase

Panel 6: Database Connections (Graph)
- Query: pg_stat_activity_count
- Display: Time series of connection count
- Threshold Line: Max connections limit
```

### 2.3 Custom Panels for Business Metrics

**Custom Application Metrics**:

```yaml
Panel: User Login Success Rate
  Query: sum(rate(auth_login_success_total[5m])) / sum(rate(auth_login_attempts_total[5m]))
  Display: Percentage over time
  Alert: If < 95% for 5 minutes, investigate

Panel: API Cost (if metered)
  Query: sum(rate(api_calls_total[5m])) * UNIT_COST
  Display: Estimated hourly cost
  Alert: If > $X/hour, notify finance

Panel: Feature Adoption
  Query: count(distinct(user_id)) - count(distinct(user_id) without(feature_x))
  Display: Number of users with new feature
  Target: Track adoption rate

Panel: Customer Satisfaction (if available)
  Query: sum(customer_satisfaction_score) / count(customer_satisfaction_score)
  Display: Average satisfaction
  Alert: If < 4.0/5.0, investigate
```

---

## Alert Management

### 3.1 Alert Severity Levels

**Alert Configuration**:

| Severity | Response Time | Escalation | Example |
|----------|---------------|-----------|---------|
| Critical | 5 minutes | Immediate page | API down, data loss |
| High | 15 minutes | Page + Slack | Error rate > 1%, latency > 1s |
| Medium | 1 hour | Slack #alerts | Moderate anomaly |
| Low | 24 hours | Email | Minor drift, advisory |

### 3.2 Alert Tuning

**Avoiding False Positives**:

```bash
# Issue: Alert fires for every minor spike
# Fix 1: Increase threshold
# Before: error_rate > 0.5%
# After: error_rate > 1% (more realistic threshold)

# Fix 2: Increase duration
# Before: for: 1m (too sensitive)
# After: for: 5m (allows for transient spikes)

# Fix 3: Add correlation
# Instead of: AlertA = high_error_rate
# Use: AlertA = high_error_rate AND pod_restart_count > 5
# (Ignore errors during pod restart)

# Example: Refined alert rule
- alert: APIHighErrorRate
  expr: (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.01
  for: 5m  # Increased from 2m
  annotations:
    summary: "API error rate {{ $value | humanizePercentage }} > 1%"
```

### 3.3 Alert Routing (PagerDuty Integration)

**Alert Routing Configuration**:

```yaml
# alertmanager-config.yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  routes:
    # Critical alerts → Immediate page
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      group_wait: 0s  # Don't wait
      repeat_interval: 1h
    
    # High alerts → Slack + PagerDuty
    - match:
        severity: high
      receiver: 'pagerduty-high'
      group_wait: 30s
      repeat_interval: 4h
    
    # Medium alerts → Slack only
    - match:
        severity: medium
      receiver: 'slack-alerts'
      group_wait: 5m
      repeat_interval: 24h

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY' <!-- pragma: allowlist secret -->
        severity: 'critical'
    slack_configs:
      - channel: '#prod-incidents'
        color: 'danger'

  - name: 'pagerduty-high'
    slack_configs:
      - channel: '#prod-alerts'
        color: 'warning'
    
  - name: 'slack-alerts'
    slack_configs:
      - channel: '#alerts'
        color: 'warning'
```

---

## Log Aggregation and Analysis

### 4.1 Elasticsearch Configuration

**Log Index Strategy**:

```bash
# Create daily indices for log rotation
# Index pattern: logs-application-YYYY.MM.DD
# Retention: 30 days hot, 90 days archived

# Mapping for optimal queries
PUT /logs-application-2024.01.15
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date",
        "format": "epoch_millis"
      },
      "level": {
        "type": "keyword"
      },
      "logger": {
        "type": "keyword"
      },
      "message": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "service": {
        "type": "keyword"
      },
      "pod_name": {
        "type": "keyword"
      },
      "request_id": {
        "type": "keyword"
      },
      "user_id": {
        "type": "keyword"
      },
      "duration_ms": {
        "type": "long"
      }
    }
  }
}
```

### 4.2 Log Analysis Patterns

**Common Log Queries**:

```bash
# Query 1: Find errors in last 5 minutes
GET logs-application-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "range": { "timestamp": { "gte": "now-5m" } } },
        { "term": { "level": "ERROR" } }
      ]
    }
  },
  "size": 100,
  "sort": [{"timestamp": {"order": "desc"}}]
}

# Query 2: Find slow requests
GET logs-application-*/_search
{
  "query": {
    "range": {
      "duration_ms": {
        "gte": 1000
      }
    }
  },
  "aggs": {
    "avg_duration": {
      "avg": {
        "field": "duration_ms"
      }
    }
  }
}

# Query 3: Find errors by service
GET logs-application-*/_search
{
  "query": {
    "term": {
      "level": "ERROR"
    }
  },
  "aggs": {
    "by_service": {
      "terms": {
        "field": "service",
        "size": 10
      }
    }
  }
}

# Query 4: Trace user activity
GET logs-application-*/_search
{
  "query": {
    "term": {
      "user_id": "USER_123"
    }
  },
  "sort": [{"timestamp": {"order": "asc"}}],
  "size": 1000
}
```

### 4.3 Log Retention Policies

**Retention Strategy**:

```bash
# Hot tier (Days 0-7): Full retention, fast queries
# Warm tier (Days 7-30): Rolled-over indices, slower queries
# Cold tier (Days 30-90): Archived to S3, minimal queries
# Deletion (Days > 90): Purge old logs

# ILM (Index Lifecycle Management) policy
PUT _ilm/policy/logs-policy
{
  "policy": "logs-policy",
  "phases": {
    "hot": {
      "min_age": "0d",
      "actions": {
        "rollover": {
          "max_primary_shard_size": "50GB",
          "max_age": "1d"
        }
      }
    },
    "warm": {
      "min_age": "7d",
      "actions": {
        "set_priority": {
          "priority": 50
        },
        "forcemerge": {
          "max_num_segments": 1
        },
        "shrink": {
          "number_of_shards": 1
        }
      }
    },
    "cold": {
      "min_age": "30d",
      "actions": {
        "set_priority": {
          "priority": 0
        }
      }
    },
    "delete": {
      "min_age": "90d",
      "actions": {
        "delete": {}
      }
    }
  }
}
```

---

## Health Check Procedures

### 5.1 Regular Health Checks

**Daily Health Check Checklist**:

```bash
#!/bin/bash
# daily-health-check.sh

# 1. Cluster health
echo "=== Cluster Health ==="
kubectl cluster-info
kubectl get nodes
echo ""

# 2. Pod health
echo "=== Pod Health ==="
kubectl get pods -n production --field-selector=status.phase!=Running
echo ""

# 3. API health
echo "=== API Health ==="
curl -s https://${API_ENDPOINT}/health | jq .
echo ""

# 4. Database health
echo "=== Database Health ==="
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT now() - pg_postmaster_start_time() AS uptime;"
echo ""

# 5. Cache health
echo "=== Cache Health ==="
redis-cli -h $REDIS_ENDPOINT PING
echo ""

# 6. Monitoring health
echo "=== Monitoring Health ==="
curl -s http://prometheus:9090/-/ready
echo ""

# 7. Alert count
echo "=== Active Alerts ==="
curl -s http://alertmanager:9093/api/v1/alerts | jq '.data | length'
echo ""
```

### 5.2 Synthetic Monitoring

**Uptime Monitoring**:

```yaml
# synth-test.yaml - Synthetic monitoring tests
tests:
  - name: "API health check"
    url: "https://${API_ENDPOINT}/health"
    method: GET
    interval: 60s
    timeout: 5s
    expected_status: 200
    
  - name: "Login endpoint"
    url: "https://${API_ENDPOINT}/auth/login"
    method: POST
    interval: 300s
    timeout: 10s
    body: '{"username":"monitor","password":"monitor"}' <!-- pragma: allowlist secret -->
    expected_status: 200
    
  - name: "Database connectivity"
    url: "https://${API_ENDPOINT}/health/db"
    method: GET
    interval: 120s
    timeout: 5s
    expected_status: 200
    
  - name: "Cache connectivity"
    url: "https://${API_ENDPOINT}/health/cache"
    method: GET
    interval: 120s
    timeout: 5s
    expected_status: 200
```

---

## Runbook: Emergency Response Using Monitoring

### 6.1 Alert Fired: API Error Rate High

**Decision Tree**:

```
Alert: APIHighErrorRate
  │
  ├─ Step 1: Check error rate in Grafana
  │   Query: rate(http_requests_total{status=~"5.."}[5m])
  │   │
  │   ├─ Error rate confirmed > 1%? YES → Continue
  │   └─ Error rate < 1%? → False positive, investigate alert rule
  │
  ├─ Step 2: Check error distribution
  │   Query: http_requests_total{status=~"5.."}
  │   Group by: handler (endpoint)
  │   │
  │   ├─ Single endpoint affected? → Issue with that service
  │   └─ All endpoints affected? → System-wide issue
  │
  ├─ Step 3: Check application logs
  │   Query: level:ERROR
  │   Filter: Last 5 minutes
  │   │
  │   ├─ Find common error pattern
  │   └─ Database connection error? → Check DB metrics
  │       Out of memory? → Check memory usage
  │       Timeout? → Check dependent services
  │
  ├─ Step 4: Check infrastructure
  │   ├─ Pod restarts? kubectl get pods -n production
  │   ├─ Resource constraints? kubectl top pods -n production
  │   └─ Network issues? kubectl get events -n production
  │
  └─ Step 5: Trigger incident if still unexplained
```

### 6.2 Alert Fired: Database Connection Pool Exhausted

**Diagnostic Procedure**:

```bash
# Step 1: Verify alert
curl 'http://prometheus:9090/api/v1/query?query=pg_stat_activity_count / pg_settings_max_connections'

# Step 2: Get connection details
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT pid, usename, state, query FROM pg_stat_activity LIMIT 50;"

# Step 3: Find idle connections
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction';"

# Step 4: Kill idle connections
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND query_start < now() - INTERVAL '30 minutes';"

# Step 5: Restart application connection pool
kubectl delete pod -n production -l app=codex-api

# Step 6: Monitor recovery
watch -n 5 'curl http://prometheus:9090/api/v1/query?query=pg_stat_activity_count'
```

---

## Dashboard Quick Reference

**Accessing Dashboards**:

```bash
# Grafana (local access)
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
# Access: http://localhost:3000
# Default: admin / admin

# Prometheus (local access)
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
# Access: http://localhost:9090

# Kibana (local access)
kubectl port-forward -n logging svc/kibana 5601:5601 &
# Access: http://localhost:5601
```

---

**Document Version**: 1.0  
**Last Reviewed**: 2024-01-15  
**Next Review Date**: 2024-02-15
