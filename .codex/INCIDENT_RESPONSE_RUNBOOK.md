# Incident Response Runbook - Phase 9.3.4

**Document Version:** 1.0  
**Last Updated:** 2026-07-07 08:00 UTC  
**Scope:** Production Incident Response Procedures  

---

## Alert to Action Mapping

| Alert | Severity | RTO | Action |
|-------|----------|-----|--------|
| ServiceDown | CRITICAL | 2 min | Execute emergency rollback |
| HighErrorRate | CRITICAL | 5 min | Investigate & rollback if >5% |
| HighLatency | WARNING | 10 min | Check resources & scale if needed |
| HighCPUUsage | WARNING | 10 min | Scale up or optimize configuration |
| HighMemoryUsage | WARNING | 10 min | Scale up or check for memory leak |
| PodCrashLooping | CRITICAL | 5 min | Check logs & rollback |
| NodeNotReady | CRITICAL | 10 min | Drain node & reschedule pods |
| PVCAlmostFull | WARNING | 30 min | Cleanup or expand volume |

---

## Incident 1: Service Down (All Pods Offline)

**Alert:** ServiceDown (CRITICAL)  
**RTO:** 2 minutes  

### Detection
- Alert fires when `up{job='kubernetes-pods'} == 0`
- PagerDuty notification sent immediately
- Slack alert posted to #incidents

### Immediate Response (T+0 to T+1min)

1. **Acknowledge alert in PagerDuty** (on-call engineer)
2. **Verify issue:**
   ```bash
   kubectl get pods -n codex-ml
   kubectl describe deployment codex-ml-server -n codex-ml
   ```
3. **Check recent logs:**
   ```bash
   kubectl logs -n codex-ml deployment/codex-ml-server --tail=50
   ```

### Remediation (T+1 to T+2min)

**Execute emergency rollback:**
```bash
kubectl rollout undo deployment/codex-ml-server -n codex-ml

# Verify rollback
kubectl rollout status deployment/codex-ml-server -n codex-ml --timeout=2m
```

**Confirm service restored:**
```bash
# Check pods are running
kubectl get pods -n codex-ml -l app=codex-ml

# Test service endpoint
kubectl exec -it <pod-name> -n codex-ml -- curl -s http://localhost:8000/health
```

### Post-Incident (T+2 to T+30min)

1. **Document incident:**
   - Time detected
   - Root cause (check logs)
   - Rollback success
   - Post-recovery metrics

2. **Analyze logs:**
   ```bash
   kubectl logs -n codex-ml deployment/codex-ml-server --all-containers=true
   ```

3. **Export metrics for analysis:**
   ```bash
   # Prometheus query
   curl -s "http://prometheus:9090/api/v1/query_range?query=rate(http_requests_total[5m])&start=<time>&end=<time>" | jq .
   ```

4. **Schedule postmortem:**
   - When: Within 24 hours
   - Who: Team lead, on-call, deployment engineer
   - Goal: Identify root cause & prevent recurrence

---

## Incident 2: High Error Rate (>5%)

**Alert:** HighErrorRate (CRITICAL)  
**RTO:** 5 minutes  

### Detection
- Alert fires when `rate(http_requests_total{status=~"5.."}[5m]) > 0.05`
- Alert duration: 5 minutes (requires sustained high error rate)
- PagerDuty notification sent
- Slack alert to #incidents

### Immediate Response (T+0 to T+2min)

1. **Acknowledge alert**
2. **Check current status:**
   ```bash
   # Error rate now
   curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])"
   
   # Error details
   curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=\"500\"}[5m])"
   ```

3. **Check pod logs for errors:**
   ```bash
   kubectl logs -n codex-ml deployment/codex-ml-server --tail=100 | grep -i error
   ```

4. **Check if issue is widespread:**
   ```bash
   # Errors by pod
   kubectl logs -n codex-ml -l app=codex-ml --all-containers=true | grep -i error | wc -l
   ```

### Decision: Continue or Rollback? (T+2 to T+3min)

**Continue if:**
- ✅ Error rate is decreasing
- ✅ Root cause identified (e.g., external dependency)
- ✅ Expected recovery time < 5 minutes
- ✅ Error rate < 3% and declining

**Rollback if:**
- ❌ Error rate increasing or persistent
- ❌ Root cause unknown
- ❌ Multiple pods affected
- ❌ Error rate > 8%

### Rollback Procedure (T+3 to T+5min)

```bash
# Execute rollback
kubectl rollout undo deployment/codex-ml-server -n codex-ml

# Verify success
kubectl rollout status deployment/codex-ml-server -n codex-ml

# Confirm error rate dropped
curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])"
```

### Post-Incident Analysis

1. **Identify root cause from logs:**
   ```bash
   kubectl logs -n codex-ml deployment/codex-ml-server --previous --all-containers=true > incident-logs.txt
   ```

2. **Export error metrics:**
   ```bash
   # Get distribution of errors
   curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{status=~\"5..\"}[5m]))by(status,handler)"
   ```

3. **Document findings in incident tracker**

---

## Incident 3: High Latency (P95 > 1.0s)

**Alert:** HighLatency (WARNING)  
**RTO:** 10 minutes  

### Detection
- Alert fires when P95 latency > 1.0 second
- Alert duration: 5 minutes
- Slack alert to #alerts-warning

### Response Steps (T+0 to T+10min)

1. **Acknowledge warning**
2. **Check current latency:**
   ```bash
   curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))"
   ```

3. **Check if isolated to specific handler:**
   ```bash
   curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))by(handler)"
   ```

4. **Check resource usage:**
   ```bash
   kubectl top pods -n codex-ml
   kubectl top nodes
   ```

### Actions

**If CPU > 85%:**
- Scale up replicas: `kubectl scale deployment codex-ml-server --replicas=6`
- Monitor latency improvement

**If Memory > 85%:**
- Check for memory leak: `kubectl logs -n codex-ml deployment/codex-ml-server`
- Restart pods if needed: `kubectl rollout restart deployment/codex-ml-server -n codex-ml`

**If database slow:**
- Check database connection pool
- Check query performance in database logs
- May need to optimize queries

**If external dependency slow:**
- Check dependency health
- Implement circuit breaker if available
- Document and retry later

### Escalation

If latency doesn't improve after 10 minutes:
- Escalate to team lead
- Execute rollback if suspected in current deployment
- Check external dependencies

---

## Incident 4: Pod Crash Looping

**Alert:** PodCrashLooping (CRITICAL)  
**RTO:** 5 minutes  

### Detection
- Alert fires when restart rate > 0.1 restarts/minute over 15 minutes
- PagerDuty notification sent

### Response (T+0 to T+5min)

1. **Identify crashing pod:**
   ```bash
   kubectl get pods -n codex-ml
   kubectl describe pod <crashing-pod> -n codex-ml
   ```

2. **Check crash logs:**
   ```bash
   kubectl logs -n codex-ml <pod-name> --previous
   ```

3. **Common causes:**
   - OOM (Out of Memory): Check memory limits
   - ConfigMap/Secret missing: Verify mounted config
   - Bad image: Check image pull policy
   - Port binding failed: Check port availability

### Remediation

**If configuration issue:**
```bash
# Fix ConfigMap
kubectl edit configmap codex-ml-config -n codex-ml

# Restart pods to pick up new config
kubectl rollout restart deployment/codex-ml-server -n codex-ml
```

**If image issue:**
```bash
# Check image pull status
kubectl describe deployment codex-ml-server -n codex-ml

# Rollback to previous image
kubectl rollout undo deployment/codex-ml-server -n codex-ml
```

**If resource issue:**
```bash
# Increase resource limits
kubectl patch deployment codex-ml-server -n codex-ml --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value":"8Gi"}]'
```

---

## Incident 5: Node Not Ready

**Alert:** NodeNotReady (CRITICAL)  
**RTO:** 10 minutes  

### Detection
- Alert fires when node status != Ready
- Pods may be in pending/terminating state

### Response

1. **Identify affected node:**
   ```bash
   kubectl get nodes
   kubectl describe node <node-name>
   ```

2. **Check what's wrong:**
   - Network issue
   - Kubelet crashed
   - Disk/memory pressure
   - Check node logs: `journalctl -u kubelet`

3. **Immediate action - drain node:**
   ```bash
   kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
   ```

4. **Pods will be rescheduled** to other nodes automatically

5. **Fix node issue** (contact infrastructure team)

6. **Bring node back online:**
   ```bash
   kubectl uncordon <node-name>
   ```

---

## Post-Incident Procedure

### All Incidents Follow This Process

1. **Document in incident tracker:**
   - Time detected
   - Alert fired
   - Actions taken
   - Rollback executed (yes/no)
   - Impact duration
   - Root cause

2. **Export evidence:**
   ```bash
   # Save logs
   kubectl logs -n codex-ml deployment/codex-ml-server --all-containers=true > incident-logs.txt
   
   # Save metrics
   # (Export from Prometheus UI)
   
   # Save pod state
   kubectl get pods -n codex-ml -o yaml > pod-state.yaml
   ```

3. **Schedule postmortem within 24 hours:**
   - Participants: Team lead, on-call, deployment engineer
   - Review root cause
   - Identify preventive measures
   - Update runbooks if needed

4. **Implement improvements:**
   - Increase monitoring thresholds if false positives
   - Add tests for scenarios
   - Update deployment procedures
   - Document findings

---

## Escalation Path

**T+0-2min:** On-call engineer (acknowledge & begin response)  
**T+2-5min:** Team lead (if not resolved by on-call)  
**T+5-10min:** Engineering manager (if escalation needed)  
**T+10min+:** Director (critical outage coordinator)  

---

## Communication Template

### Incident Alert (Post immediately when alert fires)
```
🚨 INCIDENT DETECTED

Service: Codex ML
Alert: [Alert Name]
Severity: [CRITICAL/WARNING]
Status: Under Investigation

Current Action: [Action being taken]
ETA to Resolution: [Time estimate]

Updates will be posted to #incidents
```

### Incident Resolution (Post when issue resolved)
```
✅ INCIDENT RESOLVED

Service: Codex ML
Alert: [Alert Name]
Duration: [Time from detection to resolution]
Root Cause: [Brief description]
Action Taken: [Rollback/Scale/etc]

Next Steps: [Monitoring/Follow-up required]
Postmortem: [Scheduled for date/time]
```

---

**Document Status:** ✅ COMPLETE  
**Last Updated:** 2026-07-07 08:00 UTC

