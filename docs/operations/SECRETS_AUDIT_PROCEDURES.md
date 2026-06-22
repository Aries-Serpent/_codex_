# Secrets & Credentials Audit Procedures

**Document**: Operations & Investigation Guide  
**Audience**: Security Team, Incident Responders, Auditors  
**Last Updated**: 2026-06-14  
**Classification**: Internal  

---

## Executive Summary

This document provides procedures for conducting audits and investigations involving secrets and credentials, including:
- Quarterly compliance audits
- Incident investigation queries
- Access pattern analysis
- Compromise detection procedures

---

## 1. Quarterly Audit Procedures

### 1.1 Audit Checklist

- [ ] Verify all secrets properly scoped by environment
- [ ] Check for hardcoded credentials in source code
- [ ] Review rotation logs for compliance
- [ ] Verify no cross-environment secret sharing
- [ ] Check audit log integrity and completeness
- [ ] Test alert system functionality
- [ ] Verify backup key validity
- [ ] Document audit findings

### 1.2 Scoping Audit

**Procedure**:
```bash
#!/bin/bash
# 1. Export current secrets
gh secret list --repo Aries-Serpent/_codex_ > /tmp/secrets_audit.txt

# 2. Check environment-specific secrets
for env in production staging development; do
    echo "=== $env environment ==="
    grep -E "_${env^^}" /tmp/secrets_audit.txt || echo "✓ Clean"
done

# 3. Verify no cross-environment issues
if grep -E "_DEV.*_PRODUCTION|_STAGING.*_PRODUCTION" /tmp/secrets_audit.txt; then
    echo "⚠️  Cross-environment secrets detected!"
    exit 1
else
    echo "✓ All secrets properly scoped"
fi
```

---

## 2. Audit Log Analysis

### 2.1 Query Recent Access

```bash
#!/bin/bash
# Query: Who accessed CODEX_MASTER_KEY in last 7 days?

grep "CODEX_MASTER_KEY" .codex/aftermath/secrets_audit.jsonl | \
  jq 'select(.timestamp > "'$(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ)'") |
  {timestamp, actor: .actor.id, action: .action.type, status: .result.status}'
```

## 2.2 Analyze Access Patterns

```python
#!/usr/bin/env python3
# Analyze access patterns for anomalies

import json
from collections import defaultdict
from datetime import datetime, timedelta

def analyze_access_patterns():
    """Analyze audit logs for suspicious patterns"""

    access_by_actor = defaultdict(list)
    access_by_secret = defaultdict(list)  # pragma: allowlist secret
    failed_attempts = []

    # Read audit log
    with open(".codex/aftermath/secrets_audit.jsonl", "r") as f:  # pragma: allowlist secret
        for line in f:
            event = json.loads(line)

            actor = event["actor"]["id"]
            secret = event["action"]["secret_name"]  # pragma: allowlist secret
            status = event["result"]["status"]
            timestamp = event["timestamp"]

            access_by_actor[actor].append((secret, timestamp, status))  # pragma: allowlist secret
            access_by_secret[secret].append((actor, timestamp, status))  # pragma: allowlist secret

            if status == "failure":
                failed_attempts.append(event)

    # Analyze patterns
    print("🔍 ACCESS PATTERN ANALYSIS")
    print("=" * 50)

    # Check for excessive failed attempts
    if len(failed_attempts) > 10:
        print(f"⚠️  {len(failed_attempts)} failed access attempts")
        print("   Actors:")
        for event in failed_attempts[-5:]:
            print(f"   - {event['actor']['id']} at {event['timestamp']}")

    # Check for unusual access times
    print("\nAccess by time of day:")
    for actor, accesses in access_by_actor.items():
        hours = [
            datetime.fromisoformat(ts.replace("Z", "")).hour
            for _, ts, _ in accesses
        ]
        print(f"  {actor}: {set(hours)}")

    # Check for privilege escalation patterns
    print("\nPrivilege escalation audit:")
    for secret, accesses in access_by_secret.items():  # pragma: allowlist secret
        if "PRODUCTION" in secret:  # pragma: allowlist secret
            for actor, ts, status in accesses:
                if actor not in ["devops-lead", "security-lead"]:
                    print(f"  ⚠️  Unexpected access: {actor} to {secret}")  # pragma: allowlist secret

if __name__ == "__main__":
    analyze_access_patterns()
```

## 2.3 Incident Timeline Query

```bash
#!/bin/bash
# Build timeline of events around incident time

INCIDENT_TIME="2026-06-14T12:34:56Z"
WINDOW_HOURS=24

echo "📊 INCIDENT TIMELINE: $INCIDENT_TIME (±${WINDOW_HOURS}h window)"
echo "============================================================"

# Query audit logs
python3 << 'PYTHON'
import json
from datetime import datetime, timedelta

incident_time = datetime.fromisoformat("2026-06-14T12:34:56Z")
start = incident_time - timedelta(hours=24)
end = incident_time + timedelta(hours=24)

events = []
with open(".codex/aftermath/secrets_audit.jsonl", "r") as f:
    for line in f:
        event = json.loads(line)
        event_time = datetime.fromisoformat(event["timestamp"].replace("Z", ""))
        if start <= event_time <= end:
            events.append(event)

# Sort by timestamp
events.sort(key=lambda x: x["timestamp"])

# Print timeline
for event in events:
    offset = (
        datetime.fromisoformat(event["timestamp"].replace("Z", "")) - incident_time
    ).total_seconds() / 3600
    
    sign = "+" if offset >= 0 else ""
    print(f"{sign}{offset:6.1f}h: {event['actor']['id']:20} "
          f"{event['action']['type']:6} "
          f"{event['action']['secret_name']:25} "
          f"{event['result']['status']}")
PYTHON
```

---

## 3. Compromise Detection

### 3.1 Unauthorized Access Detection

```bash
#!/bin/bash
# Check for signs of compromise

echo "🔍 COMPROMISE DETECTION SCAN"
echo "============================="

# Check 1: Failed access attempts spike
echo "Recent failed access attempts:"
grep '"success": false' .codex/aftermath/secrets_audit.jsonl | \
  jq '.timestamp' | tail -20

# Check 2: Access from unexpected locations
echo ""
echo "Access patterns (should be from CI/CD only):"
grep 'CODEX_MASTER_KEY' .codex/aftermath/secrets_audit.jsonl | \
  jq '{actor: .actor.id, context: .context.workflow}' | sort | uniq -c

# Check 3: Off-hours access
echo ""
echo "Off-hours access (outside 8 AM - 6 PM UTC):"
grep 'CODEX_MASTER_KEY' .codex/aftermath/secrets_audit.jsonl | \
  jq 'select((.timestamp | split("T")[1] | split(":")[0] | tonumber) < 8 or 
            (.timestamp | split("T")[1] | split(":")[0] | tonumber) > 18)' | \
  jq '.timestamp'
```

## 3.2 Escalation Pattern Detection

```python
#!/usr/bin/env python3
# Detect privilege escalation attempts

import json
from collections import defaultdict

escalation_patterns = defaultdict(list)

with open(".codex/aftermath/secrets_audit.jsonl", "r") as f:  # pragma: allowlist secret
    for line in f:
        event = json.loads(line)

        # Pattern: Multiple failed attempts followed by success
        actor = event["actor"]["id"]
        status = event["result"]["status"]

        escalation_patterns[actor].append(status)

# Analyze for suspicious patterns
print("🔒 ESCALATION PATTERN DETECTION")
print("=" * 50)

for actor, statuses in escalation_patterns.items():
    # Pattern: 5+ failures then success = suspicious
    recent = statuses[-10:]
    failed_count = sum(1 for s in recent if s == "failure")

    if failed_count >= 5 and recent[-1] == "success":
        print(f"⚠️  SUSPICIOUS: {actor}")
        print(f"   Failed attempts: {failed_count}")
        print(f"   Pattern: Failures followed by success")
        print(f"   Action: INVESTIGATE")
```

---

## 4. Investigation Procedures

### 4.1 Credential Compromise Investigation

**Step 1: Confirm Compromise**
```bash
# Check if secret value changed unexpectedly
OLD_HASH=$(grep "ROTATION_START" .codex/key-archive/rotation-log.txt | \
  grep "old_key_hash" | tail -1)
CURRENT_HASH=$(grep "ROTATION_COMPLETE" .codex/key-archive/rotation-log.txt | \
  tail -1)

if [ "$OLD_HASH" != "$CURRENT_HASH" ]; then
    echo "✓ Confirmed: Key was rotated (expected)"
else
    echo "⚠️  WARNING: Key hash unchanged"
fi
```

**Step 2: Determine Scope**
```bash
# How long was key compromised?
FIRST_ACCESS=$(grep '"success": true' .codex/aftermath/secrets_audit.jsonl | \
  grep CODEX_MASTER_KEY | head -1 | jq '.timestamp')

LAST_NORMAL_ACCESS=$(grep '"success": true' .codex/aftermath/secrets_audit.jsonl | \
  grep CODEX_MASTER_KEY | grep -v github-action | head -1 | jq '.timestamp')

echo "Potentially compromised from: $FIRST_ACCESS"
echo "Until: $LAST_NORMAL_ACCESS"
```

**Step 3: Audit Impacted Systems**
```bash
# Check what systems used the compromised key
grep CODEX_MASTER_KEY .codex/aftermath/secrets_audit.jsonl | \
  jq '.context | {workflow, job_id, repository}' | sort | uniq

# For each job, check what actions were taken
gh api repos/Aries-Serpent/_codex_/actions/runs \
  --jq '.workflow_runs[] | select(.created_at > "2026-06-14") | 
  {id, status, conclusion, created_at}'
```

**Step 4: Containment**
```bash
# Immediately rotate key
bash docs/production/KEY_ROTATION_RUNBOOK.md

# Invalidate any generated artifacts during compromise window
echo "Invalidate artifacts created: 2026-06-14T12:34:56Z to $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

---

## 5. Reporting & Sign-off

### 5.1 Audit Report Template

```json
{
  "audit_date": "2026-06-14",
  "audit_type": "quarterly_compliance",
  "findings": {
    "scoping_compliance": "PASS",
    "rotation_schedule_compliance": "PASS",
    "no_hardcoded_secrets": "PASS", <!-- pragma: allowlist secret -->
    "audit_logging_completeness": "PASS"
  },
  "issues_found": 0,
  "remediation_items": [],
  "sign_off": {
    "auditor": "Security Lead",
    "date": "2026-06-14",
    "approved": true
  }
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-14
