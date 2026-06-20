# Rollback Validation Checklist

**Status:** DRAFT - Use as template for rollback validation  
**Last Updated:** 2026-06-20T09:00:00Z

---

## Pre-Rollback Validation (Do This Before Starting Rollback)

### 1. Cluster Connectivity Check

- [ ] Cluster is responding to kubectl commands
  ```bash
  kubectl cluster-info
  # Expected: Kubernetes master is running
  ```

- [ ] API server is accessible
  ```bash
  kubectl api-resources
  # Expected: List of all API resources
  ```

- [ ] Current context is correct
  ```bash
  kubectl config current-context
  # Expected: Correct cluster name (NOT production if testing)
  ```

- [ ] RBAC permissions are valid
  ```bash
  kubectl auth can-i get deployments --as=[current-user]
  # Expected: yes
  ```

### 2. Service Status Assessment

- [ ] Current service status documented
  ```bash
  kubectl get deployment -A
  # Record current deployment status
  ```

- [ ] Pod status recorded
  ```bash
  kubectl get pods -A --sort-by=.metadata.creationTimestamp
  # Record pod age and status
  ```

- [ ] Error rate verified
  - [ ] Error rate spike confirmed in monitoring
  - [ ] Error pattern documented (which endpoints?)
  - [ ] Root cause suspected (new deployment? config change?)

- [ ] User impact confirmed
  - [ ] Number of affected users documented
  - [ ] Service tier affected (free/paid/enterprise?)
  - [ ] Business criticality assessed

### 3. Deployment Health Check

For each deployment that will be rolled back:

**Deployment: `codex-ml-server`**
- [ ] Current revision documented
  ```bash
  kubectl rollout history deployment/codex-ml-server -n default
  ```

- [ ] Previous revision(s) exist
  - Expected: At least 2 revisions in history
  - [ ] Can we identify which revision was stable?

- [ ] Current image version noted
  ```bash
  kubectl describe deployment codex-ml-server -n default | grep Image:
  ```

- [ ] Previous image version(s) documented
  - [ ] Previous image is in registry
  - [ ] Previous image is accessible

- [ ] Resource limits are reasonable
  ```bash
  kubectl describe deployment codex-ml-server -n default | grep -A2 "Limits\|Requests"
  ```

- [ ] Health probes are configured
  - [ ] Liveness probe: YES / NO
  - [ ] Readiness probe: YES / NO
  - [ ] Startup probe: YES / NO (if applicable)

### 4. Backup & Recovery Preparation

- [ ] Current deployment backed up
  ```bash
  kubectl get deployment codex-ml-server -n default -o yaml > backup-deployment.yaml
  ```

- [ ] Current pod logs captured
  ```bash
  kubectl logs deployment/codex-ml-server -n default --all-containers --tail=1000 > backup-logs.txt
  ```

- [ ] Current configuration captured
  ```bash
  kubectl get configmap codex-ml-config -n default -o yaml > backup-configmap.yaml
  ```

- [ ] Data backup verified (if applicable)
  - [ ] Database backup recent (< 1 hour old)
  - [ ] Backup location documented
  - [ ] Restore procedure verified

### 5. Stakeholder Communication

- [ ] Team notified of planned rollback
  - [ ] Slack message sent to #incident-response
  - [ ] Incident ticket created
  - [ ] Impact statement documented

- [ ] Maintenance window declared (if needed)
  - [ ] Maintenance page deployed
  - [ ] Customers notified
  - [ ] ETA provided

- [ ] Rollback authority confirmed
  - [ ] L2+ manager approval obtained
  - [ ] Decision documented in incident ticket
  - [ ] Approval timestamp recorded

### 6. Monitoring & Observability Ready

- [ ] Monitoring dashboard open
  - [ ] Error rate dashboard visible
  - [ ] Performance metrics dashboard visible
  - [ ] Custom metrics (if applicable) visible

- [ ] Log aggregation ready
  ```bash
  kubectl logs deployment/codex-ml-server -n default -f
  # Terminal open and ready to monitor
  ```

- [ ] Alerts active
  - [ ] Alert rules enabled
  - [ ] Alert notification channels verified
  - [ ] Slack/PagerDuty connectivity confirmed

---

## During-Rollback Validation (Monitor These During Rollback)

### 1. Rollback Command Execution

- [ ] Rollback command executed
  ```bash
  kubectl rollout undo deployment/codex-ml-server -n default
  ```

- [ ] Command output checked
  - [ ] No errors in stderr
  - [ ] Deployment name confirmed
  - [ ] Revision reverted shown

- [ ] Timestamp recorded
  - Rollback start time: `YYYY-MM-DD HH:mm:ss UTC`

### 2. Rollout Status Monitoring

- [ ] Rollout status visible
  ```bash
  kubectl rollout status deployment/codex-ml-server -n default --timeout=10m
  ```

- [ ] Replica update progression monitored
  - [ ] Old pods terminating
  - [ ] New (previous) pods starting
  - [ ] Desired replicas being created

- [ ] Progressive rollout observed
  ```bash
  # Watch pods come up one by one
  watch kubectl get pods -n default -l app=codex-ml
  ```

- [ ] No failed pods detected
  - [ ] CrashLoopBackOff: NO
  - [ ] ImagePullBackOff: NO
  - [ ] Pending: NO (should be Running/Terminating only)

### 3. Health Check Monitoring

- [ ] Pod health probes active
  - [ ] Liveness probe: PASSING
  - [ ] Readiness probe: PASSING
  - [ ] No restart loops detected

- [ ] Service endpoints updated
  ```bash
  kubectl get endpoints codex-ml-service -n default
  # Should show updated IPs
  ```

- [ ] Load balancer updated (if applicable)
  - [ ] Endpoints added to load balancer
  - [ ] Health checks passing
  - [ ] Traffic can flow through

### 4. Application-Level Health

- [ ] HTTP health endpoint responding
  ```bash
  kubectl exec -it deployment/codex-ml-server -n default -- curl localhost:8000/health
  # Expected: 200 OK with health status
  ```

- [ ] Readiness endpoint responding
  ```bash
  kubectl exec -it deployment/codex-ml-server -n default -- curl localhost:8000/ready
  # Expected: 200 OK
  ```

- [ ] Application logs show normal startup
  ```bash
  kubectl logs deployment/codex-ml-server -n default --tail=50
  # Look for: successful startup, no errors, expected messages
  ```

### 5. Metrics Verification During Rollout

- [ ] Error rate declining
  - Target: < 1% after rollback
  - Timeline: Should drop within 2-3 minutes

- [ ] Latency returning to normal
  - Target: P99 latency < 1 second
  - Timeline: Should normalize within 2 minutes

- [ ] CPU/Memory within expected range
  - CPU: 30-70% normal, spike to 100% OK during startup
  - Memory: 50-80% normal

- [ ] Database connection count normal
  - Should match expected baseline
  - No connection leaks

---

## Post-Rollback Validation (Do This After Rollback Complete)

### 1. Deployment Stability

- [ ] All replicas running
  ```bash
  kubectl get deployment codex-ml-server -n default
  # Expected: Desired: 3, Current: 3, Ready: 3, Available: 3
  ```

- [ ] No pods in error states
  ```bash
  kubectl get pods -n default | grep -v Running
  # Expected: Only Terminating pods from old revision
  ```

- [ ] Pod age reasonable
  ```bash
  kubectl get pods -n default -o wide --sort-by=.metadata.creationTimestamp
  # All pods < 5 minutes old
  ```

### 2. Service Health

- [ ] Service responding to requests
  ```bash
  curl http://codex-ml-service:8000/health
  # Expected: 200 OK
  ```

- [ ] API endpoints working
  - [ ] POST /predict: 200 OK with valid response
  - [ ] GET /models: 200 OK with model list
  - [ ] GET /metrics: 200 OK with metrics data

- [ ] Error rate at baseline
  - [ ] Error rate < 0.1%
  - [ ] Latency P99 < 1 second
  - [ ] No timeout errors

### 3. Metrics Verification

- [ ] All critical metrics nominal
  - [ ] Error rate: < 0.1% (was > 10%)
  - [ ] Latency P99: < 1 second (was > 5 seconds)
  - [ ] Throughput: Normal baseline
  - [ ] CPU: 50-70%
  - [ ] Memory: 60-80%

- [ ] No new alerts firing
  - [ ] Check PagerDuty for new incidents
  - [ ] Check Datadog for critical alerts
  - [ ] Check custom monitoring dashboards

### 4. Data Integrity Checks

- [ ] No data loss detected
  - [ ] Transaction count matches expected
  - [ ] No orphaned records
  - [ ] Database consistency verified

- [ ] Cache consistency verified (if applicable)
  - [ ] Cache hit rate normal
  - [ ] No stale data being returned

### 5. Feature Verification

- [ ] Core features working
  - [ ] Primary user workflows functional
  - [ ] Secondary features responsive
  - [ ] Background jobs running

- [ ] No degraded mode activated
  - [ ] Read-only mode: NO (unless intentional)
  - [ ] Limited feature set: NO
  - [ ] Maintenance mode: NO

### 6. Log Analysis

- [ ] No error patterns in logs
  ```bash
  kubectl logs deployment/codex-ml-server -n default | grep -i error
  # Expected: Only informational messages, no error patterns
  ```

- [ ] Application performance normal
  ```bash
  kubectl logs deployment/codex-ml-server -n default | tail -100
  # Look for: normal request patterns, no warnings
  ```

### 7. Customer-Facing Validation

- [ ] Customer reports of issue resolved
  - [ ] Support tickets: No new issues
  - [ ] Customer emails: Resolved
  - [ ] Social media: No ongoing complaints

- [ ] Status page updated
  - [ ] Incident marked resolved
  - [ ] Timeline updated
  - [ ] Root cause summary added

---

## Validation Success Criteria

✅ **Rollback is SUCCESSFUL if ALL of the following are true:**

1. **Deployment Status**
   - All replicas Running and Ready (3/3)
   - No crashed or pending pods
   - Pod age < 5 minutes

2. **Service Health**
   - Health endpoints: 200 OK
   - API endpoints: 200 OK with valid data
   - Error rate: < 0.1%

3. **Performance**
   - Latency P99: < 1 second (baseline)
   - CPU: 50-70% normal range
   - Memory: 60-80% normal range

4. **Data Integrity**
   - No data loss or corruption
   - Database consistency verified
   - Transaction log intact

5. **Monitoring**
   - No critical alerts
   - All metrics nominal
   - No error patterns in logs

---

## Rollback Failed - Recovery Steps

❌ **If validation FAILS, execute these steps:**

### Immediate Actions

- [ ] Stop monitoring with this checklist
- [ ] Escalate to L2+ immediately (use ESCALATION_PROCEDURES.md)
- [ ] Revert to previous state if possible
  ```bash
  kubectl rollout undo deployment/codex-ml-server -n default
  ```

- [ ] Declare incident SEV-1 if:
  - Service remains completely down
  - Data corruption detected
  - Customer-facing impact ongoing

### Investigation Steps

- [ ] Capture pod logs before any cleanup
  ```bash
  kubectl logs deployment/codex-ml-server -n default --previous > failed-rollback.logs
  ```

- [ ] Get pod descriptions
  ```bash
  kubectl describe pods -n default > pod-describe.txt
  ```

- [ ] Check events
  ```bash
  kubectl get events -n default --sort-by='.lastTimestamp' > events.txt
  ```

- [ ] Get deployment yaml
  ```bash
  kubectl get deployment codex-ml-server -n default -o yaml > deployment-state.yaml
  ```

### Decision Points

- **If previous revision also failing:** Database issue suspected
  - Contact DBA
  - Review database logs
  - Consider restore from backup

- **If image unavailable:** Registry/image pull issue
  - Check registry connectivity
  - Verify image exists
  - Check pull secrets

- **If resource exhaustion:** Cluster resource issue
  - Check node capacity
  - Look for pod evictions
  - Scale down other workloads

---

## Post-Success Documentation

After successful rollback:

- [ ] Update incident ticket with timeline
- [ ] Document what went wrong
- [ ] Schedule post-mortem meeting
- [ ] Update runbook if needed
- [ ] Share lessons learned with team
- [ ] Update monitoring/alerts for future prevention

---

## Checklist Maintenance

- **Review:** Quarterly (Q1, Q2, Q3, Q4)
- **Update:** After each rollback incident
- **Version:** Track changes in CHANGELOG
- **Owner:** [DevOps/SRE team]

**Last Reviewed:** 2026-06-20  
**Next Review:** 2026-09-20

