# Production Observability: Alerting & Incident Response Setup

**Phase**: 7D (Pre-v0.1.0-final)  
**Authority**: @mbaetiong (D-level autonomy)  
**Status**: Production-Ready Implementation Guide  
**Last Updated**: 2026-06-20  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Alert Rules Configuration](#alert-rules-configuration)
3. [Severity Levels & Escalation](#severity-levels--escalation)
4. [Notification Channels](#notification-channels)
5. [On-Call Scheduling](#on-call-scheduling)
6. [Runbook Templates](#runbook-templates)
7. [Alert Deduplication](#alert-deduplication)
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
---

## Executive Summary

This guide establishes the alerting infrastructure for v0.1.0-final production deployment. All alerts should:

- Notify on-call engineers within 1 minute of trigger
- Provide actionable context (not just metrics)
- Include runbook links for resolution
- Auto-escalate if unacknowledged after 30 minutes
- Automatically resolve when conditions clear

---

## Alert Rules Configuration

### Step 1: Create Alertmanager Configuration

File: `/opt/monitoring/alertmanager/config/alertmanager.yml`

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Alert routing tree
route:
  receiver: 'ops-team'
  group_by: ['alertname', 'job', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    # Critical alerts
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      group_wait: 10s
      repeat_interval: 1h
      continue: true

    # Warning alerts
    - match:
        severity: warning
      receiver: 'slack-channel'
      group_wait: 60s
      repeat_interval: 4h

    # Info alerts
    - match:
        severity: info
      receiver: 'slack-silent'
      group_wait: 300s
      repeat_interval: 24h

# Receivers
receivers:
  - name: 'null'

  - name: 'slack-channel'
    slack_configs:
      - channel: '#alerts-prod'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'slack-silent'
    slack_configs:
      - channel: '#alerts-info'
        title: 'Info: {{ .GroupLabels.alertname }}'
        send_resolved: false

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        description: '{{ .GroupLabels.alertname }}: {{ .GroupLabels.instance }}'
        details:
          firing: '{{ template "pagerduty.default.instances" .Alerts.Firing }}'
        severity: 'critical'

# Inhibition rules (suppress alerts under certain conditions)
inhibit_rules:
  # Suppress warning if critical already firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']

  # Suppress info if warning already firing
  - source_match:
      severity: 'warning'
    target_match:
      severity: 'info'
    equal: ['alertname', 'instance']
```

### Step 2: Define Alert Rules

File: `/opt/monitoring/prometheus/rules/alerts.yml`

```yaml
groups:
  - name: infrastructure
    interval: 30s
    rules:
      # CPU Usage Alert
      - alert: HighCPUUsage
        expr: 'rate(process_cpu_seconds_total[5m]) * 100 > 80'
        for: 5m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "High CPU usage detected ({{ $value | humanize }}%)"
          description: "Instance {{ $labels.instance }} CPU > 80% for 5 minutes"
          runbook_url: "https://wiki.example.com/runbooks/high-cpu-usage"
          dashboard: "http://grafana:3000/d/system-health"

      # Memory Alert
      - alert: HighMemoryUsage
        expr: '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85'
        for: 3m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "High memory usage ({{ $value | humanize }}%)"
          description: "Instance {{ $labels.instance }} memory > 85%"
          runbook_url: "https://wiki.example.com/runbooks/high-memory"

      # Disk Space Alert
      - alert: DiskSpaceRunningOut
        expr: '(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10'
        for: 5m
        labels:
          severity: critical
          component: infrastructure
        annotations:
          summary: "Disk space running out ({{ $value | humanize }}%)"
          description: "{{ $labels.device }} has only {{ $value }}% free"
          runbook_url: "https://wiki.example.com/runbooks/disk-space"

      # Instance Down
      - alert: InstanceDown
        expr: 'up{job="codex-ml"} == 0'
        for: 1m
        labels:
          severity: critical
          component: infrastructure
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
          description: "Instance {{ $labels.instance }} (job: {{ $labels.job }}) is unreachable"
          runbook_url: "https://wiki.example.com/runbooks/instance-down"

  - name: application
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: '(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100 > 5'
        for: 3m
        labels:
          severity: critical
          component: application
        annotations:
          summary: "High error rate detected ({{ $value | humanize }}%)"
          description: "Error rate on {{ $labels.instance }} > 5%"
          runbook_url: "https://wiki.example.com/runbooks/high-error-rate"
          dashboard: "http://grafana:3000/d/app-performance"

      # High Latency
      - alert: HighLatency
        expr: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2'
        for: 5m
        labels:
          severity: warning
          component: application
        annotations:
          summary: "High latency detected ({{ $value | humanize }}s)"
          description: "P95 latency on {{ $labels.instance }} > 2s"
          runbook_url: "https://wiki.example.com/runbooks/high-latency"

      # Service Degradation
      - alert: ServiceDegraded
        expr: |
          (count(up{job="codex-ml"} == 1) / count(up{job="codex-ml"})) < 0.5
        for: 2m
        labels:
          severity: critical
          component: application
        annotations:
          summary: "Service degradation: <50% instances healthy"
          description: "Less than 50% of codex-ml instances are healthy"
          runbook_url: "https://wiki.example.com/runbooks/service-degradation"

      # Request Timeout
      - alert: RequestTimeout
        expr: 'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 5'
        for: 2m
        labels:
          severity: warning
          component: application
        annotations:
          summary: "Request timeout ({{ $value | humanize }}s)"
          description: "P99 latency on {{ $labels.instance }} > 5s"
          runbook_url: "https://wiki.example.com/runbooks/request-timeout"

  - name: dependencies
    interval: 30s
    rules:
      # Database Slow Queries
      - alert: DatabaseSlowQueries
        expr: 'mysql_global_status_slow_queries > 100'
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "High number of slow queries ({{ $value }})"
          description: "Database {{ $labels.instance }} has {{ $value }} slow queries"
          runbook_url: "https://wiki.example.com/runbooks/slow-queries"

      # Redis Connection Issues
      - alert: RedisConnectionPoolExhausted
        expr: 'redis_connected_clients > redis_config_maxclients * 0.9'
        for: 3m
        labels:
          severity: warning
          component: cache
        annotations:
          summary: "Redis connection pool near exhaustion"
          description: "Redis {{ $labels.instance }} connection pool {{ $value }}% full"
          runbook_url: "https://wiki.example.com/runbooks/redis-exhaustion"

      # Cache Hit Ratio Low
      - alert: LowCacheHitRatio
        expr: 'rate(cache_hits[5m]) / (rate(cache_hits[5m]) + rate(cache_misses[5m])) < 0.7'
        for: 10m
        labels:
          severity: info
          component: cache
        annotations:
          summary: "Low cache hit ratio ({{ $value | humanizePercentage }})"
          description: "Cache hit ratio on {{ $labels.instance }} < 70%"
          runbook_url: "https://wiki.example.com/runbooks/low-cache-hits"

  - name: business_metrics
    interval: 60s
    rules:
      # SLA Violation
      - alert: SLAViolation
        expr: |
          (count(up{job="codex-ml"} == 1) / count(up{job="codex-ml"}) * 100) < 99.5
        for: 5m
        labels:
          severity: critical
          component: business
        annotations:
          summary: "SLA violation: availability < 99.5%"
          description: "Current uptime {{ $value | humanize }}%"
          runbook_url: "https://wiki.example.com/runbooks/sla-violation"

      # Prediction Accuracy Degradation
      - alert: PredictionAccuracyDegraded
        expr: 'model_accuracy_percent < 92'
        for: 10m
        labels:
          severity: warning
          component: ml-model
        annotations:
          summary: "Model accuracy degraded ({{ $value | humanize }}%)"
          description: "Model on {{ $labels.instance }} accuracy < 92%"
          runbook_url: "https://wiki.example.com/runbooks/accuracy-degradation"
```

---

## Severity Levels & Escalation

### Severity Matrix

| Level | Response Time | Escalation | Example |
|-------|---------------|------------|---------|
| **Critical** | <5 min | Page on-call | Instance down, data loss, SLA violation |
| **High** | <15 min | Slack + escalate if no response | Error rate >10%, latency >5s |
| **Warning** | <1 hour | Slack #alerts-prod | Error rate >5%, CPU >80% |
| **Info** | <4 hours | Slack #alerts-info only | Low cache hit ratio, minor degradation |

### Escalation Policy

```yaml
escalation_policy:
  level_1:
    duration: 30m
    notify: ["on-call-primary", "slack:#alerts-prod"]
  level_2:
    duration: 15m
    notify: ["on-call-primary", "on-call-backup"]
  level_3:
    duration: 10m
    notify: ["on-call-manager", "leadership-team"]

  on_acknowledge:
    action: "STOP_ESCALATION"
    notify: "slack-channel"
```

---

## Notification Channels

### Slack Integration

```yaml
# alertmanager configuration
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL' <!-- pragma: allowlist secret -->
    channel: '#alerts-prod'
    title: '{{ .GroupLabels.alertname }}'
    title_link: 'http://grafana:3000/alerting/list'
    pretext: 'Alert: {{ .Status | toUpper }}'
    text: |
      {{ if eq .Status "firing" }}
        *Firing:* {{ range .Alerts.Firing }}{{ .Labels.instance }}{{ end }}
      {{ else }}
        *Resolved:* {{ range .Alerts.Resolved }}{{ .Labels.instance }}{{ end }}
      {{ end }}

    fields:
      - title: 'Severity'
        value: '{{ .GroupLabels.severity }}'
        short: true
      - title: 'Service'
        value: '{{ .GroupLabels.job }}'
        short: true
      - title: 'Details'
        value: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        short: false
      - title: 'Runbook'
        value: '{{ range .Alerts }}{{ .Annotations.runbook_url }}{{ end }}'
        short: false
    send_resolved: true
    actions:
      - type: button
        text: 'View Dashboard'
        url: 'http://grafana:3000/d/system-health'
      - type: button
        text: 'View Logs'
        url: 'http://kibana:5601'
```

### Email Configuration

```yaml
email_configs:
  - to: 'oncall@company.com'
    from: 'alertmanager@company.com'
    smarthost: 'smtp.company.com:587'
    auth_username: 'alertmanager@company.com'
    auth_password: 'YOUR_EMAIL_PASSWORD'
    headers:
      Subject: 'Alert: {{ .GroupLabels.alertname }}'
    html: |
      <h3>{{ .GroupLabels.alertname }}</h3>
      <p><strong>Severity:</strong> {{ .GroupLabels.severity }}</p>
      <p><strong>Details:</strong></p>
      {{ range .Alerts }}
        <p>{{ .Annotations.description }}</p>
      {{ end }}
```

### PagerDuty Integration

```yaml
pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
    description: '{{ .GroupLabels.alertname }}: {{ .GroupLabels.instance }}'
    details:
      firing: '{{ template "pagerduty.default.instances" .Alerts.Firing }}'
      num_firing: '{{ .Alerts.Firing | len }}'
      num_resolved: '{{ .Alerts.Resolved | len }}'
    severity: '{{ if eq .GroupLabels.severity "critical" }}critical{{ else }}warning{{ end }}'
    client: 'Prometheus AlertManager'
    client_url: 'http://grafana:3000/alerting/list'
```

---

## On-Call Scheduling

### Step 1: Create On-Call Schedule Template

File: `/opt/monitoring/oncall/schedule.yml`

```yaml
schedule:
  # Week 1
  week_1:
    monday_friday:
      primary: alice@company.com
      backup: bob@company.com
      business_hours: "09:00-17:00 UTC"
    weekend:
      primary: charlie@company.com
      escalation_1: alice@company.com
      escalation_2: bob@company.com

  # Week 2
  week_2:
    monday_friday:
      primary: bob@company.com
      backup: charlie@company.com
    weekend:
      primary: alice@company.com
      escalation_1: bob@company.com
      escalation_2: charlie@company.com

  # Escalation contacts
  escalation:
    level_1_manager: engineering-manager@company.com
    level_2_director: engineering-director@company.com
    on_call_coordinator: coordinator@company.com

contact_info:
  alice@company.com:
    phone: "+1-555-0100"
    slack: "@alice"
  bob@company.com:
    phone: "+1-555-0101"
    slack: "@bob"
  charlie@company.com:
    phone: "+1-555-0102"
    slack: "@charlie"
```

### Step 2: Configure PagerDuty Escalation

```bash
# Create escalation policy via API
curl -X POST 'https://api.pagerduty.com/escalation_policies' \
  -H 'Authorization: Token token=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "escalation_policy": {
      "name": "Codex-ML Escalation",
      "repeat_enabled": true,
      "num_loops": 3,
      "escalation_rules": [
        {
          "escalation_delay_in_minutes": 30,
          "targets": [
            {
              "type": "user",
              "id": "on-call-primary"
            }
          ]
        },
        {
          "escalation_delay_in_minutes": 15,
          "targets": [
            {
              "type": "user",
              "id": "on-call-backup"
            }
          ]
        },
        {
          "escalation_delay_in_minutes": 10,
          "targets": [
            {
              "type": "user",
              "id": "engineering-manager"
            }
          ]
        }
      ]
    }
  }'
```

---

## Runbook Templates

### Template 1: High CPU Usage

File: `/opt/monitoring/runbooks/high-cpu-usage.md`

```markdown
# Runbook: High CPU Usage

## Alert Criteria
- CPU usage > 80% for > 5 minutes

## Immediate Actions (< 5 min)

1. **Acknowledge alert** in PagerDuty
2. **Check affected service**
   ```bash
   kubectl top pod -n production | grep codex-ml
   ```
3. **Verify it's not expected**
   - Check deployment logs
   - Recent code changes?
   - Scheduled batch jobs?

## Diagnosis (5-15 min)

```bash
# Login to instance
ssh user@instance

# Top processes
top -o %CPU

# Specific service profiling
ps aux | grep python  # if Python app

# Docker container stats
docker stats
```

## Resolution

### Option 1: Horizontal Scaling (Preferred)
```bash
kubectl scale deployment codex-ml --replicas=5
```

### Option 2: Service Restart
```bash
kubectl rollout restart deployment/codex-ml
```

### Option 3: Resource Limits
```bash
# Temporarily reduce rate limiting
curl -X POST http://app:8000/admin/rate-limit \
  -d '{"requests_per_sec": 50}'
```

## Validation

- [ ] CPU usage < 70% after fix
- [ ] No errors in application logs
- [ ] Request latency still normal
- [ ] Alert auto-resolves

## Escalation
If CPU remains high after 15 min:
- Escalate to on-call manager
- Page infrastructure team
```

### Template 2: High Error Rate

File: `/opt/monitoring/runbooks/high-error-rate.md`

```markdown
# Runbook: High Error Rate

## Alert Criteria
- Error rate > 5% for > 3 minutes

## Immediate Actions (< 5 min)

1. **Acknowledge alert**
2. **View error dashboard**
   - Go to Grafana: Errors & Logs dashboard
   - Filter by error type
3. **Check error logs**
   ```bash
   kubectl logs -n production -l app=codex-ml --tail=100 | grep ERROR
   ```

## Diagnosis (5-15 min)

```bash
# Get recent errors from Loki
curl 'http://loki:3100/loki/api/v1/query?query={level="error"}'

# Check for specific error types
curl 'http://loki:3100/loki/api/v1/query?query={level="error"} | json | error_type="OutOfMemory"'
```

## Common Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| Dependency unavailable | 503 errors | Check Redis, DB, external APIs |
| Memory leak | 500 errors | Restart service |
| Code bug | Specific error type | Check recent deployments |
| Rate limiting | 429 errors | Increase quotas |

## Resolution

### Check dependencies
```bash
# Database
kubectl get svc postgres -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Cache
redis-cli ping

# External APIs
curl https://api.external.com/health
```

### Rollback if needed
```bash
# Check current version
kubectl rollout history deployment/codex-ml

# Rollback to previous
kubectl rollout undo deployment/codex-ml
```

## Validation

- [ ] Error rate < 1% after fix
- [ ] No new errors in logs
- [ ] All dependencies responding
- [ ] Alert auto-resolves
```

---

## Alert Deduplication

### Configuration

```yaml
# Deduplicate similar alerts
deduplication:
  # Group alerts from same job within time window
  group_wait: 30s
  group_interval: 5m

  # Remove duplicate alerts
  duplicate_filter:
    enabled: true
    time_window: 5m

  # Suppress repeat notifications
  repeat_prevention:
    enabled: true
    min_interval: 4h

  # Correlation rules
  correlation:
    # Suppress instance-level if service-level alert exists
    - condition: "job == 'codex-ml' AND severity == 'warning'"
      suppress_labels: ["instance"]
```

### Alert Correlation Example

```yaml
# When InstanceDown fires, suppress HighErrorRate for same instance
inhibit_rules:
  - source_match:
      alertname: 'InstanceDown'
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['instance']
```

---

## Testing Alerts

### Manual Alert Test

```bash
# Trigger test alert
kubectl exec -it alertmanager-pod -- amtool alert add TestAlert \
  severity=critical \
  instance=test-instance

# Verify notification received
# Check Slack/PagerDuty/Email

# Clean up test alert
kubectl exec -it alertmanager-pod -- amtool alert expire TestAlert
```

### Synthetic Testing

```bash
# Simulate high CPU
docker run --name cpu-test \
  --cpus="0.9" \
  stress-ng:latest stress --cpu 4 --timeout 5m

# Verify alert fires
# Check Grafana -> Alerting
```

---

## Validation Checklist

- [ ] All alert rules loaded in Prometheus
- [ ] Alertmanager routing configured
- [ ] Notification channels tested (Slack, PagerDuty, Email)
- [ ] Escalation policy tested
- [ ] On-call schedule updated in PagerDuty
- [ ] Team acknowledged alert channels
- [ ] Runbooks reviewed by team
- [ ] Test alerts successfully fired and resolved
- [ ] Response time SLAs documented

---

**Next Steps:**
1. Review PHASE_7D_HEALTH_CHECK_PROCEDURES.md
2. Review PHASE_7D_INCIDENT_RESPONSE.md
3. Schedule alert testing session with ops team
4. Update on-call schedule in PagerDuty
