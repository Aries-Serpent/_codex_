# Health Check Procedures

## Overview

This document describes all health check endpoints and procedures for post-deployment verification.

## Health Check Endpoints

### 1. Root Health Endpoint

**Endpoint:** `GET /health`

**Purpose:** Basic liveness check and service status verification

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response (200 OK):**
```json
{
  "service": "mcp-facade",
  "status": "ok",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok"
  }
}
```

**Response Fields:**
- `service` (string): Service name identifier
- `status` (string): Service status ("ok", "degraded", "unhealthy")
- `adapter` (string): Currently loaded adapter name
- `adapter_status` (object): Adapter-specific status information

**Response Time SLA:** < 500ms

**Failure Scenarios:**
- Status Code 500: Service is not responding (critical failure)
- Status Code 503: Service is degraded (non-critical)
- Timeout (>500ms): Network latency or service overload
- Missing fields: Invalid configuration

### 2. MCP Health Endpoint

**Endpoint:** `GET /mcp/v1/health`

**Purpose:** MCP-specific health check with detailed adapter status

**Request:**
```bash
curl -X GET http://localhost:8000/mcp/v1/health
```

**Expected Response (200 OK):**
```json
{
  "status": "ok",
  "adapter": "zendesk_adapter",
  "adapter_status": {
    "status": "ok",
    "connected": true,
    "latency_ms": 45
  }
}
```

**Response Fields:**
- `status` (string): Overall MCP status
- `adapter` (string): Adapter identifier
- `adapter_status` (object): Detailed adapter state including:
  - `connected` (boolean): Adapter connection state
  - `latency_ms` (number): Adapter response latency

**Response Time SLA:** < 500ms

## Health Check Interpretation Guide

### Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `ok` | Service fully operational | ✅ Continue deployment |
| `degraded` | Service partially operational | ⚠️ Investigate before proceeding |
| `unhealthy` | Service not operational | ❌ Halt deployment, investigate |

### Common Failure Patterns

#### Pattern 1: Adapter Connection Failed
**Symptom:** Adapter status shows `"status": "failed"` or `"connected": false`

**Root Causes:**
- Adapter service is down
- Credentials are invalid
- Network connectivity issue

**Remediation:**
1. Verify adapter service is running: `systemctl status <adapter-service>`
2. Check adapter credentials in configuration
3. Verify network connectivity: `ping <adapter-host>`
4. Check adapter logs: `tail -f /var/log/<adapter>.log`
5. Restart adapter if needed: `systemctl restart <adapter-service>`

#### Pattern 2: High Latency Response
**Symptom:** Response time > 500ms

**Root Causes:**
- Adapter is overloaded
- Network latency is high
- Database performance degraded

**Remediation:**
1. Check adapter resource usage: `top`, `ps aux`
2. Check network latency: `ping -c 5 <adapter-host>`
3. Check database performance metrics
4. Consider scaling adapter instances
5. Review recent code changes for performance regressions

#### Pattern 3: Timeout (No Response)
**Symptom:** Request times out after 30 seconds

**Root Causes:**
- Service crashed or hung
- Network connection dropped
- Firewall/security group issue

**Remediation:**
1. Verify service is running: `ps aux | grep <service>`
2. Check service logs: `journalctl -u <service> -f`
3. Verify network connectivity: `telnet <host> <port>`
4. Check firewall rules: `sudo iptables -L`
5. Restart service if needed

#### Pattern 4: Invalid Response Format
**Symptom:** Response missing expected fields or invalid JSON

**Root Causes:**
- Service code change introduced regression
- Configuration mismatch
- Middleware corruption

**Remediation:**
1. Verify service version matches deployment package
2. Check configuration files for errors
3. Review recent code changes
4. Check for middleware issues (proxies, load balancers)
5. Restart service

## Health Check Automation

### Automated Health Check Script

Use the provided health check runner script to automate health checks:

```bash
# Run health checks with default settings
python scripts/deployment/health_check_runner.py

# Run against specific host/port
python scripts/deployment/health_check_runner.py --host api.example.com --port 443

# Save results to custom directory
python scripts/deployment/health_check_runner.py --output ./reports
```

### Output Files

The health check runner generates:
- `health_report_<timestamp>.json` - Full health check results in JSON format
- `health_summary.md` - Human-readable summary report
- `health_latest.json` - Latest health check results (always updated)

## Health Check Scheduling

### Pre-Deployment Health Check
Run before starting deployment:
```bash
# Check current health
python scripts/deployment/health_check_runner.py --output .codex/pre-deploy
```

### During Deployment Health Check
Run during deployment at 30-second intervals:
```bash
# Monitor health during deployment
watch -n 30 'python scripts/deployment/health_check_runner.py'
```

### Post-Deployment Health Check
Run after deployment completes:
```bash
# Check health after deployment
python scripts/deployment/health_check_runner.py --output .codex/post-deploy
```

### Continuous Monitoring
Set up continuous health monitoring:
```bash
# Monitor every 60 seconds
while true; do
  python scripts/deployment/health_check_runner.py
  sleep 60
done
```

## Integration with Monitoring Systems

### Prometheus Metrics Integration

Health checks can be exposed as Prometheus metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'health-checks'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboard

Example Grafana dashboard query:

```promql
# Health status gauge
health_check_passed{job="health-checks"} == 1

# Response time histogram
histogram_quantile(0.95, health_check_response_time)
```

### Alert Rules

Example alert rules for Prometheus:

```yaml
groups:
  - name: health_checks
    rules:
      - alert: HealthCheckFailed
        expr: health_check_passed{job="health-checks"} == 0
        for: 1m
        annotations:
          summary: "Health check failed for {{ $labels.instance }}"
          description: "Service health check has been failing for 1 minute"

      - alert: HighHealthCheckLatency
        expr: health_check_response_time_ms{quantile="0.95"} > 500
        for: 5m
        annotations:
          summary: "High health check latency on {{ $labels.instance }}"
```

## Troubleshooting

### Health Endpoint Not Responding

**Check:**
1. Service is running: `ps aux | grep <service>`
2. Port is listening: `netstat -tuln | grep <port>`
3. Firewall allows traffic: `sudo iptables -L | grep <port>`
4. Check logs: `journalctl -u <service> -n 50 -f`

**Fix:**
```bash
# Restart service
systemctl restart <service>

# Verify health endpoint
curl -v http://localhost:8000/health
```

### Adapter Status Shows "Disconnected"

**Check:**
1. Adapter service status: `systemctl status <adapter-service>`
2. Adapter logs: `tail -f /var/log/<adapter>.log`
3. Network connectivity: `ping <adapter-host>`
4. Credentials in configuration

**Fix:**
```bash
# Restart adapter
systemctl restart <adapter-service>

# Verify connection
curl -X POST http://localhost:8000/mcp/v1/health
```

### High Response Time

**Check:**
1. CPU/memory usage: `top -b -n 1`
2. Disk I/O: `iostat -x 1`
3. Network latency: `ping -c 5 <adapter-host>`
4. Database performance: `mysql -e "SHOW PROCESSLIST;"`

**Fix:**
```bash
# Scale up instances
kubectl scale deployment mcp-facade --replicas=5

# Clear cache if applicable
redis-cli FLUSHDB

# Optimize database
mysql -e "OPTIMIZE TABLE users;"
```

## Documentation References

- [CRITICAL_PATHS_FOR_VERIFICATION.md](./CRITICAL_PATHS_FOR_VERIFICATION.md)
- [HEALTH_CHECK_RESPONSES.md](./HEALTH_CHECK_RESPONSES.md)
- [SUCCESS_CRITERIA_BY_ENVIRONMENT.md](./SUCCESS_CRITERIA_BY_ENVIRONMENT.md)
- [Monitoring Setup Guide](./MONITORING_SETUP_GUIDE.md)

## Support

For health check issues:
- Check service logs: `journalctl -u <service> -f`
- Contact: #devops on Slack
- On-call: Check PagerDuty
- Escalation: @ops-team
