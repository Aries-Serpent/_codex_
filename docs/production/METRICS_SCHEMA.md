# Production Metrics Schema

**Last Updated:** 2026-06-22
**Version**: 1.0.0
**Status**: Ready for Implementation
**Date**: 2026-06-14

---

## 📊 Metrics Overview

This document defines all production metrics, their schema, collection methods, and retention policies.

---

## 🎯 Core Metrics

### 1. Request Latency

**Metric Name**: `http_request_duration_seconds`

**Description**: Time taken to process an HTTP request from receiving to sending response

**Type**: Histogram

**Dimensions**:
```yaml
dimensions:
  - method: "GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS"
  - route: "/api/users|/api/orders|etc"
  - status: "2xx|3xx|4xx|5xx"
  - service: "api-gateway|auth-service|user-service"
  - environment: "production|staging"
  - version: "1.2.3"
```

**Percentiles**:
```
p50 (median): 50th percentile
p75: 75th percentile
p90: 90th percentile
p95: 95th percentile
p99: 99th percentile
p99.9: 99.9th percentile
```

**Buckets** (in seconds):
```
[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
```

**Targets**:
```yaml
targets:
  p50: 50ms
  p95: 200ms
  p99: 1000ms
  p99.9: 2000ms
```

**Alerting Thresholds**:
```yaml
warnings:
  - p95_latency > 500ms for 5 minutes
  - p99_latency > 1500ms for 5 minutes

critical:
  - p99_latency > 2000ms for 5 minutes
  - p99_latency > 5000ms for 1 minute
```

**Collection Method**: Instrumented via OpenTelemetry middleware

**Example**:
```prometheus
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",route="/api/users",status="200",service="user-service",le="0.1"} 1024
http_request_duration_seconds_bucket{method="GET",route="/api/users",status="200",service="user-service",le="1"} 2048
http_request_duration_seconds_sum{method="GET",route="/api/users",status="200",service="user-service"} 256.5
http_request_duration_seconds_count{method="GET",route="/api/users",status="200",service="user-service"} 2500
```

---

## 2. Request Throughput

**Metric Name**: `http_requests_total`

**Description**: Total number of HTTP requests processed

**Type**: Counter

**Dimensions**:
```yaml
dimensions:
  - method: "GET|POST|PUT|DELETE|PATCH"
  - route: "/api/users|/api/orders"
  - status: "200|201|400|404|500"
  - service: "api-gateway|auth-service"
  - environment: "production"
```

**Unit**: Requests per second (calculated from rate)

**Targets**:
```yaml
targets:
  p50: 5000 req/s
  peak: 15000 req/s
```

**Alerting Thresholds**:
```yaml
warnings:
  - throughput increase >50% over 5 minutes (potential attack)
  - throughput decrease >30% for 5 minutes (potential issue)

critical:
  - throughput drops to <100 req/s from >1000 req/s
```

**Collection Method**: Automatic via Prometheus counter

**Example**:
```prometheus
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/api/users",status="200",service="user-service"} 1000000
```

---

## 3. Error Rate

**Metric Name**: `http_requests_errors_total`

**Description**: Total number of failed requests (4xx, 5xx)

**Type**: Counter

**Dimensions**:
```yaml
dimensions:
  - method: "GET|POST|PUT|DELETE"
  - route: "/api/users|/api/orders"
  - status: "400|401|403|404|500|502|503"
  - error_type: "validation|authentication|authorization|not_found|timeout|server_error"
  - service: "api-gateway|user-service"
```

**Derived Metric**: Error Rate = errors_total / requests_total

**Targets**:
```yaml
targets:
  baseline: <0.1%
  warning: 0.1%-0.5%
  critical: >0.5%
  spike_tolerance: <1% for <1 minute
```

**Alerting Thresholds**:
```yaml
warnings:
  - error_rate > 0.5% for 5 minutes

critical:
  - error_rate > 1% for 5 minutes
  - error_rate > 5% for 1 minute
  - HTTP 500 errors > 100 in 1 minute
```

**Collection Method**: Automatic via Prometheus counter

**Example**:
```prometheus
http_requests_errors_total{method="POST",route="/api/orders",status="500",service="order-service"} 150
```

---

### 4. Database Metrics

**Metric Names**:
```
database_connection_pool_current
database_connection_pool_max
database_query_duration_seconds
database_query_errors_total
database_connection_errors_total
```

**Pool Utilization** (calculated):
```
pool_utilization = current_connections / max_connections
```

**Targets**:
```yaml
targets:
  pool_utilization: <60%
  warning: >75%
  critical: >90%

query_latency_p95: <50ms
query_latency_p99: <200ms
```

**Alerting Thresholds**:
```yaml
warnings:
  - pool_utilization > 75% for 5 minutes
  - query_latency_p99 > 500ms for 5 minutes

critical:
  - pool_utilization > 90%
  - query_latency_p99 > 1000ms for 5 minutes
  - connection_errors > 10 in 1 minute
```

**Example**:
```prometheus
database_connection_pool_current{service="user-service",database="postgres"} 45
database_connection_pool_max{service="user-service",database="postgres"} 100
database_query_duration_seconds_bucket{query_type="select",service="user-service",le="0.05"} 1024
```

---

### 5. Cache Metrics

**Metric Names**:
```
cache_hits_total
cache_misses_total
cache_evictions_total
cache_memory_bytes
cache_operation_duration_seconds
```

**Hit Ratio** (calculated):
```
hit_ratio = hits / (hits + misses)
```

**Targets**:
```yaml
targets:
  hit_ratio: >85%
  warning: <80%
  critical: <60%

operation_latency_p95: <5ms
operation_latency_p99: <20ms
```

**Alerting Thresholds**:
```yaml
warnings:
  - hit_ratio < 80% for 10 minutes
  - operation_latency_p99 > 50ms for 10 minutes

critical:
  - hit_ratio < 60% for 5 minutes
  - operation_latency_p99 > 100ms for 5 minutes
```

**Example**:
```prometheus
cache_hits_total{service="user-service",cache_type="redis"} 500000
cache_misses_total{service="user-service",cache_type="redis"} 50000
cache_memory_bytes{service="user-service",cache_type="redis"} 536870912
```

---

### 6. Resource Utilization

**CPU Metrics**:
```
container_cpu_usage_seconds_total
container_cpu_throttle_seconds_total
process_cpu_seconds_total
```

**Memory Metrics**:
```
container_memory_usage_bytes
container_memory_max_usage_bytes
container_memory_working_set_bytes
process_resident_memory_bytes
```

**Disk Metrics**:
```
node_disk_read_bytes_total  # pragma: allowlist secret
node_disk_write_bytes_total  # pragma: allowlist secret
node_filesystem_avail_bytes
node_filesystem_size_bytes
```

**Network Metrics**:
```
container_network_receive_bytes_total
container_network_transmit_bytes_total
container_network_receive_errors_total
container_network_transmit_errors_total
```

**Targets**:
```yaml
targets:
  cpu_utilization: <70%
  memory_utilization: <75%
  disk_utilization: <80%

warnings:
  cpu: >80%
  memory: >85%
  disk: >85%

critical:
  cpu: >95%
  memory: >95%
  disk: >90%
```

**Alerting Thresholds**:
```yaml
warnings:
  - cpu_utilization > 80% for 5 minutes
  - memory_utilization > 85% for 5 minutes
  - disk_utilization > 85% for 30 minutes

critical:
  - cpu_utilization > 95% for 1 minute
  - memory_utilization > 95%
  - disk_utilization > 90% for 5 minutes
```

**Example**:
```prometheus
container_cpu_usage_seconds_total{pod="user-service-pod-1",namespace="production"} 1234.56
container_memory_usage_bytes{pod="user-service-pod-1",namespace="production"} 2147483648
node_disk_read_bytes_total{device="sda1"} 1099511627776
```

---

### 7. Message Queue Metrics

**Metric Names**:
```
kafka_consumer_lag_sum
kafka_messages_in_per_sec
kafka_messages_out_per_sec
kafka_messages_in_rate_per_sec
kafka_messages_out_rate_per_sec
```

**Consumer Lag** (calculated):
```
lag = latest_offset - consumer_offset
```

**Targets**:
```yaml
targets:
  consumer_lag: <10s
  warning: >30s
  critical: >60s

throughput: >1000 msg/s
```

**Alerting Thresholds**:
```yaml
warnings:
  - consumer_lag > 30s for 5 minutes
  - message_throughput < 500 msg/s for 10 minutes

critical:
  - consumer_lag > 60s for 5 minutes
  - consumer_lag > 300s for 1 minute
```

**Example**:
```prometheus
kafka_consumer_lag_sum{group="order-processing",topic="orders",namespace="production"} 1000
kafka_messages_in_per_sec{topic="orders",namespace="production"} 5000
```

---

### 8. Business Metrics

**Order Metrics**:
```
orders_created_total
orders_completed_total
orders_failed_total
order_processing_duration_seconds
order_value_sum
```

**User Metrics**:
```
users_registered_total
users_active_today
users_session_duration_seconds
```

**Conversion Metrics**:
```
conversion_rate
cart_abandonment_rate
checkout_completion_rate
```

**Example**:
```prometheus
orders_created_total{region="us-west",product_category="electronics"} 10000
order_processing_duration_seconds_bucket{le="5"} 8000
```

---

## 📈 Metrics Collection Pipeline

**Architecture**:
```
Application Instrumentation (OpenTelemetry SDK)
  ↓
Metrics Exporter (Prometheus endpoint)
  ↓
Prometheus Scraper (every 15s)
  ↓
Time Series Database (Prometheus/VictoriaMetrics)
  ↓
Visualization (Grafana)
  ↓
Alerting Engine (Prometheus AlertManager)
```

**Scrape Configuration**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "production"
    static_configs:
      - targets: ["api-gateway:8080", "user-service:8080", "order-service:8080"]
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: "/metrics"
```

---

## 🗄️ Data Retention

| Granularity | Retention | Storage | Notes |
|-------------|-----------|---------|-------|
| **1-second** | 1 hour | Prometheus (RAM) | Raw data for debugging |
| **1-minute** | 7 days | Prometheus | Average, max, min, p95, p99 |
| **5-minute** | 30 days | Prometheus | Same aggregations |
| **1-hour** | 1 year | Long-term storage (S3) | Yearly trends |
| **1-day** | 5 years | Archive (Glacier) | Historical reference |

**Retention Configuration**:
```yaml
prometheus:
  retention:
    time: 15d  # Keep 15 days in hot storage
    size: 10GB  # Or 10GB, whichever comes first
  
  remote_storage:
    enabled: true
    url: "s3://bucket/prometheus"
    retention: 1y
```

---

## 🧪 Metrics Validation

### Sanity Checks

```python
# 1. All required dimensions present
assert set(metric_dims.keys()) >= required_dims

# 2. Metric values are valid
assert metric_value >= 0 or metric_value is None
assert latency_ms >= 0
assert cpu_percent <= 100

# 3. Cardinality within limits
assert cardinality < MAX_CARDINALITY  # Prevents explosion

# 4. No stale metrics
assert (now - metric_timestamp) < 5 * scrape_interval
```

## Sample Validation Query

```promql
# Check for metrics older than 2 scrape intervals
absent(up) > 120  # Alert if no metrics for 2+ minutes
```

---

## 📊 Dashboard Metrics

**Primary Production Dashboard** includes:

```yaml
panels:
  - "HTTP Request Latency (p50, p95, p99)"
  - "Request Throughput (req/s)"
  - "Error Rate (%)"
  - "Database Pool Utilization (%)"
  - "Cache Hit Ratio (%)"
  - "Consumer Lag (seconds)"
  - "CPU Utilization (%)"
  - "Memory Utilization (%)"
  - "Disk Utilization (%)"
  - "Active Alerts"
  - "SLA Compliance"
```

---

## 🚀 Deployment Checklist

- [ ] OpenTelemetry SDK integrated in all services
- [ ] Prometheus scrape endpoints configured
- [ ] Metrics collection tested (verify data appearing in Prometheus)
- [ ] Alerting rules configured
- [ ] Alert thresholds tuned based on baselines
- [ ] Dashboard created with all key metrics
- [ ] Retention policies enforced
- [ ] Long-term storage configured
- [ ] Grafana plugins installed (if needed)
- [ ] On-call team trained on metric interpretation
- [ ] Runbooks prepared for common scenarios

---

**Last Updated**: 2026-06-14 | **Next Review**: 2026-07-14 | **Owned by**: Platform Engineering
