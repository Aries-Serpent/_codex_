# Production Observability: Incident Response & Rollback Procedures

**Phase**: 7D (Pre-v0.1.0-final)  
**Authority**: @mbaetiong (D-level autonomy)  
**Status**: Production-Ready Implementation Guide  
**Last Updated**: 2026-06-20  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Incident Classification](#incident-classification)
3. [Common Incident Scenarios](#common-incident-scenarios)
4. [Rollback Decision Matrix](#rollback-decision-matrix)
5. [Rollback Procedures](#rollback-procedures)
6. [Communication Protocol](#communication-protocol)
7. [Post-Incident Review](#post-incident-review)
8. [Escalation Matrix](#escalation-matrix)

---

## Executive Summary

An incident is any unplanned event causing or potentially causing:
- Service unavailability
- Data loss or corruption
- Performance degradation affecting users
- Security compromise
- SLA violation

**Incident Severity Levels**:
- **SEVER.IOU.S** (Critical): Immediate user impact, rollback likely
- **HIGH**: Significant degradation, manual intervention needed
- **MEDIUM**: Functional degradation, monitoring required
- **LOW**: Minor issue, monitor and resolve

**Decision Point**: Decide within 5 minutes whether to rollback

---

## Incident Classification

### Severity 1: Critical (Immediate Rollback Likely)

**Triggers**:
- Complete service outage (0 healthy instances)
- Data loss or corruption reported
- Security breach detected
- Error rate > 20% sustained
- Availability dropped < 95%
- Revenue-impacting feature broken

**Response Time**: < 2 minutes
**Decision Time**: < 5 minutes
**Recovery Target**: < 15 minutes

```bash
# Severity 1 Response Template
echo "🚨 CRITICAL INCIDENT - AUTO-PAGING"
# 1. Immediate: Page on-call primary + manager
# 2. Minute 2: Declare incident in war room
# 3. Minute 5: Make rollback decision
# 4. Minute 15: Target resolution
```

### Severity 2: High (Manual Intervention Needed)

**Triggers**:
- Error rate 10-20% sustained
- Availability 95-99%
- Partial feature degradation
- Database slow queries causing timeouts
- Cache unavailable

**Response Time**: < 15 minutes
**Decision Time**: < 30 minutes
**Recovery Target**: < 1 hour

### Severity 3: Medium (Monitor & Investigate)

**Triggers**:
- Error rate 5-10%
- Minor feature issues
- Performance degradation
- Single instance down

**Response Time**: < 1 hour
**Investigation**: Ongoing
**No immediate rollback unless escalates

### Severity 4: Low (Informational)

**Triggers**:
- Error rate < 5%
- Performance within acceptable range
- Low-impact feature issue
- Scheduled maintenance

**Response**: Monitor, resolve during business hours

---

## Common Incident Scenarios

### Scenario 1: Out of Memory (OOM)

**Symptoms**:
- Pod evictions or restarts
- Error rate spike to 50%+
- New pods failing to start

**Root Causes**:
- Memory leak introduced
- Spike in traffic exceeding capacity
- Cache growth uncontrolled

**Investigation (5 min)**:

```bash
#!/bin/bash

echo "=== OOM Incident Investigation ==="

# 1. Check recent memory trends
curl -s 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=process_resident_memory_bytes' \
  --data-urlencode 'start=2026-06-20T00:00:00Z' \
  --data-urlencode 'end=2026-06-20T01:00:00Z' \
  --data-urlencode 'step=60s' > memory_trend.json

# 2. Identify pod evictions
kubectl describe pod $POD_NAME | grep -A 5 "State:"

# 3. Check application logs for allocation failures
kubectl logs $POD_NAME | grep -i "memory\|malloc\|OOM"

# 4. Get memory by process
kubectl exec $POD_NAME -- ps aux --sort=-rss | head -10
```

**Resolution Options**:

| Option | Effort | Downtime | Risk |
|--------|--------|----------|------|
| Scale down replicas | 1 min | None | Medium (fewer capacity) |
| Increase resource limits | 5 min | None | Low |
| Restart pods | 2 min | <30s | High (may recur) |
| **Rollback** | 10 min | 1-2min | Low |

**Recommended Action**: If memory growing uncontrolled → **Rollback**

### Scenario 2: Database Connection Pool Exhaustion

**Symptoms**:
- "Too many connections" errors
- Response latency spike
- New requests queued

**Investigation**:

```bash
# Check active connections
psql $DB_NAME << SQL
SELECT count(*) as active_connections FROM pg_stat_activity;
SELECT client_addr, count(*) FROM pg_stat_activity GROUP BY client_addr;
SQL

# Check slow queries holding locks
SELECT pid, query, query_start FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 min';

# Check for idle transactions
SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';
```

**Resolution Options**:

| Option | Action | Recovery Time |
|--------|--------|----------------|
| Increase pool size | Quick fix | 1 min |
| Kill idle transactions | Moderate | 2 min |
| Restart app | Temporary fix | 5 min |
| Database optimization | Proper fix | 30 min |
| **Rollback** | Last resort | 10 min |

**Recommended Action**: Increase pool size first, rollback if ineffective

### Scenario 3: High Error Rate in Single Endpoint

**Symptoms**:
- /api/v1/predict returns 500 errors
- Other endpoints working fine
- Error spike coincides with deployment

**Investigation (3 min)**:

```bash
# Get error logs from last 5 minutes
curl -s 'http://loki:3100/loki/api/v1/query' \
  --data-urlencode 'query={job="codex-ml", level="error"}' | \
  jq '.data.result[0].values[] | select(.[0] > '$(date -d "5 min ago" +%s%N)')'

# Check endpoint-specific logs
kubectl logs -l app=codex-ml | grep -i "predict" | grep ERROR

# Verify recent code changes
git log --oneline -5
```

**Resolution Options**:

| Root Cause | Solution | Rollback? |
|-----------|----------|-----------|
| Bug in new code | Hotfix + deploy | Maybe |
| Dependency unavailable | Restore dependency | Maybe |
| Configuration wrong | Fix config + restart | No |
| Load issue | Scale horizontally | No |

**Recommended Action**: Investigate root cause first (5-10 min), rollback if unclear

### Scenario 4: External API Dependency Down

**Symptoms**:
- Timeouts calling external API
- Cascading failures in dependent services
- Error rate increasing over time

**Investigation**:

```bash
# Check connectivity to external service
curl -I https://api.external.com/health

# Check DNS resolution
nslookup api.external.com

# Monitor for connection timeouts
kubectl logs -l app=codex-ml | grep -i "timeout\|refused"

# Check firewall/network policies
kubectl exec $POD_NAME -- nc -zv api.external.com 443
```

**Resolution Options**:

| Action | Time | Effectiveness |
|--------|------|----------------|
| Enable fallback cache | 2 min | High if stale data OK |
| Reduce timeout | 1 min | Partial (faster failures) |
| Redirect traffic elsewhere | 5 min | If alt available |
| **Do NOT rollback** | - | External issue |

**Recommended Action**: Implement circuit breaker, use cached data, monitor for recovery

### Scenario 5: Model Prediction Accuracy Degraded

**Symptoms**:
- Model returning predictions with low confidence
- Customer reports (not alerts)
- Accuracy metric drops below threshold

**Investigation (15 min)**:

```bash
# Check model version
curl http://codex-ml/model/info

# Compare recent predictions vs baseline
SELECT avg(confidence) as accuracy FROM predictions
WHERE created_at > now() - interval '1 hour'
GROUP BY created_at;

# Check for data quality issues
SELECT count(*) FROM training_data
WHERE quality_score < 0.5 AND created_at > now() - interval '24 hours';

# Check for model drift
SELECT * FROM model_metrics WHERE timestamp > now() - interval '24 hours'
ORDER BY timestamp DESC LIMIT 20;
```

**Resolution Options**:

| Action | Time | Risk |
|--------|------|------|
| Retrain model | 30-60 min | Medium (risky timing) |
| Use previous model version | 5 min | Low (regression) |
| Apply confidence threshold | 1 min | Medium (reject predictions) |
| **Rollback** | 10 min | Low |

**Recommended Action**: Check recent training data quality, consider rollback if caused by code changes

---

## Rollback Decision Matrix

### When to Rollback (Decision Tree)

```
Incident occurs
    ├─ Error rate > 20%?
    │  └─ YES → Rollback likely
    │      └─ Check: Unknown root cause within 5 min?
    │          ├─ YES → Rollback
    │          └─ NO → Investigate 5 more min
    │
    ├─ Complete service down?
    │  └─ YES → Rollback
    │
    ├─ Data loss or corruption?
    │  └─ YES → Rollback + restore from backup
    │
    ├─ Dependency failure (external)?
    │  └─ YES → DO NOT rollback (external issue)
    │      └─ Implement workaround
    │
    ├─ Configuration error detected?
    │  └─ YES → Fix config + restart (faster than rollback)
    │
    ├─ Known issue with quick fix?
    │  └─ YES → Hotfix + deploy
    │
    └─ Unknown cause after 10 min?
       └─ YES → Rollback (safety first)
```

### Rollback Criteria Checklist

**ROLLBACK if ANY of these are true**:
- [ ] Error rate > 20% sustained
- [ ] Service completely unavailable
- [ ] Data loss reported or suspected
- [ ] Unknown root cause after 10 minutes
- [ ] Security breach detected
- [ ] Availability < 95%

**DO NOT ROLLBACK if**:
- [ ] Root cause identified and quick fix available
- [ ] Issue is external dependency (not app issue)
- [ ] Issue is configuration-only (no code change needed)
- [ ] Single endpoint affected with known workaround
- [ ] Error rate low and stable

---

## Rollback Procedures

### Pre-Rollback Checklist

```bash
#!/bin/bash

echo "🔄 PRE-ROLLBACK VALIDATION"

# 1. Verify current version
CURRENT=$(kubectl rollout history deployment/codex-ml | tail -2 | head -1 | awk '{print $1}')
echo "Current revision: $CURRENT"

# 2. Verify previous version exists
PREVIOUS=$((CURRENT - 1))
PREV_STATUS=$(kubectl rollout history deployment/codex-ml | grep -F "  $PREVIOUS  ")
if [ -z "$PREV_STATUS" ]; then
  echo "❌ Previous revision $PREVIOUS not found!"
  exit 1
fi
echo "✓ Previous revision $PREVIOUS available"

# 3. Verify rollback won't cause data loss
# (Custom check based on app specifics)
echo "Checking for pending transactions..."
PENDING=$(kubectl exec $POSTGRES_POD -- psql -c "SELECT count(*) FROM transactions WHERE status='pending'")
if [ $PENDING -gt 0 ]; then
  echo "⚠️  WARNING: $PENDING pending transactions"
  echo "Rollback may leave these incomplete"
  read -p "Continue with rollback? (y/n) " -n 1
  echo
fi

# 4. Notify stakeholders
echo "Sending notification..."
# Post to #incidents channel
curl -X POST $SLACK_WEBHOOK \
  -d '{"text":"🔄 Initiating rollback from v0.1.0-final to previous version"}'

echo "✓ Pre-rollback validation complete"
```

### Step-by-Step Rollback (Kubernetes)

**Duration**: ~5 minutes

```bash
#!/bin/bash

set -e
TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
echo "[$TIMESTAMP] Starting rollback procedure..."

# Step 1: Check current state (30 sec)
echo "[Step 1] Verifying current deployment state..."
kubectl get deployment codex-ml -o jsonpath='{.spec.template.spec.containers[0].image}'
CURRENT_REV=$(kubectl rollout history deployment/codex-ml | tail -2 | head -1 | awk '{print $1}')
echo "Current revision: $CURRENT_REV"

# Step 2: Trigger rollback (30 sec)
echo "[Step 2] Rolling back to previous version..."
kubectl rollout undo deployment/codex-ml
echo "Rollback initiated"

# Step 3: Wait for rollout to complete (2-3 min)
echo "[Step 3] Waiting for rollback to complete..."
kubectl rollout status deployment/codex-ml --timeout=300s
ROLLBACK_STATUS=$?

if [ $ROLLBACK_STATUS -ne 0 ]; then
  echo "❌ Rollback failed or timed out!"
  kubectl describe deployment codex-ml
  exit 1
fi

# Step 4: Verify new (old) deployment (1 min)
echo "[Step 4] Verifying rolled-back version..."
NEW_IMAGE=$(kubectl get deployment codex-ml -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "New image: $NEW_IMAGE"

# Check pod health
RUNNING=$(kubectl get pods -l app=codex-ml -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | wc -w)
TOTAL=$(kubectl get pods -l app=codex-ml -o jsonpath='{.items[*].metadata.name}' | wc -w)
echo "Pods running: $RUNNING/$TOTAL"

# Step 5: Verify connectivity (1 min)
echo "[Step 5] Verifying service connectivity..."
for i in {1..30}; do
  if curl -s http://codex-ml/health > /dev/null 2>&1; then
    echo "✓ Service responding"
    break
  fi
  echo "Attempt $i/30..."
  sleep 1
done

# Step 6: Monitor metrics (ongoing)
echo "[Step 6] Monitoring post-rollback metrics..."
for i in {1..60}; do
  ERROR_RATE=$(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])' | \
    jq '.data.result[0].value[1]' 2>/dev/null || echo "0")

  if (( $(echo "$ERROR_RATE < 0.01" | bc -l) )); then
    echo "✓ Error rate normalizing: ${ERROR_RATE}%"
    break
  fi

  echo "Error rate: ${ERROR_RATE}% (waiting for stabilization...)"
  sleep 1
done

# Step 7: Post-rollback notification
echo "[Step 7] Sending completion notification..."
curl -X POST $SLACK_WEBHOOK \
  -d '{
    "text": "✓ Rollback completed successfully",
    "attachments": [{
      "fields": [
        {"title": "Previous Revision", "value": "'$CURRENT_REV'"},
        {"title": "New Revision", "value": "'$(kubectl rollout history deployment/codex-ml | tail -1 | awk '{print $1}')'"},
        {"title": "Duration", "value": "~5 minutes"}
      ]
    }]
  }'

echo ""
echo "✓ ROLLBACK COMPLETE"
echo "Next: Review root cause and post-incident actions"
```

### Alternative: Manual Rollback (No Kubernetes)

```bash
#!/bin/bash

# If using direct Docker/systemd

# 1. Stop current version
systemctl stop codex-ml

# 2. Backup current state
cp -r /opt/codex-ml/data /opt/codex-ml/data.backup.$(date +%s)

# 3. Deploy previous version
cd /opt/codex-ml
git checkout v0.1.0-previous
docker build -t codex-ml:v0.1.0-previous .
docker stop codex-ml-prod
docker rm codex-ml-prod
docker run -d \
  --name codex-ml-prod \
  -p 8000:8000 \
  codex-ml:v0.1.0-previous

# 4. Verify
sleep 5
curl http://localhost:8000/health
```

---

## Communication Protocol

### Incident Declared

**Timing**: Immediately (< 1 min)

```bash
# Template: Incident Declaration Message

cat > /tmp/incident_message.txt << EOF
🚨 INCIDENT DECLARED: $(date -u +'%Y-%m-%d %H:%M:%S UTC')

SEVERITY: $SEVERITY (1=Critical, 2=High, 3=Medium, 4=Low)
STATUS: Investigating
AFFECTED: $AFFECTED_SERVICE
IMPACT: $IMPACT_DESCRIPTION

Details:
- Error rate: $ERROR_RATE
- Availability: $AVAILABILITY
- Affected users: $AFFECTED_USERS

Incident Lead: $INCIDENT_COMMANDER
Slack Channel: #incident-$INCIDENT_ID

Updates every 5 minutes.
EOF

# Post to Slack
curl -X POST $SLACK_WEBHOOK -d @/tmp/incident_message.txt

# Page on-call if severity 1 or 2
if [ $SEVERITY -le 2 ]; then
  pd trigger-incident \
    --description "INCIDENT: $AFFECTED_SERVICE ($SEVERITY)" \
    --service-key $PAGERDUTY_KEY
fi
```

### Hourly Status Updates

```
[HH:MM UTC] 🔴 ACTIVE - Investigation ongoing

Last Update: Analysis shows [ROOT_CAUSE]
Current Action: [ACTION_BEING_TAKEN]
ETA to Resolution: [ETA or "Unknown - investigating"]

Metrics:
- Error rate: DOWN from XX% to XX%
- Availability: UP to XX%
- Customer Impact: [NUMBER] affected
- Pending: [NEXT_STEPS]

Next Update: [HH+1:MM UTC]
```

### Resolution Announced

```
✅ INCIDENT RESOLVED - $(date -u +'%Y-%m-%d %H:%M:%S UTC')

Root Cause: [DESCRIPTION]
Resolution: [DESCRIPTION]
Duration: [HH:MM]

Timeline:
- Detected: HH:MM
- Investigated: HH:MM - HH:MM
- Resolved: HH:MM

Post-incident review scheduled for: [DATE/TIME]
Slack channel remains active for 24 hours.
```

---

## Post-Incident Review

### Within 1 Hour of Resolution

**Blameless Post-Mortem Template**

File: `/opt/monitoring/postmortems/incident-$INCIDENT_ID.md`

```markdown
# Post-Mortem: [Incident Title]

**Date**: YYYY-MM-DD
**Duration**: HH:MM to HH:MM (X hours Y minutes)
**Severity**: 1/2/3/4

## Executive Summary

[2-3 sentence summary of what happened and impact]

## Timeline

| Time | What Happened | Who | Status |
|------|---------------|-----|--------|
| HH:MM | Incident detected by [alert/user] | [name] | Ongoing |
| HH:MM | Root cause identified as [cause] | [name] | Investigating |
| HH:MM | [Action] taken | [name] | In progress |
| HH:MM | Service recovered | [name] | Resolved |

## Root Cause Analysis

### What Went Wrong
[Describe the technical failure]

### Why It Happened
[Explain the underlying cause(s)]

### Why We Didn't Catch It
[What monitoring/testing gaps existed]

## Impact Assessment

- **Users Affected**: [NUMBER]
- **Duration**: X minutes
- **Data Loss**: [YES/NO] - if yes, describe
- **Revenue Impact**: $[AMOUNT] (if applicable)
- **SLA Impact**: [Availability drop to XX%]

## Contributing Factors

1. [Factor] - contributed by [REASON]
2. [Factor] - contributed by [REASON]
3. [Factor] - contributed by [REASON]

## Immediate Actions Taken

- [Action 1] at [TIME]
- [Action 2] at [TIME]
- [Action 3] at [TIME]

## Lessons Learned

### What Went Well ✓
- Good monitoring alerted us
- Team responded quickly
- Clear communication

### What Could Be Better ⚠️
- [Gap 1] - we should have [prevention]
- [Gap 2] - we should have [prevention]
- [Gap 3] - we should have [prevention]

## Action Items (30-60 days)

| Item | Owner | Target Date | Type |
|------|-------|-------------|------|
| Implement [monitoring] | [Name] | [DATE] | Detection |
| Add [test case] | [Name] | [DATE] | Prevention |
| Update [runbook] | [Name] | [DATE] | Response |
| [Code change] | [Name] | [DATE] | Prevention |

## Prevention & Remediation

### Short-term (1-7 days)
- [ ] Add alerting for [metric]
- [ ] Update [runbook]
- [ ] Deploy hotfix [PR#]

### Medium-term (1-4 weeks)
- [ ] Implement [architecture change]
- [ ] Add integration test for [scenario]
- [ ] Refactor [component]

### Long-term (1-3 months)
- [ ] Redesign [system]
- [ ] Migrate to [new platform]
- [ ] Implement [major feature]

## Attendees

- Incident Commander: [Name]
- On-Call Primary: [Name]
- Engineering Lead: [Name]
- Product Lead: [Name]
- Customer Success: [Name]

---

**Next Review**: [DATE] at [TIME]
**Approval**: [Name] (Post-Mortem Lead)
```

### Post-Mortem Meeting (T+24 hours)

```bash
# Scheduling
# Invite: incident team + relevant leads
# Duration: 60-90 minutes
# Format: Blameless review (not "who failed but what failed)

# Agenda:
# 1. Timeline walkthrough (15 min)
# 2. Root cause discussion (20 min)
# 3. Contributing factors (15 min)
# 4. Action items & owners (15 min)
# 5. Lessons learned discussion (10-15 min)
```

### Action Item Tracking

```bash
# Create Jira tickets for action items
for item in "${action_items[@]}"; do
  jira create --summary "$item" \
    --type "Incident Action" \
    --priority "High" \
    --component "Production" \
    --duedate "$(date -d '+14 days' +%Y-%m-%d)"
done
```

---

## Escalation Matrix

### Contact Information

```yaml
escalation_matrix:
  level_1:
    on_call_primary: alice@company.com (+1-555-0100)
    on_call_backup: bob@company.com (+1-555-0101)
    response_time: 5 minutes
    capability: "Investigate & resolve most incidents"

  level_2:
    engineering_manager: charlie@company.com (+1-555-0102)
    incident_commander: diana@company.com (+1-555-0103)
    response_time: 10 minutes
    capability: "Escalate, authorize rollbacks, coordinate response"

  level_3:
    engineering_director: evan@company.com (+1-555-0104)
    vp_operations: frank@company.com (+1-555-0105)
    response_time: 15 minutes
    capability: "Authorize emergency actions, customer communication"

  level_4:
    ceo: grace@company.com (+1-555-0106)
    legal_team: legal@company.com
    response_time: 30 minutes
    capability: "High-impact decisions, customer communications"
```

### Escalation Triggers

| Condition | Escalate To | Action |
|-----------|-------------|--------|
| Error rate > 50% for 5 min | Level 2 | Page manager |
| Service down > 10 min | Level 2 | Declare SEV-1 |
| Data loss confirmed | Level 2 | Page director on-call |
| Requires emergency deploy | Level 2 | Authorize hotfix |
| Customer reports data loss | Level 3 | Legal notification |
| Rollback fails | Level 2 | Manual intervention |
| Unresolved after 1 hour | Level 3 | Strategy change |

### Communication Escalation

```
Level 1: Team Slack channel
  ├─ 15 min → Level 2: Page on-call manager
  ├─ 30 min → Level 3: VP notification
  └─ 60 min → Level 4: Executive briefing

Each escalation includes:
  - Current status summary
  - ETA to resolution
  - Customer-facing message
  - Remediation plan
```

---

## 24/7 On-Call Responsibilities

### Primary On-Call Engineer

**Availability**: 24/7 during rotation

**Responsibilities**:
1. Respond to pages/alerts within 5 minutes
2. Assess incident severity
3. Implement immediate mitigations
4. Coordinate with other engineers
5. Provide hourly status updates
6. Make rollback decisions
7. Document incident timeline

**Cannot Delegate**:
- Initial incident response
- Severity assessment
- Escalation decisions

**Can Delegate**:
- Investigation details to specific engineers
- Implementation of fixes
- Communication to team (through IC)

### Backup On-Call Engineer

**Availability**: 24/7 during rotation

**Responsibilities**:
1. Support primary on-call
2. Take over if primary unavailable
3. Provide additional capacity for major incidents
4. Shadow incident response if escalated

### Incident Commander (Severity 1 Only)

**Availability**: 24/7 pager on for SEV-1

**Responsibilities**:
1. Coordinate all aspects of response
2. Maintain incident timeline
3. Provide status updates to leadership
4. Make strategic decisions
5. Authorize rollbacks/emergency actions
6. Prepare customer communications

---

## Checklist: Incident Response

### At Incident Start
- [ ] Alert acknowledged
- [ ] Incident declared in #incidents
- [ ] Incident ID created (INC-YYYYMMDD-HHmm)
- [ ] Slack channel created (#incident-[ID])
- [ ] Incident commander assigned
- [ ] Page appropriate escalation level

### During Investigation (every 15 min)
- [ ] Status update posted to #incident-[ID]
- [ ] Metrics being collected
- [ ] Root cause investigation underway
- [ ] Mitigation options documented

### At Decision Point (10 min)
- [ ] Rollback decision made and recorded
- [ ] If rollback: Pre-rollback validation complete
- [ ] If no rollback: Remediation plan documented
- [ ] Timeline captured in incident log

### Post-Resolution
- [ ] Service health confirmed
- [ ] Metrics returning to baseline
- [ ] Resolution message posted
- [ ] Post-mortem scheduled
- [ ] Action items created

---

**Next Steps:**
1. Test rollback procedure in staging
2. Schedule quarterly incident simulations
3. Update team contact list
4. Share runbooks with team members
5. Review procedures quarterly

---

**Document Status**: Ready for v0.1.0-final Production Deployment
**Last Tested**: [DATE]
**Next Review**: [DATE + 90 days]
