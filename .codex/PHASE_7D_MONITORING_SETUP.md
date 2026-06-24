# Production Observability: Monitoring Infrastructure Setup Guide

**Phase**: 7D (Pre-v0.1.0-final)  
**Authority**: @mbaetiong (D-level autonomy)  
**Status**: Production-Ready Implementation Guide  
**Last Updated**: 2026-06-20  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Dashboard Templates](#grafana-dashboard-templates)
5. [Centralized Logging (ELK Alternative)](#centralized-logging)
6. [Metrics Export Configuration](#metrics-export-configuration)
7. [Cost Estimation](#cost-estimation)
8. [Troubleshooting & Support](#troubleshooting--support)

---

## Executive Summary

This guide provides step-by-step instructions for deploying a production-grade observability stack for v0.1.0-final. The recommended stack consists of:

- **Metrics**: Prometheus + Grafana (time-series monitoring)
- **Logs**: Loki + Promtail OR ELK Stack (log aggregation)
- **Distributed Tracing**: Jaeger (optional, for complex flows)
- **APM**: Elastic APM (optional, advanced scenario)

**Deployment Models**:
- **Option A** (Recommended): Docker Compose on existing VM/EC2
- **Option B**: Kubernetes (Helm charts)
- **Option C**: Managed Services (Datadog, New Relic, AWS CloudWatch)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Application: v0.1.0-final                                   │
│ ├─ Prometheus exporter (port 9090)                          │
│ ├─ Structured logs (JSON to stdout)                         │
│ └─ Health endpoint (/health)                                │
└──────────┬──────────────────────────────────────────────────┘
           │
    ┌──────┴─────────────┬──────────────────────┐
    │                    │                      │
┌───▼────┐          ┌────▼─────┐          ┌────▼─────┐
│ Prom.  │          │ Promtail  │          │ App Logs │
│ scrape │          │  (Loki)   │          │(JSON)    │
└───┬────┘          └────┬─────┘          └────┬─────┘
    │                    │                      │
    │ metrics            │ indexed logs         │ raw logs
    │                    │                      │
┌───▼────────────────────▼──────────────────────▼───┐
│ Observability Backend (Docker Compose)            │
├───────────────────────────────────────────────────┤
│ • Prometheus (15GB storage, 2 CPU)                │
│ • Grafana (dashboards, alerting)                  │
│ • Loki (log aggregation, 10GB)                    │
│ • Alertmanager (alert routing)                    │
│ • Redis (metrics cache, optional)                 │
└───┬──────────────────────────────────────┬────────┘
    │                                      │
    └──────────────────┬───────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼──────┐             ┌────────▼─────┐
   │ Slack/PD  │             │ On-Call Team  │
   │(Alerts)   │             │(Paging)       │
   └───────────┘             └───────────────┘
```

---

## Prometheus Setup

### Step 1: Install Prometheus

#### Option A: Docker (Recommended)

```bash
# Create directories
mkdir -p /opt/monitoring/{prometheus,grafana,loki,alertmanager}
cd /opt/monitoring

# Download latest Prometheus Docker image
docker pull prom/prometheus:latest

# Create config directory
mkdir -p /opt/monitoring/prometheus/config
```

#### Option B: Binary Installation (Linux)

```bash
# Download latest release
PROM_VERSION="2.45.0"
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz
tar xvfz prometheus-${PROM_VERSION}.linux-amd64.tar.gz
sudo mv prometheus-${PROM_VERSION}.linux-amd64 /opt/prometheus
```

### Step 2: Create Prometheus Configuration

Create `/opt/monitoring/prometheus/config/prometheus.yml`:

```yaml
# Global settings
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'
    service: 'codex-ml'
    version: '0.1.0-final'

# Alert rules file
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'
      path_prefix: '/'

# Scrape configs
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:9090']

  # Application metrics (codex-ml)
  - job_name: 'codex-ml'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['app:9090']
    scrape_interval: 10s
    scrape_timeout: 5s
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [__scheme__]
        target_label: scheme

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    metric_path: '/metrics'
    scrape_interval: 30s

  # Docker metrics (if using Docker)
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
    scrape_interval: 30s

  # Kubernetes metrics (if applicable)
  - job_name: 'kubernetes-nodes'
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    static_configs:
      - targets: ['kubernetes.default.svc:443']

# Service discovery (optional - for dynamic environments)
  - job_name: 'docker-swarm'
    dockersd_configs:
      - host: unix:///var/run/docker.sock

# Remote storage (optional - for long-term retention)
# remote_write:
#   - url: "http://remote-storage:9009/api/v1/write"
#     write_relabel_configs:
#       - source_labels: [__name__]
#         regex: 'go_.*|process_.*'
#         action: drop
```

### Step 3: Configure Data Retention

```bash
# Edit prometheus systemd service or docker command:
# For Docker:
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /opt/monitoring/prometheus/config:/etc/prometheus \
  -v /opt/monitoring/prometheus/data:/prometheus \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --storage.tsdb.retention.time=15d \
  --storage.tsdb.retention.size=15GB \
  --query.max-samples=1000000 \
  --query.timeout=2m
```

**Retention Strategy**:
- Development: 7 days
- Staging: 14 days
- Production: 30 days (or with remote storage)

### Step 4: Set up Prometheus Storage

#### Local Storage (Single Node)
```bash
# On host machine
mkdir -p /var/lib/prometheus
sudo chown -R 65534:65534 /var/lib/prometheus
sudo chmod -R 755 /var/lib/prometheus

# Check disk capacity
df -h /var/lib/prometheus
# Recommended: 50GB for 30-day retention
```

#### Remote Storage (High Availability)
```bash
# Option 1: Thanos (long-term retention)
# Option 2: AWS S3 + Thanos sidecar
# Option 3: InfluxDB long-term storage

# Example: Thanos sidecar configuration
# Add to docker-compose.yml
thanos-sidecar:
  image: quay.io/thanos/thanos:latest
  volumes:
    - /opt/monitoring/prometheus/data:/prometheus
  command:
      - 'sidecar'
      - '--tsdb.path=/prometheus'
      - '--prometheus.url=http://prometheus:9090'
      - '--objstore.config-file=/etc/thanos/objstore.yml'
```

### Step 5: Verify Prometheus Setup

```bash
# Access Prometheus UI
curl http://localhost:9090

# Check targets
curl http://localhost:9090/api/v1/targets

# Check query capability
curl 'http://localhost:9090/api/v1/query?query=up'

# Check alert rules
curl http://localhost:9090/api/v1/rules
```

**Expected Response**:
```json
{
  "status": "success",
  "data": {
    "activeAlerts": 0,
    "groups": []
  }
}
```

---

## Grafana Dashboard Templates

### Step 1: Install Grafana

```bash
# Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -v grafana-storage:/var/lib/grafana \
  -v /opt/monitoring/grafana/provisioning:/etc/grafana/provisioning \
  grafana/grafana:latest

# Access at http://localhost:3000 (admin/admin)
```

### Step 2: Add Prometheus Data Source

Create `/opt/monitoring/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: 15s

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    editable: true
```

### Step 3: Create Dashboard Templates

#### Dashboard 1: System Health Overview

Create `/opt/monitoring/grafana/dashboards/01-system-health.json`:

```json
{
  "dashboard": {
    "title": "System Health Overview",
    "tags": ["production", "health"],
    "timezone": "browser",
    "panels": [
      {
        "title": "CPU Usage %",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m]) * 100",
            "legendFormat": "CPU Usage"
          }
        ],
        "alert": {
          "name": "High CPU Usage",
          "conditions": [
            {
              "evaluator": { "params": [80], "type": "gt" },
              "query": { "params": ["A", "5m", "now"] }
            }
          ],
          "frequency": "60s"
        }
      },
      {
        "title": "Memory Usage (MB)",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "Memory MB"
          }
        ]
      },
      {
        "title": "Disk Usage %",
        "targets": [
          {
            "expr": "(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100",
            "legendFormat": "{{ device }}"
          }
        ]
      },
      {
        "title": "Network I/O (bytes/sec)",
        "targets": [
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "TX {{ device }}"
          },
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "RX {{ device }}"
          }
        ]
      }
    ]
  }
}
```

#### Dashboard 2: Application Performance

Create `/opt/monitoring/grafana/dashboards/02-app-performance.json`:

```json
{
  "dashboard": {
    "title": "Application Performance",
    "tags": ["production", "app"],
    "panels": [
      {
        "title": "Request Rate (req/sec)",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ path }}"
          }
        ]
      },
      {
        "title": "Request Latency (p95, p99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "Error Rate %",
        "targets": [
          {
            "expr": "(rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])) * 100",
            "legendFormat": "Error Rate"
          }
        ],
        "alert": {
          "name": "High Error Rate",
          "conditions": [
            {
              "evaluator": { "params": [5], "type": "gt" }
            }
          ]
        }
      },
      {
        "title": "Active Connections",
        "targets": [
          {
            "expr": "process_open_fds",
            "legendFormat": "Open FDs"
          }
        ]
      },
      {
        "title": "Goroutines",
        "targets": [
          {
            "expr": "runtime_goroutines",
            "legendFormat": "Goroutines"
          }
        ]
      }
    ]
  }
}
```

#### Dashboard 3: Error Tracking & Logs

Create `/opt/monitoring/grafana/dashboards/03-errors-logs.json`:

```json
{
  "dashboard": {
    "title": "Errors & Logs",
    "tags": ["production", "errors"],
    "panels": [
      {
        "title": "Error Rate by Type",
        "targets": [
          {
            "expr": "rate(errors_total[5m])",
            "legendFormat": "{{ error_type }}"
          }
        ]
      },
      {
        "title": "Top Errors (last 1h)",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, increase(errors_total[1h]))",
            "format": "table"
          }
        ]
      },
      {
        "title": "Exception Rate",
        "targets": [
          {
            "expr": "rate(exceptions_total[5m])",
            "legendFormat": "{{ exception_type }}"
          }
        ]
      },
      {
        "title": "Recent Error Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{level=\"error\"}",
            "refId": "A"
          }
        ]
      }
    ]
  }
}
```

#### Dashboard 4: SLA & Availability

Create `/opt/monitoring/grafana/dashboards/04-sla-availability.json`:

```json
{
  "dashboard": {
    "title": "SLA & Availability",
    "tags": ["production", "sla"],
    "panels": [
      {
        "title": "Uptime %",
        "targets": [
          {
            "expr": "(count(up{job=\"codex-ml\"} == 1) / count(up{job=\"codex-ml\"})) * 100",
            "legendFormat": "Uptime"
          }
        ]
      },
      {
        "title": "SLA Compliance",
        "targets": [
          {
            "expr": "((1 - (rate(http_requests_total{status=~\"5..\"}[30m]) / rate(http_requests_total[30m]))) * 100)",
            "legendFormat": "SLA %"
          }
        ]
      },
      {
        "title": "MTTR - Mean Time to Recovery",
        "targets": [
          {
            "expr": "avg(rate(incidents_mttr_seconds[30m]))",
            "legendFormat": "MTTR"
          }
        ]
      },
      {
        "title": "Deployment Frequency",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(deployments_total[30d])",
            "legendFormat": "Deploys/Month"
          }
        ]
      }
    ]
  }
}
```

### Step 4: Import Dashboards

```bash
# Add to grafana provisioning
mkdir -p /opt/monitoring/grafana/provisioning/dashboards

# Create dashboard provider
cat > /opt/monitoring/grafana/provisioning/dashboards/dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Main Dashboards'
    orgId: 1
    folder: 'Production'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Copy dashboards to provisioning directory
cp /opt/monitoring/grafana/dashboards/*.json \
   /opt/monitoring/grafana/provisioning/dashboards/
```

---

## Centralized Logging

### Option A: Loki Stack (Recommended - Lightweight)

```bash
# 1. Install Promtail on application server
mkdir -p /opt/promtail/config

# 2. Create Promtail config
cat > /opt/promtail/config/promtail-config.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: app-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: codex-ml
          environment: production
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            service: service
      - timestamp:
          source: timestamp
          format: Unix
      - labels:
          level:
          service:

  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
    pipeline_stages:
      - regex:
          expression: '(?P<timestamp>\S+) (?P<level>\w+) (?P<message>.+)'
EOF

# 3. Run Promtail
docker run -d \
  --name promtail \
  -v /opt/promtail/config:/etc/promtail \
  -v /var/log:/var/log \
  grafana/promtail:latest \
  -config.file=/etc/promtail/promtail-config.yml
```

### Option B: ELK Stack (Advanced - Full-Featured)

```bash
# 1. Docker Compose ELK setup
cat > /opt/monitoring/docker-compose-elk.yml << 'EOF'
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    mem_limit: 2g

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    ports:
      - "5000:5000/udp"
    volumes:
      - /opt/monitoring/logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch
    environment:
      - "ES_HOSTS=elasticsearch:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
EOF

# 2. Create Logstash pipeline
mkdir -p /opt/monitoring/logstash/pipeline
cat > /opt/monitoring/logstash/pipeline/logstash.conf << 'EOF'
input {
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  date {
    match => ["timestamp", "UNIX_MS"]
    target => "@timestamp"
  }

  if [level] == "error" or [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "codex-ml-%{+YYYY.MM.dd}"
  }
}
EOF

# 3. Launch ELK
docker-compose -f /opt/monitoring/docker-compose-elk.yml up -d
```

### Step: Configure Log Shipping from Application

Update application to emit structured logs:

```python
import json
import logging
from datetime import datetime

class StructuredLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'service': 'codex-ml',
            'version': '0.1.0-final'
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(StructuredLogFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## Metrics Export Configuration

### Step 1: Expose Prometheus Metrics from Application

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

active_requests = Gauge(
    'http_requests_active',
    'Active HTTP requests'
)

error_count = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'severity']
)

# Start metrics server
if __name__ == '__main__':
    start_http_server(9090)  # Expose on :9090/metrics
```

### Step 2: Configure Custom Metrics

```yaml
# Custom metrics for v0.1.0-final
custom_metrics:
  # Model-specific metrics
  - model_inference_latency_ms
  - model_inference_throughput_req_sec
  - model_accuracy_percent
  - model_drift_score

  # Data pipeline metrics
  - data_ingestion_rate_records_sec
  - data_processing_latency_ms
  - data_validation_errors_total

  # Business metrics
  - predictions_generated_total
  - prediction_confidence_avg
  - user_satisfaction_score

  # Infrastructure metrics
  - database_query_latency_ms
  - cache_hit_ratio_percent
  - api_rate_limit_remaining
```

### Step 3: Set Up Custom Exporters

```bash
# Example: Custom application exporter
cat > /opt/monitoring/exporters/app-exporter.py << 'EOF'
#!/usr/bin/env python3
from prometheus_client import start_http_server, Counter, Gauge
import requests
import time

# Custom gauges
model_latency = Gauge('codex_model_inference_latency_ms', 'Model inference latency')
throughput = Gauge('codex_model_throughput_req_sec', 'Model throughput')

def collect_metrics():
    while True:
        try:
            # Query application API
            resp = requests.get('http://app:8000/metrics/custom')
            data = resp.json()

            model_latency.set(data.get('inference_latency_ms', 0))
            throughput.set(data.get('throughput_req_sec', 0))

        except Exception as e:
            print(f"Error collecting metrics: {e}")

        time.sleep(10)

if __name__ == '__main__':
    start_http_server(9091)
    collect_metrics()
EOF

chmod +x /opt/monitoring/exporters/app-exporter.py
```

---

## Cost Estimation

### Infrastructure Costs (Monthly)

#### Option A: Docker Compose on EC2

| Component | Size | Cost/Month | Details |
|-----------|------|-----------|---------|
| EC2 Instance | t3.large | $50 | 2 CPU, 8GB RAM |
| EBS Storage | 100GB | $10 | Prometheus + logs |
| Data Transfer | 10GB out | $0.90 | Metric egress |
| **Total** | | **$60.90** | Single-region |

#### Option B: Kubernetes (EKS)

| Component | Size | Cost/Month | Details |
|-----------|------|-----------|---------|
| EKS Cluster | 3 nodes t3.large | $150 | Master + workers |
| EBS Storage | 100GB | $10 | Persistent volumes |
| ALB | 1 | $15 | Load balancer |
| Data Transfer | 20GB out | $1.80 | Cross-AZ traffic |
| **Total** | | **$176.80** | HA setup |

#### Option C: Managed Services

| Service | Tier | Cost/Month | Notes |
|---------|------|-----------|-------|
| Datadog | Pro | $500+ | Full stack, includes logs |
| New Relic | Standard | $300+ | APM + logs |
| AWS CloudWatch | Standard | $200-400 | Logs + metrics |
| Grafana Cloud | Pro | $150+ | Just dashboards |

#### Option D: Hybrid (Recommended for v0.1.0)

| Component | Cost/Month |
|-----------|-----------|
| Docker Compose Instance | $60 |
| Grafana Cloud (dashboards) | $50 |
| Datadog (APM, 7-day logs) | $300 |
| **Total** | **$410** |

### Optimization Strategies

```yaml
Cost Optimization:
  Retention:
    - Metrics: 15 days local → 30d remote storage
    - Logs: 7 days hot → 30d archived
    - Traces: 24 hours default

  Sampling:
    - Trace sampling: 10% for low-value operations
    - Log sampling: 100% for errors, 10% for info
    - Metric cardinality: Limit to <100k time series

  Instance Sizing:
    - Dev: t3.micro ($10/mo)
    - Staging: t3.small ($20/mo)
    - Production: t3.large ($50/mo)

  Reserved Capacity:
    - Commit to 1-year: 33% discount
    - Commit to 3-year: 55% discount
```

---

## Troubleshooting & Support

### Common Issues

#### Issue: Prometheus memory consumption high

```bash
# Check current memory
curl http://localhost:9090/api/v1/query?query=process_resident_memory_bytes

# Reduce cardinality
# 1. Drop high-cardinality labels
# 2. Reduce scrape frequency
# 3. Enable compression
```

#### Issue: Disk space exhausted

```bash
# Check disk usage
df -h /var/lib/prometheus

# Solutions:
# 1. Reduce retention: --storage.tsdb.retention.time=7d
# 2. Enable compression: --storage.tsdb.compress-wal=true
# 3. Add remote storage: AWS S3, Thanos
```

#### Issue: Grafana dashboards slow

```bash
# Solutions:
# 1. Reduce query time range
# 2. Increase Prometheus query.timeout
# 3. Add Redis cache
# 4. Use recording rules for expensive queries
```

### Support Contacts

- **Prometheus Docs**: https://prometheus.io/docs
- **Grafana Docs**: https://grafana.com/docs
- **Community Slack**: #monitoring in codex-ml workspace
- **On-Call**: See PHASE_7D_INCIDENT_RESPONSE.md

### Validation Checklist

- [ ] Prometheus scraping all targets
- [ ] Grafana dashboards loading in <2s
- [ ] Logs appearing in Loki/ELK within 30s
- [ ] Alerts firing correctly
- [ ] Disk usage <80% capacity
- [ ] Memory usage <75% capacity
- [ ] Query latency <500ms p95
- [ ] No data loss over 24h period

---

**Next Steps:**
1. Review PHASE_7D_ALERTING_SETUP.md (alert rules & incidents)
2. Review PHASE_7D_HEALTH_CHECK_PROCEDURES.md (validation steps)
3. Schedule deployment review meeting
4. Assign on-call rotations (see PHASE_7D_INCIDENT_RESPONSE.md)
