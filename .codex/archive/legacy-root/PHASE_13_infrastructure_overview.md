# PHASE 13 PERMANENT INFRASTRUCTURE OVERVIEW
# Architecture & Component Integration
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 13 OPERATIONS INFRASTRUCTURE            │
└─────────────────────────────────────────────────────────────────────┘

┌─ METRIC COLLECTION LAYER ────────────────────────────────────────┐
│                                                                   │
│  ┌──────────────────┐        ┌──────────────────┐                │
│  │   Node Exporters │        │  App Metrics     │                │
│  │  (3 instances)   │        │  (codex-ml API)  │                │
│  └────────┬─────────┘        └────────┬─────────┘                │
│           │                           │                           │
│  ┌────────────────┐    ┌─────────────────────┐                  │
│  │ PostgreSQL     │    │ Redis Exporters     │                  │
│  │ Exporter       │    │ (primary + replica) │                  │
│  └────────┬───────┘    └─────────┬───────────┘                  │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
└───────────────────────┼──────────────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                   PROMETHEUS (9090)                              │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ • Scrape interval: 60 seconds                        │       │
│  │ • Retention: 15 days (configured)                    │       │
│  │ • Rules: 40+ alert rules loaded                      │       │
│  │ • Targets: 30+ endpoints monitored                   │       │
│  └──────────────────────────────────────────────────────┘       │
└───────────────────────┬──────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼─────┐  ┌─────▼──────┐  ┌────▼──────────┐
│ GRAFANA     │  │ALERTMANAGER│  │  PROMETHEUS  │
│  (3000)     │  │   (9093)   │  │  WebUI       │
│             │  │            │  │  (9090)      │
└───────┬─────┘  └─────┬──────┘  └──────────────┘
        │              │
        │     ┌────────┴─────────┐
        │     │                  │
   ┌────▼─────▼────┐  ┌──────────▼────────┐
   │    Slack      │  │   PagerDuty      │
   │  #oncall-     │  │  Incident Mgmt   │
   │  alerts       │  │  & Escalation    │
   └───────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ON-CALL & RESPONSE LAYER                            │
│                                                                  │
│  Tier 1: @mbaetiong (primary, 5min SLA)                          │
│  Tier 2: ci-emergency-response-agent (automation)               │
│  Tier 3: @[infra-lead] (escalation, 3min SLA)                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─ RUNBOOK EXECUTION & INCIDENT MANAGEMENT ──────────────────────┐
│                                                                 │
│  • 12 comprehensive runbooks (.codex/PHASE_13_RB_*.md)          │
│  • Auto-response for common patterns                           │
│  • Escalation decision tree built into Slack bot              │
│  • Incident tracking & post-mortems automated                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## COMPONENT SPECIFICATIONS

### 1. PROMETHEUS

**Purpose:** Metrics collection and storage

**Deployment:**
- Image: `prom/prometheus:latest` (or pinned version)
- Port: 9090
- Memory: 4GB (with 15-day retention)
- Disk: 200GB (SSD recommended for TS queries)
- Uptime: 99.9% SLA

**Configuration:**
- Location: `/etc/prometheus/prometheus.yml`
- Scrape interval: 60 seconds
- Evaluation interval: 30 seconds
- External labels: cluster=production, environment=prod

**Scaling:**
- Single instance: handles up to 100 targets
- If >100 targets: Use Prometheus federation or Thanos
- HA setup: 2 instances + deduplication via Thanos

**Backup Strategy:**
- Daily snapshots of TSDB
- Location: `/var/lib/prometheus/snapshots/`
- Retention: 30 days

**Monitoring Prometheus itself:**
```
prometheus_tsdb_symbol_table_size_bytes (memory)
prometheus_tsdb_wal_checkpoint_delete_failures_total (errors)
prometheus_rule_evaluation_duration_seconds (performance)
```

---

### 2. GRAFANA

**Purpose:** Visualization and SLA dashboards

**Deployment:**
- Image: `grafana/grafana:latest`
- Port: 3000
- Memory: 1GB
- Auth: OAuth2 (Google/GitHub) or LDAP
- TLS: Required (https:// only)

**Dashboards:**
1. **SLA Status** - Uptime, error rate, latency, resources
2. **Application Performance** - Throughput, latency p95, errors
3. **Database Health** - Query perf, replication lag, connections
4. **Kubernetes** - Pod status, resource usage, restarts
5. **Infrastructure** - CPU, memory, disk, network trends

**Configuration:**
- Data source: Prometheus (http://prometheus:9090)
- Admin: RBAC enabled (viewer/editor/admin)
- Alerts: Notification channels to Slack + PagerDuty

**Backup Strategy:**
- Dashboard JSON backups daily
- Location: `/var/backups/grafana/`
- Provisioning: Infrastructure-as-code (dashboards as JSON files)

**Performance:**
- Query timeout: 30 seconds
- Caching: 1 minute minimum
- Max concurrent queries: 100

---

### 3. ALERTMANAGER

**Purpose:** Alert routing and deduplication

**Deployment:**
- Image: `prom/alertmanager:latest`
- Port: 9093
- Memory: 512MB
- Clustering: Enabled (for HA)

**Alert Routes:**
- Critical SLA violations → #oncall-alerts + PagerDuty (5s delay)
- Infrastructure alerts → #infrastructure (10s delay)
- Database alerts → #database-alerts (immediate)
- Low priority → #monitoring-logs (batch, 5min delay)

**Configuration:**
- Location: `/etc/alertmanager/alertmanager.yml`
- Receiver grouping: alertname + cluster + service
- Inhibition rules: 12 rules to prevent alert spam

**Notifications:**
- Slack webhook URLs: 5+ channels configured
- PagerDuty service keys: 3 (critical, database, infrastructure)
- Email: Optional (for audit trail)

**Backup & Recovery:**
- Configuration versioned in Git
- Template files backed up
- No persistent state (stateless design)

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Hardware provisioned (CPU/memory/disk specs met)
- [ ] Network connectivity verified (all targets reachable)
- [ ] TLS certificates obtained (for https://)
- [ ] OAuth2 credentials configured (for Grafana auth)
- [ ] Slack webhook URLs created
- [ ] PagerDuty API keys generated
- [ ] Database backups configured
- [ ] NTP sync verified on all servers

### Deployment Phase 1: Prometheus (1 hour)

```bash
# 1. Pull and run Prometheus
docker pull prom/prometheus:latest
docker run -d \
  --name prometheus \
  --restart always \
  -p 9090:9090 \
  -v /etc/prometheus:/etc/prometheus \
  -v prometheus_data:/prometheus \
  prom/prometheus:latest

# 2. Verify connectivity
curl http://localhost:9090/api/v1/status/runtimeinfo

# 3. Check target scrape
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Expected: 30+

# 4. Query metrics
curl 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result | length'
```

### Deployment Phase 2: Grafana (30 minutes)

```bash
# 1. Pull and run Grafana
docker pull grafana/grafana:latest
docker run -d \
  --name grafana \
  --restart always \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=<random-password> \
  grafana/grafana:latest

# 2. Configure data source (Prometheus)
curl -X POST http://localhost:3000/api/datasources \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "isDefault": true
  }'

# 3. Import dashboards
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Authorization: ******" \
  -d @sla_status_dashboard.json
```

### Deployment Phase 3: AlertManager (30 minutes)

```bash
# 1. Pull and run AlertManager
docker pull prom/alertmanager:latest
docker run -d \
  --name alertmanager \
  --restart always \
  -p 9093:9093 \
  -v /etc/alertmanager:/etc/alertmanager \
  prom/alertmanager:latest

# 2. Verify connectivity
curl http://localhost:9093/api/v1/status

# 3. Test alert routing
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "labels": {"alertname": "TestAlert", "severity": "critical"},
    "annotations": {"description": "Test alert"}
  }]'
```

### Post-Deployment Validation

- [ ] Prometheus scraping all 30+ targets
- [ ] Grafana dashboards displaying metrics
- [ ] AlertManager routing alerts correctly
- [ ] Slack notifications delivering
- [ ] PagerDuty incidents creating
- [ ] All runbooks accessible from dashboard
- [ ] On-call rotation schedule published
- [ ] Health checks passing

---

## INTEGRATION POINTS

### With Kubernetes

```yaml
# ServiceMonitor for Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: codex-ml-services
spec:
  selector:
    matchLabels:
      app: codex-ml
  endpoints:
    - port: metrics
      interval: 60s
```

### With External Services

- **PagerDuty:** Incident escalation for P1 events
- **Slack:** Multi-channel alert routing
- **Datadog:** Optional metrics export (if using)
- **Splunk:** Optional log aggregation (if using)

### With Application

```python
# Python: Expose metrics endpoint
from prometheus_client import start_http_server, Counter, Gauge
import time

# Create metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Gauge('app_request_latency_seconds', 'Request latency')

# Expose on port 8000
start_http_server(8000)

# Increment counter
REQUEST_COUNT.labels(method='GET', endpoint='/api/users').inc()

# Record latency
REQUEST_LATENCY.set(0.123)
```

---

## SCALING & HIGH AVAILABILITY

### Single-Instance Configuration

- Prometheus: 1 instance (primary)
- Grafana: 1 instance (can access Prometheus)
- AlertManager: 1 instance

**Limitations:**
- No high availability
- Single point of failure
- Max 100 targets

### Multi-Instance Configuration

```
┌─────────────────────────────┐
│   Prometheus Federation     │
├─────────────────────────────┤
│ ├─ Prom-1 (targets 1-50)    │
│ ├─ Prom-2 (targets 51-100)  │
│ └─ Prom-3 (global view)     │
└────────┬────────────────────┘
         │
    ┌────▼─────┐
    │ Thanos   │  (deduplication + querying)
    └────┬─────┘
         │
    ┌────▼────────┐
    │ Grafana     │
    └─────────────┘
```

**Benefits:**
- Scales to 500+ targets
- High availability (1 instance failure = no impact)
- Deduplication for accurate SLA calculations

---

## DISASTER RECOVERY

### Scenario 1: Prometheus Disk Full

```bash
# 1. Find oldest blocks and delete
du -sh /var/lib/prometheus/wal/*
rm -rf /var/lib/prometheus/wal/oldest-block

# 2. Restart Prometheus
docker restart prometheus

# 3. Verify metrics still coming in
curl http://localhost:9090/api/v1/query?query=up | jq '.data.result | length'
```

### Scenario 2: All Metrics Lost

```bash
# 1. Restore from backup
cp -r /var/backups/prometheus/daily_2026-07-16.tar.gz /var/lib/prometheus/

# 2. Restart Prometheus
docker restart prometheus

# 3. Verify data restored
curl http://localhost:9090/api/v1/query_range?query=up&start=1689500000&end=1689586400
```

---

## MONITORING THE MONITORS

**Health Checks:**
```bash
# Prometheus health
curl http://prometheus:9090/-/healthy

# Grafana health
curl http://grafana:3000/api/health

# AlertManager health
curl http://alertmanager:9093/-/healthy
```

**Metrics to Monitor:**
- `prometheus_tsdb_wal_segment_create_failures_total` (write failures)
- `prometheus_rule_evaluation_failures_total` (rule errors)
- `alertmanager_alerts_received_total` (alert ingestion rate)

---

## REFERENCES

- Prometheus Docs: https://prometheus.io/docs/
- Grafana Docs: https://grafana.com/docs/
- AlertManager Docs: https://prometheus.io/docs/alerting/latest/alertmanager/
- Phase 12 Transition: `.codex/PHASE_12_SESSION_EXECUTION_STATUS_2026_07_16.md`

---

**Status:** ✅ PRODUCTION READY (v0.2.0 stable)  
**Deployment Target:** 2026-07-17T20:00Z  
**Last Updated:** 2026-07-16T20:51Z
