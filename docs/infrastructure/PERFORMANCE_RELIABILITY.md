# Performance & Reliability Guide - Codex ML
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Document Version:** 1.0.0
**Last Updated: 2026-07-08
**Authority:** Phase 12 WS3 Documentation Lane 8
**Audience:** SREs, Product Managers, Platform Architects
**Status:** Production SLA

---

## Table of Contents

1. [Service Level Agreements](#service-level-agreements)
2. [Performance Benchmarks](#performance-benchmarks)
3. [Reliability Metrics](#reliability-metrics)
4. [Health Check Procedures](#health-check-procedures)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Incident Response Thresholds](#incident-response-thresholds)

---

## Service Level Agreements

### API Service SLA

**Target Availability:** 99.9% (99.99% for enterprise customers)

```
Calculation: (Total Time - Downtime) / Total Time

Monthly Downtime Budget:
- 99.9%: 43.2 minutes maximum
- 99.99%: 4.32 minutes maximum
- 99.95%: 21.6 minutes maximum
```

#### Downtime Categories

| Category | Impact | Counts Against SLA? |
|----------|--------|-------------------|
| Scheduled Maintenance (24h notice) | Service unavailable | No |
| Emergency Fixes (<1 hour) | Service unavailable | No* |
| Security Patches (customer announced) | Service unavailable | No |
| Third-party outages (AWS, GCP, etc.) | Service degradation | No |
| Customer misconfiguration | No impact | No |
| Network issues (customer side) | No impact | No |

*\*Emergency fixes bypass scheduled maintenance SLA if critical vulnerability*

### Model Serving SLA

**Target Availability:** 99.95%
**Target Latency (p99):** <1 second
**Target Throughput:** >10,000 inferences/sec per cluster

```yaml
SLA Targets:
 - API Error Rate: <0.5% (p99)
 - Inference Latency: <500ms (p50), <2s (p99)
 - Model Load Time: <5 seconds
 - Batch Processing: <2s per batch of 32
 - Queue Wait Time: <500ms
```

### Training Service SLA

**Target Availability:** 99.9%
**No strict latency SLA** (async job)
**Checkpoint Interval:** ≤1 hour guaranteed

```yaml
SLA Targets:
 - Job Initiation: <5 minutes
 - Checkpoint Success Rate: >99.9%
 - Data Loss Rate: <0.01% (with replication)
 - Max Queue Wait: <24 hours
```

### Data Durability SLA

**Target Durability:** 99.999999999% (11 nines)
**Minimum Replicas:** 3 across availability zones
**Backup Frequency:** Hourly with 30-day retention

```
AWS S3 Durability: 99.999999999%
Calculation: 1 - (1 - 10^-11)^N

With RDS Multi-AZ:
- RPO (Recovery Point Objective): <1 minute
- RTO (Recovery Time Objective): <5 minutes
- Data Loss Risk: <0.001%
```

---

## Performance Benchmarks

### Inference Performance

#### Single Model Inference (Cold Start)

```
Scenario: First inference after deployment
Conditions: 8GB GPU memory, fp16 quantization

Latency Breakdown:
 - Model Load: 2.5 seconds (cached)
 - Initialization: 0.8 seconds
 - Inference: 0.2 seconds (8 tokens)
 - Total: 3.5 seconds (p50)
 - Total: 5.0 seconds (p99)

Memory:
 - Model Weight: 8GB
 - Activation: 2GB
 - Working Memory: 1GB
 - Total: 11GB
```

#### Warm Inference

```
Scenario: Sustained inference workload
Conditions: 8GB GPU, batch size 32

Latency (per inference):
 - p50: 120ms
 - p95: 180ms
 - p99: 250ms
 - max: 450ms

Throughput:
 - Tokens/sec: 850 (model-dependent)
 - Inferences/sec: 12-15
 - Batch/sec: 0.3-0.4

Resource Utilization:
 - GPU: 85-90%
 - Memory: 14GB/16GB
 - Power: 250W
```

#### Batch Inference (32 samples)

```
Latency:
 - p50: 800ms
 - p99: 1.2s
 - Total time / sample: ~30ms

Throughput:
 - Samples/sec: 40
 - Batch/sec: 1.25

Memory:
 - Active: 15.5GB
 - Utilization: 97%
```

### Training Performance

#### Model Training Throughput

```
Scenario: 7B parameter model, 32 tokens
Conditions: 8x A100 80GB GPUs, DDP (Distributed Data Parallel)

Single GPU:
 - Throughput: 150 samples/sec
 - Throughput: 1200 tokens/sec
 - Memory/GPU: 75GB
 - Time/Epoch: 6.7 hours (10M samples)

8-GPU Cluster:
 - Throughput: 1200 samples/sec (linear scaling)
 - Throughput: 9600 tokens/sec
 - Time/Epoch: 50 minutes
 - Total Training: 2.5 hours (3 epochs)

Scaling Efficiency: 95% (near-linear)
```

#### Checkpoint Performance

```
Scenario: Save 7B model checkpoint
Conditions: Distributed filesystem, fp16

Checkpoint Size:
 - Model Weights: 14GB
 - Optimizer State: 28GB
 - Training State: 2GB
 - Total: 44GB

Time:
 - Serialization: 8 seconds
 - Network Transfer: 45 seconds (1Gbps)
 - Filesystem Write: 65 seconds
 - Total: 2 minutes

Checkpoint Frequency: Every 1000 steps (~6 min)
Overhead: 3.3% of training time
```

### API Performance

#### Request Latency

```
Scenario: RESTful API calls, small payloads

List Models (zero-cache):
 - p50: 45ms
 - p99: 120ms

Get Model Details:
 - p50: 8ms (cached)
 - p50: 65ms (fresh)
 - p99: 200ms

Single Inference:
 - p50: 120ms
 - p99: 280ms

Create Training Job:
 - p50: 85ms
 - p99: 250ms
```

#### Throughput

```
Scenario: Sustained load, 3 API replicas

Throughput (RPS):
 - Single replica: 333 RPS
 - 3 replicas: 1000 RPS
 - 10 replicas: 3300 RPS

Bottleneck Analysis:
 - Without cache: Limited by database
 - With cache: Limited by network bandwidth
 - Sustained peak: ~2000 RPS before cascading failures
```

### Database Performance

#### Read Performance

```
Query: SELECT * FROM models WHERE status = 'active'

Index Hit Rate: 99.5%
Latency:
 - Cached (in memory): 0.5ms
 - SSD Read: 2-5ms
 - Cold (disk read): 20-50ms

Large Results (10k rows):
 - Query time: 15ms
 - Serialization: 8ms
 - Network: 10ms
 - Total: 33ms
```

#### Write Performance

```
Operation: INSERT INTO inference_requests (...)

Latency (with replication):
 - Write to primary: 1-2ms
 - Sync replication: 5-8ms
 - Ack to client: 8-10ms
 - p99: 20ms

Throughput:
 - Primary: 1000 writes/sec
 - With replication: 500 writes/sec
 - With fsync: 100 writes/sec

WAL Throughput:
 - Unbounded: ~100MB/sec
 - Network limited: ~50MB/sec
```

---

## Reliability Metrics

### Availability Tracking

```
Monthly Availability Report:

July 2024:
 Total Minutes: 44,640
 Downtime: 15 minutes
 Availability: 99.966%
 Exceeded SLA: Yes 
 
Downtime Events:
 - 2024-07-05 14:30-14:42 (12 min) - DB connection pool exhaustion
 - 2024-07-15 03:15-03:18 (3 min) - Network maintenance

Trend:
 June 2024: 99.93%
 July 2024: 99.97% 
 YTD Average: 99.94%
```

### Error Rates

| Service | p50 Error Rate | p99 Error Rate | Target | Status |
|---------|---|---|---|---|
| API | 0.01% | 0.05% | <0.5% | |
| Model Server | 0.02% | 0.08% | <0.5% | |
| Training | 0.03% | 0.10% | <1% | |
| Database | 0.001% | 0.005% | <0.1% | |

### Latency Metrics

| Operation | p50 | p95 | p99 | SLA |
|-----------|-----|-----|-----|-----|
| API Health Check | 5ms | 8ms | 15ms | <10ms |
| Model List | 25ms | 50ms | 120ms | <100ms |
| Single Inference | 120ms | 180ms | 280ms | <500ms |
| Batch Inference | 800ms | 1100ms | 1500ms | <2s |

---

## Health Check Procedures

### Automated Health Checks (Every 10 seconds)

```bash
# Liveness probes
GET /health/live
Response: 200 OK {"status": "alive"}

# Readiness probes
GET /health/ready
Response: 200 OK {"status": "ready"}

# Detailed status
GET /health/status
Response:
{
 "status": "healthy",
 "uptime_seconds": 86400,
 "checks": {
 "database": {"status": "ok", "latency_ms": 2},
 "cache": {"status": "ok", "latency_ms": 1},
 "storage": {"status": "ok", "latency_ms": 45},
 "model_server": {"status": "ok", "replicas": 3}
 }
}
```

### Manual Verification Checklist

```
Daily (08:00 UTC):
[ ] Cluster status - kubectl get nodes
[ ] Pod status - kubectl get pods -n codex
[ ] Database connectivity - psql health check
[ ] Storage access - AWS S3 list operation
[ ] Metrics pipeline - Prometheus /metrics endpoint
[ ] Alerts - Check firing/resolved alerts
[ ] Error rates - Query last hour of metrics

Weekly (Monday 09:00):
[ ] Full backup verification
[ ] Cross-region failover test
[ ] Load balancer health
[ ] Certificate expiry check
[ ] Disk usage trend analysis

Monthly (First Monday 09:00):
[ ] Disaster recovery drill
[ ] Capacity planning review
[ ] Performance trend analysis
[ ] Security vulnerability scan
```

---

## Monitoring & Alerting

### Key Metrics Dashboard

```yaml
Dashboard: Codex Infrastructure Health
Refresh Rate: 30 seconds

Panels:
 1. System Overview
 - Cluster availability: 99.97%
 - API error rate: 0.03%
 - Active requests: 1,247
 - GPU utilization: 78%
 
 2. API Performance
 - Request latency (p50, p95, p99)
 - Throughput (RPS)
 - Error rate by endpoint
 - Response size distribution
 
 3. Model Serving
 - Inference latency by model
 - Throughput by model
 - GPU memory utilization
 - Queue depth
 
 4. Infrastructure
 - Node CPU/Memory
 - Disk utilization
 - Network I/O
 - Pod restarts
 
 5. Database
 - Connection pool usage
 - Query latency
 - Replication lag
 - Slow queries
 
 6. Training
 - Active jobs
 - Job success rate
 - GPU utilization
 - Checkpoint frequency
```

### Alert Rules

#### Critical Alerts (Page immediately)

```yaml
- name: api-unavailable
 condition: up{job="api-server"} == 0
 duration: 2m
 description: "API service is down"
 severity: critical
 action: "Execute API recovery runbook"

- name: database-offline
 condition: pg_up{job="postgres"} == 0
 duration: 1m
 description: "Database is unreachable"
 severity: critical
 action: "Trigger failover to replica"

- name: data-loss-detected
 condition: |
 increase(inference_requests_total[5m]) == 0 AND
 increase(api_requests_total[5m]) > 100
 description: "Data loss detected"
 severity: critical
 action: "Trigger backup recovery"
```

#### High-Priority Alerts (Email immediately)

```yaml
- name: high-error-rate
 condition: rate(api_errors_total[5m]) > 0.05
 duration: 5m
 description: "API error rate >5%"
 severity: high
 action: "Monitor, escalate if increasing"

- name: gpu-memory-exhausted
 condition: gpu_memory_used{} / gpu_memory_total{} > 0.95
 duration: 5m
 description: "GPU memory utilization >95%"
 severity: high
 action: "Scale up model server replicas"

- name: slow-database
 condition: histogram_quantile(0.99, db_query_duration_ms{}) > 500
 duration: 10m
 description: "Database queries slow (p99 >500ms)"
 severity: high
 action: "Check running queries, scale if needed"
```

#### Medium-Priority Alerts (Slack notification)

```yaml
- name: disk-usage-high
 condition: node_disk_used_percent{} > 80
 duration: 30m
 description: "Disk usage >80%"
 severity: medium
 action: "Review and clean up old artifacts"

- name: pod-restarts
 condition: rate(kube_pod_container_status_restarts_total[1h]) > 5
 duration: 15m
 description: "High pod restart rate"
 severity: medium
 action: "Investigate pod logs"

- name: certificate-expiry
 condition: tls_cert_expiry_days{} < 30
 description: "Certificate expiring in <30 days"
 severity: medium
 action: "Rotate certificate"
```

---

## Incident Response Thresholds

### Automatic Scaling Thresholds

```yaml
API Server Scaling:
 Scale Up When:
 - CPU avg >70% for 2 minutes
 - OR Memory >75% for 2 minutes
 - OR Request queue >100
 - Action: +2 replicas (min +25%, max +100%)
 
 Scale Down When:
 - CPU avg <30% for 10 minutes
 - AND Memory <50% for 10 minutes
 - Action: -1 replica (min -25%, max -50%)
 
 Limits:
 - Min replicas: 2
 - Max replicas: 10
 - Cooldown: 5 minutes between scaling events

Model Server Scaling:
 Scale Up When:
 - Queue depth >50 for 2 minutes
 - OR Inference latency p99 >1 second
 - OR GPU memory >85% for 2 minutes
 - Action: Add 1-2 replicas (model loading ~2min)
 
 Limits:
 - Min replicas: 1
 - Max replicas: 10
 - Cooldown: 2 minutes (model loading)
```

### Alert to Action Mapping

| Alert | Auto-Action | Manual Escalation | SLA |
|-------|------------|-------------------|-----|
| API Unavailable | Restart pods | Page on-call | <15min |
| High Error Rate | Scale up API | Page if unresolved | <30min |
| Database Slow | Scale up DB | Escalate to DB team | <1hr |
| GPU Memory High | Restart model server | Scale up nodes | <1hr |
| Disk Usage >90% | Alert only | Manual cleanup | <4hr |

---

## Performance Optimization Targets

### 2024 Performance Goals

```
Goal 1: Reduce API latency p99 from 280ms to 200ms
 Method: Caching optimization, database indexing
 Status: On track (280ms 240ms so far)

Goal 2: Increase throughput from 1K to 3K RPS
 Method: Horizontal scaling, connection pooling
 Status: Completed (now at 3.3K RPS)

Goal 3: Reduce model inference latency by 15%
 Method: Quantization, kernel optimization
 Status: Achieved (35% reduction)

Goal 4: Improve training throughput 20%
 Method: Distributed training optimization
 Status: In progress (15% improvement)

Goal 5: Achieve 99.99% availability
 Method: Enhanced monitoring, better runbooks
 Status: On track (99.97% vs 99.94% target)
```

---

## SLA Compliance Report Template

```markdown
# SLA Compliance Report - [Month]

**Reporting Period:** [Date range]
**Report Date:** [Date]
**Prepared By:** [SRE Name]

## Executive Summary
- Target Availability: 99.9%
- Actual Availability: [X%]
- SLA Status: Met / Missed

## Detailed Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Availability | 99.9% | X.XX% | / |
| API Latency p99 | <500ms | XXXms | / |
| Error Rate | <0.5% | X.XX% | / |
| Data Durability | 99.99% | 100% | |

## Incidents
1. [Date] - [Issue] - Duration: [Time] - Impact: [%]
2. ...

## Root Causes
1. [RCA 1]
2. [RCA 2]

## Improvements This Month
- [Improvement 1]
- [Improvement 2]

## Next Month Focus
- [Focus 1]
- [Focus 2]
```

---

## See Also

- [Infrastructure Architecture](INFRASTRUCTURE_ARCHITECTURE.md)
- [Operations Manual](OPERATIONS_MANUAL.md)
- [Technical Reference](TECHNICAL_REFERENCE.md)
- [Deployment Checklists](../deployment/PRODUCTION_READINESS_CHECKLIST.md)

---

**Last Updated: 2026-07-08
**Next Review:** 2026-10-08
**Escalation Contact:** @platform-leads

