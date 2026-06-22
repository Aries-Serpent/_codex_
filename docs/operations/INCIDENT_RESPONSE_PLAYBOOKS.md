# Incident Response Playbooks

**Version**: 2.0.0  
**Effective Date**: 2026-06-14  
**Classification**: Internal — Operations  
**Owner**: Security & Operations Team  
**Last Updated**: 2026-06-14

---

## Table of Contents

1. [Overview](#overview)
2. [Incident Classification](#incident-classification)
3. [General Response Process](#general-response-process)
4. [Playbook: Credential Compromise](#playbook-credential-compromise)
5. [Playbook: Unauthorized Access](#playbook-unauthorized-access)
6. [Playbook: Data Breach](#playbook-data-breach)
7. [Playbook: Service Degradation](#playbook-service-degradation)
8. [Playbook: Supply Chain Attack](#playbook-supply-chain-attack)
9. [Communication & Escalation](#communication--escalation)
10. [Post-Incident Procedures](#post-incident-procedures)

---

## Overview

### Purpose

This document provides step-by-step procedures for responding to security incidents affecting the _codex_ platform. Each playbook is designed for rapid response with minimal escalation.

### Core Principles

1. **Containment First**: Stop the threat before investigation
2. **Communication**: Keep stakeholders informed
3. **Evidence Preservation**: Maintain audit trail
4. **Recovery**: Restore normal operations
5. **Learning**: Post-incident analysis

### Incident Response Team Roles

| Role | Responsibilities | Contact |
|------|---|---|
| **Incident Commander** | Overall coordination, decision-making | @on-call |
| **Security Lead** | Threat analysis, containment | @security-team |
| **Infrastructure Lead** | System remediation, recovery | @infrastructure-team |
| **Communications Lead** | Internal/external notifications | @communications-team |
| **Evidence Officer** | Log preservation, chain of custody | @security-team |

---

## Incident Classification

### Severity Levels

| Level | Name | Response Time | Example | Escalation |
|-------|------|---|---|---|
| **P0** | Critical | < 15 minutes | Service outage, data breach, RCE | CEO + Board |
| **P1** | High | < 1 hour | Auth bypass, privilege escalation | CTO + Security Lead |
| **P2** | Medium | < 4 hours | Performance degradation, suspicious activity | Team Leads |
| **P3** | Low | < 24 hours | Minor policy violation, information leak | Managers |

### Incident Categories

| Category | Examples | Detection Method |
|---|---|---|
| **Credential Compromise** | Leaked API key, stolen token | Monitoring alerts, external reports | <!-- pragma: allowlist secret -->
| **Unauthorized Access** | Brute force, SSRF attack | Failed auth logs, anomaly detection |
| **Data Breach** | Data exfiltration, unauthorized access | Data access monitoring, logs |
| **Service Degradation** | CPU spike, memory leak, DoS | Performance monitoring, alerts |
| **Supply Chain** | Malicious dependency, compromised dev tool | Dependency scanning, integrity checks |
| **Configuration Error** | Exposed secrets, bad firewall rule | Compliance scanning, audits | <!-- pragma: allowlist secret -->

---

## General Response Process

### Phase 1: Detection & Triage (0-15 minutes)

```
DETECT INCIDENT
  ├─ Alert triggered / Report received
  ├─ Log initial information
  └─ Acknowledge receipt
  
CLASSIFY
  ├─ Severity level (P0-P3)
  ├─ Category (Credential/Access/Breach/Performance/Supply Chain)
  └─ Initial impact assessment
  
ASSEMBLE TEAM
  ├─ Notify Incident Commander
  ├─ Notify Security Lead
  ├─ Notify Infrastructure Lead
  └─ Create incident Slack channel: #incident-YYYY-MMDD-XXX
  
CREATE INCIDENT LOG
  ├─ Incident ID
  ├─ Detection time
  ├─ Severity
  ├─ Category
  ├─ Commander assigned
  └─ Initial impact
```

**Incident Log Template**:
```
INCIDENT ID: INC-2026-0614-001
SEVERITY: P1
CATEGORY: Credential Compromise
COMMANDER: @on-call
CREATED: 2026-06-14T14:30:00Z
STATUS: Investigating

TIMELINE:
- [14:30] Initial alert (SSH key detected in logs)
- [14:35] Incident commander assigned
- [14:40] Investigation started
```

### Phase 2: Investigation (15 min - 2 hours)

**Immediate Actions**:
```bash
# 1. Secure the scene (stop automatic remediation)
export INCIDENT_MODE=true

# 2. Collect initial evidence
python scripts/security/collect_incident_evidence.py \
  --incident-id=$INCIDENT_ID \
  --start-time="$INCIDENT_TIME" \
  --preserve-logs=true

# 3. Review affected systems
./scripts/incident/affected_systems.sh

# 4. Check for active threats
./scripts/security/check_active_threats.sh
```

**Investigation Checklist**:
- [ ] Application logs for error patterns
- [ ] System logs for unauthorized access
- [ ] Network logs for anomalous traffic
- [ ] Recent deployments/changes
- [ ] External service status
- [ ] Affected user/data scope
- [ ] Root cause hypothesis

## Phase 3: Containment (Immediate)

**For Security Incidents**:
```
CONTAIN THREAT
  ├─ Isolate affected systems
  ├─ Revoke compromised credentials
  ├─ Block malicious IPs
  ├─ Enable enhanced logging
  ├─ Preserve evidence
  └─ Activate backup systems
```

**For Performance Incidents**:
```
STABILIZE SERVICE
  ├─ Enable circuit breakers
  ├─ Scale down non-critical services
  ├─ Redirect traffic to healthy instances
  ├─ Enable maintenance mode if needed
  └─ Activate on-call for monitoring
```

### Phase 4: Remediation

1. Implement fix or workaround
2. Test in staging (if possible)
3. Deploy to production with monitoring
4. Verify fix effectiveness
5. Monitor for regression

### Phase 5: Recovery

1. Restore normal operations
2. Re-enable disabled features
3. Clear maintenance mode
4. Verify all systems operational
5. Get stakeholder confirmation

### Phase 6: Post-Incident

1. Schedule post-incident review (within 48 hours)
2. Complete incident report
3. Identify follow-up actions
4. Update runbooks/documentation
5. Share learnings with team

---

## Playbook: Credential Compromise

### Detection Signals

- ✅ Credential found in public repository
- ✅ API key detected in logs or metrics
- ✅ Suspicious token usage from unknown IP
- ✅ Failed authentication attempts spike
- ✅ External security report of leaked credential
- ✅ Audit log shows credential in logs
- ✅ Pre-commit hook alert (credential pattern)

### P0 Response (< 15 minutes)

```bash
# ⚠️ IMMEDIATE ACTIONS - Execute within 5 minutes

# 1. IDENTIFY compromised credential
CREDENTIAL_TYPE="github_oauth_token"  # or: api_key, jwt_key, db_password
LAST_USAGE="2026-06-14T14:22:00Z"
COMPROMISED_AT="2026-06-14T14:15:00Z"

# 2. REVOKE compromised credential
python scripts/security/revoke_credential.py \
  --type=$CREDENTIAL_TYPE \
  --emergency \
  --immediate-effect

# Output: ✅ Credential revoked, cache cleared

# 3. ROTATE replacement credential
python scripts/rotate_secret.py \
  --secret=$CREDENTIAL_TYPE \
  --emergency \
  --notify-on-complete

# Output: ✅ New credential active

# 4. BLOCK suspicious IP/account
if [ ! -z "$ATTACKER_IP" ]; then
  python scripts/security/block_ip.py \
    --ip=$ATTACKER_IP \
    --duration=24h \
    --reason="Credential compromise"
fi

# 5. INVALIDATE active sessions
python scripts/security/invalidate_sessions.py \
  --reason="Credential compromise" \
  --grace-period=60min

# 6. NOTIFY team immediately
python scripts/incident/notify_team.py \
  --severity=P0 \
  --channel=security \
  --message="Credential compromised: $CREDENTIAL_TYPE, rotated and revoked"
```

## P1 Response (1-4 hours)

**Investigation Phase**:
```bash
# 1. Determine compromise scope
# - When was credential created?
# - When was it compromised?
# - What was accessed with it?

git log --all --oneline | grep -i "$CREDENTIAL"
# Find: When credential was introduced

# 2. Analyze credential usage
python scripts/security/analyze_credential_usage.py \
  --credential-id=$COMPROMISED_CRED_ID \
  --lookback=7days

# Review: All access made with this credential

# 3. Check for unauthorized actions
# - Deployment history
# - Code changes
# - Configuration modifications
# - Secret access

git log --since="$COMPROMISED_AT" --oneline
github api repos/Aries-Serpent/_codex_/pulls \
  --search="created:>$COMPROMISED_AT"

# 4. Identify affected systems/data
python scripts/security/affected_systems_scan.py \
  --credential=$CREDENTIAL_TYPE \
  --since=$COMPROMISED_AT

# 5. Review access logs
grep "$ATTACKER_IP\|$STOLEN_TOKEN" /var/log/auth.log
grep "$STOLEN_TOKEN" ~/.bash_history 2>/dev/null

# 6. Determine if data was accessed
# - Check data access audit trail
# - Review database query logs
# - Check S3 access logs

# 7. Assess credential lifetime and impact
COMPROMISE_DURATION=$(($(date +%s) - $(date -d "$COMPROMISED_AT" +%s)))
echo "Credential compromised for: $COMPROMISE_DURATION seconds"
```

**Containment Phase**:
```bash
# 1. Review deployment history with compromised token
# - Check who deployed what, when
# - Verify all deployments are legitimate

# 2. Audit code changes
# - Check all commits during compromise window
# - Verify commits are from expected developers
# - Review code for malicious changes

# 3. If malicious code found:
# - Revert commits
# - Re-deploy clean version
# - Notify team

# 4. If data was accessed:
# - Begin data breach response (see Playbook: Data Breach)

# 5. Monitor for reuse of same credential
while true; do
  python scripts/security/monitor_credential_usage.py \
    --credential-id=$COMPROMISED_CRED_ID \
    --alert-on-usage
  sleep 60
done
```

## Recovery Phase

```bash
# 1. Deploy with new credential
# - Verify new credential is in secrets
# - Deploy application
# - Monitor for errors

# 2. Verify normal operations
curl https://api.example.com/health
# Expected: 200 OK

# 3. Confirm credential rotation
python scripts/rotate_secret.py --verify $CREDENTIAL_TYPE
# Expected: ✅ New credential active

# 4. Clear temporary security measures
# - Remove IP block (after 24 hours)
# - Restore normal rate limiting

# 5. Update incident log
echo "Credential compromise contained and remediated" >> incident.log
```

## Post-Incident

```bash
# 1. Root cause analysis
# - How was credential exposed?
# - Why wasn't it detected earlier?
# - What preventive measures needed?

# 2. Update documentation
# - Update rotation procedures
# - Add new detection rules
# - Improve secret protection

# 3. Team briefing
# - Review what happened
# - Discuss lessons learned
# - Update training materials

# 4. Implement preventive measures
# - Better secret scanning
# - Improved rotation automation
# - Enhanced monitoring
```

---

## Playbook: Unauthorized Access

### Detection Signals

- ✅ 100+ failed login attempts (brute force)
- ✅ Successful login from unusual location
- ✅ Access to sensitive operations (escalation)
- ✅ Suspicious API calls from unknown source
- ✅ Privilege escalation detection
- ✅ Policy violation alert

### P0 Response (< 15 minutes)

```bash
# ⚠️ IMMEDIATE ACTIONS

# 1. IDENTIFY attacker
ATTACKER_IP=$(grep "Failed password" /var/log/auth.log | tail -1 | awk '{print $NF}')
echo "Attacker IP: $ATTACKER_IP"

# 2. BLOCK attacker immediately
sudo iptables -A INPUT -s $ATTACKER_IP -j DROP
# For production: Update WAF/firewall rules

python scripts/security/block_ip.py \
  --ip=$ATTACKER_IP \
  --duration=24h \
  --reason="Unauthorized access attempt"

# 3. INVALIDATE compromised session
python scripts/security/invalidate_session.py \
  --ip=$ATTACKER_IP \
  --reason="Unauthorized access"

# 4. LOCK potentially compromised account
if [ ! -z "$COMPROMISED_USER" ]; then
  python scripts/security/lock_account.py \
    --username=$COMPROMISED_USER \
    --require-password-reset
fi

# 5. RESET MFA for affected user
python scripts/security/reset_mfa.py --user=$COMPROMISED_USER

# 6. NOTIFY immediately
slack-notify "#security" "🚨 UNAUTHORIZED ACCESS: IP $ATTACKER_IP blocked, account locked"
```

## Investigation Phase

```bash
# 1. Analyze attack pattern
grep "$ATTACKER_IP" /var/log/auth.log | head -100
# Look for: Attack timeframe, methods, targets

# 2. Check what was accessed
curl -H "Authorization: ******" \
  https://api.example.com/admin/users 2>&1 | grep -i error
# Check: What endpoints did attacker try?

# 3. Determine if attacker got in
# - Check for successful authentication
# - Review access logs for successful actions
# - Check for data copies/changes

# 4. Identify vulnerability exploited
# - Weak password? (password spray)
# - Phishing/social engineering?
# - Application vulnerability? (SQL injection)
# - Compromised credential? (reuse)

# 5. Assess damage
# - What data accessed?
# - What was changed?
# - What was exfiltrated?
```

## Containment & Recovery

```bash
# 1. If attacker didn't succeed:
# - Maintain IP block
# - Monitor for retry attempts
# - Strengthen targeted system

# 2. If attacker got in:
# - Begin Data Breach response (see Playbook)
# - Review all recent activities
# - Check for persistent backdoors

# 3. Reset affected systems
# - Force password reset
# - Revoke all tokens/sessions
# - Re-provision security keys

# 4. Deploy hardening
# - Increase MFA enforcement
# - Reduce password lifetime
# - Add rate limiting
# - Deploy honeypot accounts
```

---

## Playbook: Data Breach

### Detection Signals

- ✅ Unusual data access patterns
- ✅ Large data downloads detected
- ✅ Exfiltration to external system
- ✅ Data modification timestamp anomaly
- ✅ External report of leaked data
- ✅ Unauthorized database query

### P0 Response (< 15 minutes)

```bash
# ⚠️ IMMEDIATE ACTIONS

# 1. ISOLATE affected database
python scripts/security/isolate_database.py \
  --database=$DB_NAME \
  --allow-current-connections-only

# 2. ENABLE immutable audit logging
python scripts/security/enable_immutable_logging.py

# 3. SNAPSHOT for forensics
pg_dump --all > /secure/forensics/db-snapshot-$(date +%s).sql
chmod 600 /secure/forensics/db-snapshot-*.sql

# 4. IDENTIFY scope of breach
# - What data was accessed?
# - How much data?
# - How many records?
# - Sensitive data types?

# 5. NOTIFY stakeholders
slack-notify "#security" "🚨 P0 DATA BREACH: Scope being determined"

# 6. BEGIN investigation
python scripts/security/analyze_data_access.py \
  --since="$BREACH_START_TIME" \
  --generate-report
```

## Investigation Phase

```bash
# 1. Determine breach timeline
# - When did access start?
# - When was it discovered?
# - How long was breach active?

BREACH_DURATION=$(($(date +%s) - $(date -d "$BREACH_START" +%s)))

# 2. Identify affected data
# - Which tables were accessed?
# - Which columns (PII/sensitive)?
# - Which records (user count)?

psql -U postgres $DB_NAME << EOF
SELECT table_name FROM accessed_tables WHERE breach_time > '$BREACH_START'
SELECT COUNT(*) FROM users WHERE last_access > '$BREACH_START'
EOF

# 3. Determine if data was copied
# - Check for large SELECT queries
# - Check for data exports/dumps
# - Check for network transfers

# 4. Identify exfiltration path
# - Internal attacker or external?
# - Application vulnerability?
# - Compromised account?

# 5. Assess regulatory impact
# - GDPR: EU user data affected?
# - CCPA: California user data affected?
# - HIPAA: Protected health info?
# - PCI DSS: Payment card data?
```

## Response Phase

```bash
# 1. Restore database to pre-breach state
# - Use clean backup
# - Verify integrity
# - Monitor for regression

# 2. Notify affected users
# - Prepare notification template
# - Legal review required
# - Compliance team approval

# 3. Notify regulators/authorities
# - Submit required breach notifications
# - Include scope, timeline, remediation
# - Follow regulatory timelines

# 4. Preserve evidence
# - Immutable backup of logs
# - Chain of custody documentation
# - Forensic evidence collection

# 5. Update security controls
# - Patch vulnerability
# - Enhance detection
# - Improve access controls
```

---

## Playbook: Service Degradation

### Detection Signals

- ✅ Error rate > 5% (alert threshold)
- ✅ Response latency > 5 seconds
- ✅ Health check failures
- ✅ Resource exhaustion (CPU > 90%, memory > 85%)
- ✅ Database connection pool exhausted
- ✅ Dependency service unreachable

### P1 Response (< 1 hour)

```bash
# 1. DETECT root cause
python scripts/incident/diagnose_degradation.py \
  --metric="error_rate|latency|cpu|memory"

# Output examples:
# ❌ Database connection pool exhausted (95/100)
# ❌ CPU spike due to runaway query
# ❌ Memory leak in cache layer

# 2. IMMEDIATE MITIGATION
case "$ROOT_CAUSE" in
  "db_connections_exhausted")
    # Restart connection pool / scale read replicas
    kubectl scale deployment codex-api --replicas=5
    ;;
  "memory_leak")
    # Restart affected pods
    kubectl rollout restart deployment/codex-api
    ;;
  "cpu_spike")
    # Disable non-critical features / scale up
    kubectl scale deployment codex-api --replicas=8
    ;;
  "external_dependency")
    # Activate circuit breaker / failover
    curl -X POST https://api.example.com/admin/circuit-breaker?state=open
    ;;
esac

# 3. MONITOR recovery
python scripts/incident/monitor_recovery.py \
  --target-metric="error_rate<1%" \
  --timeout=5min

# Output: ✅ Service recovered
```

## Investigation & Fix

```bash
# 1. Identify root cause
# - Recent deployment?
# - Traffic spike?
# - Resource leak?
# - Third-party issue?

git log --since="1 hour ago" --oneline  # Recent changes?
kubectl top nodes                       # Resource usage
kubectl logs deployment/codex-api --tail=100 | grep -i error

# 2. Apply fix
# If recent deployment: Rollback
kubectl rollout undo deployment/codex-api --to-revision=0

# If resource issue: Scale up
kubectl scale deployment codex-api --replicas=10

# If database issue: Query optimization / restart
# If external issue: Activate failover

# 3. Monitor for regression
while true; do
  curl -f https://api.example.com/health || break
  sleep 10
done
echo "✅ Service stable"
```

---

## Playbook: Supply Chain Attack

### Detection Signals

- ✅ Unknown dependency version in lock file
- ✅ Malicious code in dependency (SBOM scan)
- ✅ Dependency with unusual activity
- ✅ Security advisory for dependency
- ✅ Build artifact hash mismatch

### P0 Response

```bash
# 1. IDENTIFY malicious dependency
pip-audit --format=json | jq '.vulnerabilities[]'

# 2. QUARANTINE affected builds
python scripts/security/quarantine_builds.py \
  --dependency=$MALICIOUS_PKG \
  --version=$VERSION

# 3. REVOKE affected releases
python scripts/security/revoke_release.py \
  --package=$MALICIOUS_PKG \
  --version=$VERSION

# 4. SCAN for exploitation
grep -r "from $MALICIOUS_PKG import" src/
# Check: Was malicious code used?

# 5. BEGIN forensics
python scripts/security/analyze_build_history.py \
  --dependency=$MALICIOUS_PKG \
  --generate-report
```

---

## Communication & Escalation

### Incident Notification

**Immediate** (within 5 minutes):
```
🚨 INCIDENT - [SEVERITY]

Incident ID: INC-2026-0614-001
Category: [Type]
Status: Investigating
Commander: [Name]
Impact: [Systems/Services affected]

Updates every 30 minutes in #incident-[id]
```

**Escalation Path**:
```
P0 (Critical):
  0-15 min  → Incident Commander + On-call
  15-30 min → Team Lead + Security Lead
  30+ min   → CTO + Security Director
  
P1 (High):
  0-1 hour  → Incident Commander
  1+ hour   → Team Lead + Security Lead
  
P2 (Medium):
  0-4 hours → Incident Commander
  
P3 (Low):
  0-24 hours → Assigned engineer
```

### External Communication

**If customer impact confirmed**:
```
We are investigating [issue type].

Affected Services: [List services]
Your Impact: [What customers experience]
Our Response: Our team is actively investigating.
Status: [Current status]
Updates: [Expected timeline]

We apologize for the disruption.
```

---

## Post-Incident Procedures

### Incident Report Template

```markdown
# Incident Report: INC-2026-0614-001

## Summary
- **Date**: 2026-06-14
- **Duration**: 14:30 - 15:45 (75 minutes)
- **Severity**: P1
- **Category**: Credential Compromise
- **Impact**: 120 users unable to authenticate

## Timeline
| Time | Event |
|------|-------|
| 14:30 | Alert: SSH key found in logs |
| 14:35 | Incident commander assigned |
| 14:40 | Investigation started |
| 14:50 | Credential revoked |
| 15:00 | New credential deployed |
| 15:45 | Service fully recovered |

## Root Cause
Developer accidentally committed SSH key during rebasing. Key was live for 15 minutes.

## Impact Assessment
- Accounts: 120 users (0.5%)
- Data: No unauthorized access detected
- Severity: Medium (detection was quick)

## Remediation
1. Revoked compromised key immediately
2. Rotated all related credentials
3. Deployed new authentication key
4. Implemented pre-commit hook to catch secrets

## Lessons Learned
- Pre-commit hooks are effective (this would have been caught)
- Our detection was rapid (15 minutes)
- Rotation procedures worked smoothly
- Team response was efficient

## Action Items
- [ ] Deploy pre-commit hook across all repos (engineer: @alice, due: 2026-06-16)
- [ ] Review SSH key handling procedures (owner: @bob, due: 2026-06-20)
- [ ] Training: Secret management best practices (owner: @carol, due: 2026-06-25)
```

### Post-Incident Meeting

**Within 48 hours**:
1. Review incident timeline
2. Discuss what went well
3. Discuss what could improve
4. Assign follow-up actions
5. Share learnings with team

---

**Document Version**: 2.0.0  
**Created**: 2026-06-14  
**Owner**: Security & Operations Team  
**Review Frequency**: Quarterly  
**Next Review**: 2026-09-14

---

*These playbooks are mandatory for all incident response.*
