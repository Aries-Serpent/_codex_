# PHASE 13 SLA METRICS & TRACKING
# Production SLA Targets and Monitoring
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z

---

## EXECUTIVE SUMMARY

**Overall SLA Target:** 99.9% uptime (8.64 seconds downtime/day budget)
**Error Rate Target:** <0.05%
**Latency Target:** p95 ≤ 350ms
**Data Loss Policy:** Zero tolerance (RPO = 0)

---

## PRIMARY METRICS

### 1. UPTIME (99.9% Target)

**Definition:**
- Uptime = (Total Time - Downtime) / Total Time
- Downtime = Time when service unable to serve requests
- Excludes: Planned maintenance, customer-caused issues, DDos

**Measurement Points:**
- Application health checks (every 10 seconds)
- HTTP 200 responses from public endpoints
- Database connectivity tests
- Cache layer availability

**Calculation (Monthly):**
```
Days in Month: 30
Total Seconds: 30 × 24 × 3600 = 2,592,000 seconds
99.9% Budget: 2,592 seconds (43.2 minutes downtime allowed)
```

**Daily Breakdown:**
- 24 hours = 86,400 seconds
- 99.9% budget = 86.4 seconds downtime/day

**Alert Thresholds:**
- Warning: 99.5% (432 seconds lost in day)
- Critical: 99% (864 seconds lost in day)

**Tracking:**
```
SELECT
  DATE(timestamp) as date,
  COUNT(*) filter (WHERE status = 200) as successful_checks,
  COUNT(*) as total_checks,
  100.0 * COUNT(*) filter (WHERE status = 200) / COUNT(*) as uptime_pct
FROM health_checks
WHERE timestamp > now() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### 2. ERROR RATE (<0.05% Target)

**Definition:**
- Error Rate = Failed Requests / Total Requests
- Failed = HTTP 5xx responses
- Excludes: 4xx (client errors), 429 (rate limiting)

**Measurement Points:**
- Application HTTP errors
- Database query errors
- API timeout errors
- Service exceptions

**Alert Thresholds:**
- Warning: 0.01% (1 error per 10,000 requests)
- Critical: 0.05% (1 error per 2,000 requests)

**Calculation (Per Minute):**
```
Target: 1,000 requests/min with <0.05% error rate
= Max 0.5 errors/min allowed (rolling)
```

**Tracking:**
```
SELECT
  DATE(timestamp) as date,
  COUNT(*) filter (WHERE status >= 500) as errors,
  COUNT(*) as total_requests,
  100.0 * COUNT(*) filter (WHERE status >= 500) / COUNT(*) as error_rate_pct
FROM http_requests
WHERE timestamp > now() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### 3. LATENCY - p95 (≤350ms Target)

**Definition:**
- p95 = 95th percentile response time
- Measurement: Request received → Response sent
- Includes: Network time + Application processing

**Service Breakdown:**
| Service | p95 Target | p99 Target | p99.9 Target |
|---------|-----------|-----------|-------------|
| API Gateway | 100ms | 200ms | 500ms |
| Application | 200ms | 400ms | 800ms |
| Database Queries | 150ms | 300ms | 600ms |
| Cache Operations | 10ms | 20ms | 50ms |
| Search (ElasticSearch) | 300ms | 600ms | 1000ms |

**Alert Thresholds:**
- Warning: p95 > 250ms (trending up)
- Critical: p95 > 350ms (SLA violation)

**Tracking:**
```
SELECT
  DATE(timestamp) as date,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99,
  PERCENTILE_CONT(0.999) WITHIN GROUP (ORDER BY latency_ms) as p99_9,
  MAX(latency_ms) as max
FROM request_latencies
WHERE timestamp > now() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### 4. RESOURCE UTILIZATION

**CPU Utilization (Target: <70% peak)**
- Warning: >60% for >5 min
- Critical: >80% sustained
- Panic: >95% (immediate action)

**Memory Utilization (Target: <75% peak)**
- Warning: >65% for >10 min
- Critical: >85% sustained
- Panic: >95% (risk of OOMKill)

**Disk Utilization (Target: <80% used)**
- Warning: >75%
- Critical: >90%
- Panic: >95% (risk of "no space left")

**Network Utilization (Target: <70% of link capacity)**
- Warning: >60% for >5 min
- Critical: >80% (packet loss risk)

**Tracking:**
```
SELECT
  DATE(timestamp) as date,
  MAX(cpu_percent) as cpu_max,
  AVG(cpu_percent) as cpu_avg,
  MAX(memory_percent) as mem_max,
  AVG(memory_percent) as mem_avg,
  MAX(disk_percent) as disk_max,
  MAX(network_mbps) as net_max
FROM system_metrics
WHERE timestamp > now() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### 5. DATABASE METRICS

**Query Performance (p95 ≤150ms)**
- Alert: >300ms sustained
- Action: Check slow query log, add index if needed

**Replication Lag (≤1 second)**
- Alert: >5 seconds
- Critical: >30 seconds (failover risk)

**Connection Pool Health**
- Warning: >300 connections (75% of pool)
- Critical: >350 connections (approaching limit)

**Backup Status**
- Check: Completed daily ✓
- RPO: < 1 hour (max data loss)
- Frequency: Daily incremental + weekly full

**Tracking:**
```
SELECT
  DATE(timestamp) as date,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY query_time_ms) as query_p95,
  MAX(replication_lag_seconds) as max_replication_lag,
  MAX(active_connections) as max_connections,
  SUM(case when backup_status = 'complete' then 1 else 0 end) as backups_completed
FROM database_metrics
WHERE timestamp > now() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

### 6. CACHE LAYER METRICS

**Hit Rate (Target: ≥80%)**
- Warning: <75%
- Critical: <60% (cache ineffective)

**Eviction Rate (Target: <5%)**
- Alert: >10%
- Action: Increase cache size or reduce TTL

**Memory Usage (Target: <90% of limit)**
- Warning: >80%
- Critical: >95%

---

## MONTHLY SLA REPORT

**Auto-Generated:** First Friday of each month

**Contents:**
1. **Executive Summary**
   - Uptime %, Error Rate %, Latency p95
   - Pass/Fail against targets
   - Major incidents summary

2. **Detailed Metrics**
   - Daily uptime breakdown
   - Peak error rate & when
   - Latency trends
   - Resource utilization

3. **Incidents**
   - All incidents (P1-P4)
   - Duration, impact, root cause
   - Resolution & lessons learned

4. **Compliance**
   - SLA credit calculation (if applicable)
   - Customer communication
   - Follow-up actions

**Distribution:**
- Internal: #operations Slack channel
- Customer: Email to primary contact
- Leadership: Shared with VP Engineering

---

## SLA VIOLATION PROCEDURES

**When SLA is Breached:**

1. **Detection (Automated)**
   - AlertManager fires: `sla_violation_detected`
   - Slack alert: #oncall-alerts (immediate)
   - PagerDuty: Pages Tier 1

2. **Investigation (Within 5 minutes)**
   - Identify root cause
   - Classify as: True violation vs false positive
   - Document in incident tracker

3. **Response (Within 15 minutes)**
   - Implement fix (if auto-recovery possible)
   - Or escalate to appropriate team
   - Update customers of timeline

4. **Follow-Up (Within 24 hours)**
   - Root cause analysis
   - Preventive action plan
   - Update monitoring/alerting if needed

**SLA Credits (if applicable):**
- 99.5%-99.9%: 10% monthly credit
- 99%-99.5%: 25% monthly credit
- 95%-99%: 50% monthly credit
- <95%: 100% monthly credit

---

## EXAMPLE METRIC QUERIES

**Real-Time SLA Status (Dashboard):**
```
# Uptime percentage (last 24 hours)
(up_hours / 24) * 100

# Error rate (last 5 minutes)
(errors_5min / total_requests_5min) * 100

# Latency p95 (last 1 hour)
PERCENTILE_CONT(0.95) of response_times_1h

# Critical resource stats
SELECT cpu_max, mem_max, disk_usage FROM system_metrics ORDER BY timestamp DESC LIMIT 1;
```

**Trending Analysis (Weekly):**
```
# Uptime trend (past 4 weeks)
SELECT week, uptime_pct FROM weekly_sla WHERE date > now() - INTERVAL '1 month' ORDER BY week;

# Error rate trend
SELECT day, error_rate FROM daily_metrics WHERE date > now() - INTERVAL '1 month' ORDER BY day;

# Latency trend
SELECT day, p95_latency FROM daily_metrics WHERE date > now() - INTERVAL '1 month' ORDER BY day;
```

---

## DASHBOARD DISPLAYS

**Grafana Dashboard: "SLA Status"**

Panels:
1. **Uptime Gauge**
   - Display: Percentage
   - Color: Green (>99.9%), Yellow (>99%), Red (<99%)
   - Update interval: 1 minute

2. **Error Rate Trend**
   - Display: Line chart
   - Threshold: 0.05% SLA line
   - Range: Last 7 days

3. **Latency p95 Trend**
   - Display: Line chart
   - Threshold: 350ms SLA line
   - Range: Last 24 hours (rolling)

4. **Resource Utilization Heatmap**
   - CPU, Memory, Disk, Network
   - Color: Green (<70%), Yellow (70-85%), Red (>85%)

5. **Incident History**
   - Table: Date, Duration, Impact, Cause
   - Range: Last 30 days

6. **SLA Credit Calculation**
   - Current month uptime %
   - Credit owed to customers (if applicable)

---

## OPERATIONAL THRESHOLDS

| Metric | Green | Yellow | Red | Action |
|--------|-------|--------|-----|--------|
| Uptime | >99.9% | 99%-99.9% | <99% | Page Tier 1 |
| Error Rate | <0.01% | 0.01-0.05% | >0.05% | Investigate |
| p95 Latency | <250ms | 250-350ms | >350ms | Optimize |
| CPU | <70% | 70-85% | >85% | Scale |
| Memory | <75% | 75-90% | >90% | Alert |
| Disk | <80% | 80-90% | >90% | Clean |

---

## REFERENCES

- SLA Definition: https://www.example.com/sla-policy
- Monitoring Setup: `.codex/PHASE_13_prometheus_config.yml`
- Grafana Dashboards: `.codex/PHASE_13_grafana_dashboards.json`
- Alert Rules: `.codex/PHASE_13_alert_rules.yml`

---

**Status:** ✅ LIVE (effective 2026-07-16T20:51Z)  
**Last Review:** 2026-07-16T20:51Z  
**Next Review:** 2026-08-16
