# Alert Rules Documentation

**Document Version:** 1.0  
**Last Updated:** 2026-06-20  
**Status:** Complete

## Overview

This document describes the alert rules and recording rules deployed in the monitoring stack. The rules are designed to provide comprehensive coverage of critical infrastructure and application metrics.

## Alert Rules (13 Total)

### Application Alerts (4 rules)

#### 1. HighErrorRate
**Severity:** CRITICAL  
**Expression:** `rate(http_requests_total{status=~"5.."}[5m]) > 0.05`  
**Duration:** 5 minutes  
**Description:** Triggers when error rate exceeds 5% for 5 minutes

**Impact:** Application serving incorrect responses  
**Response:** Investigate application logs, check for failures, rollback if needed  
**Threshold Rationale:** 5% error rate indicates significant issues (typical is <0.1%)

#### 2. HighLatency
**Severity:** WARNING  
**Expression:** `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0`  
**Duration:** 5 minutes  
**Description:** Triggers when P95 latency exceeds 1 second for 5 minutes

**Impact:** Degraded user experience  
**Response:** Check application performance, database queries, external services  
**Threshold Rationale:** 1 second P95 latency is typical SLA threshold

#### 3. ServiceDown
**Severity:** CRITICAL  
**Expression:** `up{job='kubernetes-pods'} == 0`  
**Duration:** 1 minute  
**Description:** Triggers when service is unreachable

**Impact:** Service unavailable to users  
**Response:** Immediate incident response, check logs, investigate deployment  
**Threshold Rationale:** Any downtime is critical

#### 4. (Implicit) - No Alert Name (Custom Application)
**Purpose:** Custom application monitoring  
**Available for:** Application-specific metrics

### Resource Alerts (4 rules)

#### 5. HighCPUUsage
**Severity:** WARNING  
**Expression:** `rate(container_cpu_usage_seconds_total[5m]) > 0.85`  
**Duration:** 5 minutes  
**Description:** Triggers when CPU usage exceeds 85%

**Impact:** Reduced performance, potential throttling  
**Response:** Check for resource limits, scale horizontally, optimize code  
**Threshold Rationale:** 85% usage leaves limited headroom

#### 6. HighMemoryUsage
**Severity:** WARNING  
**Expression:** `container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9`  
**Duration:** 5 minutes  
**Description:** Triggers when memory usage exceeds 90% of limit

**Impact:** OOMKill risk, performance degradation  
**Response:** Increase memory limit, optimize memory usage, investigate leaks  
**Threshold Rationale:** High memory pressure indicates imminent failure

#### 7. DiskSpaceRunningOut
**Severity:** CRITICAL  
**Expression:** `(node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.15`  
**Duration:** 5 minutes  
**Description:** Triggers when available disk space < 15%

**Impact:** Cannot write new data, application failure imminent  
**Response:** Immediate cleanup, expand storage, investigate growth  
**Threshold Rationale:** 15% free space is critical threshold

#### 8. HighNetworkTraffic
**Severity:** WARNING  
**Expression:** `rate(node_network_transmit_bytes_total[5m]) > 100000000`  
**Duration:** 5 minutes  
**Description:** Triggers when network bandwidth exceeds 100 MB/s

**Impact:** Potential network saturation  
**Response:** Investigate traffic patterns, check for DDoS, optimize transfers  
**Threshold Rationale:** 100 MB/s indicates unusual traffic patterns

### Kubernetes Alerts (4 rules)

#### 9. PodCrashLooping
**Severity:** CRITICAL  
**Expression:** `rate(kube_pod_container_status_restarts_total[15m]) > 0.1`  
**Duration:** 5 minutes  
**Description:** Triggers when pod restarts frequently (>0.1 restarts/min)

**Impact:** Service instability, data loss risk  
**Response:** Check pod logs, investigate application errors, fix root cause  
**Threshold Rationale:** Frequent restarts indicate serious issues

#### 10. NodeNotReady
**Severity:** CRITICAL  
**Expression:** `kube_node_status_condition{condition='Ready',status='true'} == 0`  
**Duration:** 5 minutes  
**Description:** Triggers when node is not in Ready state

**Impact:** Pods cannot be scheduled, reduced capacity  
**Response:** Check node health, investigate kubelet, potentially restart node  
**Threshold Rationale:** Non-ready nodes impact scheduling

#### 11. PVCAlmostFull
**Severity:** WARNING  
**Expression:** `(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) > 0.85`  
**Duration:** 5 minutes  
**Description:** Triggers when PVC usage exceeds 85%

**Impact:** Storage exhaustion risk  
**Response:** Expand PVC, cleanup data, investigate growth  
**Threshold Rationale:** 85% indicates approaching full capacity

#### 12. StatefulSetReplicasMismatch
**Severity:** WARNING  
**Expression:** `kube_statefulset_status_replicas_ready != kube_statefulset_status_replicas`  
**Duration:** 5 minutes  
**Description:** Triggers when not all replicas are ready

**Impact:** Reduced redundancy, potential service impact  
**Response:** Check pod status, investigate failures, scale if needed  
**Threshold Rationale:** Replicas should always match

### Monitoring System Alerts (2 rules)

#### 13. AlertmanagerConfigReloadFailed
**Severity:** CRITICAL  
**Expression:** `alertmanager_config_last_reload_successful == 0`  
**Duration:** 5 minutes  
**Description:** Triggers when AlertManager fails to reload configuration

**Impact:** Alert routing may be broken  
**Response:** Check configuration syntax, fix errors, manual reload  
**Threshold Rationale:** Configuration failures disable alerting

#### 14. AlertmanagerFilingNotifications
**Severity:** WARNING  
**Expression:** `rate(alertmanager_notifications_failed_total[5m]) > 0.01`  
**Duration:** 5 minutes  
**Description:** Triggers when >1% of notifications fail

**Impact:** Alerts not reaching operators  
**Response:** Check notification channel credentials, investigate failures  
**Threshold Rationale:** Some failures acceptable, but track trend

## Recording Rules (15 Total)

Recording rules pre-compute frequently used expressions for faster query performance.

### HTTP Metrics Group (6 rules)

- `http:requests:rate1m` - 1-minute request rate
- `http:requests:rate5m` - 5-minute request rate
- `http:errors:rate5m` - 5-minute error rate
- `http:latency:p50` - P50 latency percentile
- `http:latency:p95` - P95 latency percentile
- `http:latency:p99` - P99 latency percentile

### CPU/Memory Metrics Group (4 rules)

- `node:cpu:usage` - Node CPU usage percentage
- `node:memory:usage` - Node memory usage percentage
- `container:cpu:usage` - Container CPU usage rate
- `container:memory:usage` - Container memory usage ratio

### Disk/Network Metrics Group (5 rules)

- `node:disk:usage` - Node disk usage percentage
- `node:disk:iops_read` - Disk read IOPS
- `node:disk:iops_write` - Disk write IOPS
- `node:network:in` - Network inbound traffic
- `node:network:out` - Network outbound traffic

## Alert Routing

### Severity-Based Routing

```
├── CRITICAL
│   ├── PagerDuty (immediate)
│   └── Repeat interval: 4 hours
│
├── WARNING
│   ├── Slack #alerts-warning
│   └── Repeat interval: 24 hours
│
└── INFO
    ├── Email notifications
    └── Repeat interval: 7 days
```

### Group Configuration

- **Group By:** alertname, cluster, service
- **Group Wait:** 10 seconds (collect related alerts)
- **Group Interval:** 10 seconds (resend group)
- **Repeat Interval:** 12 hours (default)

## Notification Channels

### PagerDuty
- **Severity:** CRITICAL
- **Channel:** PagerDuty incident creation
- **Configuration:** Requires service key
- **Format:** Incident with severity and cluster labels

### Slack
- **Severity:** WARNING
- **Channel:** #alerts-warning
- **Configuration:** Requires webhook URL
- **Format:** Rich message with alert details

### Email
- **Severity:** INFO
- **Recipients:** alerts@example.com
- **Configuration:** SMTP credentials required
- **Format:** Email with alert summary

## Alert Inhibition

Inhibition rules prevent alert storms:

1. **Info suppressed by Warning**
   - When WARNING alert fires for same resource, INFO alerts are suppressed

2. **Warning suppressed by Critical**
   - When CRITICAL alert fires for same resource, WARNING alerts are suppressed

**Effect:** Users see only the most severe issue for each resource

## Threshold Tuning

### Adjusting Alert Thresholds

All thresholds can be adjusted in `scripts/deployment/generate_alert_rules.py`:

```python
def generate_alert_rules() -> Dict[str, Any]:
    return {
        "groups": [
            {
                "name": "application_alerts",
                "rules": [
                    {
                        "alert": "HighErrorRate",
                        "expr": 'rate(http_requests_total{status=~"5.."}[5m]) > 0.05',  # <-- ADJUST HERE
```

### Common Adjustments

| Alert | Current Threshold | Lower | Higher |
|-------|------------------|-------|--------|
| HighErrorRate | 5% | 2% (stricter) | 10% (lenient) |
| HighLatency | 1s | 500ms | 2s |
| HighCPUUsage | 85% | 75% | 95% |
| HighMemoryUsage | 90% | 80% | 95% |
| DiskSpaceRunningOut | 15% free | 20% | 10% |

## Monitoring the Monitoring Stack

The monitoring stack includes self-monitoring:

- **prometheus_config_last_reload_successful** - Configuration reload status
- **prometheus_tsdb_symbol_table_size_bytes** - Database size
- **alertmanager_alerts** - Active alert count
- **alertmanager_notifications_total** - Notification counts

Access these via Prometheus UI: http://prometheus:9090/metrics

## Best Practices

1. **Alert Naming:** Use descriptive names that clearly indicate the problem
2. **Severity Levels:** Use appropriate severity (avoid alert fatigue)
3. **Duration:** Allow time for transient issues (5-10 minutes)
4. **Annotations:** Provide clear remediation steps
5. **Testing:** Test alert rules in staging before production
6. **Review:** Quarterly review of alert effectiveness
7. **Tuning:** Adjust thresholds based on actual metrics distribution

## Maintenance

### Monthly Tasks
- Review alert firing patterns
- Identify noisy alerts (tune thresholds)
- Verify notification channels working
- Check alert response effectiveness

### Quarterly Tasks
- Review alert coverage for new services
- Update alert thresholds based on metrics trends
- Train on-call engineers on alert meanings
- Archive old alert history

## Troubleshooting

### Alerts Not Firing
1. Check Prometheus scrape targets are up
2. Verify alert rule syntax: `kubectl logs prometheus`
3. Test PromQL expression manually
4. Check if metrics exist: `prometheus:9090/targets`

### Alerts Firing Incorrectly
1. Review alert expression and thresholds
2. Check metric values: `prometheus:9090/graph`
3. Adjust duration (alert wait time)
4. Add label filters to reduce false positives

### Notifications Not Sending
1. Check AlertManager health: `alertmanager:9093/-/healthy`
2. Verify notification channel configuration
3. Check credentials for external services
4. Review AlertManager logs: `kubectl logs alertmanager`

## References

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Alert Rules Syntax](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
