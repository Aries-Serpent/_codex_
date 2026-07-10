# RUNBOOK: Monitoring & Alerting Configuration

**Version:** 1.0.0  
**Last Updated:** 2026-07-10  
**Audience:** DevOps, SRE  

---

## Table of Contents

1. [Prometheus Configuration](#prometheus-configuration)
2. [Key Metrics](#key-metrics)
3. [Alerting Rules](#alerting-rules)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Health Check Procedures](#health-check-procedures)

---

## Prometheus Configuration

### Setup

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'codex-prod'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'codex-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s

  - job_name: 'codex-worker'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 15s

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 30s
```

### Docker Compose

```yaml
version: "3"
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/config.yml

volumes:
  prometheus_data:
  grafana_data:
```

---

## Key Metrics

### API Metrics

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (% of requests that are 5xx)
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100

# Latency p50
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))

# Latency p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Latency p99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### System Metrics

```promql
# CPU usage (%)
(1 - rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# Memory usage (%)
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage (%)
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100

# Disk I/O (writes per second)
rate(node_disk_writes_completed_total[5m])
```

### Database Metrics

```promql
# Active connections
pg_stat_activity_count

# Slow queries (>1s)
rate(pg_slow_queries_total[5m])

# Cache hit ratio (%)
rate(pg_stat_database_blks_hit_total[5m]) / (rate(pg_stat_database_blks_hit_total[5m]) + rate(pg_stat_database_blks_read_total[5m])) * 100
```

---

## Alerting Rules

### Create `/etc/prometheus/rules/codex.yml`

```yaml
groups:
  - name: codex_alerts
    interval: 30s
    rules:
      # P1: API Down
      - alert: APIDown
        expr: up{job="codex-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API is down"
          description: "Codex API has been down for 1 minute"

      # P1: High Error Rate
      - alert: HighErrorRate
        expr: |
          (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) > 0.10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate >10%"
          description: "{{ $value | humanizePercentage }} errors in last 5m"

      # P2: High Latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency >2s"
          description: "P95 latency: {{ $value | humanize }}s"

      # P2: Memory Pressure
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage >85%"
          description: "{{ $value | humanizePercentage }} memory in use"

      # P2: Disk Pressure
      - alert: HighDiskUsage
        expr: |
          (node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk usage >85%"
          description: "{{ $value | humanizePercentage }} disk used"

      # P3: Database Slow Queries
      - alert: SlowQueries
        expr: rate(pg_slow_queries_total[5m]) > 5
        for: 15m
        labels:
          severity: info
        annotations:
          summary: "High rate of slow queries"
          description: "{{ $value | humanize }} slow queries per second"

      # P3: Low Cache Hit Ratio
      - alert: LowCacheHitRatio
        expr: |
          (rate(pg_stat_database_blks_hit_total[5m]) / 
           (rate(pg_stat_database_blks_hit_total[5m]) + rate(pg_stat_database_blks_read_total[5m]))) < 0.90
        for: 30m
        labels:
          severity: info
        annotations:
          summary: "Database cache hit ratio <90%"
          description: "Cache hit ratio: {{ $value | humanizePercentage }}"
```

---

## Grafana Dashboards

### Create Dashboard "Codex Platform Overview"

```json
{
  "dashboard": {
    "title": "Codex Platform Overview",
    "panels": [
      {
        "title": "API Request Rate (req/s)",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{path}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "title": "Error Rate (%)",
        "targets": [
          {
            "expr": "(rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])) * 100"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "thresholds": [
          {"value": 1, "color": "yellow"},
          {"value": 5, "color": "red"}
        ]
      },
      {
        "title": "Latency Distribution",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
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
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "title": "Resource Usage",
        "targets": [
          {
            "expr": "(1 - rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100",
            "legendFormat": "CPU %"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ]
  }
}
```

---

## Health Check Procedures

### Daily Health Check

```bash
#!/bin/bash
# run_daily_health_check.sh

echo "=== Daily Health Check ==="
echo "Time: $(date)"

# 1. API Health
echo -n "API Health: "
curl -s http://localhost:8000/health | jq .

# 2. Database Health
echo -n "Database Connection: "
python -c "
import sqlite3
try:
    conn = sqlite3.connect('/var/lib/codex/codex.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM models')
    count = cursor.fetchone()[0]
    print(f'✓ {count} models')
except Exception as e:
    print(f'✗ {e}')
"

# 3. Metrics Available
echo -n "Prometheus Metrics: "
curl -s http://localhost:9090/api/v1/series | jq '.data | length'

# 4. Alert Rules
echo -n "Active Alerts: "
curl -s http://localhost:9093/api/v1/alerts | jq '.data | length'

# 5. Disk Space
echo -n "Disk Usage: "
df -h / | tail -1 | awk '{print $5}'

# 6. Memory Usage
echo -n "Memory Usage: "
free -h | grep Mem | awk '{print $3 "/" $2}'

echo "=== Health Check Complete ==="
```

**Run daily at 9 AM:**

```bash
# Add to crontab
0 9 * * * /opt/codex/run_daily_health_check.sh >> /var/log/codex/health_check.log
```

---

**Maintained by:** @mbaetiong  
**Last reviewed:** 2026-07-10
