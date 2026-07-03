# Phase 12 Track 3: Enterprise Monitoring Runbook
**Version:** 1.0.0-enterprise  
**Authority:** @mbaetiong (D-tier AUTO-GO)  
**Status:** Complete & Production Ready  
**Timeline:** Days 9-10 Deliverable (2026-07-09 → 2026-07-11)  
**Release Target:** v1.0.0-enterprise (2026-07-11)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Dashboard Setup & Configuration](#dashboard-setup)
3. [Alert Policy Customization](#alert-policies)
4. [Troubleshooting Procedures](#troubleshooting)
5. [Performance Optimization](#performance-optimization)
6. [Scalability Considerations](#scalability)
7. [Backup & Disaster Recovery](#backup-recovery)
8. [Quick Reference Guide](#quick-reference)

---

## <a name="overview"></a>📊 Overview

This runbook provides comprehensive guidance for operating the Phase 12 Track 3 enterprise observability and monitoring system. The system monitors 50+ critical metrics across four integration tracks and provides real-time dashboards, alerting, and incident analysis.

### System Components

| Component | Purpose | File | Status |
|-----------|---------|------|--------|
| **Metrics Engine** | Collect, aggregate, export metrics | `scripts/observability/metrics_engine.py` | ✅ Production |
| **Dashboard Engine** | Real-time dashboards, alerts, incidents | `scripts/observability/dashboard_engine.py` | ✅ Production |
| **Framework Document** | Metric taxonomy, SLOs, export specs | `.codex/OBSERVABILITY_FRAMEWORK.md` | ✅ Reference |
| **System Metrics Collector** | OS-level metrics (CPU, memory, disk, network) | `scripts/observability/metrics_engine.py` | ✅ Embedded |

### Integration Points

```
Track 12.1 (RBAC)              Track 12.2 (Governance)         Phase 10 (Cognitive)
├─ Permission checks           ├─ Approval workflows           ├─ Session metrics
├─ Role assignments           ├─ Compliance status            ├─ OODA cycles
├─ Unauthorized attempts      ├─ Audit events                 ├─ Memory consolidation
│                              │                                │
└─────────────────────────────┴────────────────────────────────┘
                               │
                    Metrics Collection Engine
                               │
                ┌──────────────┬──────────────┐
                │              │              │
          Real-Time      Alert Manager    Metrics Cache
          Dashboard      (P0-P3)          (Time-series)
                │              │              │
                └──────────────┼──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         Prometheus      CloudWatch          JSON
         Export         Export            Export
```

---

## <a name="dashboard-setup"></a>🎛️ Dashboard Setup & Configuration

### 1. Initial Setup (First Run)

#### Step 1: Verify Metrics Engine

```bash
# Check that metrics engine is running
python scripts/observability/metrics_engine.py &
METRICS_PID=$!

# Wait for engine to initialize
sleep 5

# Verify export directory
ls -la metrics_export/

# You should see files like:
# - metrics.prom (Prometheus format)
# - metrics_<timestamp>.json (JSON exports)
```

#### Step 2: Start Dashboard Engine

```bash
# Start dashboard in separate session
python scripts/observability/dashboard_engine.py &
DASHBOARD_PID=$!

# Verify dashboard is accepting updates
sleep 3
echo "Dashboard started with PID: $DASHBOARD_PID"
```

#### Step 3: Test Metric Flow

```python
# Test script: test_metrics_flow.py
from scripts.observability.metrics_engine import create_metrics_engine
from scripts.observability.dashboard_engine import create_dashboard_engine
import time

# Create both engines
collector, system = create_metrics_engine()
dashboard = create_dashboard_engine()

# Register collectors to dashboard
def export_to_dashboard(metrics):
    for metric in metrics:
        dashboard.update_metric_value(metric.metric_id, metric.p99)

collector.register_export_handler(export_to_dashboard)

# Run test for 10 seconds
for i in range(10):
    # Simulate metric updates
    collector.record_metric('sys.health_score', 95 + (i % 5))
    collector.record_metric('rbac.permission_check_latency_ms', 5 + (i % 15))
    
    # Check dashboard state
    snapshot = dashboard.get_dashboard_snapshot()
    print(f"Health: {snapshot['health_scorecard']['overall_score']:.1f}")
    time.sleep(1)

# Export dashboard snapshot
from scripts.observability.dashboard_engine import DashboardExporter
html = DashboardExporter.to_html_summary(dashboard, 'dashboard_snapshot.html')
print("Dashboard snapshot saved to dashboard_snapshot.html")

system.stop()
collector.stop()
dashboard.stop()
```

### 2. Dashboard Configuration

#### Standard Dashboard Widgets

| Dashboard | Widgets | Refresh | Purpose |
|-----------|---------|---------|---------|
| **System Health** | Health gauge, uptime, error rate | <1s | Overall system status |
| **RBAC Security** | Permission latency, denials, unauthorized | <2s | Security monitoring |
| **Governance** | Compliance %, pending approvals, SLA status | <3s | Governance tracking |
| **Cognitive** | Session restore, OODA cycles, memory | <1s | AI/ML system health |
| **Agent Performance** | Throughput, queue depth, errors | <2s | Agent operation |
| **Incident Management** | Active incidents, alerts, correlations | <5s | Incident response |

#### Custom Widget Configuration

To add a custom widget:

```python
from scripts.observability.dashboard_engine import (
    DashboardEngine,
    DashboardMetric,
    DashboardWidget
)

engine = DashboardEngine()

# Register custom widget
custom_widget = DashboardMetric(
    widget_id='custom_widget_1',
    metric_id='your.custom.metric',
    widget_type=DashboardWidget.TIMESERIES,
    title='Your Custom Metric',
    unit='ms',
    min_value=0,
    max_value=1000,
    refresh_interval_ms=2000,
    alert_thresholds={
        'warning': 700,
        'critical': 900,
    }
)

engine.register_widget(custom_widget)
engine.start()
```

### 3. Dashboard Access & Viewing

#### Export Formats

```bash
# Export as JSON
python -c "
from scripts.observability.dashboard_engine import DashboardExporter, create_dashboard_engine
engine = create_dashboard_engine()
json_output = DashboardExporter.to_json(engine)
print(json_output)
"

# Export as HTML summary
python -c "
from scripts.observability.dashboard_engine import DashboardExporter, create_dashboard_engine
engine = create_dashboard_engine()
html = DashboardExporter.to_html_summary(engine, 'dashboard.html')
"

# View dashboard in browser
open dashboard.html
```

---

## <a name="alert-policies"></a>🚨 Alert Policy Customization

### 1. Alert Rule Structure

```python
from scripts.observability.metrics_engine import AlertRule, Severity

# Create custom alert rule
rule = AlertRule(
    alert_id='custom_p0_alert',
    metric_id='sys.error_rate',
    condition='>',  # ">" | "<" | ">=" | "<=" | "==" | "!="
    threshold=1.0,  # Error rate > 1%
    duration_seconds=300,  # Alert if true for 5 minutes
    severity=Severity.P0,  # P0 (critical) | P1 (high) | P2 (medium) | P3 (low)
    enabled=True,
    message='System error rate exceeded 1%',
    action_handler=None,  # Optional callback function
)

# Register with collector
collector.register_alert_rule(rule)
```

### 2. Pre-configured Alert Rules

#### P0 (Critical) Alerts

| Alert ID | Metric | Condition | Threshold | Duration | Action |
|----------|--------|-----------|-----------|----------|--------|
| `p0.system_down` | sys.uptime | < | 95% | 5min | Page on-call, lock system |
| `p0.critical_breach` | gov.policy_violations | > | 0 | 1min | Page CISO, create incident |
| `p0.rbac_failure` | rbac.permission_check_latency_ms | > | 1000 | 2min | Page auth team |
| `p0.data_loss_risk` | sys.disk_usage | > | 95% | 1min | Alert infra team |

#### P1 (High) Alerts

| Alert ID | Metric | Condition | Threshold | Duration |
|----------|--------|-----------|-----------|----------|
| `p1.performance_degradation` | sys.network_latency_ms | > | 500 | 5min |
| `p1.rbac_anomaly` | rbac.unauthorized_attempts | > | 5/min | 10min |
| `p1.cognitive_slowdown` | cog.session_restore_time_ms | > | 5000 | 5min |
| `p1.governance_delay` | gov.approval_workflow_latency_ms | > | 3600000 | 15min |

### 3. Alert Customization

#### Add Custom Action Handler

```python
import logging

def custom_alert_handler(rule):
    """Custom action when alert triggers."""
    logger.warning(f"ALERT TRIGGERED: {rule.alert_id}")
    
    # Send to external system
    send_to_slack(f"🚨 {rule.message}")
    
    # Create incident ticket
    create_jira_ticket(
        summary=rule.alert_id,
        description=f"Alert: {rule.message}",
        priority="Critical" if rule.severity.name == "P0" else "High"
    )
    
    # Trigger auto-remediation (if applicable)
    if rule.alert_id == 'p0.system_down':
        trigger_failover()

# Register handler with alert rule
rule.action_handler = custom_alert_handler
```

#### Modify Alert Thresholds

```python
# Example: Make RBAC permission checks stricter
permission_check_rule = AlertRule(
    alert_id='p1.rbac_permission_latency',
    metric_id='rbac.permission_check_latency_ms',
    condition='>',
    threshold=5,  # Changed from 10ms to 5ms
    duration_seconds=60,  # Changed from 120s to 60s
    severity=Severity.P1,
)

collector.register_alert_rule(permission_check_rule)
```

### 4. Alert Suppression

```python
# Suppress alerts during maintenance window
from datetime import datetime, timedelta

maintenance_start = datetime.utcnow()
maintenance_end = maintenance_start + timedelta(hours=2)

# Mark alerts as suppressed
for rule_id, rule in collector.alert_rules.items():
    if rule.severity in [Severity.P0, Severity.P1]:
        rule.enabled = False

print(f"Alerts suppressed until {maintenance_end}")

# ... perform maintenance ...

# Re-enable alerts
for rule_id, rule in collector.alert_rules.items():
    rule.enabled = True
print("Alerts re-enabled")
```

---

## <a name="troubleshooting"></a>🔧 Troubleshooting Procedures

### 1. Metrics Not Being Collected

**Symptom:** Dashboard shows no data or flat metrics

**Diagnosis:**
```bash
# Check if metrics engine is running
ps aux | grep metrics_engine.py

# Check for errors in logs
tail -f /var/log/metrics_engine.log

# Verify metrics are being written
ls -la metrics_export/
du -sh metrics_export/
```

**Common Causes & Fixes:**

| Cause | Symptom | Fix |
|-------|---------|-----|
| Engine not started | No metrics files in `metrics_export/` | Run `python scripts/observability/metrics_engine.py` |
| Permissions issue | Cannot write to `metrics_export/` | `chmod 755 metrics_export/` or check disk space |
| Memory pressure | Metrics drop sporadically | Reduce buffer size: `TimeSeriesBuffer(max_points=1800)` |
| Network issue | Cannot export to Prometheus/CloudWatch | Check network connectivity, auth credentials |

**Recovery:**
```bash
# Restart metrics engine
pkill -f metrics_engine.py
sleep 2
python scripts/observability/metrics_engine.py &

# Verify recovery
sleep 10
ls -la metrics_export/metrics.prom
```

### 2. High Alert Noise (False Positives)

**Symptom:** Too many P1/P2 alerts firing, masking real issues

**Diagnosis:**
```python
# Check alert rate
from scripts.observability.dashboard_engine import DashboardEngine

engine = DashboardEngine()
snapshot = engine.get_dashboard_snapshot()

# Print active alerts
for alert in snapshot['alerts']['active']:
    print(f"{alert['alert_id']}: {alert['message']}")

# Count by severity
summary = snapshot['alerts']['summary']
print(f"P0: {summary.get('P0', 0)}, P1: {summary.get('P1', 0)}, P2: {summary.get('P2', 0)}")
```

**Solutions:**

1. **Increase threshold values** (for non-critical metrics)
   ```python
   # Original: RBAC latency > 10ms for 60s triggers alert
   # New: RBAC latency > 20ms for 120s triggers alert
   rule.threshold = 20
   rule.duration_seconds = 120
   ```

2. **Add hysteresis** (require sustained condition)
   ```python
   # Only alert if metric stays above threshold for 5+ minutes
   rule.duration_seconds = 300
   ```

3. **Reduce severity** (downgrade non-critical alerts)
   ```python
   # Change from P1 to P2 to reduce page spam
   rule.severity = Severity.P2
   ```

### 3. Dashboard Slow or Unresponsive

**Symptom:** Dashboard takes >2s to refresh, UI freezes

**Diagnosis:**
```python
# Check dashboard snapshot generation time
import time
from scripts.observability.dashboard_engine import DashboardEngine

engine = DashboardEngine()

start = time.time()
snapshot = engine.get_dashboard_snapshot()
elapsed = time.time() - start

print(f"Snapshot generation: {elapsed:.3f}s")
print(f"Widgets: {len(snapshot['widgets'])}")
print(f"Alerts: {len(snapshot['alerts']['active'])}")
print(f"Incidents: {len(snapshot['incidents'])}")
```

**Performance Bottlenecks:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| Too many widgets | Snapshot >1s | Remove unused widgets, reduce history size |
| Large history | Memory usage grows | Reduce `MetricsCache.max_history` |
| Slow subscribers | Callbacks taking >100ms | Async notify subscribers, batch updates |

**Optimization:**
```python
# Reduce metric history window (from 1h to 30min)
metrics_cache = MetricsCache(max_history=1800)

# Remove unused widgets
engine.widgets = {
    k: v for k, v in engine.widgets.items()
    if k in ['health_gauge', 'error_rate_stat']
}

# Increase export interval (aggregate every 120s instead of 60s)
collector = MetricsCollector(export_interval_seconds=120)
```

### 4. Missing Metrics from Specific Tracks

**Symptom:** Dashboard shows some metrics but not Track 12.1 (RBAC) or Track 12.2 (Governance) metrics

**Diagnosis:**
```python
from scripts.observability.metrics_engine import create_metrics_engine

collector, system = create_metrics_engine()

# Check registered metrics
rbac_metrics = [m for m in collector.registry.list_metrics() if m.startswith('rbac.')]
gov_metrics = [m for m in collector.registry.list_metrics() if m.startswith('gov.')]
cog_metrics = [m for m in collector.registry.list_metrics() if m.startswith('cog.')]

print(f"RBAC metrics: {len(rbac_metrics)}")
print(f"Governance metrics: {len(gov_metrics)}")
print(f"Cognitive metrics: {len(cog_metrics)}")
```

**Integration Issues:**

| Track | Typical Issue | Fix |
|-------|---------------|-----|
| **12.1 (RBAC)** | Permission metrics not flowing | Ensure `rbac.permission_check_latency_ms` is being recorded |
| **12.2 (Governance)** | Approval workflow metrics missing | Check workflow engine is calling `collector.record_metric()` |
| **Phase 10 (Cognitive)** | Session restore time not updating | Verify cognitive session API is instrumented |

**Recovery:**
```python
# Manually register missing metrics
collector.register_metric(
    'rbac.permission_check_latency_ms',
    'Permission Check Latency',
    MetricType.HISTOGRAM,
    unit='ms',
    slo_target='<10ms p99'
)

# Manually inject test data
collector.record_metric('rbac.permission_check_latency_ms', 7.5)
collector.record_metric('gov.compliance_status_pct', 100.0)
collector.record_metric('cog.session_restore_time_ms', 350.0)
```

---

## <a name="performance-optimization"></a>⚡ Performance Optimization

### 1. Metrics Engine Tuning

#### Aggregation Interval

```python
# Default: 60 second intervals
collector = MetricsCollector(export_interval_seconds=60)

# For high-frequency systems, reduce to 30s
collector = MetricsCollector(export_interval_seconds=30)

# For lower-frequency systems, increase to 120s
collector = MetricsCollector(export_interval_seconds=120)
```

**Trade-offs:**
- **Shorter intervals** (30s): More responsive alerts, higher CPU/memory
- **Longer intervals** (120s): Lower overhead, but slower to detect issues

#### Time-Series Buffer Size

```python
# Default: 3600 points (1 hour at 1Hz)
buffer = TimeSeriesBuffer(max_points=3600)

# For memory-constrained systems
buffer = TimeSeriesBuffer(max_points=1800)  # 30 minutes

# For extended history
buffer = TimeSeriesBuffer(max_points=7200)  # 2 hours
```

**Memory Usage:**
- ~8KB per 100 points
- Default (3600): ~288KB per metric
- With 50 metrics: ~14.4MB total

### 2. Dashboard Optimization

#### Widget Refresh Rates

```python
# Critical metrics: <1s refresh
widget.refresh_interval_ms = 1000  # System health

# Standard metrics: <2s refresh
widget.refresh_interval_ms = 2000  # RBAC, Cognitive

# Non-critical: <5s refresh
widget.refresh_interval_ms = 5000  # Governance trends
```

#### History Window

```python
# Default: 5-minute history
history = engine.metrics_cache.get_history(metric_id, minutes=5)

# For trending analysis: 1-hour history
history = engine.metrics_cache.get_history(metric_id, minutes=60)

# For real-time only: 30-second history
history = engine.metrics_cache.get_history(metric_id, minutes=0.5)
```

### 3. Export Performance

#### Prometheus Export

```bash
# Export every 60 seconds (default)
# File size: ~50KB for 50 metrics

# Optimize for high-cardinality metrics
# Use label-based filtering in Prometheus config
global:
  scrape_interval: 60s
  evaluation_interval: 60s

scrape_configs:
  - job_name: 'codex_metrics'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:9090']
```

#### JSON Export

```bash
# Default: New file every 60s
# Size: ~100KB per file

# Cleanup old exports periodically
find metrics_export/ -name 'metrics_*.json' -mtime +7 -delete

# Compress old files
tar -czf metrics_export_backup_$(date +%Y%m%d).tar.gz metrics_export/
```

---

## <a name="scalability"></a>📈 Scalability Considerations

### 1. System Load Testing

#### Test with Simulated Load

```python
# Test with 100 metrics updating every second
import concurrent.futures
from scripts.observability.metrics_engine import create_metrics_engine
import random
import time

collector, system = create_metrics_engine()

def simulate_metric_stream(metric_id, count=1000):
    """Simulate metric updates."""
    for i in range(count):
        collector.record_metric(metric_id, random.uniform(0, 100))
        if i % 100 == 0:
            print(f"  {metric_id}: {i} updates")
        time.sleep(0.001)

# Run load test with thread pool
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = []
    for i in range(100):
        metric_id = f'test.metric_{i}'
        collector.register_metric(metric_id, f'Test Metric {i}', MetricType.GAUGE)
        futures.append(executor.submit(simulate_metric_stream, metric_id))
    
    concurrent.futures.wait(futures)

print("Load test complete")
```

#### Monitor Resource Usage

```bash
# Watch CPU, memory, disk during load test
watch -n 1 'ps aux | grep metrics_engine | grep -v grep'

# Check metrics file growth
watch -n 1 'du -sh metrics_export/'

# Monitor disk I/O
iostat -x 1 10
```

### 2. Scaling Strategies

#### Horizontal Scaling (Multiple Collectors)

```
┌──────────────────┐
│  Metrics Shard 1 │ → RBAC metrics (Track 12.1)
├──────────────────┤
│  Metrics Shard 2 │ → Governance metrics (Track 12.2)
├──────────────────┤
│  Metrics Shard 3 │ → Cognitive metrics (Phase 10)
├──────────────────┤
│  Metrics Shard 4 │ → System metrics
└──────────────────┘
         │
    ┌────┴────┐
    │          │
Aggregator   Dashboard
  (1 master)  (read-only)
```

**Implementation:**
```python
# Shard by metric prefix
shards = {
    'rbac': MetricsCollector(),
    'gov': MetricsCollector(),
    'cog': MetricsCollector(),
    'sys': MetricsCollector(),
}

# Register metrics to appropriate shard
shards['rbac'].register_metric('rbac.permission_check_latency_ms', ...)
shards['gov'].register_metric('gov.compliance_status_pct', ...)

# Aggregate for dashboard
def aggregate_all(dashboard):
    for shard_name, collector in shards.items():
        metrics = collector._aggregate_all()
        for metric in metrics:
            dashboard.update_metric_value(metric.metric_id, metric.p99)
```

#### Vertical Scaling (Bigger Machine)

**Resource Targets:**
- **CPU:** <50% utilization for sustained load
- **Memory:** <4GB for 1000+ metrics
- **Disk:** SSD preferred, <500MB/hour growth

---

## <a name="backup-recovery"></a>💾 Backup & Disaster Recovery

### 1. Metrics Backup Strategy

#### Daily Backup

```bash
#!/bin/bash
# backup_metrics.sh

BACKUP_DIR=/backups/metrics
DATE=$(date +%Y%m%d)
METRICS_EXPORT=./metrics_export

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup metrics files
cp -r $METRICS_EXPORT/* $BACKUP_DIR/$DATE/

# Compress
tar -czf $BACKUP_DIR/metrics_$DATE.tar.gz $BACKUP_DIR/$DATE/

# Keep last 7 days
find $BACKUP_DIR -name 'metrics_*.tar.gz' -mtime +7 -delete

echo "Metrics backup complete: $BACKUP_DIR/metrics_$DATE.tar.gz"
```

**Schedule with cron:**
```bash
# Daily at 2 AM
0 2 * * * /scripts/backup_metrics.sh
```

#### Export to Cold Storage

```python
import boto3
from datetime import datetime

def archive_metrics_to_s3(bucket_name, retention_days=90):
    """Archive old metrics to S3."""
    s3 = boto3.client('s3')
    
    # Find files older than retention period
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    
    for file in Path('metrics_export').glob('metrics_*.json'):
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        if file_time < cutoff:
            # Upload to S3
            key = f'metrics/archive/{file.name}'
            s3.upload_file(str(file), bucket_name, key)
            print(f"Archived {file.name} to S3")
            
            # Delete local copy
            file.unlink()
```

### 2. Disaster Recovery

#### Full System Recovery

**Scenario:** Metrics engine crashes, need to rebuild dashboard state

```python
# recovery_script.py
from pathlib import Path
from scripts.observability.metrics_engine import create_metrics_engine
from scripts.observability.dashboard_engine import create_dashboard_engine
import json

# 1. Create fresh engines
collector, system = create_metrics_engine()
dashboard = create_dashboard_engine()

# 2. Restore from backups
backup_dir = Path('/backups/metrics/latest')
for backup_file in backup_dir.glob('metrics_*.json'):
    with open(backup_file) as f:
        data = json.load(f)
        for metric in data['metrics']:
            collector.record_metric(
                metric['metric_id'],
                metric['value'],
                labels=metric['labels']
            )

print("Dashboard recovered from backups")

# 3. Verify integrity
snapshot = dashboard.get_dashboard_snapshot()
print(f"Recovered {len(snapshot['widgets'])} widgets")
print(f"Health score: {snapshot['health_scorecard']['overall_score']:.1f}")
```

### 3. Testing Recovery Procedures

#### Disaster Recovery Drill

```bash
#!/bin/bash
# dr_drill.sh - Monthly disaster recovery test

# 1. Backup current state
cp -r metrics_export metrics_export_backup_$(date +%Y%m%d)

# 2. Simulate failure by clearing metrics
rm -rf metrics_export/*

# 3. Run recovery
python recovery_script.py

# 4. Verify recovery
python -c "
from scripts.observability.dashboard_engine import create_dashboard_engine
engine = create_dashboard_engine()
snapshot = engine.get_dashboard_snapshot()
print(f'Health: {snapshot[\"health_scorecard\"][\"overall_score\"]:.1f}')
"

# 5. Restore original state
rm -rf metrics_export
mv metrics_export_backup_$(date +%Y%m%d) metrics_export

echo "DR Drill complete"
```

---

## <a name="quick-reference"></a>⚡ Quick Reference Guide

### Common Commands

```bash
# Start all monitoring services
python scripts/observability/metrics_engine.py &
python scripts/observability/dashboard_engine.py &

# Check service health
ps aux | grep observability

# View latest metrics
cat metrics_export/metrics.prom

# Export current snapshot
python -c "
from scripts.observability.dashboard_engine import DashboardExporter, create_dashboard_engine
engine = create_dashboard_engine()
DashboardExporter.to_html_summary(engine, 'dashboard.html')
print('Snapshot exported to dashboard.html')
"

# Stop services
pkill -f metrics_engine.py
pkill -f dashboard_engine.py
```

### Key Metrics to Monitor

| Metric | SLO | Alert Threshold |
|--------|-----|-----------------|
| `sys.uptime` | 99.99% | < 95% |
| `sys.health_score` | > 95 | < 80 |
| `sys.error_rate` | < 0.1% | > 1% |
| `rbac.permission_check_latency_ms` | < 10ms p99 | > 50ms |
| `cog.session_restore_time_ms` | < 500ms p99 | > 5s |
| `gov.compliance_status_pct` | 100% | < 100% |

### Emergency Escalation

```
[Alert Triggered]
    │
    ├─ P0 (Critical): Page on-call immediately (<5 min)
    ├─ P1 (High): Create ticket, notify team lead (<15 min)
    ├─ P2 (Medium): Create ticket, track in standup (<30 min)
    └─ P3 (Low): Log in dashboard, track trend (<60 min)
```

---

## 📞 Support & Escalation

### Getting Help

**For Metrics Issues:**
- Check metrics_export directory for recent files
- Verify system_collector thread is running
- Check disk space and permissions

**For Dashboard Issues:**
- Clear browser cache and reload
- Verify dashboard_engine process is running
- Check metrics are being updated (tail metrics.prom)

**For Integration Issues:**
- Verify Track 12.1, 12.2, Phase 10 systems are running
- Check metric IDs match framework document
- Run integration test suite

### Escalation Path

1. **Auto-diagnosis:** Check common issues in Troubleshooting section
2. **Team Notification:** Alert appropriate team (infra, auth, governance, ML)
3. **Incident Creation:** Create incident ticket with snapshot
4. **Executive Escalation:** For P0 breaches, escalate to @mbaetiong

---

## ✅ Verification Checklist

**Before Enterprise Deployment:**

- [ ] All 50+ metrics registered and flowing
- [ ] Dashboard refresh <1s (p99)
- [ ] All P0 alerts <5s trigger latency
- [ ] Track 12.1 RBAC metrics integrated
- [ ] Track 12.2 Governance metrics integrated
- [ ] Phase 10 Cognitive metrics integrated
- [ ] 100% SLO compliance across all services
- [ ] Backup procedures tested
- [ ] DR recovery tested
- [ ] Performance load test passed
- [ ] Export to Prometheus/CloudWatch verified
- [ ] Alert escalation procedures documented

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0-enterprise  
**Last Updated:** 2026-07-11  
**Maintained By:** Phase 12 Track 3 Team  
**Authority:** @mbaetiong (D-tier)

---

*For questions or updates, contact the Phase 12 Track 3 team or file an issue on the internal tracking system.*
