# Incident Response Playbook

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainer**: Incident Commander  
**Escalation**: SRE Lead → Engineering Director → VP Engineering  

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | Incident Commander | Initial creation for Phase 6 production readiness |

---

## Executive Summary

This playbook provides structured procedures for detecting, diagnosing, mitigating, and resolving production incidents affecting Aries-Serpent/_codex_. It covers incident classification, escalation protocols, communication procedures, and resolution workflows.

**Target SLA Response Times**:
- **SEV1** (Critical): 5 minutes to engage incident commander, 15 minutes to mitigation
- **SEV2** (High): 15 minutes to engage, 1 hour to mitigation
- **SEV3** (Medium): 1 hour to engage, 4 hours to mitigation
- **SEV4** (Low): 24 hours to engage, best effort

---

## Incident Classification

### Severity Definitions

| Severity | Impact | Example | Response Time |
|----------|--------|---------|----------------|
| **SEV1** | Complete service outage, data loss risk, security breach | API unreachable, database corrupted, data exposure | 5 min |
| **SEV2** | Major functionality unavailable, significant performance degradation | 50%+ error rate, > 2s response time | 15 min |
| **SEV3** | Minor functionality affected, workaround available | 1% error rate, specific endpoint slow | 1 hour |
| **SEV4** | Non-critical issues, cosmetic problems | Typo in UI, minor missing feature | 24 hours |

### Impact Assessment Flowchart

```
Incident Detected
  │
  ├─ Customer-facing service down?
  │   ├─ YES → SEV1/SEV2
  │   └─ NO → Continue
  │
  ├─ Data loss or integrity risk?
  │   ├─ YES → SEV1
  │   └─ NO → Continue
  │
  ├─ Security or compliance breach?
  │   ├─ YES → SEV1
  │   └─ NO → Continue
  │
  ├─ Error rate > 1%?
  │   ├─ YES → SEV2
  │   └─ NO → Continue
  │
  ├─ Response time degradation?
  │   ├─ YES → SEV2/SEV3
  │   └─ NO → SEV3/SEV4
```

---

## Incident Detection

### 1.1 Automated Alert Triggers

**Alert Monitoring Points**:

```bash
# Alert 1: API Unavailability
- Condition: All API endpoints return 5xx for > 1 minute
- Severity: SEV1
- Action: Page on-call immediately

# Alert 2: High Error Rate
- Condition: Error rate > 1% for > 5 minutes
- Severity: SEV2
- Action: Alert on-call, escalate if > 5%

# Alert 3: Response Time SLA Violation
- Condition: Response time p95 > 1 second for > 5 minutes
- Severity: SEV2/SEV3
- Action: Alert on-call, investigate

# Alert 4: Database Replication Lag
- Condition: Replication lag > 5 seconds
- Severity: SEV2
- Action: Alert database team

# Alert 5: Disk Space Critical
- Condition: Available disk < 10%
- Severity: SEV2
- Action: Alert infrastructure team

# Alert 6: Pod Restart Loop
- Condition: Pod restart count > 5 in 15 minutes
- Severity: SEV2
- Action: Alert on-call, check logs
```

### 1.2 Manual Alert Criteria

**Criteria for manual incident report**:
- Received customer complaint about service issue
- Observing unusual system behavior not covered by automated alerts
- Received security alert or data integrity concern
- Performance degradation reported by monitoring tools

**Manual Alert Process**:

```bash
1. Notify on-call: PagerDuty page or Slack @oncall
2. Provide details: What, when, impact assessment
3. Assign severity based on impact classification
4. Start incident in tracking system
5. Brief incident response team
```

### 1.3 Alert Routing Configuration

**Alert Channels**:
- **SEV1**: PagerDuty immediate page + Slack #prod-incidents + SMS
- **SEV2**: PagerDuty page + Slack #prod-incidents
- **SEV3**: Slack #prod-incidents + email
- **SEV4**: Slack #prod-incidents only

---

## Incident Response Workflow

### 2.1 Detection to Response (Immediate - 0-5 minutes)

**Step 1: Acknowledge Alert**

```bash
# On-call engineer acknowledges alert within 30 seconds
# In PagerDuty:
- Click "Acknowledge" on incident
- Add initial note with observations
- In Slack #prod-incidents:
@incident-commander I'm responding to SEV[X] incident
Observed: [symptom description]
Starting investigation now
```

**Step 2: Initial Triage**

```bash
# Execute initial diagnostic commands
kubectl cluster-info
kubectl get nodes
kubectl get pods -n production
curl http://${API_ENDPOINT}/health

# Document initial findings
# Example:
Initial findings:
- 3 out of 5 nodes healthy
- API pods CrashLoopBackOff
- Database connection pool exhausted
- Estimated impact: 95% of users affected
```

**Step 3: Declare Incident and Assemble Response Team**

```bash
# If SEV1: Immediately assemble team
# In Slack #prod-incidents:
!incident SEV1 "API service unavailable - investigate pod crash loop"
@incident-commander @sre-team @database-team @devops-lead

# Incident declared at: [timestamp]
# Incident ID: INC-2024-01-15-001
```

### 2.2 Investigation Phase (5-15 minutes)

**Step 1: Collect Diagnostic Information**

```bash
# Collect comprehensive diagnostic data
INCIDENT_ID="INC-2024-01-15-001"
INCIDENT_TIME=$(date)

# 1. Application logs
kubectl logs -n production -l app=codex-api --tail=200 > /tmp/${INCIDENT_ID}-app-logs.txt

# 2. System metrics
kubectl top nodes > /tmp/${INCIDENT_ID}-nodes.txt
kubectl top pods -n production > /tmp/${INCIDENT_ID}-pods.txt

# 3. Pod descriptions (useful for debugging)
kubectl describe pods -n production -l app=codex-api > /tmp/${INCIDENT_ID}-pod-desc.txt

# 4. Recent events
kubectl get events -n production --sort-by='.lastTimestamp' | tail -50 > /tmp/${INCIDENT_ID}-events.txt

# 5. Database status
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT pid, state, query FROM pg_stat_activity;" > /tmp/${INCIDENT_ID}-db-queries.txt

# 6. Resource limits and requests
kubectl get pods -n production -o json | jq '.items[] | {name: .metadata.name, requests: .spec.containers[].resources.requests, limits: .spec.containers[].resources.limits}' > /tmp/${INCIDENT_ID}-resources.txt
```

**Step 2: Root Cause Analysis**

**Analysis Checklist**:
- [ ] Review recent deployment changes: `git log --oneline -10`
- [ ] Check for recent configuration changes: `kubectl rollout history deployment/codex-api -n production`
- [ ] Review recent database migrations: `kubectl exec db-pod -- psql -c "SELECT version FROM alembic_version;"`
- [ ] Check external dependency status (if applicable)
- [ ] Review infrastructure metrics (CPU, memory, network)
- [ ] Review application error logs for patterns
- [ ] Check for cascading failures from dependent services

**Common Root Causes - Investigation Tree**:

```
API Endpoints Returning 5xx
  ├─ Pod crash loop?
  │   ├─ Check: kubectl get pods -n production
  │   ├─ Review: kubectl logs pod-name -n production
  │   └─ Common causes: Memory leak, unhandled exception, config error
  │
  ├─ Database connectivity issue?
  │   ├─ Check: telnet $DB_HOST 5432
  │   ├─ Verify: Connection pool status
  │   └─ Common causes: RDS failover, firewall rule, expired password  # pragma: allowlist secret
  │
  ├─ Resource exhaustion?
  │   ├─ Check: kubectl top pods -n production
  │   ├─ Verify: Available cluster resources
  │   └─ Common causes: Memory leak, unbounded loop, cache growth
  │
  └─ Recent deployment error?
      ├─ Check: kubectl rollout history deployment/codex-api
      ├─ Review: Image scanning results, test results
      └─ Common causes: Bad Docker image, uncaught dependency
```

**Step 3: Document Findings**

```bash
# Update incident status in Slack
@incident-commander: Root cause identified:
- Issue: [detailed root cause description]
- Timeline: [when it started, what caused it]
- Affected services: [list of affected components]
- Estimated time to resolution: [time estimate]
- Recommended action: [mitigation strategy]
```

---

## Mitigation and Recovery

### 3.1 Common Mitigation Strategies

**Strategy 1: Service Restart (for temporary issues)**

```bash
# For application crashes
kubectl delete pod -n production -l app=codex-api

# Wait for auto-restart
kubectl rollout status deployment/codex-api -n production --timeout=5m

# Verify recovery
curl http://${API_ENDPOINT}/health
```

**Strategy 2: Rollback Deployment (for recent changes)**

```bash
# Get previous version
PREVIOUS_VERSION=$(kubectl rollout history deployment/codex-api -n production | tail -2 | head -1 | awk '{print $1}')

# Rollback
kubectl rollout undo deployment/codex-api -n production --to-revision=${PREVIOUS_VERSION}

# Verify
kubectl rollout status deployment/codex-api -n production --timeout=5m
```

**Strategy 3: Scale Resources (for capacity issues)**

```bash
# Increase pod replicas
kubectl scale deployment codex-api --replicas=20 -n production

# Verify
kubectl get pods -n production -l app=codex-api | wc -l

# Monitor
watch -n 5 'kubectl top pods -n production'
```

**Strategy 4: Database Connection Recovery**

```bash
# If connection pool exhausted
# Option 1: Restart connection pool service
kubectl delete pod -n production -l app=connection-pool

# Option 2: Update connection pool settings
kubectl set env deployment/codex-api DB_POOL_SIZE=50 -n production

# Verify
kubectl describe pod -n production -l app=codex-api | grep DB_POOL_SIZE
```

**Strategy 5: Emergency Traffic Reduction (SEV1 - buy time)**

```bash
# If service overloaded, temporarily reduce traffic
# Scale down external traffic
kubectl patch service codex-api -n production --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/port", "value":8080}]'

# Or: Enable aggressive rate limiting
kubectl apply -f k8s/rate-limit-emergency.yaml -n production
```

### 3.2 Post-Mitigation Verification

**Verification Checklist**:
- [ ] API endpoints responding (< 200ms response time)
- [ ] Error rate < 0.5%
- [ ] Database queries executing normally
- [ ] No pod restart loops
- [ ] Cache hit ratio > 80%
- [ ] All alerts green
- [ ] Customer-facing features working
- [ ] Data integrity verified

**Verification Commands**:

```bash
# 1. Health check
curl -v http://${API_ENDPOINT}/health

# 2. Error rate monitoring
curl 'http://localhost:9090/api/v1/query?query=rate(http_errors_total[5m])'

# 3. Response time
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, http_request_duration_seconds)'

# 4. Pod status
kubectl get pods -n production

# 5. Database status
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Communication and Escalation

### 4.1 Incident Communication Protocol

**Communication Steps**:

```
T+0 min: Alert triggered
  ├─ Notify: On-call engineer (PagerDuty)
  └─ Notify: #prod-incidents Slack channel

T+5 min: Incident declared
  ├─ Update: Slack incident thread with severity and impact
  └─ Notify: Incident commander

T+10 min: Ongoing investigation
  ├─ Update: Slack with investigation progress
  ├─ Notify: Affected teams (if known)
  └─ Brief: Management if customer-impacting

T+15 min: Mitigation in progress
  ├─ Update: ETA to resolution
  ├─ Notify: Customers (if > 15 min outage)
  └─ Engage: Additional resources if needed

T+30 min: Resolution or escalation
  ├─ Notify: If still unresolved, escalate to director level
  └─ Update: Stakeholders on progress
```

### 4.2 Escalation Matrix

**Escalation Triggers and Actions**:

| Time | Trigger | Action | Escalate To |
|------|---------|--------|------------|
| 5 min | SEV1 incident declared | Notify on-call | Incident Commander |
| 15 min | No mitigation in place | Escalate investigation | SRE Lead |
| 30 min | Still investigating | Escalate leadership | Engineering Director |
| 1 hour | No resolution path identified | Executive briefing | VP Engineering |
| 2 hours | Ongoing major outage | Customer notification | VP Product |

**Escalation Contact Information**:

```
Tier 1 (On-Call Engineer): [Phone: _______, Slack: @oncall]
Tier 2 (Incident Commander): [Phone: _______, Slack: @incident-commander]
Tier 3 (SRE Lead): [Phone: _______, Slack: @sre-lead]
Tier 4 (Engineering Director): [Phone: _______, Slack: @eng-director]
Tier 5 (VP Engineering): [Phone: _______, Slack: @vp-eng]
```

### 4.3 Customer Communication Template

**Template for Customer-Impacting Incidents**:

```
Subject: Service Incident Notification - Aries-Serpent/_codex_

Dear Valued Customers,

We experienced a service disruption affecting [list affected services] 
starting at [time] UTC.

Impact:
- Approximately [number]% of requests were affected
- Duration: [start time] to [end time] UTC
- User impact: [describe impact]

Root Cause:
[Detailed but non-technical description of what happened]

Resolution:
[Describe the fix and verification steps taken]

Prevention:
[Describe preventive measures being implemented]

We sincerely apologize for the disruption and appreciate your patience.

For questions, contact: support@codex.com
Status page: status.codex.com

Regards,
Engineering Team
```

---

## Post-Incident Analysis

### 5.1 Incident Closure Criteria

**Before closing incident, verify**:
- [ ] Service fully restored and stable for > 30 minutes
- [ ] All metrics within normal range
- [ ] No error spikes or anomalies observed
- [ ] Customer services confirmed working
- [ ] Post-incident review scheduled
- [ ] Incident report started

### 5.2 Post-Incident Review (Within 48 hours)

**Review Agenda**:

1. **Timeline reconstruction** (15 min):
   - When was issue first detected?
   - When was mitigation started?
   - When was issue resolved?
   - Identify gaps between detection and response

2. **Root cause deep dive** (20 min):
   - What was the root cause?
   - Why wasn't it caught earlier?
   - What tests or monitoring would have caught it?

3. **Action items** (15 min):
   - What can we do to prevent this?
   - What can we do to detect faster?
   - What can we do to resolve faster?
   - Who owns each action item?

4. **Documentation** (10 min):
   - Update runbooks with learnings
   - Add new alert if needed
   - Update post-mortem document

**Post-Incident Report Template**:

```markdown
# Post-Incident Report: [Incident ID]

## Executive Summary
[Brief summary of what happened and impact]

## Incident Timeline
- T+0: [event]
- T+5: [event]
- T+10: [event]
...

## Root Cause
[Detailed technical analysis]

## Impact Assessment
- Duration: [start to end time]
- Users affected: [number/percentage]
- Revenue impact: [if applicable]
- Data lost: [if any]

## Immediate Actions Taken
- [action 1]
- [action 2]

## Prevention Actions
- [action 1]: Owner: [name], Due: [date]
- [action 2]: Owner: [name], Due: [date]

## Lessons Learned
- [learning 1]
- [learning 2]

## Postmortem Attendees
- [Name] - Role
- [Name] - Role
```

---

## Reference: Common Incident Scenarios

### Scenario 1: Database Connection Pool Exhaustion

**Symptoms**:
- API endpoints return database connection errors
- Response time increases dramatically
- Error rate > 50%

**Investigation**:
```bash
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction';"
```

**Mitigation**:
```bash
# Option 1: Restart connection pool
kubectl delete pod -n production -l app=connection-pool

# Option 2: Terminate idle connections
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND query_start < now() - INTERVAL '5 minutes';"
```

### Scenario 2: Memory Leak in Application

**Symptoms**:
- Pod memory usage continuously increases
- After several hours, pod gets OOMKilled
- Pod restart cycle begins

**Investigation**:
```bash
kubectl top pods -n production -l app=codex-api --containers
kubectl logs pod-name -n production | grep -i "memory\|OOM"
```

**Mitigation**:
```bash
# Immediate: Increase memory limit
kubectl set resources deployment codex-api -n production --limits=memory=2Gi

# Long-term: Deploy fixed image
kubectl set image deployment/codex-api codex-api=$FIXED_IMAGE_VERSION -n production
```

### Scenario 3: Cascading Failure (Service Dependency Chain)

**Symptoms**:
- One service goes down
- Dependent services start timing out
- Cascade causes system-wide outage

**Investigation**:
```bash
# Check service dependencies
kubectl get svc -n production
# Check network policies
kubectl get networkpolicies -n production
```

**Mitigation**:
```bash
# Enable circuit breakers to prevent cascade
kubectl apply -f k8s/istio/circuit-breaker.yaml -n production

# Restart dependent services in correct order
kubectl delete pod -n production -l app=codex-orchestrator
sleep 30
kubectl delete pod -n production -l app=codex-worker
```

---

## Appendix: Useful Commands Reference

**Quick diagnostic commands**:
```bash
# Check cluster health
kubectl cluster-info dump

# Get recent events
kubectl get events -n production --sort-by='.lastTimestamp' | tail -50

# Check resource requests vs available
kubectl top nodes
kubectl describe nodes

# Monitor deployment rollout
kubectl rollout status deployment/codex-api -n production

# Stream logs from multiple pods
kubectl logs -n production -l app=codex-api -f --tail=50

# Execute command in pod
kubectl exec -n production pod-name -- bash

# Port forward for debugging
kubectl port-forward -n production svc/codex-api 8080:8080
```

---

**Document Version**: 1.0  
**Last Reviewed**: 2024-01-15  
**Next Review Date**: 2024-02-15
