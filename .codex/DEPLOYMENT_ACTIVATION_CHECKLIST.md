# DEPLOYMENT ACTIVATION CHECKLIST (T-0)

**Date:** 2026-07-07  
**Activation Time:** 09:00 UTC  
**Authority:** @mbaetiong  

---

## ✅ PRE-ACTIVATION VERIFICATION (T-30 Min)

### Gate Requirements
- [ ] **Track 9.3.1 GATE PASS:** Semantic Router (P95 <100ms, Accuracy >95%)
- [ ] **Track 9.3.2 GATE PASS:** Workload Balancer (100+ PRs, <10% variance)
- [ ] **Track 9.3.3 GATE PASS:** Stress Tests (all tests pass, <0.5% error)
- [ ] **Activation Signal:** Received from @mbaetiong

### Infrastructure Ready
- [ ] Kubernetes cluster all nodes healthy
- [ ] Persistent volumes provisioned (60Gi total)
- [ ] Network policies configured
- [ ] Load balancer operational
- [ ] Container images built and pushed

### Monitoring Ready
- [ ] Prometheus deployed and scraping targets
- [ ] AlertManager configured with 3 receivers
- [ ] Grafana dashboards accessible
- [ ] 28 alert rules loaded and active
- [ ] Notification channels tested (Email, Slack, PagerDuty)

### Authorization Ready
- [ ] CODEX_MASTER_KEY is set and valid
- [ ] GitHub token has required scopes (repo, workflow, actions:write)
- [ ] Auto-approval capability enabled
- [ ] Fallback tokens configured (if using secondary)

### Documentation Ready
- [ ] PHASE_9_3_TRACK_4_PREP_CHECKLIST.md reviewed
- [ ] DEPLOYMENT_PROCEDURES_GUIDE.md accessible
- [ ] INCIDENT_RESPONSE_RUNBOOK.md printed/available
- [ ] HEALTH_CHECK_PROCEDURES.md understood
- [ ] DEPLOYMENT_QUICK_START.md shared with team

### Team Ready
- [ ] On-call engineer briefed and standing by
- [ ] Team lead notified and available for escalation
- [ ] #deployments Slack channel monitored
- [ ] #incidents Slack channel ready for alerts
- [ ] PagerDuty integration tested

---

## ✅ GATE ENTRY CONFIRMATION (T-15 Min)

### Record All GATE PASS Confirmations
```
Track 9.3.1 GATE PASS Received: [ ] YES [ ] NO
  Semantic Router Status: _______________
  P95 Latency: _____ ms (target: <100ms)
  Accuracy: _____%  (target: >95%)
  Timestamp: ______________
  
Track 9.3.2 GATE PASS Received: [ ] YES [ ] NO
  Workload Balancer Status: _______________
  PR Support: _____ (target: 100+)
  Variance: _____%  (target: <10%)
  Timestamp: ______________

Track 9.3.3 GATE PASS Received: [ ] YES [ ] NO
  Stress Test Status: _______________
  Tests Passed: _____ / _____
  24h Stability: ____% (target: >99.5%)
  Timestamp: ______________
```

### Activation Signal Confirmation
```
Activation Signal Status: [ ] RECEIVED [ ] PENDING
  Source: @mbaetiong
  Message: ___________________________________
  Timestamp: ______________
  URL: ___________________________________
```

---

## ✅ FINAL SYSTEM CHECK (T-10 Min)

### Cluster Verification
```bash
# Run this check 10 minutes before activation
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pvc -A
```

**Status:**
- [ ] All nodes ready
- [ ] API server responding
- [ ] Persistent volumes bound

### Monitoring Verification
```bash
# Check monitoring stack
curl -s http://prometheus:9090/-/healthy
curl -s http://alertmanager:9093/-/healthy
curl -s http://grafana:3000/api/health
```

**Status:**
- [ ] Prometheus healthy
- [ ] AlertManager healthy
- [ ] Grafana accessible

### Current Deployment Status
```bash
# Check current state
kubectl get deployment codex-ml-server -n codex-ml -o wide
kubectl get pods -n codex-ml -l app=codex-ml
```

**Status:**
- [ ] Deployment exists and is stable
- [ ] Pods are healthy
- [ ] No active rollouts

### Alert System Check
```bash
# Verify alerts can be sent
# Test PagerDuty webhook
# Test Slack webhook
# Test email routing
```

**Status:**
- [ ] PagerDuty connectivity ✅
- [ ] Slack connectivity ✅
- [ ] Email routing ✅

---

## ✅ T-5 MINUTES: FINAL GO/NO-GO DECISION

### All Go/No-Go Criteria

| Criterion | Status | Comments |
|-----------|--------|----------|
| Track 1-3 GATE PASS received | ✅ YES / ❌ NO | _____________ |
| Activation signal received | ✅ YES / ❌ NO | _____________ |
| Cluster healthy | ✅ YES / ❌ NO | _____________ |
| Monitoring ready | ✅ YES / ❌ NO | _____________ |
| Authorization configured | ✅ YES / ❌ NO | _____________ |
| Team ready | ✅ YES / ❌ NO | _____________ |
| Documentation reviewed | ✅ YES / ❌ NO | _____________ |
| No critical issues | ✅ YES / ❌ NO | _____________ |

### Final Approval

**Go / No-Go Decision:** [ ] **GO** [ ] **NO-GO**

**Authorized By:** _______________________  
**Name:** _______________________  
**Time:** _______________________  
**Authority Level:** _______________________  

**If NO-GO, reason:** 
```
__________________________________________________________________
__________________________________________________________________
__________________________________________________________________
```

---

## ✅ T+0: ACTIVATION EXECUTION

### Deployment Start
```
Activation Time: 2026-07-07 09:00:00 UTC
Actual Start Time: ___________________
Status: DEPLOYMENT IN PROGRESS
```

**Action Items:**
1. [ ] **Post to #deployments:** "🚀 PHASE 9.3.4 DEPLOYMENT STARTING - Canary phase in progress"
2. [ ] **Start canary deployment:** `kubectl set replicas deployment/codex-ml-server=2 -n codex-ml`
3. [ ] **Start health monitoring:** Run HEALTH_CHECK_PROCEDURES.md canary script
4. [ ] **Alert on-call:** Deployment starting, monitor metrics
5. [ ] **Log start time:** Record T+0 execution start

### Phase 1: Canary (T+0 to T+15)
**Expected Status:** 2/2 pods ready, Error rate <5%, P95 latency <1.0s

**Monitoring Points (check every 2-3 minutes):**
- [ ] Pod rollout status
- [ ] Error rate trending downward
- [ ] Latency stable
- [ ] No crash loops

**Success Criteria Met at T+15:**
- [ ] 2/2 pods ready ✅
- [ ] Error rate <5% ✅
- [ ] P95 latency <1.0s ✅
- [ ] No pod restarts ✅

**Decision:** [ ] **PROCEED TO REGIONAL** [ ] **ROLLBACK**

### Phase 2: Regional (T+15 to T+30)
**Expected Status:** 4/4 pods ready, Error rate <3%, Resource utilization healthy

**Action:** `kubectl set replicas deployment/codex-ml-server=4 -n codex-ml`

**Monitoring Points (check every 3-5 minutes):**
- [ ] Pod rollout progressing
- [ ] Error rate remaining low
- [ ] CPU/Memory usage within limits
- [ ] PDB operating normally

**Success Criteria Met at T+30:**
- [ ] 4/4 pods ready ✅
- [ ] Error rate <3% ✅
- [ ] CPU usage <85% ✅
- [ ] Memory usage <85% ✅
- [ ] PDB active ✅

**Decision:** [ ] **PROCEED TO FULL PRODUCTION** [ ] **PAUSE FOR INVESTIGATION**

### Phase 3: Full Production (T+30 onwards)
**Expected Status:** 5/5 pods ready, Error rate <1%, Continuous monitoring

**Action:** `kubectl set replicas deployment/codex-ml-server=5 -n codex-ml`

**Monitoring Points (every 5 minutes):**
- [ ] Pod rollout completing
- [ ] Error rate very low
- [ ] Request rate increasing normally
- [ ] No critical alerts firing

**Success Criteria (continuous):**
- [ ] 5/5 pods ready ✅
- [ ] Error rate <1% ✅
- [ ] No critical alerts ✅
- [ ] Load balancer endpoint active ✅

**Deployment Status at T+60:**
- Canary completed: ✅
- Regional completed: ✅
- Production running: ✅
- Overall: ✅ **SUCCESS**

---

## ✅ T+60 MIN: POST-DEPLOYMENT VALIDATION

### Immediate Post-Deployment (T+60)

```bash
# 1. Verify all replicas
kubectl get deployment codex-ml-server -n codex-ml -o wide

# 2. Check no recent crashes
kubectl get pods -n codex-ml -l app=codex-ml -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}'

# 3. Verify service endpoints
kubectl get endpoints codex-api-service -n codex-ml

# 4. Check metrics collection
curl -s http://prometheus:9090/api/v1/query?query=up | grep -c "success"

# 5. Verify no active critical alerts
curl -s http://alertmanager:9093/api/v1/alerts | grep -i critical
```

**Validation Results:**
- [ ] All 5 replicas ready
- [ ] No pod restarts
- [ ] Service endpoints active
- [ ] Metrics being collected
- [ ] No critical alerts

### Extended Monitoring (T+60 to T+120)

Continue monitoring every 5-10 minutes:
- Error rate trending downward or stable
- Latency metrics normal
- Resource utilization healthy
- No new alerts in past 30 minutes

**Status at T+120:** [ ] **STABLE** [ ] **UNDER INVESTIGATION**

---

## ✅ DEPLOYMENT SIGN-OFF

### Deployment Summary

```
Deployment Date:         2026-07-07
Start Time:             _______________
End Time:               _______________
Total Duration:         _____ minutes

Phase 1 (Canary):       ✅ PASS
Phase 2 (Regional):     ✅ PASS
Phase 3 (Production):   ✅ PASS

Total Downtime:         0 minutes
Errors Encountered:     _____ (none expected)
Manual Interventions:   _____ (none expected)
```

### Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Phase 1 Duration | ≤15 min | ____ min | ✅/❌ |
| Phase 2 Duration | ≤15 min | ____ min | ✅/❌ |
| Error Rate (Canary) | <5% | ___% | ✅/❌ |
| Error Rate (Regional) | <3% | ___% | ✅/❌ |
| Error Rate (Prod) | <1% | ___% | ✅/❌ |
| Pod Restarts | 0 | ____ | ✅/❌ |
| Critical Alerts | 0 | ____ | ✅/❌ |

### Rollback Status

```
Rollback Executed:      ✅ NO [ ] / ❌ YES [ ]
Reason (if yes):        ___________________________________
Rollback Success:       ___________________________________
Time to Rollback:       _____ minutes
```

### Sign-Off Approval

**Deployment Lead:**
- Name: _______________________
- Time: _______________________
- Signature: ___________________

**Engineering Manager:**
- Name: _______________________
- Time: _______________________
- Signature: ___________________

---

## ✅ POST-DEPLOYMENT TASKS (Next 24 Hours)

- [ ] Export deployment metrics to team
- [ ] Collect and archive logs
- [ ] Schedule postmortem if any issues occurred
- [ ] Update deployment summary documentation
- [ ] Send team notification
- [ ] Plan next deployment improvements

---

**Checklist Status:** ✅ READY FOR DEPLOYMENT  
**Created:** 2026-07-07 08:00 UTC  
**Authority:** @mbaetiong

