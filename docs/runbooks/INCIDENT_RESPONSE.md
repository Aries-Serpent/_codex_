# RUNBOOK: Incident Response and Recovery Procedures

**Version:** 1.0.0  
**Last Updated:** 2026-07-10  
**Audience:** On-Call Engineers, DevOps  
**Response Time SLA:** P1 issues < 15 min, P2 < 1 hour, P3 < 4 hours  

---

## Quick Reference

| Incident Type | P1 SLA | P2 SLA | P3 SLA | Action |
|---|---|---|---|---|
| API down | 15 min | — | — | Page on-call, check health |
| High error rate (>10%) | 15 min | — | — | Page on-call, check logs |
| Database corruption | 30 min | — | — | Failover, restore from backup |
| High latency (p95 >2s) | 30 min | 1 hour | — | Investigate, scale if needed |
| Memory leak | 1 hour | 2 hours | 4 hours | Identify process, restart |
| Disk full | 30 min | 1 hour | 4 hours | Clean up, expand storage |

---

## Table of Contents

1. [Incident Classification](#incident-classification)
2. [Initial Response](#initial-response)
3. [P1 Incidents (Critical)](#p1-incidents-critical)
4. [P2 Incidents (High)](#p2-incidents-high)
5. [P3 Incidents (Medium)](#p3-incidents-medium)
6. [Recovery Procedures](#recovery-procedures)
7. [Communication](#communication)

---

## Incident Classification

### P1 — Critical (Page immediately)

- **API completely down** (503 Service Unavailable)
- **Database unavailable** (cannot connect)
- **High error rate** (>10% of requests failing)
- **Data loss** or corruption
- **Security breach** or unauthorized access

**Response:** Notify on-call engineer immediately via PagerDuty

### P2 — High (Notify team, investigate within 1 hour)

- **API degraded** but partially working
- **High latency** (p95 >2 seconds)
- **Elevated error rate** (5-10%)
- **Non-critical feature broken** (e.g., RAG pipeline failing but API still works)

**Response:** Notify team, investigate within 1 hour

### P3 — Medium (Address within business hours)

- **Performance degraded** but acceptable
- **Low error rate** (<5%)
- **Minor features not working** (non-critical)
- **Logs showing warnings** but not errors

**Response:** Log ticket, address in next sprint

---

## Initial Response

**First 5 minutes:**

```bash
# 1. Acknowledge alert
echo "✓ Incident acknowledged at $(date)"

# 2. Determine scope
echo "Checking incident scope..."

# 3. Quick system status
sudo systemctl status codex-api
sudo systemctl status codex-worker

# 4. Check logs for obvious errors
tail -n 50 /var/log/codex/api.log | grep -i error

# 5. Check resource usage
free -h  # Memory
df -h    # Disk space
top -b -n 1 -p $(pgrep -f 'python -m codex.api')  # CPU/memory

# 6. Check network connectivity
ping 8.8.8.8
curl -s http://localhost:8000/health

# 7. Document findings
# Write observations to incident log
echo "Investigation started $(date)" >> /tmp/incident.log
```

---

## P1 Incidents (Critical)

### Scenario: API Completely Down

**Detection:** Monitoring shows `up == 0` for all instances

**Response (5-minute timeline):**

**Minute 0-1: Assess & Stabilize**
```bash
# Verify down
curl -v http://localhost:8000/health

# Check service status
systemctl status codex-api
systemctl status codex-worker

# Immediate attempt to restart
sudo systemctl restart codex-api
sudo systemctl restart codex-worker

# Wait 10 seconds and verify
sleep 10
curl http://localhost:8000/health
```

**Minute 1-3: Investigate Root Cause**
```bash
# If restart works, investigate why it crashed
tail -n 100 /var/log/codex/api.log > /tmp/incident_logs.txt

# Look for:
# - Out of memory errors
# - Database connection failures
# - Disk full
# - Crashed processes
grep -i "error\|exception\|fatal" /tmp/incident_logs.txt
```

**Minute 3-5: Execute Rollback (if needed)**
```bash
# If fresh restart works, done
# If restart doesn't help:

# 1. Check current deployment version
git rev-parse HEAD
git describe --tags

# 2. Check previous stable version
git log --oneline -n 5

# 3. Rollback to previous version
git checkout <previous-stable-tag>

# 4. Restart service
sudo systemctl restart codex-api
```

**Minute 5+: Communication**
- Notify #incidents channel with status
- Update status page
- Document findings

---

### Scenario: Database Connection Failure

**Detection:** API logs show `sqlite3.OperationalError`

```bash
# 1. Verify database file exists
ls -la /var/lib/codex/codex.db

# 2. Check if database is locked
lsof | grep codex.db

# 3. If locked, find process
ps aux | grep <PID>

# 4. Kill stuck process if needed
sudo kill -9 <PID>

# 5. Wait 5 seconds, restart service
sleep 5
sudo systemctl restart codex-api

# 6. If still failing, check database integrity
sqlite3 /var/lib/codex/codex.db "PRAGMA integrity_check;"

# 7. If corrupted, restore from backup
sqlite3 /var/lib/codex/codex.db < /var/backups/codex_backup_$(date +%Y%m%d).sql

# 8. Restart service
sudo systemctl restart codex-api
```

---

### Scenario: Out of Memory

**Detection:** `Out of memory: Kill process` in syslog

```bash
# 1. Free memory immediately
sudo sync; echo 3 > /proc/sys/vm/drop_caches

# 2. Check memory usage
ps aux --sort=-%mem | head -10

# 3. Kill non-essential processes if needed
sudo systemctl stop codex-worker  # Temporary

# 4. Restart API service
sudo systemctl restart codex-api

# 5. Check if stable
top -b -n 1 -p $(pgrep -f codex.api) | tail -5

# 6. If memory still growing, restart machine
# (escalate to infrastructure team)
```

---

## P2 Incidents (High)

### Scenario: High Error Rate (5-10%)

**Detection:** Monitoring shows error_rate > 5%

```bash
# 1. Understand which endpoints are failing
curl -s http://localhost:8000/metrics | grep http_requests_total

# 2. Check API logs for patterns
tail -n 200 /var/log/codex/api.log | grep "ERROR" | head -20

# 3. Check database for locks/issues
sqlite3 /var/lib/codex/codex.db "PRAGMA database_list;"

# 4. Scale up (add more replicas)
kubectl scale deployment codex-api --replicas=5 -n codex-prod

# 5. Monitor for improvement
# Watch error rate for 5 minutes

# 6. If sustained, investigate specific endpoint
python -m codex.debug.trace_errors --endpoint=/api/v1/inference
```

---

### Scenario: High Latency (p95 >2 seconds)

**Detection:** Monitoring shows high_latency_p95 > 2000ms

```bash
# 1. Check what's consuming CPU
top -b -n 3 > /tmp/top_output.txt

# 2. Check database query performance
python -m codex.db.slow_queries --duration=5s

# 3. Check if specific operation is bottleneck
python -m codex.perf.profile_inference --duration=10s

# 4. Scale horizontally
kubectl scale deployment codex-api --replicas=8 -n codex-prod

# 5. Monitor latency trends
watch -n 5 'curl -s http://localhost:8000/metrics | grep http_request_duration'
```

---

## P3 Incidents (Medium)

### Scenario: Non-Critical Feature Failing

**Detection:** Logs show warnings, but API still responding

```bash
# 1. Identify which feature is failing
grep "WARN" /var/log/codex/api.log | tail -20

# 2. Check if feature can be disabled
# Edit /etc/codex/config.yaml
sudo nano /etc/codex/config.yaml
# Set enable_feature=false

# 3. Restart service
sudo systemctl restart codex-api

# 4. Log issue for investigation
# Create GitHub issue with details
```

---

## Recovery Procedures

### Full System Recovery

**If entire system down, follow this sequence:**

```bash
# 1. Power on machines
# (Physical or cloud provider console)

# 2. Wait for boot to complete
sleep 120

# 3. Check storage
sudo fsck -n /  # Read-only check

# 4. Check services
sudo systemctl status codex-*

# 5. Restore from backup if needed
# See [Rollback Procedures](DEPLOYMENT_PROCEDURES.md#rollback-procedures)

# 6. Run smoke tests
pytest tests/smoke/ -v

# 7. Monitor for 30 minutes
watch -n 5 'curl -s http://localhost:8000/health'
```

### Database Recovery

**If database corrupted:**

```bash
# 1. Stop services accessing database
sudo systemctl stop codex-api
sudo systemctl stop codex-worker

# 2. Find latest clean backup
ls -ltr /var/backups/codex_backup*.sql | tail -3

# 3. Restore from backup
sqlite3 /var/lib/codex/codex.db < /var/backups/codex_backup_2026_07_10.sql

# 4. Verify restore
sqlite3 /var/lib/codex/codex.db "SELECT COUNT(*) FROM models;"

# 5. Restart services
sudo systemctl start codex-api
sudo systemctl start codex-worker

# 6. Verify connectivity
curl http://localhost:8000/health
```

---

## Communication

### Status Page Updates

**Every 15 minutes of incident:**

```markdown
# Status Update

## Incident Summary
- **Status:** Investigating
- **Start Time:** 2026-07-10 15:30 UTC
- **Duration:** 10 minutes
- **Impact:** API requests failing with 503 errors

## What We Know
- Database connection timing out
- Restarting service to clear connections

## What We're Doing
- Monitoring database connection pool
- Scaling up instances to reduce load
- Expected resolution: 15:45 UTC

## Customer Impact
- Inference API unavailable
- Training pipeline paused
- Batch jobs queued

**Next update: 15:45 UTC**
```

### Incident Report Template

**After incident is resolved, complete this:**

```markdown
# Incident Report: API Outage 2026-07-10

## Summary
- **Start Time:** 15:30 UTC
- **End Time:** 16:05 UTC
- **Duration:** 35 minutes
- **Severity:** P1
- **Impact:** Complete API outage, 100% request failure

## Root Cause
- Database connection pool exhausted due to slow query
- Cascading effect: new connections could not be created
- Service became unresponsive

## Timeline
| Time | Event |
|------|-------|
| 15:30 | Monitoring detected 503 errors |
| 15:31 | On-call notified, investigation started |
| 15:35 | Root cause identified (slow query) |
| 15:40 | Query killed, service restarted |
| 15:05 | Service recovered, error rate normal |

## Resolution
1. Killed stuck database query
2. Restarted API service
3. Monitors now track slow queries

## Prevention
- [ ] Add query timeout (5s max)
- [ ] Add database connection pool monitoring
- [ ] Optimize identified slow query
- [ ] Test load handling up to 2x capacity

## Action Items
- Assign: @dev1 - Optimize slow query
- Assign: @dev2 - Add query timeout
- Assign: @ops1 - Increase monitoring alerting
```

---

## Escalation Path

If incident not resolved in SLA:

**P1 (15 min):**
- ✓ Notify on-call
- → Notify team lead
- → Notify engineering manager
- → Page VP of Engineering

**P2 (1 hour):**
- ✓ Notify team
- → Notify team lead after 30 min
- → Notify engineering manager after 1 hour

**P3 (4 hours):**
- ✓ Create ticket
- → Assign to sprint
- → Review in next planning meeting

---

## Post-Incident Review

Within 24 hours of P1/P2 incident:

```bash
# 1. Gather data
# - Logs: /var/log/codex/api.log, /var/log/codex/worker.log
# - Metrics: Export from Prometheus
# - Timeline: When did alerts fire
# - Resolution: What fixed the issue

# 2. Root cause analysis
# Identify: What went wrong, why did it go wrong, why wasn't it caught

# 3. Action items
# What can we do to prevent this in the future
# - Code changes
# - Monitoring/alerting changes
# - Documentation updates
# - Process improvements

# 4. Document in GitHub issue
# Create: https://github.com/Aries-Serpent/_codex_/issues
# Title: "Post-incident review: [Incident name]"
```

---

**Maintained by:** @mbaetiong  
**Last tested:** 2026-07-10  
**Next drill:** 2026-07-17
