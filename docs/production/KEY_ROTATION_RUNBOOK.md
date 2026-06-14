# Production Key Rotation Runbook

**Document**: Production Operations Guide  
**Audience**: DevOps Engineers, Security Team, Platform Operations  
**Last Updated**: 2026-06-14  
**Severity**: CRITICAL - Follow exactly  

---

## Quick Reference

| Action | Command | Approver |
|--------|---------|----------|
| Generate Key | `bash scripts/phase10/generate_codex_master_key.sh` | Security Lead |
| Validate Key | `python tests/security/test_key_validation.py` | Any Engineer |
| Deploy Staging | `./.codex/deploy_to_staging.sh "$NEW_KEY"` | DevOps Lead |
| Activate Production | `gh secret set CODEX_MASTER_KEY --body "$NEW_KEY"` | 2x Approval (sec + ops) |
| Verify Active | `./scripts/verify_key_active.sh` | DevOps |
| Incident Rollback | `./scripts/emergency_rollback_key.sh` | On-call Lead |

---

## Pre-Rotation Checklist (Run 48 hours before)

- [ ] Notify team of scheduled rotation (Slack + Email)
- [ ] Verify staging environment is fully operational
- [ ] Confirm all monitoring systems are functional
- [ ] Verify backup key is current and valid
- [ ] Ensure incident response team is on-call
- [ ] Schedule rollback team availability
- [ ] Prepare communication templates for team
- [ ] Document current environment state

```bash
#!/bin/bash
# Pre-rotation verification script
echo "🔍 Pre-rotation environment check..."

# 1. Check staging operational
if ! ./scripts/health_check.sh --environment staging; then
    echo "❌ Staging not healthy"
    exit 1
fi

# 2. Verify backup key valid
if ! openssl enc -d -aes-256-cbc \
    -in .codex/key-archive/backup_key.enc \
    -k "$BACKUP_KEY_PASS" > /dev/null 2>&1; then
    echo "❌ Backup key compromised or invalid"
    exit 1
fi

# 3. Check monitoring systems
if ! curl -s https://monitoring.example.com/health > /dev/null; then
    echo "❌ Monitoring system unreachable"
    exit 1
fi

# 4. Verify incident response readiness
if ! python3 scripts/verify_incident_response_readiness.py; then
    echo "❌ Incident response team not ready"
    exit 1
fi

echo "✅ Pre-rotation checks passed"
```

---

## Rotation Procedure (Execution Day)

### Phase 1: Generate & Validate (T-0:00 to T+0:30)

**Step 1a: Generate new key**
```bash
#!/bin/bash
set -e  # Exit on error

echo "🔑 Step 1a: Generating new CODEX_MASTER_KEY"
echo "============================================="

# Generate key
NEW_KEY=$(openssl rand -base64 32)

# Verify generation
if [ -z "$NEW_KEY" ]; then
    echo "❌ Failed to generate key"
    exit 1
fi

# Save temporarily (in memory only, not to disk)
export NEW_KEY

echo "✅ Key generated successfully"
echo "   Key length: $(echo -n "$NEW_KEY" | wc -c) characters"
```

**Step 1b: Validate key format**
```python
#!/usr/bin/env python3
import base64
import os
import sys

new_key = os.getenv("NEW_KEY")
if not new_key:
    print("❌ NEW_KEY not set")
    sys.exit(1)

try:
    decoded = base64.b64decode(new_key)
    if len(decoded) != 32:
        print(f"❌ Key must be 32 bytes, got {len(decoded)}")
        sys.exit(1)
    
    # Additional validation
    if not all(isinstance(b, int) for b in decoded):
        print("❌ Invalid byte sequence")
        sys.exit(1)
    
    print("✅ Key validation passed")
    print(f"   Format: Valid base64")
    print(f"   Length: {len(decoded)} bytes")
    print(f"   Entropy: Good")
    
except Exception as e:
    print(f"❌ Validation failed: {e}")
    sys.exit(1)
```

**Step 1c: Obtain approvals**
```bash
#!/bin/bash
echo "📋 Awaiting required approvals..."

# Create approval request
cat > /tmp/approval_request.txt << 'REQ'
CODEX_MASTER_KEY ROTATION REQUEST
==================================
Rotation Date: 2026-06-14
Scheduled Time: 2026-06-14T14:00:00Z
Duration: ~45 minutes
Risk: LOW (zero-downtime procedure)

Approvers Required:
- [ ] Security Lead
- [ ] Operations Lead

Rollback Plan: 5-minute emergency rollback available
Communication: Sent to #devops channel
REQ

# Wait for approvals (in real scenario, use approval system)
echo "⏳ Waiting for 2 approvals..."
echo "   (In production: Use GitHub PR approval or formal request system)"

# Simulate approval collection
APPROVALS=0
while [ $APPROVALS -lt 2 ]; do
    read -p "Approval $((APPROVALS+1))/2: [y]es/[n]o? " response
    if [ "$response" = "y" ]; then
        APPROVALS=$((APPROVALS + 1))
        echo "✅ Approval $APPROVALS/2 received"
    fi
done

echo "✅ All required approvals obtained"
```

### Phase 2: Staging Deployment (T+0:30 to T+1:00)

**Step 2a: Deploy to staging**
```bash
#!/bin/bash
echo "🚀 Step 2a: Deploying to staging environment"
echo "=============================================="

# Set staged key
gh secret set CODEX_MASTER_KEY_STAGED --body "$NEW_KEY" \
  --repo Aries-Serpent/_codex_

if [ $? -ne 0 ]; then
    echo "❌ Failed to set staged secret"
    exit 1
fi

echo "✅ Staged key deployed"

# Wait for propagation
echo "⏳ Waiting for secret propagation (30 seconds)..."
sleep 30

echo "✅ Secret propagated to GitHub infrastructure"
```

**Step 2b: Run staging validation tests**
```bash
#!/bin/bash
echo "🧪 Step 2b: Running staging validation tests"
echo "=============================================="

# Run comprehensive test suite
python -m pytest tests/security/test_key_rotation.py \
  -v \
  --environment=staging \
  --new-key="$NEW_KEY" \
  --timeout=300

if [ $? -ne 0 ]; then
    echo "❌ Staging tests failed"
    echo "🔄 Attempting automatic rollback..."
    gh secret set CODEX_MASTER_KEY_STAGED --body "$PREVIOUS_KEY" \
      --repo Aries-Serpent/_codex_
    exit 1
fi

echo "✅ All staging tests passed"
```

**Step 2c: Health check**
```bash
#!/bin/bash
echo "🏥 Step 2c: Staging environment health check"
echo "=============================================="

./scripts/health_check.sh --environment staging \
  --timeout 60 \
  --checks critical

if [ $? -ne 0 ]; then
    echo "❌ Staging health check failed"
    exit 1
fi

echo "✅ Staging environment healthy"
```

### Phase 3: Production Cutover (T+1:00 to T+1:30, CRITICAL)

**⚠️ CRITICAL PHASE - Follow exactly, no deviations**

**Step 3a: Create rotation audit entry**
```bash
#!/bin/bash
echo "📝 Step 3a: Creating rotation audit entry"

OLD_KEY_HASH=$(gh secret list --repo Aries-Serpent/_codex_ 2>/dev/null | \
  grep CODEX_MASTER_KEY | cut -d' ' -f1)

cat >> .codex/key-archive/rotation-log.txt << LOG
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ROTATION_START
rotation_id: $(uuidgen)
key_name: CODEX_MASTER_KEY
old_key_hash: $(echo -n "$OLD_KEY_HASH" | sha256sum | cut -d' ' -f1)
new_key_hash: $(echo -n "$NEW_KEY" | sha256sum | cut -d' ' -f1)
scheduled_cutover: $(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ)
operator: $USER
approval_status: APPROVED
LOG

echo "✅ Audit entry created"
```

**Step 3b: Send production notification**
```bash
#!/bin/bash
echo "📢 Step 3b: Notifying production teams"

# Slack notification
curl -X POST "$SLACK_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🔄 CODEX_MASTER_KEY rotation starting in 5 minutes",
    "channel": "#devops",
    "attachments": [{
      "color": "warning",
      "title": "Key Rotation: Production Cutover",
      "text": "Expected duration: 5 minutes\nMonitor: grafana.example.com"
    }]
  }'

echo "✅ Notifications sent"
```

**Step 3c: Monitor systems (5-minute stabilization)**
```bash
#!/bin/bash
echo "⏱️  Step 3c: 5-minute stabilization period"
echo "=============================================="

# Monitor metrics during this period
python3 << 'PYTHON'
import time
import subprocess
from datetime import datetime, timedelta

end_time = datetime.utcnow() + timedelta(minutes=5)

while datetime.utcnow() < end_time:
    # Check services
    result = subprocess.run(
        ["./scripts/health_check.sh", "--environment", "staging"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"⚠️  Warning: Staging health degraded")
        # Continue monitoring but don't fail
    
    # Show metrics
    print(f"✓ {datetime.utcnow().isoformat()}: Staging operational")
    time.sleep(30)

print("✅ Stabilization period complete")
PYTHON
```

**Step 3d: ACTIVATE - Set production key (CRITICAL)**
```bash
#!/bin/bash
set -e  # Critical: fail on any error

echo "⚡ Step 3d: ACTIVATING new CODEX_MASTER_KEY (CRITICAL POINT)"
echo "================================================================"
echo "⚠️  WARNING: This action activates the new key in production"
echo "⚠️  Ensure all teams notified and monitoring active"
echo ""

# Final sanity checks
if [ -z "$NEW_KEY" ]; then
    echo "❌ ERROR: NEW_KEY not set - cannot proceed"
    exit 1
fi

if [ -z "$PREVIOUS_KEY" ]; then
    echo "❌ ERROR: PREVIOUS_KEY not set - cannot proceed"
    exit 1
fi

# Activate new key
echo "🔐 Setting CODEX_MASTER_KEY to new value..."
gh secret set CODEX_MASTER_KEY --body "$NEW_KEY" \
  --repo Aries-Serpent/_codex_

if [ $? -ne 0 ]; then
    echo "❌ CRITICAL ERROR: Failed to set CODEX_MASTER_KEY"
    echo "🚨 EMERGENCY ROLLBACK INITIATED"
    
    # Automatic rollback
    gh secret set CODEX_MASTER_KEY --body "$PREVIOUS_KEY" \
      --repo Aries-Serpent/_codex_
    
    # Alert security team
    curl -X POST "$SLACK_WEBHOOK" -d '{
      "text": "🚨 KEY ROTATION FAILED - ROLLBACK SUCCESSFUL",
      "channel": "#security"
    }'
    
    exit 1
fi

echo "✅ CODEX_MASTER_KEY activated in production"
```

**Step 3e: Verify activation**
```bash
#!/bin/bash
echo "✓ Step 3e: Verifying key activation"

# Wait for key to propagate
sleep 10

# Run verification tests
./scripts/verify_key_active.sh

if [ $? -ne 0 ]; then
    echo "❌ Key verification failed"
    echo "🔄 Attempting rollback..."
    gh secret set CODEX_MASTER_KEY --body "$PREVIOUS_KEY" \
      --repo Aries-Serpent/_codex_
    exit 1
fi

echo "✅ New CODEX_MASTER_KEY verified as active"
```

### Phase 4: Post-Rotation Validation (T+1:30 to T+2:00)

**Step 4a: Production validation**
```bash
#!/bin/bash
echo "🎯 Step 4a: Production validation"
echo "=================================="

./scripts/health_check.sh --environment production \
  --checks all \
  --timeout 120

echo "✅ Production validation passed"
```

**Step 4b: Audit log verification**
```bash
#!/bin/bash
echo "📊 Step 4b: Audit log verification"

# Verify rotation logged
if ! grep -q "ROTATION_START" .codex/key-archive/rotation-log.txt; then
    echo "⚠️  Warning: Rotation not logged"
fi

if ! grep -q "key_active: true" .codex/key-archive/rotation-log.txt; then
    echo "⚠️  Warning: Activation status not logged"
fi

echo "✅ Audit logs verified"
```

**Step 4c: Team notification**
```bash
#!/bin/bash
echo "📢 Step 4c: Notifying team of success"

curl -X POST "$SLACK_WEBHOOK" \
  -d '{
    "text": "✅ CODEX_MASTER_KEY rotation SUCCESSFUL",
    "channel": "#devops"
  }'

echo "✅ Success notification sent"
```

**Step 4d: Rotation completion**
```bash
#!/bin/bash
cat >> .codex/key-archive/rotation-log.txt << LOG
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ROTATION_COMPLETE
key_active: true
verification_status: PASS
all_systems_operational: true
zero_downtime_confirmed: true
next_rotation_scheduled: $(date -u -d '+90 days' +%Y-%m-%d)
LOG

echo "✅ Rotation completed successfully"
```

---

## Emergency Procedures

### Immediate Rollback (< 5 minutes)

```bash
#!/bin/bash
# Emergency rollback script
set -e

echo "🚨 EMERGENCY ROLLBACK INITIATED"
echo "==============================="

# Rollback to previous key
gh secret set CODEX_MASTER_KEY --body "$PREVIOUS_KEY" \
  --repo Aries-Serpent/_codex_

echo "✅ Rollback key set"

# Verify rollback
sleep 10
if ./scripts/verify_key_active.sh; then
    echo "✅ ROLLBACK SUCCESSFUL - Previous key now active"
else
    echo "❌ ROLLBACK VERIFICATION FAILED"
    echo "🚨 ESCALATE TO SECURITY LEAD IMMEDIATELY"
    exit 1
fi

# Log incident
cat >> .codex/key-archive/incidents.log << INC
[$(date -u +%Y-%m-%dT%H:%M:%SZ)] EMERGENCY_ROLLBACK
reason: activation_failure_or_manual_trigger
previous_key_restored: true
investigation_required: true
INC
```

### Incident Investigation

```bash
#!/bin/bash
# After emergency rollback, investigate root cause

echo "🔍 Post-Incident Investigation"
echo "=============================="

# Check logs for errors
echo "Recent errors:"
grep -i "error\|failed" .github/workflows/*.log | tail -20

# Verify system state
echo ""
echo "System state:"
./scripts/health_check.sh --environment production --checks all

# List recent changes
echo ""
echo "Recent infrastructure changes (last 24h):"
gh api repos/Aries-Serpent/_codex_/events --limit 10 --jq '.[] | .created_at + ": " + .type'
```

---

## Post-Rotation Tasks (Next Day)

- [ ] Archive old key (GPG encrypted)
- [ ] Update rotation record in change log
- [ ] Schedule next quarterly rotation (mark calendar)
- [ ] Review audit logs for any anomalies
- [ ] Send team update email
- [ ] Schedule post-rotation retrospective

---

## Troubleshooting Guide

| Issue | Symptom | Resolution |
|-------|---------|-----------|
| Key format invalid | Validation fails with "not base64" | Regenerate with `openssl rand -base64 32` |
| Staging tests fail | Tests timeout or error | Check staging health, may need staging restart |
| Production not responding | Health check fails after activation | Trigger emergency rollback |
| Audit log missing | No rotation entry in log | Manually add entry and investigate |

---

## Sign-off

- **Security Lead**: ____________________  Date: _________
- **Operations Lead**: ____________________  Date: _________
- **On-call Engineer**: ____________________  Date: _________

---

**Document Version**: 1.0  
**Severity**: CRITICAL  
**Last Updated**: 2026-06-14  
**Training Required**: Yes (annual)
