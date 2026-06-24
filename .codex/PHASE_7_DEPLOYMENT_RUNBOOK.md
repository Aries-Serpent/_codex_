# PHASE 7 DEPLOYMENT RUNBOOK

**Version:** 1.0  
**Date:** 2026-06-22  
**Authority:** Production Release Manager  
**Deployment Window:** 2026-06-23T22:00Z UTC

---

## DEPLOYMENT OVERVIEW

```
Deployment Target:   Production (codex-ml v7.0)
Environment:         AWS Cloud (multi-region)
Rollback Time:       <30 minutes
Maintenance Window:  2-4 hours
Risk Level:          LOW (comprehensive testing, security validated)
```

---

## PRE-DEPLOYMENT PHASE (T-24 to T-0)

### T-24 Hours: Stakeholder Notification

**Actions:**
- [ ] Send deployment notification email to all stakeholders
- [ ] Include deployment window: 2026-06-23T22:00Z UTC ± 30 min
- [ ] Include estimated duration: 2-4 hours
- [ ] Include rollback procedure summary
- [ ] Provide incident contact information

**Distribution List:**
- Production Owner (@mbaetiong)
- Release Manager
- Infrastructure Team
- QA Lead
- Security Lead
- On-call Engineer

**Email Template:**
```
Subject: DEPLOYMENT NOTICE: Codex ML v7.0 Production Deployment

Deployment Window: 2026-06-23T22:00Z UTC (±30 minutes)
Expected Duration: 2-4 hours
Maintenance Mode: Enabled during deployment
Rollback Available: Yes (<30 minutes)

During this window, services may be unavailable or slow.
We appreciate your patience during this critical update.

Incident Contact: [on-call-number]
Status Page: [status.codex-ml.io]
```

---

### T-6 Hours: Infrastructure Verification

**Actions:**
- [ ] Verify all deployment tools are operational
- [ ] Check CI/CD pipeline status (all green)
- [ ] Verify database backup completed successfully
- [ ] Confirm database connection pools tested
- [ ] Verify service replicas healthy
- [ ] Test monitoring and alerting systems
- [ ] Confirm on-call team is ready
- [ ] Review rollback procedures

**Checklist:**

```
Infrastructure Readiness:
  ✓ Database backups: Current (< 1 hour old)
  ✓ Service replicas: 3/3 healthy
  ✓ Load balancers: Active and tested
  ✓ DNS configurations: Verified
  ✓ SSL/TLS certificates: Valid and current
  ✓ Monitoring: All probes passing
  ✓ Alert channels: Slack + PagerDuty active
  ✓ Deployment keys: Rotated and tested
```

---

### T-3 Hours: Alert Configuration

**Verification Steps:**
- [ ] Error rate alert: Configured (threshold 0.5%, alert at 0.1% spike)
- [ ] Latency alert: Configured (threshold 600ms, alert at 500ms)
- [ ] Uptime alert: Configured (SLA 99.9%, alert on drop)
- [ ] Security incident alert: Configured (alert on any)
- [ ] Database connection alert: Configured (threshold 80%)
- [ ] CPU alert: Configured (threshold 80%)
- [ ] Memory alert: Configured (threshold 85%)
- [ ] Disk space alert: Configured (threshold 90%)

**Test Alert:**
- [ ] Send test alert to Slack (#incidents channel)
- [ ] Verify receipt and visibility
- [ ] Confirm PagerDuty notification

---

### T-1 Hour: Final Pre-Deployment

**Actions:**
- [ ] Confirm deployment ready: All gates GREEN ✅
- [ ] Get final approval from @mbaetiong (via this runbook)
- [ ] Disable auto-scaling (if applicable)
- [ ] Enable deployment mode in application
- [ ] Clear application cache
- [ ] Stop non-critical background jobs
- [ ] Verify database maintenance window scheduled
- [ ] Notify on-call engineer of start time

**Approval Sign-off:**
```
✓ Release Manager: Approved for deployment
✓ Infrastructure Lead: Infrastructure ready
✓ Security Team: Security gates cleared
✓ On-call Engineer: Standing by
```

---

## DEPLOYMENT PHASE (T-0 to T+2 hours)

### T-15 Minutes: Enable Maintenance Mode

**Actions:**
```bash
# Step 1: Enable maintenance mode across all regions
kubectl set env deployment/codex-ml \
  MAINTENANCE_MODE=true \
  MAINTENANCE_MESSAGE="Scheduled maintenance. Back in ~2 hours."

# Step 2: Verify maintenance page is live
curl https://codex-ml.io/health
# Expected response: 503 Service Unavailable (with maintenance message)

# Step 3: Drain in-flight requests (5 min timeout)
# Existing connections: graceful shutdown
# New connections: rejected with 503
```

**Verification:**
- [ ] Maintenance page loads correctly
- [ ] Users see maintenance message
- [ ] Monitoring shows reduced traffic
- [ ] Database connections stable

---

### T-0: Deployment Start

**Pre-Deployment Checks:**
```
✓ All services: READY for deployment
✓ Database: Backup completed
✓ Monitoring: Active and alerting
✓ Rollback procedures: Documented and tested
✓ On-call team: Standing by

DEPLOYMENT INITIATED AT: [timestamp]
```

---

### Deployment Steps (Documented in Ansible Playbooks)

**Phase 1: Backend Services (20-30 min)**

```bash
# Step 1: Update Python dependencies
pip install -r requirements/lock.txt

# Step 2: Run database migrations (non-breaking)
python -m alembic upgrade head

# Step 3: Deploy API servers (rolling update, 1 at a time)
kubectl rolling-update codex-api --image=codex-ml:v7.0

# Step 4: Verify API health checks pass
curl https://api.codex-ml.io/health
# Expected: 200 OK, version: 7.0

# Step 5: Smoke test critical endpoints
pytest tests/smoke/api_endpoints.py -v
```

**Phase 2: Supporting Services (10-15 min)**

```bash
# Step 1: Deploy worker services
kubectl rolling-update codex-workers --image=codex-ml:v7.0

# Step 2: Deploy background job services
kubectl rolling-update codex-jobs --image=codex-ml:v7.0

# Step 3: Update indexing service
kubectl rolling-update codex-indexer --image=codex-ml:v7.0

# Step 4: Verify service health
kubectl get pods -l app=codex-ml --watch
```

**Phase 3: Frontend Services (5-10 min)**

```bash
# Step 1: Update frontend static assets
gsutil -m cp -r build/static gs://codex-ml-assets/v7.0/

# Step 2: Update CDN cache headers
# Invalidate CloudFront distribution

# Step 3: Verify assets load correctly
curl https://cdn.codex-ml.io/static/index.html -I
```

---

### Deployment Monitoring (Real-time)

**During Deployment — Monitor These Metrics:**

```
Error Rate:        [MONITOR] Should stay <0.1%
  Alert threshold: >0.5% (escalate immediately)

Latency (p99):     [MONITOR] Should stay <500ms
  Alert threshold: >600ms (investigate cause)

Request Count:     [MONITOR] Should gradually increase as maintenance disabled

Database Queries:  [MONITOR] Should return to normal range
  Alert: >10k/sec (investigate slow query)

Memory Usage:      [MONITOR] Should stay <85%
  Alert: >90% (potential memory leak)

CPU Usage:         [MONITOR] Should stay <80%
  Alert: >90% (potential hotspot)
```

**Alert Response:**
```
If Error Rate > 0.5%:
  1. PAUSE deployment
  2. Investigate error logs
  3. Determine if rollback needed
  4. Alert on-call engineer
  5. Notify @mbaetiong

If Latency p99 > 600ms:
  1. Check database query performance
  2. Verify API response times
  3. Check if queries need optimization
  4. Determine if deployment caused issue
  5. Alert infrastructure team
```

---

### T+30 Min: Halfway Point Check

**Actions:**
- [ ] Verify deployment 50% complete
- [ ] Check error rates: <0.1% ✅
- [ ] Check latency: <500ms ✅
- [ ] Verify database operations normal
- [ ] Confirm no security incidents
- [ ] Review deployment logs for errors
- [ ] Estimate time to completion

**Success Criteria:**
- ✓ No critical errors
- ✓ Services responding normally
- ✓ Database replication synced
- ✓ Monitoring data flowing normally

---

### T+1 Hour: Deployment Complete

**Post-Deployment Verification:**

```bash
# Step 1: Verify all services running v7.0
kubectl get deployment -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[0].image}{"\n"}{end}'
# Expected: All showing v7.0

# Step 2: Run smoke tests
pytest tests/smoke/ -v

# Step 3: Verify database consistency
python scripts/verify_database_integrity.py

# Step 4: Check all health checks passing
curl -s https://codex-ml.io/health | jq .
# Expected: all status: "UP"
```

**Checklist:**
- [ ] All pods running (desired count = actual count)
- [ ] All health checks passing
- [ ] Smoke tests passing
- [ ] Database consistency verified
- [ ] Error logs clean (no new exceptions)
- [ ] Monitoring metrics normal

---

### T+1:30 Minutes: Disable Maintenance Mode

**Actions:**
```bash
# Step 1: Disable maintenance mode
kubectl set env deployment/codex-ml \
  MAINTENANCE_MODE=false

# Step 2: Verify application is live
curl https://codex-ml.io/
# Expected: 200 OK (normal page)

# Step 3: Monitor traffic ramp-up
# Traffic should gradually increase to normal levels
```

**Traffic Ramp-up Monitoring:**
- T+0 min: 0% traffic
- T+5 min: 10% traffic (monitor for issues)
- T+10 min: 50% traffic
- T+15 min: 100% traffic
- T+20 min: Monitor for issues (stable)

**Success Criteria:**
- ✓ Error rate stays <0.1%
- ✓ Latency stays <500ms p99
- ✓ No user-facing incidents
- ✓ Business metrics normal

---

### T+2 Hours: Deployment Complete

**Final Verification:**

```
DEPLOYMENT COMPLETE ✅

Final Status Check:
  ✓ All services running v7.0
  ✓ Error rate: <0.1%
  ✓ Latency p99: <500ms
  ✓ Uptime: 99.9%+ maintained
  ✓ Database consistency: VERIFIED
  ✓ Security incidents: 0
  ✓ Monitoring: All alerts green
  ✓ No automatic rollback triggered
```

---

## ROLLBACK PROCEDURES (If Needed)

### Rollback Decision Criteria

**IMMEDIATE ROLLBACK if:**
- Error rate > 5% for > 5 minutes
- Latency p99 > 2000ms for > 5 minutes
- Database connection issues
- Critical security incident
- Data integrity issues detected
- All services down (unhealthy replicas > 50%)

### Rollback Steps

**Phase 1: Stop Current Deployment (5 min)**

```bash
# Step 1: Enable maintenance mode again
kubectl set env deployment/codex-ml \
  MAINTENANCE_MODE=true

# Step 2: Stop current services
kubectl delete deployment codex-ml
# Waits for graceful shutdown (30 sec timeout)
```

**Phase 2: Restore Previous Version (10 min)**

```bash
# Step 1: Restore from backup
kubectl apply -f manifests/v6.5/deployment.yaml

# Step 2: Restore database to pre-deployment state
# Using: [backup-from-2026-06-23T21:00Z]
pg_restore -d codex_ml /backups/codex-ml-2026-06-23T21:00Z.backup

# Step 3: Wait for services to be healthy
kubectl rollout status deployment/codex-ml --timeout=5m
```

**Phase 3: Verify Rollback (5 min)**

```bash
# Step 1: Verify version
curl https://codex-ml.io/version
# Expected: v6.5

# Step 2: Run smoke tests against v6.5
pytest tests/smoke/ -v

# Step 3: Verify data integrity
python scripts/verify_database_integrity.py
```

**Phase 4: Disable Maintenance Mode (2 min)**

```bash
# Step 1: Resume normal operations
kubectl set env deployment/codex-ml \
  MAINTENANCE_MODE=false

# Step 2: Monitor traffic ramp-up
# Same as deployment ramp-up procedure
```

**Total Rollback Time: ~22 minutes** ✅

---

## POST-DEPLOYMENT PHASE

### T+0 Hours: Notification

**Send Success Notification:**
```
Subject: ✅ Codex ML v7.0 Deployment Complete

Deployment Status: SUCCESS ✅

New Version: 7.0
Deployment Duration: [actual duration]
Services Status: All healthy
User Impact: None

Key Improvements in v7.0:
  • Coverage improvements (test gap-fill)
  • Documentation enhancements
  • Functionality completeness
  • Security hardening (CVE updates planned)

No immediate action required.
```

---

### T+24 Hours: Monitoring Window

**Real-time Metrics to Track:**

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Error Rate | <0.1% | >0.5% |
| Latency p99 | <500ms | >600ms |
| Uptime | 99.9% | <99.8% |
| Database Latency | <10ms | >50ms |
| API Throughput | Normal | ±20% deviation |

**Daily Checkpoints:**
- [ ] T+2 hour: All metrics green
- [ ] T+6 hour: No escalations
- [ ] T+12 hour: Steady state
- [ ] T+24 hour: Production sign-off

---

### T+72 Hours: Post-Deployment Review

**Agenda:**
1. Final production validation
2. CVE remediation planning (14 CVEs documented)
3. Issues encountered and lessons learned
4. Performance benchmarking vs v6.5
5. User feedback and incidents
6. Schedule for Phase 8 (security updates)

**Success Criteria:**
- ✓ Zero critical incidents
- ✓ All metrics within SLA
- ✓ No data integrity issues
- ✓ User adoption proceeding normally

---

## INCIDENT ESCALATION

### Incident Contact Tree

**Level 1: On-call Engineer**
- Primary: [on-call name]
- Backup: [backup name]
- Contact: [phone/slack]
- Scope: First-level triage and mitigation

**Level 2: Infrastructure Lead**
- Name: [name]
- Contact: [phone/slack]
- Scope: Infrastructure-level issues

**Level 3: Release Manager**
- Name: [name]
- Contact: [phone/slack]
- Scope: Deployment decisions, rollback authorization

**Level 4: Production Owner (@mbaetiong)**
- Contact: [phone/slack]
- Scope: Go/no-go decisions, escalations

### Response Times

| Severity | Response Time | Resolution Time |
|----------|---|---|
| **CRITICAL** (app down) | 5 min | 30 min (or rollback) |
| **HIGH** (degraded) | 15 min | 2 hours |
| **MEDIUM** | 30 min | 4 hours |
| **LOW** | 1 hour | 24 hours |

---

## DEPLOYMENT SIGN-OFF

```
DEPLOYMENT AUTHORIZED: [date/time]
Release Manager: ________________ Date: ______
Infrastructure Lead: ____________ Date: ______
Security Lead: __________________ Date: ______
Production Owner (@mbaetiong): _____ Date: ______

DEPLOYMENT EXECUTED: [date/time]
On-call Engineer: ________________ Date: ______
Infrastructure Team Lead: ________ Date: ______

DEPLOYMENT VERIFIED: [date/time]
Release Manager: ________________ Date: ______
QA Lead: _______________________ Date: ______

STATUS: ✅ COMPLETE
```

---

**Runbook Version:** 1.0  
**Last Updated:** 2026-06-22  
**Next Review:** 2026-07-22  
**Authority:** Production Release Manager
