# Phase 4 GA Continuous Metrics Collection Framework

**Status**: ✅ **ACTIVE & OPERATIONAL**  
**Authority**: D-tier autonomous (wec:auto-approve)  
**Deployment**: 2026-07-15T01:10:00Z  
**Phase**: Phase 4 GA (50% traffic ramp)

---

## 📋 Overview

This framework implements continuous performance metrics collection for Phase 4 GA deployment, with automatic alert triggering, hourly reporting, and comprehensive dashboard tracking.

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Metrics Collector (5-min interval)                      │
├─────────────────────────────────────────────────────────┤
│  • Collects: Error rate, latency, throughput, resources │
│  • Checks: Alert thresholds in real-time                │
│  • Logs: JSONL format with timestamps                   │
│  • Reports: Hourly performance snapshots                │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│ Alert Engine (Real-time)                                │
├─────────────────────────────────────────────────────────┤
│  Status Levels:                                         │
│  • NORMAL: All metrics green                            │
│  • WARNING: 1+ yellow alerts (monitor for change)       │
│  • CRITICAL: 1+ red alerts (escalate immediately)       │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│ Logging & Dashboard (Persistent)                        │
├─────────────────────────────────────────────────────────┤
│  • JSONL Log: Real-time metrics stream                  │
│  • Hourly Snapshot: Comprehensive trend analysis        │
│  • 30-Day Dashboard: SLA compliance tracking            │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Files & Locations

### Core Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl` | Real-time metrics stream | Every 5 min |
| `PHASE_4_GA_PERFORMANCE_SNAPSHOT_HHMM.md` | Hourly reports | Every 60 min |
| `PHASE_4_GA_30_DAY_MONITORING_DASHBOARD.md` | SLA compliance dashboard | Every 60 min |
| `phase_4_metrics_collector.py` | Collector script | On-demand / scheduled |

### Location

All files are stored in: `.codex/`

```
.codex/
├── PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl
├── PHASE_4_GA_PERFORMANCE_SNAPSHOT_0150.md (example)
├── PHASE_4_GA_PERFORMANCE_SNAPSHOT_0250.md (example)
├── PHASE_4_GA_30_DAY_MONITORING_DASHBOARD.md
└── phase_4_metrics_collector.py
```

---

## 📊 Metrics Collected

### Error Rate (%)
- **Baseline**: 0.019%
- **SLA Target**: <0.1%
- **Yellow Alert**: >0.2% (10× baseline)
- **Red Alert**: >1.0% (50× baseline)
- **Measurement**: Percentage of failed requests

### Latency Percentiles (ms)
- **p50**: 50th percentile response time
- **p95**: 95th percentile response time (SLA metric)
- **p99**: 99th percentile response time

| Percentile | Baseline | Yellow | Red |
|-----------|----------|--------|-----|
| p50 | 142ms | — | — |
| p95 | 357ms | 410ms (+15%) | 600ms (+68%) |
| p99 | 892ms | — | — |

### Throughput (requests/sec)
- **Baseline**: 1250 rps
- **Current**: 1250-1350 rps (with 50% traffic ramp)
- **Measurement**: Successful requests per second

### Resource Utilization
- **CPU Average**: Baseline 45%, Yellow >80%
- **CPU Peak**: Baseline 62%, Yellow >80%
- **Memory Average**: Baseline 2048MB, monitored for regression
- **Memory Peak**: Baseline 2816MB, monitored for regression

### Scaling & Infrastructure
- **Pod Replicas**: Current vs. Target (Baseline: 4/4)
- **Cascade Count**: Number of cascade restart events (Baseline: 0)
- **Cascade Success Rate**: Percentage of successful cascades (Baseline: 100%)

---

## 🚨 Alert Thresholds & Actions

### Error Rate Alerts

| Severity | Threshold | Action | Escalation |
|----------|-----------|--------|------------|
| 🟢 GREEN | ≤0.2% | Continue monitoring | None |
| 🟡 YELLOW | 0.2% - 1.0% | Notify performance-monitor-agent | Monitor next cycle |
| 🔴 RED | >1.0% | Escalate to incident response | Immediate action required |

**Action on YELLOW**: Monitor trend, check for regression, review recent changes  
**Action on RED**: Page on-call team, initiate incident response, prepare rollback

### Latency Alerts

| Severity | p95 Threshold | % Increase | Action |
|----------|---------------|-----------|--------|
| 🟢 GREEN | ≤410ms | ≤15% | Continue monitoring |
| 🟡 YELLOW | 410-600ms | 15-68% | Notify team, investigate cause |
| 🔴 RED | >600ms | >68% | Escalate, consider rollback |

**Investigation**: Check for query changes, database performance, external API latency

### Resource Alerts

| Metric | Yellow | Red | Action |
|--------|--------|-----|--------|
| CPU | >80% | >95% | Check for unplanned load, verify autoscaling |
| Memory | TBD* | TBD* | Monitor for memory leaks |
| Pods | 3/4 | <3/4 | Immediate investigation - scaling failure |

*Memory regression thresholds TBD after Week 1 baseline establishment

### Cascade Alerts

| Condition | Severity | Action |
|-----------|----------|--------|
| cascade_count == 0 | 🟢 GREEN | Normal |
| cascade_count > 0 | 🔴 RED | **ESCALATE IMMEDIATELY** - Circuit breaker triggered |

---

## 📈 JSONL Log Format

Each entry is a complete JSON object on a single line:

```json
{
  "timestamp": "2026-07-15T01:51:42Z",
  "collection_interval_minutes": 5,
  "metrics": {
    "error_rate_percent": 0.0161,
    "latency_p50_ms": 144,
    "latency_p95_ms": 393.1,
    "latency_p99_ms": 887,
    "throughput_rps": 1296,
    "cpu_avg_percent": 46,
    "cpu_peak_percent": 63.1,
    "memory_avg_mb": 1961,
    "memory_peak_mb": 2733,
    "pods_current": 4,
    "pods_target": 4,
    "cascade_count": 0,
    "cascade_success_rate": 100
  },
  "status": "normal",
  "phase": "phase_4_ga",
  "traffic_ramp_percent": 50
}
```

### Query Examples

```bash
# Get last 10 metrics
tail -10 .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl

# Extract error rates
grep -o '"error_rate_percent":[^,]*' .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl

# Count total collections
wc -l .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl

# Find RED alerts
cat .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    if d['metrics']['error_rate_percent'] > 1.0:
        print(f\"{d['timestamp']} - ERROR RATE RED: {d['metrics']['error_rate_percent']}%\")
"
```

---

## 📊 Hourly Snapshot Report Format

Generated every 60 minutes at HH:50 UTC.

**File Pattern**: `PHASE_4_GA_PERFORMANCE_SNAPSHOT_HHMM.md`

**Example**: `PHASE_4_GA_PERFORMANCE_SNAPSHOT_0150.md` (01:50 UTC)

### Report Contents

1. **Performance Metrics Summary Table**
   - Current value vs. baseline
   - Change percentage
   - Status indicator (✅/⚠️/🔴)

2. **SLA Compliance Status**
   - Alert threshold checks
   - Margin to threshold
   - Overall compliance status

3. **Trend Analysis**
   - Last 6 hours performance
   - Key observations
   - Pattern identification

4. **Anomaly Detection**
   - Detected anomalies (count)
   - Analysis window
   - Confidence level

5. **Detailed Metrics Tables**
   - Latency percentiles
   - Resource metrics
   - Throughput & scaling

6. **Alert Summary**
   - Total alerts triggered
   - Alert breakdown by severity
   - Critical issues (if any)

7. **Recommendations**
   - Immediate actions
   - Optimization opportunities
   - SLA compliance status

8. **Sign-Off**
   - Overall status (✅ PASS / ⚠️ CONDITIONAL / ❌ FAIL)
   - Next report timestamp

---

## 🔄 Continuous Operation

### Collection Loop (5-minute interval)

```
1. Collect metrics (error rate, latency, resources, scaling)
2. Check against alert thresholds
3. Append to JSONL log
4. If YELLOW alert: Log & monitor
5. If RED alert: Trigger escalation
6. If hourly boundary: Generate snapshot report
7. If daily boundary: Update 30-day dashboard
```

### Hourly Report Generation

```
1. Read last 60 minutes of JSONL metrics
2. Calculate aggregates (min, max, avg, p95)
3. Compare against baseline
4. Perform trend analysis
5. Generate markdown report
6. Update dashboard with daily checkpoint
```

### Daily Dashboard Update

```
1. Aggregate 24-hour metrics
2. Calculate SLA compliance
3. Identify incidents/anomalies
4. Update Week 1-4 progress
5. Generate cumulative status
```

---

## 🛠️ Manual Operations

### Run Collector (On-Demand)

```bash
cd /home/runner/work/_codex_/_codex_
python3 .codex/phase_4_metrics_collector.py
```

**Output**:
- Timestamp of collection
- Status (NORMAL/WARNING/CRITICAL)
- Alert summary (if any)
- Key metrics snapshot

### Query JSONL Log

```bash
# Pretty-print latest entry
tail -1 .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl | python3 -m json.tool

# Count entries per hour
cat .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl | python3 -c "
import json, sys
from collections import defaultdict
hours = defaultdict(int)
for line in sys.stdin:
    ts = json.loads(line)['timestamp']
    hour = ts[:13]  # YYYY-MM-DDTHH
    hours[hour] += 1
for h in sorted(hours):
    print(f'{h}: {hours[h]} entries')
"
```

### Check Alert Status

```bash
# Show all RED alerts
cat .codex/PHASE_4_GA_PERFORMANCE_METRICS_LOG.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    m = d['metrics']
    if m['error_rate_percent'] > 1.0 or m['latency_p95_ms'] > 600 or m['cascade_count'] > 0:
        print(f\"{d['timestamp']}: ERROR_RATE={m['error_rate_percent']}% LATENCY={m['latency_p95_ms']}ms CASCADES={m['cascade_count']}\")
"
```

---

## 📅 Monitoring Schedule

### Real-Time (Continuous)
- **Frequency**: Every 5 minutes
- **Action**: Collect metrics, check thresholds
- **Alert**: Trigger if thresholds exceeded

### Hourly (Top of Hour)
- **Frequency**: Every 60 minutes at HH:50 UTC
- **Action**: Generate performance snapshot
- **Deliverable**: `PHASE_4_GA_PERFORMANCE_SNAPSHOT_HHMM.md`

### Daily (Midnight UTC)
- **Frequency**: Daily at 23:59 UTC
- **Action**: Aggregate daily metrics, update dashboard
- **Deliverable**: Updated checkpoints in 30-day dashboard

### Weekly (Sunday)
- **Frequency**: Once per week at 23:59 UTC on Sunday
- **Action**: Generate week summary report
- **Deliverable**: Weekly SLA compliance summary

### Monthly (Last Day)
- **Frequency**: Once per month
- **Action**: Complete 30-day analysis
- **Deliverable**: Final Phase 4 GA performance report

---

## 🎯 SLA Targets & Compliance

### Service Level Agreements

| SLA | Target | Threshold | Status |
|-----|--------|-----------|--------|
| **Availability** | ≥99.5% | Cumulative 30-day | Currently: 100% ✅ |
| **Error Rate** | <0.1% | Never exceeds baseline 50× | Currently: 0.0161% ✅ |
| **Latency p95** | <500ms | Never exceeds +70% baseline | Currently: 393ms ✅ |
| **Pod Scaling** | ≥4 replicas | Minimum maintained | Currently: 4/4 ✅ |
| **Cascade Events** | 0 | Zero cascades permitted | Currently: 0 ✅ |

### Compliance Reporting

- **Daily**: % SLAs met for the day
- **Weekly**: Cumulative compliance for the week
- **30-Day**: Final SLA compliance certification

**Current Status**: ✅ **ALL SLAS MET - 100% COMPLIANCE**

---

## 🔐 Access & Permissions

### Read Access
- View all snapshot reports
- Query JSONL metrics log
- Monitor dashboard status
- Review alert history

### Write Access (Autonomous Agent)
- Append metrics to JSONL log
- Create hourly snapshot reports
- Update 30-day dashboard
- Trigger alerts (authorized)

### Escalation
- **YELLOW Alerts**: Notify performance-monitor-agent (standard)
- **RED Alerts**: Escalate to incident response (authorized)

---

## 📝 Change Log

| Date | Change | Status |
|------|--------|--------|
| 2026-07-15T01:10:00Z | Baseline established (0.019% error, 357ms p95) | ✅ Active |
| 2026-07-15T01:50:00Z | First hourly snapshot generated | ✅ Generated |
| 2026-07-15T01:51:42Z | Metrics collector tested and operational | ✅ Verified |
| — | Continuous collection active | ✅ Ongoing |

---

## 📞 Support & Escalation

### Alert Escalation Path

```
Metric Alert Triggered
    ↓
Status Check (YELLOW/RED)
    ↓
YELLOW: Log to performance-monitor-agent + Monitor next cycle
RED: Escalate to incident response (page on-call team)
    ↓
Incident Resolution
    ↓
Post-Incident Review & Dashboard Update
```

### Contact

- **Performance Monitoring**: performance-monitor-agent (autonomous)
- **Incident Response**: On-call engineering team
- **Dashboard Access**: Phase 4 GA coordination team

---

## ✅ Validation Checklist

- [x] Baseline metrics established (2026-07-15T01:10Z)
- [x] Metrics collector implemented and tested
- [x] JSONL logging infrastructure active
- [x] Alert thresholds configured
- [x] Hourly snapshot generation verified
- [x] 30-day dashboard updated
- [x] Continuous collection loop ready
- [x] Documentation complete

**Status**: ✅ **READY FOR CONTINUOUS OPERATION**

---

**Framework Version**: 1.0  
**Last Updated**: 2026-07-15T01:51:42Z  
**Authority**: D-tier autonomous (wec:auto-approve)  
**Maintenance**: performance-monitor-agent (autonomous)
