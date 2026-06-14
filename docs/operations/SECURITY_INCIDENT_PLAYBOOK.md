# Security Incident Response Playbook

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainer**: Security Engineer  
**Classification**: Confidential - Internal Use Only  

---

## Executive Summary

This playbook provides structured procedures for detecting, responding to, and recovering from security incidents. It covers incident classification, containment, eradication, evidence preservation, and recovery workflows.

**Security SLA Response Times**:
- **Critical** (Data breach, RCE): 15 minutes to engage security team
- **High** (Privilege escalation, account compromise): 30 minutes to engage
- **Medium** (Suspicious activity, failed attempts): 2 hours to engage
- **Low** (Security configuration drift): 24 hours to engage

---

## Security Incident Classification

### Incident Severity Matrix

| Severity | Type | Example | Response | Escalation |
|----------|------|---------|----------|-----------|
| **Critical** | Data breach, RCE, account takeover | SQL injection successful, credentials exposed | Immediate | CEO, Legal, PR |
| **High** | Privilege escalation, malware detected | User elevated to admin, virus signature match | 30 min | Security Director, CTO |
| **Medium** | Suspicious activity, policy violation | Multiple failed logins, unusual API patterns | 2 hours | Security Lead, Manager |
| **Low** | Security config drift, patch needed | Outdated TLS version, missing WAF rule | 24 hours | Security team |

### Incident Triage Decision Tree

```
Security Alert Detected
  │
  ├─ Data accessed/exfiltrated?
  │   ├─ YES → CRITICAL - Immediate response
  │   └─ NO → Continue
  │
  ├─ System compromised (RCE, shell access)?
  │   ├─ YES → CRITICAL - Immediate response
  │   └─ NO → Continue
  │
  ├─ Credentials/tokens exposed?
  │   ├─ YES → HIGH - Escalate immediately
  │   └─ NO → Continue
  │
  ├─ Unauthorized access attempt (successful)?
  │   ├─ YES → HIGH - Escalate immediately
  │   └─ NO → Continue
  │
  ├─ Policy violation (intentional)?
  │   ├─ YES → MEDIUM - Investigate
  │   └─ NO → Continue
  │
  └─ Configuration drift/patch needed?
      └─ LOW - Schedule remediation
```

---

## Incident Detection

### 1.1 Security Monitoring Sources

**Sources of Security Alerts**:

1. **WAF (Web Application Firewall)**
   - SQL injection attempts
   - Cross-site scripting (XSS) attempts
   - Path traversal attacks

2. **IDS/IPS (Intrusion Detection/Prevention)**
   - Malicious traffic patterns
   - Port scanning activity
   - DDoS signatures

3. **SIEM (Security Information & Event Management)**
   - Failed authentication bursts
   - Privilege escalation attempts
   - Suspicious API calls

4. **Application Logs**
   - Unhandled exceptions
   - Authentication failures
   - Authorization failures

5. **Infrastructure Monitoring**
   - Unusual process execution
   - Unexpected network connections
   - File integrity changes

6. **Third-party Services**
   - HaveiBeenPwned database breach notification
   - GitHub secret scanning alerts
   - Dependency vulnerability warnings

### 1.2 Alert Configuration

**Critical Security Alerts**:

```bash
# Alert 1: SQL Injection Detection
Alert: WAF detects SQL injection pattern
Trigger: CRITICAL
Action: Block request, log IP, notify security

# Alert 2: Authentication Bypass
Alert: Multiple failed logins followed by success
Trigger: HIGH
Action: Force password reset, notify user, review access logs

# Alert 3: Privilege Escalation
Alert: User permission changed from user to admin
Trigger: CRITICAL
Action: Review RBAC change, revert if unauthorized

# Alert 4: Secret Detected in Repository
Alert: API key, database password in code commit
Trigger: CRITICAL
Action: Revoke secret, notify developer, audit access logs

# Alert 5: Suspicious API Pattern
Alert: High rate of failed API calls from single IP
Trigger: MEDIUM
Action: Rate limit IP, alert security, investigate

# Alert 6: Unsigned Code Execution
Alert: Process executing from unexpected location
Trigger: HIGH
Action: Quarantine pod, investigate process, audit logs
```

---

## Incident Response Workflow

### 2.1 Detection to Response (0-15 minutes)

**Step 1: Alert Acknowledgment**

```bash
# Upon receiving security alert:

# 1. Acknowledge alert in SIEM
# 2. Create incident ticket in security tracking system
# 3. Notify security team in Slack #security-incidents
# 4. Document alert details

INCIDENT_ID="SEC-2024-01-15-001"
ALERT_TYPE="SQL Injection Attempt"
ALERT_TIME=$(date)
SOURCE_IP="192.168.1.100"
TARGET="POST /api/v1/users"
PAYLOAD="'; DROP TABLE users; --"

# Store details
cat > /tmp/${INCIDENT_ID}-details.txt << EOF
Incident ID: ${INCIDENT_ID}
Detection Time: ${ALERT_TIME}
Alert Type: ${ALERT_TYPE}
Source IP: ${SOURCE_IP}
Target: ${TARGET}
Payload: ${PAYLOAD}
EOF
```

**Step 2: Initial Assessment**

```bash
# Quick assessment questions:
# - Is active attack ongoing?
# - Are systems compromised?
# - What is scope of attack?
# - Are there indicators in logs?

# Checklist:
- [ ] Alert verified as not false positive
- [ ] Attacker IP identified
- [ ] Affected systems identified
- [ ] Initial action taken (block IP, quarantine system)
- [ ] Security team assembled
- [ ] Executive notification prepared
```

**Step 3: Immediate Containment Action**

```bash
# For network-based attacks:
# Step 1: Block attacker IP
iptables -A INPUT -s ${SOURCE_IP} -j DROP

# Step 2: Enable enhanced logging
kubectl set env deployment/codex-api -n production DEBUG_LOGGING=true

# Step 3: Preserve evidence (logs, network packets)
tcpdump -i any -w /tmp/${INCIDENT_ID}-traffic.pcap

# For application-level attacks:
# Step 1: Disable affected endpoint
kubectl patch deployment codex-api -n production --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env", "value":[{"name":"DISABLE_VULNERABLE_ENDPOINT","value":"true"}]}]'

# Step 2: Increase monitoring on endpoint
# Step 3: Prepare rollback if needed
```

---

## Investigation and Analysis

### 3.1 Evidence Collection

**Procedure**:

```bash
# Step 1: Collect system logs
journalctl -u codex-api --since "2024-01-15 10:00:00" > /tmp/${INCIDENT_ID}-service-logs.txt
dmesg > /tmp/${INCIDENT_ID}-kernel-logs.txt

# Step 2: Collect application logs
kubectl logs deployment/codex-api -n production --all-containers --tail=10000 > /tmp/${INCIDENT_ID}-app-logs.txt

# Step 3: Collect network information
netstat -antp > /tmp/${INCIDENT_ID}-netstat.txt
ss -s > /tmp/${INCIDENT_ID}-socket-stats.txt

# Step 4: Collect process information
ps auxww > /tmp/${INCIDENT_ID}-processes.txt
lsof -p [PID] > /tmp/${INCIDENT_ID}-process-files.txt

# Step 5: Collect authentication logs
auth_logs=$(journalctl SYSLOG_IDENTIFIER=sshd --since "1 hour ago")
echo "$auth_logs" > /tmp/${INCIDENT_ID}-auth-logs.txt

# Step 6: Collect file integrity information
find / -newer /tmp/baseline -type f 2>/dev/null > /tmp/${INCIDENT_ID}-modified-files.txt

# Step 7: Collect database audit logs
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT * FROM audit_log WHERE timestamp > NOW() - INTERVAL '1 hour' ORDER BY timestamp DESC;" \
  > /tmp/${INCIDENT_ID}-db-audit.txt

# Step 8: Package all evidence
tar -czf /tmp/${INCIDENT_ID}-evidence.tar.gz /tmp/${INCIDENT_ID}-*
```

**Evidence Preservation**:

```bash
# Make evidence immutable
chattr +i /tmp/${INCIDENT_ID}-evidence.tar.gz

# Create hash for verification
sha256sum /tmp/${INCIDENT_ID}-evidence.tar.gz > /tmp/${INCIDENT_ID}-evidence.sha256

# Backup to secure location
aws s3 cp /tmp/${INCIDENT_ID}-evidence.tar.gz \
  s3://security-evidence-archive/${INCIDENT_ID}/evidence.tar.gz \
  --sse AES256 --storage-class GLACIER
```

### 3.2 Root Cause Analysis

**Analysis Procedures**:

```bash
# For SQL Injection:
1. Review WAF logs for pattern
   - What input field was vulnerable?
   - What query was executed?
   - Was it successful?

2. Check application code
   - Is query parameterized?
   - Is input sanitized?
   - What is vulnerable code path?

3. Audit database changes
   PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
     -c "SELECT * FROM pg_stat_statements WHERE query LIKE '%DROP%' OR query LIKE '%DELETE%';"

# For Account Compromise:
1. Review authentication logs for anomalies
2. Check access patterns (IP, location, time)
3. Review API calls from account
4. Audit permission changes
5. Check data access patterns

# For Privilege Escalation:
1. Review RBAC changes in Kubernetes
   kubectl get rolebindings -n production --all-namespaces -o wide
   
2. Check sudo/privileged command logs
   journalctl SYSLOG_IDENTIFIER=sudo

3. Review IAM policy changes
   aws iam list-role-policies --role-name prod-app-role

# For Malware/RCE:
1. Check running processes for anomalies
   ps auxww | grep -v "^root\|^USER" | sort -k3 -nr | head

2. Check network connections
   netstat -antp | grep ESTABLISHED

3. Check file system for unauthorized files
   find / -name "*.sh" -o -name "*.exe" -o -name "*backdoor*" 2>/dev/null

4. Check cron jobs and startup scripts
   crontab -l
   ls -la /etc/cron.d/
   ls -la /usr/local/bin/ | head -20
```

---

## Containment and Eradication

### 4.1 Containment Strategies

**Strategy 1: Network Containment**

```bash
# Isolate compromised system from network
# Option 1: Block IP at firewall
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp --port 22 \
  --cidr 10.0.0.0/8

# Option 2: Disconnect pod from cluster
kubectl delete pod ${POD_NAME} -n production

# Option 3: Enable network policy
kubectl apply -f - << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-compromised-pod
spec:
  podSelector:
    matchLabels:
      compromised: "true"
  policyTypes:
  - Ingress
  - Egress
EOF
```

**Strategy 2: Access Revocation**

```bash
# Revoke compromised credentials
# Step 1: Rotate database password
ALTER USER codex_admin PASSWORD 'new_secure_password_here'; <!-- pragma: allowlist secret -->

# Step 2: Rotate API keys
aws apigateway create-api-key --name "prod-api-key-$(date +%s)" --enabled

# Step 3: Invalidate all sessions
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "DELETE FROM sessions WHERE created_at < NOW();"

# Step 4: Update RBAC
kubectl delete rolebinding suspicious-binding -n production
kubectl create rolebinding restricted-binding \
  --clusterrole=edit \
  --serviceaccount=production:default \
  -n production
```

**Strategy 3: Malware Eradication**

```bash
# Step 1: Identify malicious process
MALICIOUS_PID=12345

# Step 2: Capture process memory for analysis
gcore -o /tmp/${INCIDENT_ID}-core ${MALICIOUS_PID}

# Step 3: Terminate process
kill -9 ${MALICIOUS_PID}

# Step 4: Remove malicious files
find / -name "*malware*" -o -name "*backdoor*" 2>/dev/null | xargs rm -f

# Step 5: Reinstall from clean image
kubectl delete pod ${POD_NAME} -n production
# Pod will restart with clean image from registry
```

### 4.2 Eradication

**Eradication Steps**:

```bash
# Step 1: Patch vulnerability
# Apply security patch or code fix
git apply /tmp/security-patch.diff
docker build -t codex-api:patched -f Dockerfile.prod .
docker push ${REGISTRY}/codex-api:patched

# Step 2: Verify fix
# Run tests to verify vulnerability closed
./tests/security/sql-injection-test.sh
./tests/security/xss-test.sh

# Step 3: Force password reset for affected users
# Query affected accounts
AFFECTED_USERS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT id FROM users WHERE last_login > NOW() - INTERVAL '24 hours';")

# Invalidate their sessions
for user_id in $AFFECTED_USERS; do
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
    -c "DELETE FROM sessions WHERE user_id = ${user_id};"
done

# Step 4: Apply WAF rules to prevent recurrence
# Add rule blocking SQL injection patterns
aws wafv2 update-web-acl \
  --name prod-waf \
  --region us-east-1 \
  --scope REGIONAL \
  --rules '[{...sql_injection_rule...}]'
```

---

## Recovery and Validation

### 5.1 System Recovery

**Recovery Procedure**:

```bash
# Step 1: Verify vulnerability is patched
./tests/security/vulnerability-scan.sh

# Step 2: Restore from clean backup if needed
# Only if system is compromised beyond repair
# Pre-incident backup available

# Restore database
BACKUP_ID="secure-backup-2024-01-15-08-00"
PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -U $DB_USER -d codex_prod \
  s3://security-backups/${BACKUP_ID}.dump

# Restore application
kubectl set image deployment/codex-api codex-api=${CLEAN_IMAGE} -n production

# Step 3: Verify integrity
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
  -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM orders;"

# Step 4: Validate system functionality
./tests/smoke-tests/critical-paths.sh
```

### 5.2 Post-Incident Validation

**Validation Checklist**:

- [ ] Vulnerability is patched/closed
- [ ] No unauthorized changes remain
- [ ] Credentials rotated
- [ ] Logs show no further malicious activity (24 hours)
- [ ] Performance metrics normal
- [ ] All security tests passing
- [ ] Monitoring rules updated to detect similar attacks
- [ ] Incident documentation complete

---

## Incident Communication

### 6.1 Internal Communication

**Internal Notification Sequence**:

```
T+0: Security alert detected
  └─ Notify: Security team in #security-incidents

T+5: Incident assessment complete
  └─ Notify: Engineering director, on-call lead
  └─ Notify: Product lead if customer-impacting

T+15: Containment actions initiated
  └─ Update: Executive summary in Slack
  └─ Create: Internal incident ticket

T+30: Root cause identified
  └─ Brief: Management team on findings

T+60: Mitigation in progress
  └─ Update: All stakeholders on remediation steps

T+24h: Post-incident review
  └─ Brief: Full team on lessons learned
```

### 6.2 Customer Communication

**Decision Tree for Customer Notification**:

```
Was customer data accessed?
  ├─ YES → Immediate notification (GDPR/CCPA requirement)
  │   └─ Notify: Affected customers, regulators if required
  │
  └─ NO → Were systems unavailable?
      ├─ YES (> 1 hour) → Notify: Customers of incident
      │   └─ Emphasize: No data access, system restored, security review ongoing
      │
      └─ NO → No customer notification required
          └─ Publish: General security update in blog/security page
```

**Customer Notification Template**:

```
Subject: Security Incident Update - [Company Name]

Dear Valued Customers,

We want to inform you about a security incident we detected and 
immediately contained on [date] at [time] UTC.

INCIDENT DETAILS:
- Type: [Incident type, e.g., "Unauthorized access attempt"]
- Duration: [Start time] to [end time] UTC
- Status: Resolved and secured

WHAT WE FOUND:
- [Description of what happened in plain language]
- [Any data potentially affected]
- [Current status of investigation]

WHAT WE DID:
- Immediately isolated the affected system
- Revoked all potentially compromised credentials
- Patched the vulnerability
- Enhanced monitoring to prevent recurrence

WHAT YOU SHOULD DO:
- [If password reset needed]: "We recommend you change your password"
- [If data breach]: "Monitor accounts for suspicious activity"
- [If service disrupted]: "No action needed, service is now restored"

For detailed information and support:
- Security Update: https://security.codex.com/incidents/[incident_id]
- Support: security@codex.com / 1-800-CODEX-911

We take your security seriously and appreciate your trust.

Regards,
Security Team
```

---

## Post-Incident Review

### 7.1 Post-Incident Review Meeting (Within 48 hours)

**Review Agenda**:

1. **Timeline Review** (15 min)
   - When was incident detected?
   - When was it contained?
   - When was it resolved?
   - Identify gaps in response time

2. **Root Cause Analysis** (20 min)
   - What was the vulnerability?
   - Why wasn't it caught in testing?
   - Why didn't monitoring detect it earlier?

3. **Response Effectiveness** (15 min)
   - Were procedures effective?
   - What worked well?
   - What could be improved?

4. **Prevention Actions** (20 min)
   - How do we prevent this in future?
   - What additional testing/scanning needed?
   - What monitoring improvements needed?
   - Who owns action items and when?

5. **Communication Review** (10 min)
   - Was communication timely?
   - Were stakeholders properly informed?
   - Any communication improvements?

### 7.2 Post-Incident Report

**Report Structure**:

```markdown
# Post-Incident Security Report: SEC-2024-01-15-001

## Executive Summary
[Brief summary of incident and impact]

## Incident Timeline
- T+0: [Alert triggered]
- T+5: [Incident classified]
- T+15: [Containment begun]
- T+30: [Root cause identified]
- T+120: [System recovered]
- T+1440: [All-clear confirmed]

## Root Cause
[Technical details of vulnerability]

## Impact Assessment
- Systems affected: [List of systems]
- Data exposed: [If any, describe]
- User impact: [Quantify impact]
- Availability impact: [Duration of disruption]

## Response Actions
- Immediate: [What was done immediately]
- Containment: [How was spread prevented]
- Eradication: [How was vulnerability fixed]
- Recovery: [How was system restored]

## Prevention Actions
- [Action 1]: Owner: [Name], Due: [Date]
- [Action 2]: Owner: [Name], Due: [Date]
- [Action 3]: Owner: [Name], Due: [Date]

## Lessons Learned
- [Learning 1]
- [Learning 2]
- [Learning 3]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add SAST scanning to CI/CD | Security | 2024-02-01 | In Progress |
| Update WAF rules | Ops | 2024-01-31 | Pending |
| Security training for team | HR | 2024-03-01 | Not Started |
```

---

## Security Incident Response Contact Tree

**Escalation Contacts**:

```
Security Incident
  │
  ├─ SEV-Critical
  │   ├─ On-Call Security: [Phone: _____, Slack: @security-oncall]
  │   ├─ Security Director: [Phone: _____, Slack: @security-director]
  │   ├─ CTO: [Phone: _____, Slack: @cto]
  │   └─ CEO: [Phone: _____, Slack: @ceo]
  │
  ├─ SEV-High
  │   ├─ On-Call Security: [Phone: _____, Slack: @security-oncall]
  │   ├─ Security Manager: [Phone: _____, Slack: @security-manager]
  │   └─ Engineering Director: [Phone: _____, Slack: @eng-director]
  │
  └─ SEV-Medium/Low
      ├─ Security Team: [Slack: #security-team]
      └─ Security Lead: [Slack: @security-lead]
```

---

## Appendix: Security Tools and Commands

**Vulnerability Scanning**:
```bash
# SAST: Static Application Security Testing
semgrep --config=p/security-audit --json -o semgrep-results.json .

# Dependency scanning
pip-audit
npm audit
cargo audit

# Container scanning
trivy image codex-api:latest
```

**Network Security**:
```bash
# Check open ports
netstat -tlnp

# Check firewall rules
sudo iptables -L -n -v

# Check network policies
kubectl get networkpolicies -n production
```

---

**Document Version**: 1.0  
**Last Reviewed**: 2024-01-15  
**Next Review Date**: 2024-02-15
