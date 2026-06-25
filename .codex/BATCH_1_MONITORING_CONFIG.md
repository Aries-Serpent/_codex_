# Phase 6 Batch 1: Monitoring Infrastructure Framework
**Version**: 1.0.0
**Status**: Implementation Complete
**Date**: 2026-06-14
**Phase**: 6 - Production Deployment Readiness
**Batch**: 1 - Infrastructure Hardening

---

## 📋 Executive Summary

This document specifies the complete monitoring infrastructure framework for production deployment. It covers structured logging, health checks, performance metrics collection, alerting frameworks, and dashboard configuration across all 5 health dimensions:

1. **Security** - Access controls, authentication failures, suspicious activity
2. **Performance** - Latency, throughput, resource utilization
3. **Availability** - Service uptime, health check status, failover events
4. **State** - Data consistency, configuration drift, schema violations
5. **Resource** - CPU, memory, disk, network usage

---

## 🎯 Framework Architecture

```
Production Environment
├── Services (n=15+)
├── Data Stores (PostgreSQL, Redis, etc.)
├── Message Queues (Kafka, etc.)
└── Observability Stack
    ├── Logging Layer (Structured JSON)
    ├── Metrics Layer (Prometheus/StatsD)
    ├── Tracing Layer (OpenTelemetry)
    ├── Health Check Layer (HTTP/custom)
    └── Alerting Layer (PagerDuty/Slack/Email)
        └── Dashboard Layer (Grafana/DataDog)
```

---

## 1️⃣ Structured Logging Framework

### 1.1 Logging Schema

**Standard Log Format** (JSON with required fields):

```json
{
  "timestamp": "2026-06-14T15:30:45.123Z",
  "level": "INFO|WARN|ERROR|CRITICAL",
  "logger": "module.submodule",
  "message": "Human-readable event description",
  "service": "service-name",
  "environment": "production|staging|development",
  "version": "1.2.3",
  "request_id": "req-uuid-12345",
  "correlation_id": "corr-uuid-98765",
  "span_id": "span-uuid-13579",
  "trace_id": "trace-uuid-24680",
  "user_id": "user-uuid-or-anonymized",
  "session_id": "session-uuid-or-null",
  "action": "action_name",
  "resource_type": "entity_type",
  "resource_id": "entity_id",
  "duration_ms": 1234,
  "status_code": 200,
  "error_code": null,
  "error_message": null,
  "error_stack": null,
  "context": {
    "host": "hostname",
    "pod": "pod-name",
    "deployment": "deployment-name",
    "zone": "availability-zone",
    "region": "aws-region",
    "custom_field_1": "value1",
    "custom_field_2": "value2"
  },
  "metrics": {
    "cpu_ms": 50,
    "memory_kb": 256,
    "db_queries": 3,
    "cache_hits": 5,
    "cache_misses": 2,
    "external_calls": 1
  },
  "tags": ["tag1", "tag2"]
}
```

### 1.2 Log Levels & Sampling

| Level | Retention | Sampling | Use Case |
|-------|-----------|----------|----------|
| **CRITICAL** | 365 days | 100% | System failures, data loss, security incidents |
| **ERROR** | 90 days | 100% | Exception handling, operation failures |
| **WARN** | 30 days | 100% | Degraded performance, recoverable errors |
| **INFO** | 14 days | 1:10 (10%) | Significant events, state changes |
| **DEBUG** | 7 days | 1:100 (1%) | Detailed flow information (dev/staging only) |

### 1.3 Log Aggregation Pipeline

**Flow**:
```
Application → Log Buffer (in-memory)
  ↓
JSON Formatter (sync with sampling)
  ↓
Log Sink (file, stdout, syslog)
  ↓
Fluentd/Filebeat (collection)
  ↓
Log Aggregator (ELK, DataDog, Splunk)
  ↓
Archival (S3, GCS after 90 days)
```

**Configuration** (Python):
```python
# logging_config.yaml
formatters:
  json_structured:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: "%(timestamp)s %(level)s %(logger)s %(message)s"
    rename_fields:
      timestamp: "@timestamp"
      level: "log.level"

  structured:
    class: structlog.processors.JSONRenderer
    ensure_ascii: false

handlers:
  production_json:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/application/app.log
    maxBytes: 104857600  # 100MB
    backupCount: 10
    formatter: json_structured
    level: INFO
```

### 1.4 Log Sampling Strategy

**Adaptive Sampling**:
- **High-Traffic Routes** (>1000 req/s): Sample 1%
- **Medium-Traffic Routes** (100-1000 req/s): Sample 10%
- **Low-Traffic Routes** (<100 req/s): Sample 100%
- **Error Logs**: Never sample (100%)
- **Critical Events**: Never sample (100%)

**Implementation**:
```python
def should_log_info(route_traffic_rate: float) -> bool:
    if route_traffic_rate > 1000:
        return random.random() < 0.01  # 1%
    elif route_traffic_rate > 100:
        return random.random() < 0.10  # 10%
    else:
        return True  # 100%
```

### 1.5 Retention Policies

| Log Type | Retention | Storage | Archival |
|----------|-----------|---------|----------|
| CRITICAL/ERROR | 90 days live, 1 year archive | ELK cluster | S3 Glacier |
| WARN | 30 days live, 6 months archive | ELK cluster | S3 Standard-IA |
| INFO | 14 days live | ELK cluster | None (sampled) |
| DEBUG | 7 days | Dev/Staging only | None |

---

## 2️⃣ Health Check Framework

### 2.1 Health Check Categories

#### A. Service Health (HTTP)
```
GET /health/live → 200 OK (liveness probe)
GET /health/ready → 200 OK (readiness probe)
GET /health/detailed → 200 OK + JSON (detailed status)
```

#### B. Dependency Health
```
- Database connectivity
- Cache connectivity (Redis)
- Message queue connectivity (Kafka)
- External API availability
- File system accessibility
```

#### C. Data Health
```
- Data consistency checks
- Schema validation
- Reference integrity
- Staleness detection
```

### 2.2 Health Check Endpoints

**Liveness Probe** (`/health/live`):
```json
{
  "status": "alive",
  "timestamp": "2026-06-14T15:30:45Z",
  "uptime_seconds": 86400
}
```

**Readiness Probe** (`/health/ready`):
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "message_queue": "ok",
    "disk_space": "ok",
    "memory": "ok"
  },
  "timestamp": "2026-06-14T15:30:45Z"
}
```

**Detailed Health** (`/health/detailed`):
```json
{
  "status": "healthy",
  "timestamp": "2026-06-14T15:30:45Z",
  "version": "1.2.3",
  "environment": "production",
  "uptime_seconds": 86400,
  "health_dimensions": {
    "security": {
      "status": "healthy",
      "last_auth_failure": "2h ago",
      "active_sessions": 245,
      "suspicious_activity": 0
    },
    "performance": {
      "status": "healthy",
      "p50_latency_ms": 45,
      "p95_latency_ms": 120,
      "p99_latency_ms": 350,
      "request_rate": 1200,
      "error_rate": 0.0015
    },
    "availability": {
      "status": "healthy",
      "uptime_percentage": 99.98,
      "last_restart": "7d ago",
      "failed_dependencies": 0
    },
    "state": {
      "status": "healthy",
      "data_consistency_check": "passed",
      "schema_violations": 0,
      "stale_data_items": 0
    },
    "resource": {
      "status": "healthy",
      "cpu_percent": 45,
      "memory_percent": 62,
      "disk_percent": 35,
      "network_connections": 156
    }
  },
  "dependencies": {
    "database": {
      "status": "connected",
      "latency_ms": 5,
      "pool_utilization": 0.45
    },
    "cache": {
      "status": "connected",
      "latency_ms": 2,
      "hit_ratio": 0.92
    },
    "message_queue": {
      "status": "connected",
      "pending_messages": 234,
      "lag_seconds": 0.5
    }
  },
  "alerts": []
}
```

### 2.3 Health Check SLAs

| Check | Endpoint | Interval | Timeout | Success Rate SLA | Response Time SLA |
|-------|----------|----------|---------|------------------|-------------------|
| **Liveness** | /health/live | 10s | 2s | 99.9% | <200ms |
| **Readiness** | /health/ready | 30s | 5s | 99.8% | <500ms |
| **Detailed** | /health/detailed | 60s | 10s | 99.5% | <1000ms |
| **Database** | Internal check | 60s | 5s | 99.9% | <100ms |
| **Cache** | Internal check | 30s | 2s | 99.8% | <50ms |
| **Queue** | Internal check | 60s | 5s | 99.5% | <200ms |

---

## 3️⃣ Performance Metrics Framework

### 3.1 Key Performance Indicators (KPIs)

#### Request Latency
```yaml
metric_name: request_latency_ms
dimensions:
  - route: string (e.g., "/api/users", "/api/orders")
  - method: string (GET, POST, PUT, DELETE)
  - status: integer (200, 400, 500, etc.)
  - service: string (service name)
percentiles: [p50, p75, p95, p99, p99.9]
targets:
  p50: 50ms
  p95: 200ms
  p99: 1000ms
  p99.9: 2000ms
```

#### Throughput
```yaml
metric_name: request_throughput
dimensions:
  - route: string
  - method: string
  - service: string
unit: requests/second
target: 10000 req/s (depends on service)
```

#### Error Rate
```yaml
metric_name: error_rate
dimensions:
  - service: string
  - route: string
  - error_type: string (timeout, validation, server_error, etc.)
unit: percentage
targets:
  p50: <0.1%
  p95: <0.5%
  p99: <1.0%
```

#### Resource Utilization
```yaml
metrics:
  - cpu_percent
  - memory_percent
  - disk_io_read_mb_s
  - disk_io_write_mb_s
  - network_in_mb_s
  - network_out_mb_s
targets:
  cpu: <80% (spike ok)
  memory: <85% (with headroom)
  disk: <80% (with growth buffer)
```

### 3.2 Metrics Collection Pipeline

**Architecture**:
```
Application Instrumentation (OpenTelemetry)
  ↓
Metrics Exporter (Prometheus format)
  ↓
Metrics Aggregator (Prometheus/Datadog)
  ↓
Time Series Database (TSDB)
  ↓
Visualization (Grafana/Datadog)
  ↓
Alerting Engine
```

### 3.3 Retention & Aggregation

| Granularity | Retention | Rollup |
|-------------|-----------|--------|
| **1-second** | 1 hour | None |
| **1-minute** | 7 days | Average, Max, Min |
| **5-minute** | 30 days | Average, Max, Min, p95, p99 |
| **1-hour** | 1 year | Average, Max, Min, p95, p99 |
| **1-day** | 5 years | Average, Max, Min |

---

## 4️⃣ Alerting & Escalation Framework

### 4.1 Alert Thresholds

#### Tier 1: CRITICAL (Page On-Call)
```yaml
alerts:
  - name: error_rate_high
    condition: "error_rate > 5% over 5 minutes"
    threshold: 0.05
    window: 5m
    severity: CRITICAL
    escalation: "PagerDuty + Slack + Email"

  - name: response_latency_critical
    condition: "p99_latency > 2 seconds"
    threshold: 2000ms
    window: 5m
    severity: CRITICAL
    escalation: "PagerDuty + Slack"

  - name: health_check_failed
    condition: "3+ consecutive failures"
    threshold: 3
    window: 1m
    severity: CRITICAL
    escalation: "PagerDuty + Slack + Email"

  - name: resource_exhaustion
    condition: "CPU > 95% OR Memory > 95%"
    threshold: 0.95
    window: 5m
    severity: CRITICAL
    escalation: "PagerDuty + Slack + Email"
```

#### Tier 2: WARNING (Notify Team)
```yaml
alerts:
  - name: response_latency_elevated
    condition: "p95_latency > 500ms"
    threshold: 500ms
    window: 10m
    severity: WARNING
    escalation: "Slack + Email"

  - name: error_rate_elevated
    condition: "error_rate > 1% over 10 minutes"
    threshold: 0.01
    window: 10m
    severity: WARNING
    escalation: "Slack + Email"

  - name: resource_warning
    condition: "CPU > 80% OR Memory > 85%"
    threshold: 0.80
    window: 10m
    severity: WARNING
    escalation: "Slack"
```

#### Tier 3: INFO (Log Only)
```yaml
alerts:
  - name: deployment_event
    condition: "deployment started/completed"
    severity: INFO
    escalation: "Log + Slack (optional)"

  - name: config_drift
    condition: "configuration differs from expected"
    severity: INFO
    escalation: "Log"
```

### 4.2 Escalation Procedures

**On-Call Escalation Path**:
```
Tier 1 Alert (CRITICAL)
  ↓ (5 min no response)
  ↓
Page Primary On-Call Engineer
  ↓ (15 min no ack)
  ↓
Notify Backup On-Call Engineer
  ↓ (15 min no ack)
  ↓
Notify Engineering Manager
  ↓ (15 min no ack)
  ↓
Notify Director of Engineering
```

**Notification Channels**:
- **PagerDuty**: For CRITICAL (creates incident, pages)
- **Slack**: All tiers (#alerts channel, @on-call mentions)
- **Email**: CRITICAL and WARNING only
- **Log**: All alerts with full context

### 4.3 Alert Deduplication & Cooldown

```yaml
deduplication:
  window: 1m  # Look for duplicates in last 1 minute
  key: [alert_name, dimensions]  # Dedup by alert + key labels

cooldown:
  CRITICAL: 5m   # Wait 5 min before alerting again
  WARNING: 30m   # Wait 30 min before alerting again
  INFO: 60m      # Wait 60 min before alerting again

grouping:
  CRITICAL: alert on first, then group subsequent
  WARNING: wait 5m, then group and send single notification
  INFO: wait 10m, then group and send single notification
```

---

## 5️⃣ Dashboard Configuration

### 5.1 Production Monitoring Dashboard

**Primary Dashboard** (Real-time view, 30-second refresh):

```yaml
dashboard:
  name: "Production Monitoring - Primary"
  layout: 3-column
  refresh: 30s

  panels:
    # Top Row - Critical Metrics (Red on failure)
    - name: "System Status"
      type: "status_card"
      metrics: [health_status, uptime_percentage, last_alert]
      span: 1

    - name: "Error Rate"
      type: "gauge"
      metric: error_rate
      thresholds: [0, 0.01, 0.05]  # OK, WARNING, CRITICAL
      unit: "%"
      span: 1

    - name: "Response Time (p99)"
      type: "gauge"
      metric: response_latency_p99
      thresholds: [0, 500, 2000]
      unit: "ms"
      span: 1

    # Second Row - Latency Distribution
    - name: "Request Latency Distribution"
      type: "histogram"
      metric: request_latency_ms
      percentiles: [p50, p95, p99]
      span: 2

    - name: "Throughput (req/s)"
      type: "timeseries"
      metric: request_throughput
      span: 1

    # Third Row - Resource Utilization
    - name: "CPU Utilization"
      type: "timeseries"
      metric: cpu_percent
      thresholds: [80, 95]
      span: 1

    - name: "Memory Utilization"
      type: "timeseries"
      metric: memory_percent
      thresholds: [80, 95]
      span: 1

    - name: "Disk Utilization"
      type: "timeseries"
      metric: disk_percent
      thresholds: [80, 95]
      span: 1

    # Fourth Row - Dependency Health
    - name: "Database Connection Pool"
      type: "timeseries"
      metrics: [pool_utilization, pool_connections]
      span: 1

    - name: "Cache Hit Ratio"
      type: "gauge"
      metric: cache_hit_ratio
      unit: "%"
      span: 1

    - name: "Message Queue Lag"
      type: "timeseries"
      metric: queue_lag_seconds
      thresholds: [10, 60]
      span: 1

    # Fifth Row - Alerts
    - name: "Recent Alerts"
      type: "alert_list"
      limit: 20
      span: 3
```

### 5.2 Service Health Dashboard

```yaml
dashboard:
  name: "Service Health Details"
  refresh: 60s

  panels:
    - name: "Service Status Overview"
      type: "status_grid"
      services: [api-gateway, auth-service, user-service, order-service, payment-service]
      span: 3

    - name: "API Gateway - Latency"
      type: "timeseries"
      metric: "api_gateway.request_latency"
      span: 1

    - name: "Auth Service - Error Rate"
      type: "timeseries"
      metric: "auth_service.error_rate"
      span: 1

    - name: "User Service - Throughput"
      type: "timeseries"
      metric: "user_service.throughput"
      span: 1
```

### 5.3 Incident Response Dashboard

```yaml
dashboard:
  name: "Incident Response"
  refresh: 10s  # Fast refresh during incidents

  panels:
    - name: "Active Incidents"
      type: "alert_list"
      state: "firing"
      span: 3

    - name: "Error Log Tail"
      type: "log_viewer"
      filter: 'level="ERROR" OR level="CRITICAL"'
      span: 2

    - name: "Trace Analysis"
      type: "trace_list"
      filter: 'has_error=true'
      span: 1

    - name: "System Resource Contention"
      type: "heatmap"
      metric: "resource_contention"
      span: 1
```

### 5.4 Historical Trends Dashboard

```yaml
dashboard:
  name: "Historical Trends"
  refresh: 300s
  timerange: "7d"  # Default to 7 days

  panels:
    - name: "Error Rate Trend"
      type: "timeseries"
      metric: "error_rate"
      span: 2

    - name: "Latency Trend (p50, p95, p99)"
      type: "timeseries"
      metrics: [p50_latency, p95_latency, p99_latency]
      span: 1

    - name: "Throughput Trend"
      type: "timeseries"
      metric: "throughput"
      span: 1

    - name: "Resource Utilization Trend"
      type: "timeseries"
      metrics: [cpu_percent, memory_percent, disk_percent]
      span: 1
```

---

## 6️⃣ Health Dimension Monitoring

### Matrix: All 5 Health Dimensions

| Dimension | Metrics | Thresholds | Alerts | Dashboard |
|-----------|---------|-----------|--------|-----------|
| **Security** | Auth failures, suspicious IPs, rate limits, TLS errors | Failed auth >10/min, Suspicious >5/min | CRITICAL if sustained | Security dashboard |
| **Performance** | Latency (p50/p95/p99), throughput, CPU, memory | p99 >2s, error >5%, CPU >95% | CRITICAL if p99 >2s | Performance dashboard |
| **Availability** | Uptime, health checks, failover events | <99.9%, health check fail >3x | CRITICAL if uptime <99.5% | Availability dashboard |
| **State** | Data consistency, schema validation, staleness | Schema violations >0, Staleness >24h | WARNING if violations | Data health dashboard |
| **Resource** | CPU, memory, disk, connections, file handles | CPU >95%, Mem >95%, Disk >85% | CRITICAL if exhaustion | Resource dashboard |

---

## 7️⃣ Monitoring Deployment Checklist

- [ ] Structured logging configured in all services
- [ ] JSON log format validated with sample logs
- [ ] Log aggregation pipeline deployed and tested
- [ ] Health check endpoints implemented in all services
- [ ] Health checks verified returning correct status codes
- [ ] Health check SLAs documented and validated
- [ ] Metrics collection instrumented with OpenTelemetry
- [ ] Prometheus scrape jobs configured
- [ ] Alert thresholds defined and tuned
- [ ] Alert routing configured (PagerDuty, Slack, Email)
- [ ] Alert runbooks prepared and linked
- [ ] Dashboard configuration deployed
- [ ] Dashboard panels validated with live data
- [ ] Incident response procedures documented
- [ ] On-call rotation configured
- [ ] Load testing validation completed
- [ ] Failover scenarios tested
- [ ] Log retention policies enforced
- [ ] Metrics retention policies enforced
- [ ] Security audit of monitoring infrastructure
- [ ] GDPR/compliance review of logged data

---

## 📊 Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Log Coverage** | 100% of services producing JSON logs | 0% | 🟡 In Progress |
| **Health Check Availability** | 99.8% (SLA) | 0% | 🟡 In Progress |
| **Metrics Collection Lag** | <10s | N/A | 🟡 In Progress |
| **Alert Response Time** | <2 min from trigger to page | N/A | 🟡 In Progress |
| **Dashboard Load Time** | <2 sec | N/A | 🟡 In Progress |
| **MTTR (Mean Time To Resolution)** | <30 min | N/A | 🟡 In Progress |
| **False Positive Rate** | <5% | N/A | 🟡 In Progress |

---

## 🚀 Rollout Plan

**Phase 1: Logging (Week 1)**
- Deploy structured logging to critical services
- Validate JSON format and aggregation
- Tune sampling thresholds

**Phase 2: Metrics (Week 2)**
- Instrument all services with OpenTelemetry
- Deploy Prometheus scrape jobs
- Validate data collection

**Phase 3: Health Checks (Week 2-3)**
- Implement health check endpoints
- Configure Kubernetes probes
- Test failover scenarios

**Phase 4: Alerting (Week 3)**
- Configure alert routing
- Deploy alert thresholds
- Run alert simulation drills

**Phase 5: Dashboard & Runbooks (Week 4)**
- Deploy Grafana dashboards
- Validate real-time data flow
- Train operations team

---

## 📞 Support & Escalation

**Questions or Issues?**
- Slack: #monitoring-infrastructure
- Email: monitoring-team@company.com
- On-Call: PagerDuty (monitoring-team)

**Related Documentation**:
- See `docs/production/HEALTH_CHECKS_SPECIFICATION.md`
- See `docs/production/METRICS_SCHEMA.md`
- See `docs/operations/ALERT_RUNBOOKS.md`
- See `docs/production/MONITORING_DASHBOARD_CONFIG.yaml`

---

**Last Updated**: 2026-06-14 | **Next Review**: 2026-07-14 | **Maintained by**: Platform Engineering Team
